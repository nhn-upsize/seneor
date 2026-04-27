"""
Android(AOS) 데이터 수집 스크립트
iOS collect_all_v2.py 와 동일한 구조로 Android 엔드포인트 사용

수집 대상:
  - app_tags_android.csv  : 퍼블리셔별 잔존율 + 광고집행율 (comparison_attributes)
  - slide2_v2_android.csv : 국가별 × 연도별 × 잔존율 D1/D7/D14/D30
  - slide1_v2_android.csv : 국가별 신규 게임 생존 분류 (3개월 생존 여부)

저장 후 merge_ios_android.py 로 iOS+AOS 통합 CSV 생성
"""
import sys, json, hashlib, time, os, re
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

# ── 수집 기간 ──────────────────────────────────────────────────────────────
MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES     = ["KR", "JP", "US"]   # CN 제외 (국가별 시장 기준)
CATEGORY_AND  = "game"               # Google Play 게임 카테고리 (소문자)
CHART_TYPE    = "topgrossing"        # Android 매출 랭킹

# ── 퍼블리셔 분류 (iOS 스크립트와 동일) ─────────────────────────────────────
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
    if not raw:
        return "기타"
    u = raw.strip().upper()
    for key, val in _FULL_NAME_MAP.items():
        if key in u:
            return val
    if u in CHINESE_CODES:
        return "중화권"
    if u in WESTERN_CODES:
        return "서구권"
    if u in {"JP","JPN"}:
        return "일본"
    if u in {"KR","KOR"}:
        return "한국"
    return "기타"

def parse_pct(val) -> float | None:
    if not val:
        return None
    m = re.search(r"[\d.]+", str(val).strip())
    return float(m.group()) if m else None

def cached_get(path: str, params: dict):
    """캐시 우선 GET 요청."""
    safe = {k: v for k, v in params.items() if k != "auth_token"}
    h = hashlib.md5(json.dumps({"path": path, "params": safe},
                                sort_keys=True).encode()).hexdigest()
    f = CACHE_DIR / f"{h}.json"
    if f.exists():
        print(f"  [CACHE] {path.split('/')[-1]}")
        return json.loads(f.read_text(encoding="utf-8"))
    print(f"  [API]   {path}")
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


# ══════════════════════════════════════════════════════════════════════════
# PART 1: app_tags_android — comparison_attributes 기반 (잔존율 + 광고집행율)
# ══════════════════════════════════════════════════════════════════════════
def collect_app_tags_android():
    print("\n" + "="*60)
    print("PART 1: Android app_tags 수집 (comparison_attributes)")
    print("="*60)

    cache_file = OUT_DIR / "app_tags_raw_android.json"
    tags_by_app: dict = {}
    if cache_file.exists():
        tags_by_app = json.loads(cache_file.read_text(encoding="utf-8"))
        print(f"  기존 캐시 로드: {len(tags_by_app)}개 앱")

    queried = set(tags_by_app.get("__queried_months__", []))

    for dt in MONTHS:
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in queried:
            continue
        print(f"  {date_str} 수집 중...")

        data = cached_get("/v1/android/sales_report_estimates_comparison_attributes", {
            "date":                date_str,
            "comparison_attribute":"absolute",
            "measure":             "revenue",
            "time_range":          "month",
            "category":            CATEGORY_AND,
        })
        if not data:
            continue  # 실패한 월은 queried에 추가 안 함 → 재시도 가능

        items = data if isinstance(data, list) else data.get("apps", [])
        for item in items:
            aid = str(item.get("app_id") or item.get("package_name", ""))
            ct  = item.get("custom_tags", {})
            if aid and ct:
                tags_by_app[aid] = ct

        queried.add(date_str)
        print(f"    → 누적 {len(tags_by_app)}개 앱")

    tags_by_app["__queried_months__"] = list(queried)
    cache_file.write_text(json.dumps(tags_by_app, ensure_ascii=False), encoding="utf-8")

    # CSV 생성
    rows = []
    for aid, ct in tags_by_app.items():
        if aid.startswith("__"):
            continue
        rows.append({
            "app_id":              aid,
            "platform":            "android",
            "publisher_country":   ct.get("Publisher Country", ""),
            "publisher_group":     classify_publisher(ct.get("Publisher Country", "")),
            "ad_active":           1 if "Active" in str(ct.get("Advertised on Any Network","")) else 0,
            "paid_display_pct_us": parse_pct(ct.get("Paid Display Downloads % (Last Q, US)", "")),
            "paid_search_pct_us":  parse_pct(ct.get("Paid Search Downloads % (Last Q, US)", "")),
            "paid_display_pct_ww": parse_pct(ct.get("Paid Display Downloads % (Last Q, WW)", "")),
            "paid_search_pct_ww":  parse_pct(ct.get("Paid Search Downloads % (Last Q, WW)", "")),
            "d30_ret_ww":          parse_pct(ct.get("Day 30 Retention (Latest Available, WW)", "")),
            "d60_ret_ww":          parse_pct(ct.get("Day 60 Retention (Latest Available, WW)", "")),
            "d90_ret_ww":          parse_pct(ct.get("Day 90 Retention (Latest Available, WW)", "")),
            "d180_ret_ww":         parse_pct(ct.get("Day 180 Retention (Latest Available, WW)", "")),
            "d365_ret_ww":         parse_pct(ct.get("Day 365 Retention (Latest Available, WW)", "")),
            "genre":               ct.get("Genre", ""),
        })

    if rows:
        df = pd.DataFrame(rows)
        out = OUT_DIR / "app_tags_android.csv"
        df.to_csv(out, index=False)
        print(f"\n  ✔ 저장: {out.name}  ({len(df)}개 앱)")
        print(f"    publisher_group 분포:\n{df['publisher_group'].value_counts().to_string()}")
        print(f"    ad_active 비율:\n{df.groupby('publisher_group')['ad_active'].mean().round(2).to_string()}")
    else:
        print("  ⚠ 수집된 앱 없음")
    return rows


