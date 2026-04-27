"""
TOP 100 신규진입 게임의 M+1~M+12 잔존율 수집
- iOS + AOS
- 국가별 (KR/JP/US)
- 퍼블리셔별 (한국/일본/서구권/중화권)
- 2025 전/후 연평균
- M+1(d30), M+2(d60), M+3(d90), M+6(d180), M+12(d365)

API: /v1/{os}/sales_report_estimates_comparison_attributes (limit=100)
"""
import sys, json, hashlib, time, os, re
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("SENSOR_TOWER_API_TOKEN")
BASE_URL = "https://api.sensortower.com"
CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
OUT_DIR = Path("C:/Users/NHN/Documents/sensortower_api")

session = requests.Session()
session.headers.update({"Accept": "application/json"})

MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES = ["KR", "JP", "US"]

# 퍼블리셔 분류
CHINESE_CODES = {"CN","HK","TW","MO"}
WESTERN_CODES = {"US","CA","GB","DE","FR","FI","SE","NO","DK","NL","BE","CH","AT",
    "AU","NZ","IE","IT","ES","PT","RU","PL","CZ","HU","RO","UA","GR","TR","IL","ZA","BR","MX","AR","CO","CL","PE"}
_FULL_NAME_MAP = {
    "SOUTH KOREA":"한국","KOREA":"한국","JAPAN":"일본",
    "CHINA":"중화권","HONG KONG":"중화권","TAIWAN":"중화권","MACAU":"중화권",
    "UNITED STATES":"서구권","UNITED KINGDOM":"서구권","CANADA":"서구권",
    "AUSTRALIA":"서구권","GERMANY":"서구권","FRANCE":"서구권",
}

def classify_publisher(raw):
    if not raw: return "기타"
    u = raw.strip().upper()
    for key, val in _FULL_NAME_MAP.items():
        if key in u: return val
    if u in CHINESE_CODES: return "중화권"
    if u in WESTERN_CODES: return "서구권"
    if u in {"JP","JPN"}: return "일본"
    if u in {"KR","KOR"}: return "한국"
    return "기타"

def parse_pct(s):
    if not s: return None
    m = re.search(r'([\d.]+)', str(s))
    return float(m.group(1)) if m else None

def cached_get(path, params):
    safe = {k: v for k, v in params.items() if k != "auth_token"}
    h = hashlib.md5(json.dumps({"path": path, "params": safe}, sort_keys=True).encode()).hexdigest()
    f = CACHE_DIR / f"{h}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    r = session.get(f"{BASE_URL}{path}", params={"auth_token": TOKEN, **params}, timeout=30)
    if r.status_code == 429:
        wait = int(r.headers.get("Retry-After", 15))
        print(f"  [RATE LIMIT] {wait}초 대기...")
        time.sleep(wait)
        r = session.get(f"{BASE_URL}{path}", params={"auth_token": TOKEN, **params}, timeout=30)
    if r.status_code != 200:
        print(f"  [ERROR] {r.status_code}: {r.text[:200]}")
        return None
    data = r.json()
    f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.3)
    return data


def collect_retention(platform):
    """iOS 또는 Android TOP 100 잔존율 수집."""
    if platform == "ios":
        api_path = "/v1/ios/sales_report_estimates_comparison_attributes"
        category = 6014
        extra_params = {"device_type": "total"}
    else:
        api_path = "/v1/android/sales_report_estimates_comparison_attributes"
        category = "game"
        extra_params = {}

    rows = []
    total = len(MONTHS) * len(COUNTRIES)
    n = 0

    for dt in MONTHS:
        ym = dt.strftime("%Y-%m")
        for country in COUNTRIES:
            n += 1
            params = {
                "date": dt.strftime("%Y-%m-%d"),
                "comparison_attribute": "absolute",
                "measure": "revenue",
                "time_range": "month",
                "category": category,
                "limit": 100,
                "country": country,
                **extra_params,
            }
            data = cached_get(api_path, params)
            if not data or not isinstance(data, list):
                continue

            for rank, app in enumerate(data, 1):
                ct = app.get("custom_tags", {})
                aid = str(app.get("app_id", ""))
                pub_country = app.get("publisher_country", "") or ""
                # Also check custom_tags for publisher country
                if not pub_country:
                    pub_country = str(ct.get("Publisher Country", "") or "")

                rows.append({
                    "platform": platform,
                    "country": country,
                    "ym": ym,
                    "rank": rank,
                    "app_id": aid,
                    "publisher_country": pub_country,
                    "publisher_group": classify_publisher(pub_country),
                    "d30": parse_pct(ct.get("Day 30 Retention (Latest Available, WW)", "")),
                    "d60": parse_pct(ct.get("Day 60 Retention (Latest Available, WW)", "")),
                    "d90": parse_pct(ct.get("Day 90 Retention (Latest Available, WW)", "")),
                    "d180": parse_pct(ct.get("Day 180 Retention (Latest Available, WW)", "")),
                    "d365": parse_pct(ct.get("Day 365 Retention (Latest Available, WW)", "")),
                    "period": "post2025" if ym >= "2025-01" else "pre2025",
                })

            if n % 10 == 0:
                print(f"  [{platform}] {n}/{total} ({ym} {country})")

    return pd.DataFrame(rows)


