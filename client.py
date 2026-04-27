"""Sensor Tower API base client — 디스크 캐싱으로 API 호출 최소화."""

import os
import json
import hashlib
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

BASE_URL = "https://api.sensortower.com"
CACHE_DIR = Path(__file__).parent / ".cache"


class SensorTowerClient:
    def __init__(self, token: str = None, use_cache: bool = True):
        self.token = token or os.getenv("SENSOR_TOWER_API_TOKEN")
        if not self.token:
            raise ValueError("API token이 없습니다. .env 파일에 SENSOR_TOWER_API_TOKEN을 설정하세요.")
        self.use_cache = use_cache
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        CACHE_DIR.mkdir(exist_ok=True)

    # ── 캐시 유틸 ──────────────────────────────────────────────
    def _cache_key(self, path: str, params: dict) -> Path:
        safe = {k: v for k, v in params.items() if k != "auth_token"}
        raw = json.dumps({"path": path, "params": safe}, sort_keys=True)
        h = hashlib.md5(raw.encode()).hexdigest()
        return CACHE_DIR / f"{h}.json"

    def _load_cache(self, key: Path):
        if key.exists():
            print(f"[CACHE HIT] {key.name}")
            return json.loads(key.read_text(encoding="utf-8"))
        return None

    def _save_cache(self, key: Path, data):
        key.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def clear_cache(self):
        """캐시 전체 삭제."""
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
        print("캐시 삭제 완료.")

    # ── HTTP ───────────────────────────────────────────────────
    def _build_params(self, **kwargs) -> dict:
        params = {"auth_token": self.token}
        for k, v in kwargs.items():
            if v is not None:
                params[k] = v
        return params

    @retry(
        retry=retry_if_exception_type(requests.exceptions.HTTPError),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
    )
    def _fetch(self, path: str, params: dict) -> dict | list:
        url = f"{BASE_URL}{path}"
        resp = self.session.get(url, params=params)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 10))
            print(f"[RATE LIMIT] {retry_after}초 대기...")
            time.sleep(retry_after)
            resp.raise_for_status()
        resp.raise_for_status()
        return resp.json()

    def get(self, path: str, **kwargs) -> dict | list:
        """GET 요청 — 캐시 히트 시 API 미호출."""
        params = self._build_params(**kwargs)
        if self.use_cache:
            key = self._cache_key(path, params)
            cached = self._load_cache(key)
            if cached is not None:
                return cached

        print(f"[API CALL] {path}")
        data = self._fetch(path, params)

        if self.use_cache:
            self._save_cache(key, data)
        return data

    def paginate(self, path: str, limit: int = 100, max_records: int = None, **kwargs):
        """페이지네이션 전체 수집 — 페이지별 캐싱."""
        results = []
        offset = 0
        while True:
            data = self.get(path, limit=limit, offset=offset, **kwargs)
            batch = (
                data if isinstance(data, list)
                else data.get("apps") or data.get("data") or data.get("results") or []
            )
            results.extend(batch)
            if len(batch) < limit:
                break
            if max_records and len(results) >= max_records:
                results = results[:max_records]
                break
            offset += limit
        return results
