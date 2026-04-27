"""앱/게임 메타데이터 및 검색 엔드포인트."""

import pandas as pd
from client import SensorTowerClient

CHART_TYPES = ["topfreeapplications", "toppaidapplications", "topgrossingapplications"]


class AppsEndpoint:
    def __init__(self, client: SensorTowerClient):
        self.client = client

    def search(
        self,
        term: str,
        os: str = "ios",
        entity_type: str = "app",
        category: int = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """앱/게임 검색 (term 필수)."""
        kwargs = dict(entity_type=entity_type, term=term, limit=limit)
        if category:
            kwargs["category"] = category
        data = self.client.get(f"/v1/{os}/search_entities", **kwargs)
        return pd.DataFrame(data if isinstance(data, list) else [])

    def get_app_details(self, app_ids: list, os: str = "ios") -> pd.DataFrame:
        """앱 상세 정보 (최대 100개씩)."""
        results = []
        for i in range(0, len(app_ids), 100):
            chunk = app_ids[i:i+100]
            data = self.client.get(
                f"/v1/{os}/apps",
                app_ids=",".join(str(x) for x in chunk),
            )
            batch = data if isinstance(data, list) else data.get("apps", [])
            results.extend(batch)
        return pd.DataFrame(results)

    def get_monthly_rankings(
        self,
        year: int,
        os: str = "ios",
        country: str = "US",
        category: int = 6014,
        chart_type: str = "topfreeapplications",
    ) -> pd.DataFrame:
        """
        월별 Top Chart 순위 수집 (매월 1일 기준).
        반환: app_id, rank, year, month
        """
        rows = []
        for month in range(1, 13):
            date_str = f"{year}-{month:02d}-01"
            data = self.client.get(
                f"/v1/{os}/ranking",
                category=category,
                chart_type=chart_type,
                date=date_str,
                country=country,
                app_ids="",  # 전체 순위 반환
            )
            ranking = data.get("ranking", []) if isinstance(data, dict) else []
            for rank, app_id in enumerate(ranking, start=1):
                rows.append({
                    "app_id": app_id,
                    "rank": rank,
                    "year": year,
                    "month": month,
                    "chart_type": chart_type,
                    "country": country,
                })
        return pd.DataFrame(rows)

    def get_new_game_entries(
        self,
        year: int,
        os: str = "ios",
        country: str = "US",
        category: int = 6014,
        chart_type: str = "topfreeapplications",
    ) -> pd.DataFrame:
        """
        특정 연도 차트에 진입한 신규 게임 수집.
        전략:
          1) 해당 연도 + 전년도 차트에서 앱 ID 수집
          2) 앱 상세 정보로 release_date 확인
          3) release_date가 해당 연도인 앱만 추출
        """
        print(f"  월별 Top Chart 수집 중 ({year})...")
        current_df = self.get_monthly_rankings(
            year=year, os=os, country=country,
            category=category, chart_type=chart_type,
        )
        if current_df.empty:
            return pd.DataFrame()

        unique_ids = current_df["app_id"].unique().tolist()
        print(f"  차트 내 고유 앱 {len(unique_ids)}개 → 상세 정보 조회...")

        details_df = self.get_app_details(app_ids=unique_ids, os=os)
        if details_df.empty:
            return pd.DataFrame()

        # release_date 필터링
        if "release_date" in details_df.columns:
            details_df["release_date"] = pd.to_datetime(
                details_df["release_date"], errors="coerce"
            )
            new_entries = details_df[
                details_df["release_date"].dt.year == year
            ].copy()
        else:
            new_entries = details_df.copy()

        # 첫 차트 진입 월 추가
        if not new_entries.empty and "app_id" in new_entries.columns:
            first_entry = (
                current_df.groupby("app_id")["month"].min()
                .reset_index()
                .rename(columns={"month": "first_chart_month"})
            )
            new_entries = new_entries.merge(first_entry, on="app_id", how="left")

        return new_entries.sort_values("release_date").reset_index(drop=True)
