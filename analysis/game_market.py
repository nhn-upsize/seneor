"""
연도별/월별 게임 시장 지표 분석.

전략: API는 최초 1회만 호출 → .cache/ 저장 → 이후 분석은 로컬 데이터.
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from client import SensorTowerClient
from endpoints.sales import SalesEndpoint
from endpoints.advertising import AdvertisingEndpoint
from endpoints.retention import RetentionEndpoint
from endpoints.apps import AppsEndpoint


def build_client() -> SensorTowerClient:
    return SensorTowerClient(use_cache=True)


# ────────────────────────────────────────────────────────────────
# 통합 연도별 리포트
# ────────────────────────────────────────────────────────────────
def yearly_game_market_report(
    years: list,
    os: str = "ios",
    country: str = "US",
    category: int = 6014,
    chart_type: str = "topgrossingapplications",
    save_xlsx: bool = True,
) -> dict:
    """
    연도별 게임 시장 종합 리포트.

    수집 지표:
      - 신규 진입 게임 (Top Chart 기반 + release_date 필터)
      - 월별 매출 / 다운로드
      - 광고 집행률 (%)
      - Day-1/7/14/30 잔존율

    Returns:
        { year: {
            "new_entries": DataFrame,
            "monthly_ranking": DataFrame,
            "monthly_revenue": DataFrame,
            "ad_stats": dict,
            "retention": DataFrame,
        }}
    """
    client = build_client()
    apps_ep = AppsEndpoint(client)
    sales_ep = SalesEndpoint(client)
    ad_ep = AdvertisingEndpoint(client)
    ret_ep = RetentionEndpoint(client)

    report = {}

    for year in years:
        print(f"\n{'='*50}")
        print(f"  {year}년 게임 시장 분석 시작")
        print(f"{'='*50}")

        # ── 1. 월별 Top Chart 수집 ────────────────────────────
        print(f"[1/4] 월별 Top Chart 순위 수집...")
        monthly_ranking = apps_ep.get_monthly_rankings(
            year=year, os=os, country=country,
            category=category, chart_type=chart_type,
        )

        # ── 2. 신규 게임 식별 ─────────────────────────────────
        print(f"[2/4] 신규 진입 게임 식별...")
        unique_ids = monthly_ranking["app_id"].unique().tolist() if not monthly_ranking.empty else []
        details_df = apps_ep.get_app_details(app_ids=unique_ids, os=os) if unique_ids else pd.DataFrame()

        if not details_df.empty and "release_date" in details_df.columns:
            details_df["release_date"] = pd.to_datetime(details_df["release_date"], errors="coerce")
            new_entries = details_df[details_df["release_date"].dt.year == year].copy()
            # 첫 차트 진입 월
            if not monthly_ranking.empty:
                first_entry = (
                    monthly_ranking.groupby("app_id")["month"].min()
                    .reset_index().rename(columns={"month": "first_chart_month"})
                )
                new_entries = new_entries.merge(first_entry, on="app_id", how="left")
        else:
            new_entries = pd.DataFrame()

        new_ids = new_entries["app_id"].astype(str).tolist() if not new_entries.empty and "app_id" in new_entries.columns else []
        print(f"  → 차트 내 신규 게임: {len(new_entries)}개 / 전체 차트 앱: {len(unique_ids)}개")

        # ── 3. 월별 매출/다운로드 ─────────────────────────────
        print(f"[3/4] 월별 매출/다운로드 수집...")
        if unique_ids:
            raw_sales = sales_ep.get_sales_estimates(
                app_ids=unique_ids[:100],
                start_date=f"{year}-01-01",
                end_date=f"{year}-12-31",
                os=os,
                country=country,
                granularity="monthly",
            )
            monthly_revenue = sales_ep.aggregate_by_month(raw_sales)
        else:
            monthly_revenue = pd.DataFrame()

        # 신규 게임만 필터링한 매출
        if not monthly_revenue.empty and new_ids and "app_id" in monthly_revenue.columns:
            new_revenue = monthly_revenue[monthly_revenue["app_id"].astype(str).isin(new_ids)]
        else:
            new_revenue = pd.DataFrame()

        # ── 4. 광고 집행률 ────────────────────────────────────
        print(f"[4/4] 광고 집행 & 잔존율 수집...")
        if new_ids:
            ad_stats = ad_ep.calc_ad_rate(
                app_ids=new_ids[:50],
                start_date=f"{year}-01-01",
                end_date=f"{year}-12-31",
                os=os,
                country=country,
            )
            retention = ret_ep.get_retention(
                app_ids=new_ids[:50],
                start_date=f"{year}-01-01",
                end_date=f"{year}-12-31",
                os=os,
                country=country,
                retention_days=[1, 7, 14, 30],
            )
        else:
            ad_stats = {"total_apps": 0, "advertising_apps": 0, "ad_rate_pct": 0.0, "detail_df": pd.DataFrame()}
            retention = pd.DataFrame()

        result = {
            "new_entries":      new_entries,
            "monthly_ranking":  monthly_ranking,
            "monthly_revenue":  monthly_revenue,
            "new_game_revenue": new_revenue,
            "ad_stats":         ad_stats,
            "retention":        retention,
        }
        report[year] = result

        # ── 엑셀 저장 ─────────────────────────────────────────
        if save_xlsx:
            _save_xlsx(year, result)

    # 요약 출력
    _print_summary(report)
    return report


def _strip_tz(df: pd.DataFrame) -> pd.DataFrame:
    """Excel 저장을 위해 timezone-aware datetime 컬럼의 tz 제거."""
    df = df.copy()
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
    return df


def _save_xlsx(year: int, result: dict):
    out = Path(__file__).parent.parent / f"report_{year}.xlsx"
    sheet_map = {
        "new_entries":      "신규게임목록",
        "monthly_ranking":  "월별차트순위",
        "monthly_revenue":  "월별매출전체",
        "new_game_revenue": "신규게임월별매출",
        "retention":        "잔존율",
    }
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        # 요약 시트
        ad = result["ad_stats"]
        summary = pd.DataFrame([{
            "연도": year,
            "신규 게임 수": len(result["new_entries"]),
            "차트 전체 앱 수": result["monthly_ranking"]["app_id"].nunique() if not result["monthly_ranking"].empty else 0,
            "광고 집행 앱 수": ad.get("advertising_apps", 0),
            "광고 집행률 (%)": ad.get("ad_rate_pct", 0),
        }])
        summary.to_excel(writer, sheet_name="요약", index=False)

        for key, sheet_name in sheet_map.items():
            df = result.get(key)
            if isinstance(df, pd.DataFrame) and not df.empty:
                _strip_tz(df).to_excel(writer, sheet_name=sheet_name, index=False)

        # 광고 크리에이티브 상세
        ad_detail = ad.get("detail_df", pd.DataFrame())
        if not ad_detail.empty:
            _strip_tz(ad_detail).to_excel(writer, sheet_name="광고크리에이티브", index=False)

    print(f"  [저장] {out.name}")


def _print_summary(report: dict):
    print(f"\n{'='*50}")
    print("  연도별 분석 결과 요약")
    print(f"{'='*50}")
    for year, data in report.items():
        ne = len(data["new_entries"])
        ar = data["ad_stats"].get("ad_rate_pct", 0)
        total = data["monthly_ranking"]["app_id"].nunique() if not data["monthly_ranking"].empty else 0
        print(f"  {year}: 신규게임 {ne}개 | 차트 전체 {total}개 | 광고집행률 {ar}%")


# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    report = yearly_game_market_report(
        years=[2022, 2023, 2024],
        os="ios",
        country="US",
        category=6014,
        chart_type="topgrossingapplications",
        save_xlsx=True,
    )
