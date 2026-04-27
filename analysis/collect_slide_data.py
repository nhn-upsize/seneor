"""
3개 신규 슬라이드용 데이터 수집 스크립트.
캐싱으로 API 호출 최소화.
"""
import sys, json
from pathlib import Path
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from client import SensorTowerClient
from endpoints.apps import AppsEndpoint
from endpoints.sales import SalesEndpoint
from endpoints.retention import RetentionEndpoint

c = SensorTowerClient(use_cache=True)
apps_ep = AppsEndpoint(c)
sales_ep = SalesEndpoint(c)

# ── 분석 기간 ────────────────────────────────────────────────────
MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)   # 51개월

COUNTRIES  = ["KR", "US", "JP", "CN"]
CHART_TYPE = "topgrossingapplications"
CATEGORY   = 6014   # iOS Games
TARGET_RANKS = [1, 10, 20, 50, 100]


# ════════════════════════════════════════════════════════════════
# [공통] 국가×월별 TOP100 랭킹 수집
# ════════════════════════════════════════════════════════════════
def fetch_all_rankings():
    """country × month 전체 랭킹 수집 → dict {(country, YYYY-MM): [app_id, ...]}"""
    print("=== 국가×월별 TOP100 랭킹 수집 ===")
    rankings = {}
    for country in COUNTRIES:
        for dt in MONTHS:
            key = (country, dt.strftime("%Y-%m"))
            data = c.get("/v1/ios/ranking",
                         category=CATEGORY,
                         chart_type=CHART_TYPE,
                         date=dt.strftime("%Y-%m-%d"),
                         country=country)
            rankings[key] = data.get("ranking", []) if isinstance(data, dict) else []
    print(f"  수집 완료: {len(rankings)}개 (국가×월)")
    return rankings


# ════════════════════════════════════════════════════════════════
# SLIDE 1: 3개월 유지 vs 미유지 게임 — 매출·다운로드 프로파일
# ════════════════════════════════════════════════════════════════
def collect_slide1(rankings: dict, country: str = "US"):
    """
    신규 진입 게임을 '3개월 이상 유지'와 '3개월 미만 탈락'으로 분류.
    각 그룹의 진입 첫 달 매출/다운로드를 비교.
    """
    print(f"\n=== SLIDE 1: 3개월 유지 vs 탈락 ({country}) ===")

    # 1) US 랭킹에서 신규 진입 앱 & 차트 유지 기간 계산
    months_in_chart: dict[int, set] = {}   # app_id → 차트에 있던 월 set
    for dt in MONTHS:
        key = (country, dt.strftime("%Y-%m"))
        for app_id in rankings.get(key, []):
            months_in_chart.setdefault(app_id, set()).add(dt.strftime("%Y-%m"))

    # 2) 앱 상세 정보 (release_date) 조회
    all_ids = list(months_in_chart.keys())
    print(f"  전체 차트 앱 {len(all_ids)}개 상세 정보 조회...")
    details = {}
    for i in range(0, len(all_ids), 100):
        chunk = all_ids[i:i+100]
        data = c.get("/v1/ios/apps", app_ids=",".join(str(x) for x in chunk))
        for app in (data if isinstance(data, list) else data.get("apps", [])):
            details[app["app_id"]] = app

    # 3) 분류: 신규 진입 (release_date 기간 내) + 첫 진입 월 식별
    rows = []
    for app_id, months_set in months_in_chart.items():
        info = details.get(app_id, {})
        rd = info.get("release_date", "")
        if not rd:
            continue
        first_month = min(months_set)
        consec = len(months_set)
        rows.append({
            "app_id": app_id,
            "name": info.get("name", ""),
            "release_date": rd[:10],
            "first_chart_month": first_month,
            "months_in_chart": consec,
            "survived_3m": consec >= 3,
        })

    df = pd.DataFrame(rows)

    # 4) 신규 진입 = release_date ≈ first_chart_month (같은 연도×월)
    df["release_ym"] = pd.to_datetime(df["release_date"]).dt.to_period("M").astype(str)
    df_new = df[df["release_ym"] == df["first_chart_month"]].copy()
    print(f"  신규 진입 게임 {len(df_new)}개 (출시 직후 차트 진입)")

    # 5) 두 그룹 매출 수집 (진입 첫 달)
    survived = df_new[df_new["survived_3m"]]["app_id"].astype(str).tolist()
    churned  = df_new[~df_new["survived_3m"]]["app_id"].astype(str).tolist()
    print(f"  3개월 유지: {len(survived)}개 / 미유지: {len(churned)}개")

    result = {"classification": df_new}

    for label, ids in [("survived", survived[:80]), ("churned", churned[:80])]:
        if ids:
            data = sales_ep.get_sales_estimates(
                app_ids=ids,
                start_date="2022-01-01", end_date="2026-03-31",
                os="ios", country=country, granularity="monthly"
            )
            result[f"{label}_sales"] = sales_ep.aggregate_by_month(data)
        else:
            result[f"{label}_sales"] = pd.DataFrame()

    return result