# ══════════════════════════════════════════════════════════════════════════
# PART 2: slide2_v2_android — 국가별 × 연도별 잔존율 D1/D7/D14/D30
# ══════════════════════════════════════════════════════════════════════════
def collect_slide2_android():
    print("\n" + "="*60)
    print("PART 2: Android slide2 수집 (국가별 랭킹 → 잔존율 D1/D7/D14/D30)")
    print("="*60)

    all_rows = []

    for country in COUNTRIES:
        print(f"\n  [{country}] 랭킹 수집 중...")
        # 해당 국가 월별 TOP 25 앱 수집
        app_seen: dict = {}   # app_id → {'year': ..., 'first_month': ...}

        for dt in MONTHS:
            date_str = dt.strftime("%Y-%m-%d")
            data = cached_get("/v1/android/ranking", {
                "category":   CATEGORY_AND,
                "chart_type": CHART_TYPE,
                "date":       date_str,
                "country":    country,
                "limit":      25,
            })
            if not data:
                continue
            # Android ranking 응답: {"ranking": ["pkg1", "pkg2", ...]}
            ranking = data.get("ranking", []) if isinstance(data, dict) else data
            for item in ranking:
                # item은 package name 문자열 또는 dict
                aid = str(item) if isinstance(item, str) else str(item.get("app_id") or item.get("package_name", ""))
                if aid and aid not in app_seen:
                    app_seen[aid] = {"year": dt.year, "first_month": date_str}

        print(f"    → {len(app_seen)}개 고유 앱 발견")
        if not app_seen:
            continue

        # 연도별로 잔존율 수집
        app_ids = list(app_seen.keys())
        for year in [2022, 2023, 2024, 2025, 2026]:
            end = "2026-03-31" if year == 2026 else f"{year}-12-31"
            start = f"{year}-01-01"

            data = cached_get("/v1/android/usage/retention", {
                "app_ids":        ",".join(app_ids[:50]),  # 한 번에 최대 50개
                "start_date":     start,
                "end_date":       end,
                "country":        country,
                "retention_days": "1,7,14,30,60,90,180,365",
                "granularity":    "monthly",
            })
            if not data:
                continue

            for item in data.get("app_data", []):
                aid    = str(item.get("app_id") or item.get("package_name", ""))
                # publisher_country는 app_seen에서 따로 조회해야 하나, 일단 빈 값
                d1   = item.get("day_1_retention")
                d7   = item.get("day_7_retention")
                d14  = item.get("day_14_retention")
                d30  = item.get("day_30_retention")
                d60  = item.get("day_60_retention")
                d90  = item.get("day_90_retention")
                d180 = item.get("day_180_retention")
                d365 = item.get("day_365_retention")
                if any(v is not None for v in [d1,d7,d14,d30]):
                    period = "post2025" if year >= 2025 else "pre2025"
                    def pct(v): return round(float(v)*100,1) if v is not None else None
                    all_rows.append({
                        "country":           country,
                        "year":              year,
                        "period":            period,
                        "platform":          "android",
                        "app_id":            aid,
                        "publisher_country": "",
                        "publisher_group":   "",
                        "d1":   pct(d1),
                        "d7":   pct(d7),
                        "d14":  pct(d14),
                        "d30":  pct(d30),
                        "d60":  pct(d60),
                        "d90":  pct(d90),
                        "d180": pct(d180),
                        "d365": pct(d365),
                    })

    if all_rows:
        df = pd.DataFrame(all_rows)
        # publisher_group 보강 (app_tags_android.csv에서)
        tags_file = OUT_DIR / "app_tags_android.csv"
        if tags_file.exists():
            tags = pd.read_csv(tags_file)[["app_id","publisher_country","publisher_group"]]
            tags["app_id"] = tags["app_id"].astype(str)
            df = df.merge(tags, on="app_id", how="left", suffixes=("_old",""))
            for col in ["publisher_country","publisher_group"]:
                if col+"_old" in df.columns:
                    df[col] = df[col].fillna(df[col+"_old"])
                    df.drop(columns=[col+"_old"], inplace=True)

        out = OUT_DIR / "slide2_v2_android.csv"
        df.to_csv(out, index=False)
        print(f"\n  ✔ 저장: {out.name}  ({len(df)}행)")
    else:
        print("  ⚠ 수집된 잔존율 데이터 없음")
    return all_rows


