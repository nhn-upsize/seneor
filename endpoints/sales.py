"""다운로드 & 매출 추정치 엔드포인트.

응답 필드 약어:
  aid = app_id
  cc  = country_code
  d   = date
  au  = actual_units (다운로드)
  ar  = actual_revenue (매출, USD cents)
  iu  = iphone_units
  ir  = iphone_revenue
"""

import pandas as pd
from client import SensorTowerClient

FIELD_MAP = {
    "aid": "app_id",
    "cc":  "country",
    "d":   "date",
    "au":  "downloads",
    "ar":  "revenue_usd_cents",
    "iu":  "iphone_downloads",
    "ir":  "iphone_revenue_usd_cents",
}


class SalesEndpoint:
    def __init__(self, client: SensorTowerClient):
        self.client = client

    def get_sales_estimates(
        self,
        app_ids: list,
        start_date: str,
        end_date: str,
        os: str = "ios",           # ios | android (unified 미지원)
        country: str = "US",       # WW = 전세계 합산 없음 → 국가별 합산 필요
        granularity: str = "monthly",
    ) -> pd.DataFrame:
        """
        앱별 다운로드/매출 추정치.
        country='WW' 시 모든 국가 반환 → 집계는 aggregate_by_month()로.
        """
        results = []
        for i in range(0, len(app_ids), 100):
            chunk = app_ids[i:i+100]
            data = self.client.get(
                f"/v1/{os}/sales_report_estimates",
                app_ids=",".join(str(x) for x in chunk),
                start_date=start_date,
                end_date=end_date,
                country=country,
                granularity=granularity,
            )
            results.extend(data if isinstance(data, list) else [])

        df = pd.DataFrame(results).rename(columns=FIELD_MAP)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["year"]  = df["date"].dt.year
            df["month"] = df["date"].dt.month
        if "revenue_usd_cents" in df.columns:
            df["revenue_usd"] = df["revenue_usd_cents"] / 100
        return df

    def aggregate_by_month(self, df: pd.DataFrame) -> pd.DataFrame:
        """국가별 행을 연/월별로 합산 (전세계 합계)."""
        if df.empty:
            return df
        grp_cols = [c for c in ["app_id", "year", "month"] if c in df.columns]
        num_cols = [c for c in ["downloads", "revenue_usd"] if c in df.columns]
        return df.groupby(grp_cols, as_index=False)[num_cols].sum()
