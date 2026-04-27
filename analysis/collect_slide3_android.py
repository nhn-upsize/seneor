"""
SLIDE 21/22: AOS 국가×순위별 월 매출 수집
- 국가: KR, JP, US
- 순위: 1, 10, 20, 50, 100위
- 기간: 2022-01 ~ 2026-03
- 저장: slide3_rank_revenue_android.csv
"""
import sys, json, hashlib, time, os
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()
TOKEN     = os.getenv("SENSOR_TOWER_API_TOKEN")
BASE      = "https://api.sensortower.com"
CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
OUT_DIR   = Path("C:/Users/NHN/Documents/sensortower_api")
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({"Accept": "application/json"})

MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES     = ["KR", "JP", "US"]
TARGET_RANKS  = [1, 10, 20, 50, 100]
CATEGORY_AND  = "game"
CHART_TYPE    = "topgrossing"

# ── 퍼블리셔 분류 ────────────────────────────────────────────────────────
CHINESE_CODES = {"CN","HK","TW","MO"}
WESTERN_CODES = {
    "US","CA","GB","DE","FR","FI","SE","NO","DK","NL","BE","CH","AT",
    "AU","NZ","IE","IT","ES","PT","RU","PL","CZ","HU","RO","UA","GR",
    "TR","IL","ZA","BR","MX","AR","CO","CL","PE"
}
_FULL_NAME_MAP = {
    "SOUTH KOREA":"한국","KOREA":"한국","JAPAN":"일본",
    "CHINA":"중화권","HONG KONG":"중화권","TAIWAN":"중화권","MACAU":"중화권",
    "UNITED STATES":"서구권","UNITED KINGDOM":"서구권","CANADA":"서구권",
    "AUSTRALIA":"서구권","GERMANY":"서구권","FRANCE":"서구권",
}

def classify_publisher(raw: str) -> str:
    if not raw: return "기타"
    u = raw.strip().upper()
    for key, val in _FULL_NAME_MAP.items():
        if key in u: return val
    if u in CHINESE_CODES: return "중화권"
    if u in WESTERN_CODES: return "서구권"
    if u in {"JP","JPN"}: return "일본"
    if u in {"KR","KOR"}: return "한국"
    return "기타"


def cached_get(path: str, params: dict):
    safe = {k: v for k, v in params.items() if k != "auth_token"}
    h = hashlib.md5(json.dumps({"path": path, "params": safe},
                                sort_keys=True).encode()).hexdigest()
    f = CACHE_DIR / f"{h}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    r = session.get(f"{BASE}{path}", params={"auth_token": TOKEN, **params}, timeout=30)
    if r.status_code == 429:
        wait = int(r.headers.get("Retry-After", 15))
        print(f"  [RATE LIMIT] {wait}초 대기...")
        time.sleep(wait)
        r = session.get(f"{BASE}{path}", params={"auth_token": TOKEN, **params}, timeout=30)
    if r.status_code != 200:
        print(f"  [ERROR] {r.status_code}: {r.text[:200]}")
        return None
    data = r.json()
    f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.3)
    return data


def load_ranking(country: str, date_str: str) -> list:
    """Android 월별 TOP 100 랭킹 반환 (package name 리스트)."""
    data = cached_get("/v1/android/ranking", {
        "category":   CATEGORY_AND,
        "chart_type": CHART_TYPE,
        "date":       date_str,
        "country":    country,
        "limit":      100,
    })
    if not data:
        return []
    ranking = data.get("ranking", []) if isinstance(data, dict) else data
    return [str(a) if isinstance(a, str) else str(a.get("app_id") or a.get("package_name",""))
            for a in ranking]