# ══════════════════════════════════════════════════════════════════════════
# PART 4: slide1_v2_android — 신규 게임 3개월 생존율
# ══════════════════════════════════════════════════════════════════════════
def get_app_details_android(app_ids: list) -> dict:
    """Android 앱 상세 정보 (package_name → release_date, publisher_country 등)."""
    results = {}
    for i in range(0, len(app_ids), 100):
        chunk = app_ids[i:i+100]
        data = cached_get("/v1/android/apps", {
            "app_ids": ",".join(chunk),
        })
        if not data:
            continue
        items = data if isinstance(data, list) else data.get("apps", [])
        for app in items:
            if isinstance(app, dict):
                aid = str(app.get("app_id") or app.get("package_name", ""))
                if aid:
                    results[aid] = app
    return results


def collect_slide1_android():
    print("\n" + "="*60)
    print("PART 4: Android slide1 — 신규 게임 3개월 생존율")
    print("="*60)

    slide1_rows = []

    for country in COUNTRIES:
        print(f"\n  [{country}] 월별 랭킹 수집 중...")

        # 월별 랭킹 수집 (캐시 우선)
        months_in_chart: dict = {}   # package_name → set of "YYYY-MM"
        for dt in MONTHS:
            date_str = dt.strftime("%Y-%m-%d")
            ym       = dt.strftime("%Y-%m")
            data = cached_get("/v1/android/ranking", {
                "category":   CATEGORY_AND,
                "chart_type": CHART_TYPE,
                "date":       date_str,
                "country":    country,
                "limit":      100,
            })
            if not data:
                continue
            ranking = data.get("ranking", []) if isinstance(data, dict) else data
            for item in ranking:
                pkg = str(item) if isinstance(item, str) else str(item.get("app_id",""))
                if pkg:
                    months_in_chart.setdefault(pkg, set()).add(ym)

        all_ids = list(months_in_chart.keys())
        print(f"    → 전체 차트 앱: {len(all_ids)}개")
        if not all_ids:
            continue

        # 앱 상세 (release_date, publisher_country)
        print(f"    앱 상세 조회 중...")
        details = get_app_details_android(all_ids)
        print(f"    → 상세 조회 완료: {len(details)}개")

        # TOP 100 매출 차트 신규진입 게임 (첫 등장 월 기준, 출시일 무관)
        # survived_3m = 첫 진입월 기준 M+1, M+2, M+3 모두 TOP 100 존재
        from dateutil.relativedelta import relativedelta as _rd
        from datetime import datetime as _dt

        for pkg, months_set in months_in_chart.items():
            info = details.get(pkg, {})
            rd   = info.get("release_date", "") or info.get("original_release_date", "")
            pc   = info.get("publisher_country", "") or ""
            first_month = min(months_set)
            try:
                fm_dt = _dt.strptime(first_month, "%Y-%m")
                m1 = (fm_dt + _rd(months=1)).strftime("%Y-%m")
                m2 = (fm_dt + _rd(months=2)).strftime("%Y-%m")
                m3 = (fm_dt + _rd(months=3)).strftime("%Y-%m")
                survived = (m1 in months_set) and (m2 in months_set) and (m3 in months_set)
            except:
                survived = False
            slide1_rows.append({
                "country":           country,
                "platform":          "android",
                "app_id":            pkg,
                "name":              info.get("name", ""),
                "publisher_name":    info.get("publisher_name", ""),
                "publisher_country": pc,
                "publisher_group":   classify_publisher(pc),
                "release_date":      rd[:10],
                "first_chart_month": first_month,
                "months_in_chart":   len(months_set),
                "survived_3m":       survived,
                "period":            "post2025" if first_month >= "2025-01" else "pre2025",
            })

        c_rows = [r for r in slide1_rows if r["country"] == country]
        surv   = sum(1 for r in c_rows if r["survived_3m"])
        print(f"    [{country}] 신규 진입: {len(c_rows)}개 → 생존 {surv} / 탈락 {len(c_rows)-surv}")

    if slide1_rows:
        df = pd.DataFrame(slide1_rows)
        out = OUT_DIR / "slide1_v2_android.csv"
        df.to_csv(out, index=False)
        print(f"\n  ✔ 저장: {out.name}  ({len(df)}행)")

        # 생존율 요약
        grp = df.groupby(["country","period"])["survived_3m"].agg(["sum","count"])
        grp["rate_pct"] = (grp["sum"]/grp["count"]*100).round(1)
        print("\n  국가별 × period 생존율:")
        print(grp.to_string())

        grp2 = df.groupby(["publisher_group","period"])["survived_3m"].agg(["sum","count"])
        grp2["rate_pct"] = (grp2["sum"]/grp2["count"]*100).round(1)
        print("\n  퍼블리셔별 × period 생존율:")
        print(grp2.to_string())
    else:
        print("  ⚠ 수집된 데이터 없음 — Android 앱 상세 API 응답 확인 필요")
    return slide1_rows