# ════════════════════════════════════════════════════════════════
# SLIDE 2: 신규 진입 게임 월별 잔존율
# ════════════════════════════════════════════════════════════════
def collect_slide2(rankings: dict, country: str = "US"):
    """
    연도별 신규 진입 게임의 D1/D7/D30 잔존율 수집.
    """
    print(f"\n=== SLIDE 2: 신규 게임 잔존율 ({country}) ===")

    # 연도별 신규 게임 수집 (각 연도의 첫 번째 달에 진입한 앱)
    all_new_ids_by_year: dict[int, list] = {}
    all_months_in_chart: dict[int, set] = {}

    for dt in MONTHS:
        key = (country, dt.strftime("%Y-%m"))
        for app_id in rankings.get(key, []):
            all_months_in_chart.setdefault(app_id, set()).add(dt)

    # 앱 상세 조회
    all_ids = list(all_months_in_chart.keys())
    details = {}
    for i in range(0, len(all_ids), 100):
        chunk = all_ids[i:i+100]
        data = c.get("/v1/ios/apps", app_ids=",".join(str(x) for x in chunk))
        for app in (data if isinstance(data, list) else data.get("apps", [])):
            details[app["app_id"]] = app

    for year in range(2022, 2027):
        yr_ids = []
        for app_id, months_set in all_months_in_chart.items():
            info = details.get(app_id, {})
            rd = info.get("release_date", "")
            if rd and rd[:4] == str(year):
                yr_ids.append(app_id)
        all_new_ids_by_year[year] = yr_ids[:50]

    # 잔존율 수집
    rows = []
    for year, ids in all_new_ids_by_year.items():
        if not ids:
            continue
        print(f"  {year}년 신규 게임 {len(ids)}개 잔존율 조회...")
        data = c.get(
            "/v1/ios/usage/retention",
            app_ids=",".join(str(x) for x in ids),
            start_date=f"{year}-01-01",
            end_date=f"{year}-12-31" if year < 2026 else "2026-03-31",
            country=country,
            retention_days="1,7,14,30",
        )
        app_data = data.get("app_data", []) if isinstance(data, dict) else []
        for item in app_data:
            ret = item.get("corrected_retention", [])
            rows.append({
                "year": year,
                "app_id": item.get("app_id"),
                "d1":  ret[0]  if len(ret) > 0  else None,
                "d7":  ret[6]  if len(ret) > 6  else None,
                "d14": ret[13] if len(ret) > 13 else None,
                "d30": ret[29] if len(ret) > 29 else None,
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        summary = df.groupby("year")[["d1","d7","d14","d30"]].mean().round(4).reset_index()
        # 퍼센트로 변환
        for col in ["d1","d7","d14","d30"]:
            summary[col] = (summary[col] * 100).round(1)
        print(summary.to_string(index=False))
        return summary
    return pd.DataFrame()


# ════════════════════════════════════════════════════════════════
# SLIDE 3: 국가×순위별 월 매출 변화
# ════════════════════════════════════════════════════════════════
def collect_slide3(rankings: dict):
    """
    각 국가에서 1, 10, 20, 50, 100위 앱의 월별 매출 추이.
    """
    print("\n=== SLIDE 3: 국가×순위별 월 매출 ===")
    rows = []

    for country in COUNTRIES:
        # 해당 국가의 순위별 앱 특정
        rank_app_map = []   # (YYYY-MM, rank, app_id)
        for dt in MONTHS:
            key = (country, dt.strftime("%Y-%m"))
            ranking_list = rankings.get(key, [])
            for rank in TARGET_RANKS:
                idx = rank - 1
                if idx < len(ranking_list):
                    rank_app_map.append({
                        "country": country,
                        "ym": dt.strftime("%Y-%m"),
                        "rank": rank,
                        "app_id": ranking_list[idx],
                    })

        if not rank_app_map:
            continue

        # 해당 국가의 고유 앱 ID 수집
        unique_ids = list({r["app_id"] for r in rank_app_map})
        print(f"  {country}: {len(unique_ids)}개 고유 앱 매출 조회...")

        # 매출 조회 (100개씩 배치)
        sales_rows = []
        for i in range(0, len(unique_ids), 100):
            chunk = unique_ids[i:i+100]
            data = sales_ep.get_sales_estimates(
                app_ids=[str(x) for x in chunk],
                start_date="2022-01-01", end_date="2026-03-31",
                os="ios", country=country, granularity="monthly",
            )
            sales_rows.extend(data.to_dict("records") if hasattr(data, "to_dict") else [])

        sales_df = pd.DataFrame(sales_rows)
        if sales_df.empty:
            continue

        # app_id+년월 → 매출 조회용 딕셔너리
        if "app_id" not in sales_df.columns and "aid" in sales_df.columns:
            sales_df = sales_df.rename(columns={"aid": "app_id"})
        if "revenue_usd" not in sales_df.columns and "ar" in sales_df.columns:
            sales_df["revenue_usd"] = sales_df["ar"] / 100  # cents → USD

        if "date" in sales_df.columns:
            sales_df["ym"] = pd.to_datetime(sales_df["date"]).dt.to_period("M").astype(str)
        elif "year" in sales_df.columns and "month" in sales_df.columns:
            sales_df["ym"] = sales_df["year"].astype(str) + "-" + sales_df["month"].astype(str).str.zfill(2)

        rev_map = {}
        for _, row in sales_df.iterrows():
            key = (int(row["app_id"]), row.get("ym",""))
            rev_map[key] = rev_map.get(key, 0) + row.get("revenue_usd", 0)

        for item in rank_app_map:
            rev = rev_map.get((int(item["app_id"]), item["ym"]), 0)
            rows.append({
                "country": item["country"],
                "ym": item["ym"],
                "rank": item["rank"],
                "app_id": item["app_id"],
                "revenue_usd": rev,
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        # 만 달러 단위로 변환
        df["revenue_10k_usd"] = (df["revenue_usd"] / 10000).round(1)
    return df


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    OUT = Path(__file__).parent.parent

    print("▶ 1단계: 전체 랭킹 수집 (204 API calls, 캐시 히트 시 무료)")
    rankings = fetch_all_rankings()

    print("\n▶ 2단계: SLIDE 1 데이터")
    s1 = collect_slide1(rankings, country="US")
    s1["classification"].to_csv(OUT / "slide1_classification.csv", index=False)
    s1["survived_sales"].to_csv(OUT / "slide1_survived.csv", index=False)
    s1["churned_sales"].to_csv(OUT / "slide1_churned.csv", index=False)

    print("\n▶ 3단계: SLIDE 2 데이터")
    s2 = collect_slide2(rankings, country="US")
    if not s2.empty:
        s2.to_csv(OUT / "slide2_retention.csv", index=False)
        print(s2)

    print("\n▶ 4단계: SLIDE 3 데이터")
    s3 = collect_slide3(rankings)
    if not s3.empty:
        s3.to_csv(OUT / "slide3_rank_revenue.csv", index=False)
        print(s3.groupby(["country","rank"])["revenue_10k_usd"].describe().round(1))

    print("\n✅ 데이터 수집 완료")