def fetch_batch_revenue_android(pkg_names: list, country: str, year: int) -> dict:
    """Android 앱 매출 조회 → {(pkg, ym): revenue_usd}.
    API 응답은 iOS와 동일한 flat list: [{aid, c, d, r, u}, ...]
    """
    end = "2026-03-31" if year == 2026 else f"{year}-12-31"
    data = cached_get("/v1/android/sales_report_estimates", {
        "app_ids":    ",".join(pkg_names),
        "start_date": f"{year}-01-01",
        "end_date":   end,
        "country":    country,
        "granularity":"monthly",
    })
    result = {}
    if not data:
        return result
    # API returns flat list: [{aid, c, d, r, u}, ...]
    items = data if isinstance(data, list) else data.get("apps", [])
    for item in items:
        if item.get("c") != country:
            continue
        pkg = str(item.get("aid") or item.get("app_id") or item.get("package_name",""))
        ym  = (item.get("d") or item.get("date",""))[:7]
        rev = item.get("r", 0) or item.get("ar", 0) or item.get("revenue", 0) or 0
        result[(pkg, ym)] = result.get((pkg, ym), 0) + rev / 100
    return result


def get_app_details_android(pkg_names: list) -> dict:
    """Android 앱 publisher_country 조회."""
    results = {}
    for i in range(0, len(pkg_names), 100):
        chunk = pkg_names[i:i+100]
        data = cached_get("/v1/android/apps", {"app_ids": ",".join(chunk)})
        if not data:
            continue
        items = data if isinstance(data, list) else data.get("apps", [])
        for app in items:
            if isinstance(app, dict):
                pkg = str(app.get("app_id") or app.get("package_name",""))
                if pkg:
                    results[pkg] = app
    return results


def fetch_slide3_android():
    rows = []

    for country in COUNTRIES:
        print(f"\n[{country}] 랭킹 로드...")

        # 1) 월별 랭킹 캐시
        ranking_map = {}
        for dt in MONTHS:
            ym = dt.strftime("%Y-%m")
            ranking_map[ym] = load_ranking(country, dt.strftime("%Y-%m-%d"))

        # 2) 타겟 앱 확정 (순위별 package name)
        targets = []
        for dt in MONTHS:
            ym = dt.strftime("%Y-%m")
            rl = ranking_map.get(ym, [])
            for rank in TARGET_RANKS:
                if rank - 1 < len(rl):
                    targets.append((ym, rank, rl[rank - 1]))

        unique_pkgs = list({t[2] for t in targets})
        print(f"  고유 앱 {len(unique_pkgs)}개")

        # 3) 10개씩 × 연도별 매출 조회
        rev_map = {}
        BATCH = 10
        years = list(range(2022, 2027))
        for year in years:
            for i in range(0, len(unique_pkgs), BATCH):
                chunk = unique_pkgs[i:i+BATCH]
                batch_rev = fetch_batch_revenue_android(chunk, country, year)
                rev_map.update(batch_rev)
                time.sleep(0.3)
            print(f"  [{country}] {year}년 매출 수집 완료")

        # 4) publisher_group 조회
        print(f"  [{country}] 앱 상세 조회...")
        details = get_app_details_android(unique_pkgs)

        # 5) 결합
        for ym, rank, pkg in targets:
            info = details.get(pkg, {})
            pc   = info.get("publisher_country","") or ""
            rows.append({
                "country":          country,
                "platform":         "android",
                "ym":               ym,
                "rank":             rank,
                "app_id":           pkg,
                "publisher_country":pc,
                "publisher_group":  classify_publisher(pc),
                "revenue_usd":      rev_map.get((pkg, ym), 0),
                "period":           "post2025" if ym >= "2025-01" else "pre2025",
            })

        print(f"  [{country}] 완료")

    df = pd.DataFrame(rows)
    df["revenue_m_usd"] = (df["revenue_usd"] / 1_000_000).round(3)
    return df


if __name__ == "__main__":
    print("AOS SLIDE 3 데이터 수집 시작 (국가×순위별 월 매출)")
    df = fetch_slide3_android()

    out = OUT_DIR / "slide3_rank_revenue_android.csv"
    df.to_csv(out, index=False)
    print(f"\n저장 완료: {out} ({len(df)}행)")

    df["year"] = df["ym"].str[:4]
    summary = df.groupby(["country","rank","year"])["revenue_m_usd"].mean().round(3).reset_index()
    print("\n국가×순위별 연평균 월매출 (백만 USD):")
    print(summary.to_string(index=False))