# ══════════════════════════════════════════════════════════════════════════
# PART 3: 광고집행율 국가별 — ad_rate_by_country_android.csv
# ══════════════════════════════════════════════════════════════════════════
def collect_ad_rate_android():
    print("\n" + "="*60)
    print("PART 3: Android 광고집행율 (국가별 시장 기준, 최신 월 기준)")
    print("="*60)

    tags_file = OUT_DIR / "app_tags_android.csv"
    if not tags_file.exists():
        print("  ⚠ app_tags_android.csv 없음 — PART 1 먼저 실행")
        return

    # 국가별 랭킹 최신 월 (2026-01) 기준 TOP 25 앱의 광고집행율
    date_str = "2026-01-01"
    rows = []
    for country in COUNTRIES:
        data = cached_get("/v1/android/ranking", {
            "category":   CATEGORY_AND,
            "chart_type": CHART_TYPE,
            "date":       date_str,
            "country":    country,
            "limit":      25,
        })
        if not data:
            continue
        ranking = data.get("ranking", []) if isinstance(data, dict) else data
        app_ids = [str(a) if isinstance(a, str) else str(a.get("app_id") or a.get("package_name",""))
                   for a in ranking]

        # app_tags_android.csv에서 해당 앱들의 광고집행율 가져오기
        tags = pd.read_csv(tags_file)
        tags["app_id"] = tags["app_id"].astype(str)
        sub = tags[tags["app_id"].isin(app_ids)]
        if len(sub) == 0:
            print(f"  [{country}] 매칭 앱 없음")
            continue

        rows.append({
            "country":             country,
            "platform":            "android",
            "n_apps":              len(sub),
            "paid_display_pct_ww": sub["paid_display_pct_ww"].mean().round(1),
            "paid_search_pct_ww":  sub["paid_search_pct_ww"].mean().round(1),
        })
        print(f"  [{country}] n={len(sub)}, display={rows[-1]['paid_display_pct_ww']}%, search={rows[-1]['paid_search_pct_ww']}%")

    if rows:
        df = pd.DataFrame(rows)
        out = OUT_DIR / "ad_rate_by_country_android.csv"
        df.to_csv(out, index=False)
        print(f"\n  ✔ 저장: {out.name}")

    return rows


