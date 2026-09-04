"""사용자 잔존율(Retention) 및 활성 사용자 엔드포인트."""

import pandas as pd
from client import SensorTowerClient


class RetentionEndpoint:
    def __init__(self, client: SensorTowerClient):
        self.client = client

    def get_retention(
        self,
        app_ids: list,
        start_date: str,
        end_date: str,
        os: str = "ios",
        country: str = "US",
        retention_days: list = None,
    ) -> pd.DataFrame:
        """앱별 Day-N 잔존율."""
        if retention_days is None:
            retention_days = [1, 7, 14, 30]

        results = []
        for i in range(0, len(app_ids), 100):
            chunk = app_ids[i:i+100]
            data = self.client.get(
                f"/v1/{os}/usage/retention",
                app_ids=",".join(str(x) for x in chunk),
                start_date=start_date,
                end_date=end_date,
                country=country,
                retention_days=",".join(str(d) for d in retention_days),
            )
            batch = data if isinstance(data, list) else data.get("apps", [])
            results.extend(batch)
        return pd.DataFrame(results)

    def get_active_users(
        self,
        app_ids: list,
        start_date: str,
        end_date: str,
        os: str = "ios",
        country: str = "US",
        granularity: str = "monthly",
        measure: str = "mau",
    ) -> pd.DataFrame:
        """월별 활성 사용자 수 (dau | wau | mau)."""
        results = []
        for i in range(0, len(app_ids), 500):
            chunk = app_ids[i:i+500]
            data = self.client.get(
                f"/v1/{os}/usage/active_users",
                app_ids=",".join(str(x) for x in chunk),
                start_date=start_date,
                end_date=end_date,
                country=country,
                granularity=granularity,
                measure=measure,
            )
            batch = data if isinstance(data, list) else data.get("apps", [])
            results.extend(batch)
        return pd.DataFrame(results)