def main():
    print("▶ TOP 100 잔존율 수집 시작 (iOS + AOS × KR/JP/US × 51개월)")
    print()

    # 신규진입 게임 목록 로드
    ios_s1 = pd.read_csv(OUT_DIR / "slide1_v2.csv")
    aod_s1 = pd.read_csv(OUT_DIR / "slide1_v2_android.csv")
    ios_new_ids = set(str(x) for x in ios_s1["app_id"].unique())
    aod_new_ids = set(str(x) for x in aod_s1["app_id"].unique())

    # iOS 수집
    print("[iOS] 수집 중...")
    df_ios = collect_retention("ios")
    print(f"  iOS 전체: {len(df_ios)}행")

    # AOS 수집
    print("\n[AOS] 수집 중...")
    df_aod = collect_retention("android")
    print(f"  AOS 전체: {len(df_aod)}행")

    # 합치기
    df_all = pd.concat([df_ios, df_aod], ignore_index=True)

    # 신규진입 게임 필터
    df_all["is_new_entry"] = False
    ios_mask = (df_all["platform"] == "ios") & (df_all["app_id"].isin(ios_new_ids))
    aod_mask = (df_all["platform"] == "android") & (df_all["app_id"].isin(aod_new_ids))
    df_all.loc[ios_mask | aod_mask, "is_new_entry"] = True

    # 신규진입 + 전체 모두 저장
    out_all = OUT_DIR / "retention_top100_full.csv"
    df_all.to_csv(out_all, index=False)
    print(f"\n전체 저장: {out_all} ({len(df_all)}행)")

    df_new = df_all[df_all["is_new_entry"]].copy()
    out_new = OUT_DIR / "retention_top100_newentry.csv"
    df_new.to_csv(out_new, index=False)
    print(f"신규진입만: {out_new} ({len(df_new)}행)")

    # ── 요약 출력 ──
    print("\n" + "="*60)
    print("▶ 국가별 × 플랫폼별 × 기간별 평균 잔존율 (신규진입 게임)")
    print("="*60)
    for plat in ["ios", "android"]:
        for pk in ["pre2025", "post2025"]:
            sub = df_new[(df_new["platform"]==plat) & (df_new["period"]==pk)]
            if len(sub) == 0: continue
            print(f"\n[{plat.upper()} / {pk}]")
            for ctr in COUNTRIES:
                s = sub[sub["country"]==ctr]
                if len(s) == 0: continue
                d30 = s["d30"].mean(); d90 = s["d90"].mean()
                d180 = s["d180"].mean(); d365 = s["d365"].mean()
                print(f"  {ctr}: n={len(s)} M+1={d30:.1f}% M+3={d90:.1f}% M+6={d180:.1f}% M+12={d365:.1f}%")

    print("\n" + "="*60)
    print("▶ 퍼블리셔별 × 플랫폼별 평균 잔존율 (신규진입 게임)")
    print("="*60)
    for plat in ["ios", "android"]:
        sub = df_new[df_new["platform"]==plat]
        if len(sub) == 0: continue
        print(f"\n[{plat.upper()}]")
        for pub in ["한국","일본","서구권","중화권"]:
            s = sub[sub["publisher_group"]==pub]
            if len(s) == 0: continue
            d30 = s["d30"].mean(); d90 = s["d90"].mean()
            d180 = s["d180"].mean(); d365 = s["d365"].mean()
            print(f"  {pub}: n={len(s)} M+1={d30:.1f}% M+3={d90:.1f}% M+6={d180:.1f}% M+12={d365:.1f}%")

    print("\n▶ 완료!")


if __name__ == "__main__":
    main()