# ══════════════════════════════════════════════════════════════════════════
# PART 5: 신규게임 광고율 — newgame_ad_rates_android.csv
# ══════════════════════════════════════════════════════════════════════════
def collect_newgame_adrates_android():
    """slide1_v2_android.csv 기반 신규게임 광고집행율 수집 (AOS)."""
    print("\n" + "="*60)
    print("PART 5: AOS 신규게임 광고집행율 수집")
    print("="*60)

    s1_file = OUT_DIR / "slide1_v2_android.csv"
    if not s1_file.exists():
        print("  ⚠ slide1_v2_android.csv 없음 — PART 4 먼저 실행")
        return

    s1 = pd.read_csv(s1_file)
    s1["app_id"] = s1["app_id"].astype(str)

    # (country, year) 조합 수집
    year_to_dates = {
        2022: ["2022-07-01", "2022-04-01", "2022-10-01"],
        2023: ["2023-07-01", "2023-04-01", "2023-10-01"],
        2024: ["2024-07-01", "2024-04-01", "2024-10-01"],
        2025: ["2025-07-01", "2026-01-01", "2025-10-01"],
        2026: ["2026-03-01", "2026-01-01"],
    }

    # app_id → year 매핑 (first_chart_month 기준)
    s1["year"] = s1["first_chart_month"].str[:4].astype(int)
    combos = s1[["country","year"]].drop_duplicates().values.tolist()
    print(f"  수집 대상: {len(combos)}개 (country × year)")

    cache: dict = {}
    for country, year in combos:
        dates = year_to_dates.get(int(year), [f"{year}-07-01"])
        found = {}
        for d in dates:
            data = cached_get("/v1/android/sales_report_estimates_comparison_attributes", {
                "date":                d,
                "comparison_attribute":"absolute",
                "measure":             "revenue",
                "time_range":          "month",
                "category":            CATEGORY_AND,
                "country":             country,
            })
            if data:
                items = data if isinstance(data, list) else data.get("apps", [])
                for item in items:
                    aid = str(item.get("app_id") or item.get("package_name", ""))
                    ct  = item.get("custom_tags", {})
                    if aid and ct:
                        found[aid] = {
                            "paid_display_pct_ww": parse_pct(ct.get("Paid Display Downloads % (Last Q, WW)")),
                            "paid_search_pct_ww":  parse_pct(ct.get("Paid Search Downloads % (Last Q, WW)")),
                        }
                if found:
                    print(f"    [{country} {year}] {d} → {len(found)}개 앱")
                    break
            time.sleep(0.3)
        cache[(country, year)] = found

    rows = []
    for _, row in s1.iterrows():
        country = row["country"]
        year    = int(row["year"])
        app_id  = str(row["app_id"])
        attrs   = cache.get((country, year), {}).get(app_id, {})
        disp    = attrs.get("paid_display_pct_ww")
        srch    = attrs.get("paid_search_pct_ww")
        rows.append({
            "country":             country,
            "year":                year,
            "period":              row["period"],
            "app_id":              app_id,
            "publisher_group":     row.get("publisher_group",""),
            "platform":            "android",
            "paid_display_pct_ww": disp,
            "paid_search_pct_ww":  srch,
            "total_ww":            (disp or 0) + (srch or 0),
        })

    df = pd.DataFrame(rows)
    has_data = df["paid_display_pct_ww"].notna()
    print(f"\n  매칭 결과: {has_data.sum()}/{len(df)}행에 광고 데이터 있음")

    out = OUT_DIR / "newgame_ad_rates_android.csv"
    df.to_csv(out, index=False)
    print(f"  ✔ 저장: {out.name}")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", type=int, default=0,
                        help="1=app_tags, 2=slide2(잔존율), 3=ad_rate, 4=slide1(신규생존율), 5=newgame_adrates, 0=전체")
    args = parser.parse_args()

    if args.part in (0, 1):
        collect_app_tags_android()
    if args.part in (0, 2):
        collect_slide2_android()
    if args.part in (0, 3):
        collect_ad_rate_android()
    if args.part in (0, 4):
        collect_slide1_android()
    if args.part in (0, 5):
        collect_newgame_adrates_android()

    print("\n▶ Android 수집 완료!")
