"""광고 집행 관련 엔드포인트.

현재 플랜에서 확인된 동작:
  - /v1/ios/ad_intel/creatives : 앱별 광고 크리에이티브 (네트워크 지정 필요)
  - /v1/ios/ad_intel/networks  : 사용 가능한 광고 네트워크 목록
"""

import pandas as pd
from client import SensorTowerClient

# 플랜에서 지원되는 주요 네트워크
MAIN_NETWORKS = ["Admob", "Applovin", "Unity", "TikTok", "Vungle"]


class AdvertisingEndpoint:
    def __init__(self, client: SensorTowerClient):
        self.client = client

    def get_available_networks(self, app_ids: list, os: str = "ios") -> list:
        """앱에서 사용 가능한 광고 네트워크 목록."""
        data = self.client.get(
            f"/v1/{os}/ad_intel/networks",
            app_ids=",".join(str(x) for x in app_ids[:10]),
        )
        return data if isinstance(data, list) else []

    def get_creatives(
        self,
        app_ids: list,
        start_date: str,
        end_date: str,
        os: str = "ios",
        country: str = "US",
        networks: list = None,
        limit: int = 50,
    ) -> pd.DataFrame:
        """
        앱별 광고 크리에이티브 수집.
        광고 집행 여부 = creative 존재 여부로 판단.
        """
        if networks is None:
            networks = MAIN_NETWORKS

        results = []
        for net in networks:
            for i in range(0, len(app_ids), 50):
                chunk = app_ids[i:i+50]
                data = self.client.get(
                    f"/v1/{os}/ad_intel/creatives",
                    app_ids=",".join(str(x) for x in chunk),
                    start_date=start_date,
                    end_date=end_date,
                    country=country,
                    networks=net,
                    limit=limit,
                )
                ad_units = data.get("ad_units", []) if isinstance(data, dict) else []
                for unit in ad_units:
                    unit["network"] = net
                    results.append(unit)

        return pd.DataFrame(results)

    def calc_ad_rate(
        self,
        app_ids: list,
        start_date: str,
        end_date: str,
        os: str = "ios",
        country: str = "US",
    ) -> dict:
        """
        광고 집행률 계산.
        Returns: {
            "total_apps": int,
            "advertising_apps": int,
            "ad_rate_pct": float,
            "detail_df": DataFrame,
        }
        """
        creative_df = self.get_creatives(
            app_ids=app_ids,
            start_date=start_date,
            end_date=end_date,
            os=os,
            country=country,
        )

        if creative_df.empty:
            return {
                "total_apps": len(app_ids),
                "advertising_apps": 0,
                "ad_rate_pct": 0.0,
                "detail_df": pd.DataFrame(),
            }

        id_col = next(
            (c for c in ["app_id", "aid"] if c in creative_df.columns), None
        )
        advertising_count = creative_df[id_col].nunique() if id_col else 0

        return {
            "total_apps": len(app_ids),
            "advertising_apps": advertising_count,
            "ad_rate_pct": round(advertising_count / len(app_ids) * 100, 2),
            "detail_df": creative_df,
        }
