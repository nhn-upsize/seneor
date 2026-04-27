"""
v2 전체 데이터 수집 스크립트
- PART 1: Slide1/2 — KR/JP/US/CN 생존분류 + 잔존율 (publisher_country 포함)
- PART 2: Custom Tags 룩업 빌드 (comparison_attributes 엔드포인트)
           → 광고집행여부, Paid Install%, 잔존율(D1~D365), DAU/MAU, 퍼블리셔국가
- PART 3: Slide3 — publisher_country 보강
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
from config import expand_country, CHINESE_REGION_CODES

load_dotenv()
TOKEN     = os.getenv("SENSOR_TOWER_API_TOKEN")
BASE      = "https://api.sensortower.com"
CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
OUT_DIR   = Path("C:/Users/NHN/Documents/sensortower_api")
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({"Accept": "application/json"})

# 분석 대상 월
MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES_S12 = ["KR", "JP", "US", "CN"]   # slide1/2 수집 대상 (CN = 중화권)
CATEGORY      = 6014
CHART_TYPE    = "topgrossingapplications"

# 서구권 국가코드
WESTERN_CODES = {
    "US","CA","GB","DE","FR","FI","SE","NO","DK","NL","BE","CH","AT",
    "AU","NZ","IE","IT","ES","PT","RU","PL","CZ","HU","RO","UA","GR",
    "TR","IL","ZA","BR","MX","AR","CO","CL","PE"
}


# API가 풀 이름("South Korea")과 코드("KR") 둘 다 반환하므로 모두 처리
_FULL_NAME_MAP = {
    "SOUTH KOREA": "한국", "KOREA": "한국",
    "JAPAN": "일본",
    "CHINA": "중화권", "HONG KONG": "중화권",
    "TAIWAN": "중화권", "MACAU": "중화권",
    "UNITED STATES": "서구권", "UNITED KINGDOM": "서구권",
    "CANADA": "서구권", "AUSTRALIA": "서구권", "NEW ZEALAND": "서구권",
    "GERMANY": "서구권", "FRANCE": "서구권", "FINLAND": "서구권",
    "SWEDEN": "서구권", "NORWAY": "서구권", "DENMARK": "서구권",
    "NETHERLANDS": "서구권", "BELGIUM": "서구권", "SWITZERLAND": "서구권",
    "AUSTRIA": "서구권", "IRELAND": "서구권", "ITALY": "서구권",
    "SPAIN": "서구권", "PORTUGAL": "서구권",
}


def classify_publisher(pc: str) -> str:
    if not pc:
        return "기타"
    pc_upper = pc.strip().upper()
    if pc_upper in _FULL_NAME_MAP:
        return _FULL_NAME_MAP[pc_upper]
    if pc_upper == "KR":
        return "한국"
    if pc_upper == "JP":
        return "일본"
    if pc_upper in {c.upper() for c in CHINESE_REGION_CODES}:
        return "중화권"
    if pc_upper in WESTERN_CODES:
        return "서구권"
    return "기타"


# ─────────────────────────────────────────────────────────────────────────────
# 공통 헬퍼
# ─────────────────────────────────────────────────────────────────────────────

def load_ranking(country_code: str, date_str: str) -> list:
    """단일 국가코드 랭킹 조회 (캐시 우선)."""
    params = {"category": CATEGORY, "chart_type": CHART_TYPE,
              "date": date_str, "country": country_code}
    h = hashlib.md5(json.dumps({"path": "/v1/ios/ranking", "params": params},
                                sort_keys=True).encode()).hexdigest()
    f = CACHE_DIR / f"{h}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8")).get("ranking", [])
    r = session.get(f"{BASE}/v1/ios/ranking",
                    params={"auth_token": TOKEN, **params}, timeout=15)
    data = r.json()
    f.write_text(json.dumps(data), encoding="utf-8")
    return data.get("ranking", []) if isinstance(data, dict) else []


def load_ranking_for_label(label: str, date_str: str) -> list:
    """레이블(KR/JP/US/CN) → 해당 국가코드 합산 랭킹 (중복 제거)."""
    codes = expand_country(label)
    seen, merged = set(), []
    for code in codes:
        for app_id in load_ranking(code, date_str):
            if app_id not in seen:
                seen.add(app_id)
                merged.append(app_id)
    return merged


def get_app_details_bulk(app_ids: list) -> dict:
    """앱 상세 100개씩 조회 (publisher_country 포함)."""
    results = {}
    for i in range(0, len(app_ids), 100):
        chunk = app_ids[i:i+100]
        r = session.get(f"{BASE}/v1/ios/apps",
            params={"auth_token": TOKEN,
                    "app_ids": ",".join(str(x) for x in chunk)},
            timeout=20)
        if r.status_code != 200:
            continue
        raw = r.json()
        items = raw if isinstance(raw, list) else raw.get("apps", [])
        for app in items:
            if isinstance(app, dict):
                results[str(app.get("app_id", ""))] = app
        time.sleep(0.2)
    return results


def get_retention(app_ids: list, label: str, year: int) -> dict:
    """레이블별 잔존율 (CN은 CN+HK+TW+MO 평균)."""
    end = "2026-03-31" if year == 2026 else f"{year}-12-31"
    codes = expand_country(label)
    all_data = []
    for code in codes:
        r = session.get(f"{BASE}/v1/ios/usage/retention",
            params={"auth_token": TOKEN,
                    "app_ids": ",".join(str(x) for x in app_ids),
                    "start_date": f"{year}-01-01", "end_date": end,
                    "country": code, "retention_days": "1,7,14,30,60,90,180,365"},
            timeout=30)
        if r.status_code == 200:
            all_data.extend(r.json().get("app_data", []))
    return {"app_data": all_data}


# ─────────────────────────────────────────────────────────────────────────────
# PART 1 : Slide1 / Slide2 수집
# ─────────────────────────────────────────────────────────────────────────────

def collect_slide1_slide2():
    print("\n" + "="*60)
    print("PART 1: Slide1/2 데이터 수집 (KR/JP/US/CN, publisher_country 포함)")
    print("="*60)

    slide1_rows, slide2_rows = [], []

    for label in COUNTRIES_S12:
        codes = expand_country(label)
        label_str = f"{label}({'+'.join(codes)})" if len(codes) > 1 else label
        print(f"\n[{label_str}] 수집 시작")

        # 월별 랭킹 (캐시 활용)
        months_in_chart: dict[int, set] = {}
        for dt in MONTHS:
            ym = dt.strftime("%Y-%m")
            for app_id in load_ranking_for_label(label, dt.strftime("%Y-%m-%d")):
                months_in_chart.setdefault(int(app_id), set()).add(ym)

        all_ids = list(months_in_chart.keys())
        print(f"  전체 차트 앱: {len(all_ids)}개")

        # 앱 상세 (release_date, publisher_country)
        print("  앱 상세 조회 중...")
        details = get_app_details_bulk(all_ids)

        # Slide 1: TOP 100 매출 차트 신규진입 게임 (첫 등장 월 기준, 출시일 무관)
        # survived_3m = 첫 진입월 기준 M+1, M+2, M+3 모두 TOP 100 존재
        from dateutil.relativedelta import relativedelta as _rd
        from datetime import datetime as _dt

        for app_id, months_set in months_in_chart.items():
            info = details.get(str(app_id), {})
            rd   = info.get("release_date") or ""
            pc   = info.get("publisher_country", "") or ""
            first_month  = min(months_set)
            # 연속 3개월 생존 판정: M+1, M+2, M+3 모두 존재해야 함
            try:
                fm_dt = _dt.strptime(first_month, "%Y-%m")
                m1 = (fm_dt + _rd(months=1)).strftime("%Y-%m")
                m2 = (fm_dt + _rd(months=2)).strftime("%Y-%m")
                m3 = (fm_dt + _rd(months=3)).strftime("%Y-%m")
                survived = (m1 in months_set) and (m2 in months_set) and (m3 in months_set)
            except:
                survived = False
            slide1_rows.append({
                "country":          label,
                "app_id":           app_id,
                "name":             info.get("name", ""),
                "publisher_name":   info.get("publisher_name", ""),
                "publisher_country":pc,
                "publisher_group":  classify_publisher(pc),
                "release_date":     rd[:10] if rd else "",
                "first_chart_month":first_month,
                "months_in_chart":  len(months_set),
                "survived_3m":      survived,
                "period":           "post2025" if first_month >= "2025-01" else "pre2025",
            })

        country_s1 = [r for r in slide1_rows if r["country"] == label]
        survived   = sum(1 for r in country_s1 if r["survived_3m"])
        churned    = len(country_s1) - survived
        print(f"  [{label}] 신규 진입: {len(country_s1)}개 → 생존 {survived} / 탈락 {churned}")

        # Slide 2: 연도별 잔존율
        new_by_year: dict[str, list] = {}
        for row in country_s1:
            yr = row["release_date"][:4]
            new_by_year.setdefault(yr, []).append(row["app_id"])

        for year in range(2022, 2027):
            ids = new_by_year.get(str(year), [])[:50]
            if not ids:
                continue
            print(f"  {label} {year}년 잔존율 조회 ({len(ids)}개)...", flush=True)
            data = get_retention(ids, label, year)

            ret_by_app: dict = {}
            for item in data.get("app_data", []):
                aid = item.get("app_id")
                ret = item.get("corrected_retention", [])
                ret_by_app.setdefault(aid, []).append(ret)

            for aid, rets in ret_by_app.items():
                def avg(idx):
                    vals = [r[idx] for r in rets if len(r) > idx]
                    return round(sum(vals) / len(vals) * 100, 1) if vals else None

                app_info = details.get(str(aid), {})
                pc       = app_info.get("publisher_country", "") or ""
                slide2_rows.append({
                    "country":         label,
                    "year":            year,
                    "period":          "post2025" if year >= 2025 else "pre2025",
                    "app_id":          aid,
                    "publisher_country": pc,
                    "publisher_group": classify_publisher(pc),
                    "d1":   avg(0),
                    "d7":   avg(6),
                    "d14":  avg(13),
                    "d30":  avg(29),
                    "d60":  avg(59),
                    "d90":  avg(89),
                    "d180": avg(179),
                    "d365": avg(364),
                })

    # 저장
    df1 = pd.DataFrame(slide1_rows)
    df1.to_csv(OUT_DIR / "slide1_v2.csv", index=False, encoding="utf-8-sig")
    print(f"\n[저장] slide1_v2.csv — {len(df1)}행")

    df2 = pd.DataFrame(slide2_rows)
    if not df2.empty:
        df2.to_csv(OUT_DIR / "slide2_v2.csv", index=False, encoding="utf-8-sig")
        print(f"[저장] slide2_v2.csv — {len(df2)}행")

    return df1, df2


# ─────────────────────────────────────────────────────────────────────────────
# PART 2 : Custom Tags 룩업 빌드 (comparison_attributes 엔드포인트)
# ─────────────────────────────────────────────────────────────────────────────

def parse_pct(val: str) -> float | None:
    """'28%' → 28.0, '$0.61' → 0.61, None → None"""
    if not val:
        return None
    val = str(val).strip()
    m = re.search(r"[\d.]+", val)
    return float(m.group()) if m else None


def collect_custom_tags():
    print("\n" + "="*60)
    print("PART 2: Custom Tags 룩업 빌드 (comparison_attributes)")
    print("="*60)

    tags_cache_file = OUT_DIR / "app_tags_raw.json"

    # 이미 수집한 캐시가 있으면 로드
    tags_by_app: dict = {}
    if tags_cache_file.exists():
        tags_by_app = json.loads(tags_cache_file.read_text(encoding="utf-8"))
        print(f"  기존 캐시 로드: {len(tags_by_app)}개 앱")

    queried_months = set(tags_by_app.get("__queried_months__", []))

    for dt in MONTHS:
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in queried_months:
            continue

        r = session.get(f"{BASE}/v1/ios/sales_report_estimates_comparison_attributes",
            params={
                "auth_token":          TOKEN,
                "date":                date_str,
                "comparison_attribute":"absolute",
                "measure":             "revenue",
                "time_range":          "month",
                "device_type":         "total",
                "category":            CATEGORY,
            }, timeout=20)

        if r.status_code != 200:
            print(f"  {date_str} → {r.status_code} skip")
            time.sleep(0.5)
            continue

        for item in r.json():
            aid = str(item.get("app_id", ""))
            ct  = item.get("custom_tags", {})
            if aid and ct:
                # 기존 데이터가 있으면 최신으로 덮어씀 (latest available)
                tags_by_app[aid] = ct

        queried_months.add(date_str)
        print(f"  {date_str} 완료  (누적 {len(tags_by_app)}개 앱)")
        time.sleep(0.3)

    tags_by_app["__queried_months__"] = list(queried_months)
    tags_cache_file.write_text(
        json.dumps(tags_by_app, ensure_ascii=False), encoding="utf-8")

    # 정제된 CSV 생성
    rows = []
    for aid, ct in tags_by_app.items():
        if aid.startswith("__"):
            continue
        rows.append({
            "app_id":              aid,
            "publisher_country":   ct.get("Publisher Country", ""),
            "publisher_group":     classify_publisher(ct.get("Publisher Country", "")),
            "ad_active":           1 if "Active" in str(ct.get("Advertised on Any Network","")) else 0,
            "paid_display_pct_us": parse_pct(ct.get("Paid Display Downloads % (Last Q, US)", "")),
            "paid_search_pct_us":  parse_pct(ct.get("Paid Search Downloads % (Last Q, US)", "")),
            "paid_display_pct_ww": parse_pct(ct.get("Paid Display Downloads % (Last Q, WW)", "")),
            "paid_search_pct_ww":  parse_pct(ct.get("Paid Search Downloads % (Last Q, WW)", "")),
            "d1_ret_ww":           parse_pct(ct.get("Day 1 Retention (Latest Available, WW)", "")),
            "d7_ret_ww":           parse_pct(ct.get("Day 7 Retention (Latest Available, WW)", "")),
            "d14_ret_ww":          parse_pct(ct.get("Day 14 Retention (Latest Available, WW)", "")),
            "d30_ret_ww":          parse_pct(ct.get("Day 30 Retention (Latest Available, WW)", "")),
            "d60_ret_ww":          parse_pct(ct.get("Day 60 Retention (Latest Available, WW)", "")),
            "d90_ret_ww":          parse_pct(ct.get("Day 90 Retention (Latest Available, WW)", "")),
            "d180_ret_ww":         parse_pct(ct.get("Day 180 Retention (Latest Available, WW)", "")),
            "d365_ret_ww":         parse_pct(ct.get("Day 365 Retention (Latest Available, WW)", "")),
            "dau_ww":              parse_pct(ct.get("Last 30 Days Average DAU (WW)", "")),
            "mau_ww":              parse_pct(ct.get("Last Month Average MAU (WW)", "")),
            "arpdau_ww":           parse_pct(ct.get("ARPDAU (Last Month, WW)", "")),
            "genre":               ct.get("Storefront Game Subcategory", ""),
            "gender_us":           ct.get("Genders (Last Quarter, US)", ""),
            "age_us":              ct.get("Predominant Age (Last Quarter, US)", ""),
            "sdk_adjust":          1 if ct.get("SDK: Adjust") == "true" else 0,
            "sdk_firebase":        1 if ct.get("SDK: Firebase") == "true" else 0,
        })

    df_tags = pd.DataFrame(rows)
    df_tags.to_csv(OUT_DIR / "app_tags.csv", index=False, encoding="utf-8-sig")
    print(f"\n[저장] app_tags.csv — {len(df_tags)}행 ({df_tags['publisher_country'].nunique()}개 국가)")

    return df_tags


# ─────────────────────────────────────────────────────────────────────────────
# PART 3 : Slide3 publisher_country 보강
# ─────────────────────────────────────────────────────────────────────────────

def enrich_slide3(df_tags: pd.DataFrame):
    print("\n" + "="*60)
    print("PART 3: Slide3 publisher_country 보강")
    print("="*60)

    df3 = pd.read_csv(OUT_DIR / "slide3_rank_revenue.csv")
    df3["app_id"] = df3["app_id"].astype(str)

    # tags 룩업
    tags_lookup = df_tags.set_index("app_id")[["publisher_country","publisher_group"]].to_dict("index")

    # 룩업에 없는 app_id → apps API fallback
    missing_ids = [x for x in df3["app_id"].unique() if x not in tags_lookup]
    if missing_ids:
        print(f"  앱 상세 fallback 조회: {len(missing_ids)}개")
        fallback = get_app_details_bulk(missing_ids)
        for aid, info in fallback.items():
            pc = info.get("publisher_country", "") or ""
            tags_lookup[aid] = {
                "publisher_country": pc,
                "publisher_group":   classify_publisher(pc),
            }

    df3["publisher_country"] = df3["app_id"].map(
        lambda x: tags_lookup.get(x, {}).get("publisher_country", ""))
    df3["publisher_group"] = df3["app_id"].map(
        lambda x: tags_lookup.get(x, {}).get("publisher_group", "기타"))
    df3["period"] = df3["ym"].apply(
        lambda x: "post2025" if x >= "2025-01" else "pre2025")

    df3.to_csv(OUT_DIR / "slide3_v2.csv", index=False, encoding="utf-8-sig")
    print(f"[저장] slide3_v2.csv — {len(df3)}행")
    print(f"  퍼블리셔 분포:\n{df3['publisher_group'].value_counts().to_string()}")

    return df3


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", type=int, default=0,
                        help="1=slide1/2(신규게임+잔존율), 2=custom_tags, 3=slide3보강, 0=전체")
    args = parser.parse_args()

    print("▶ v2 데이터 수집 시작")
    print("  대상: KR/JP/US/CN(중화권) × 2022-01~2026-03")
    print(f"  차트 기준: {CHART_TYPE}")

    if args.part in (0, 1):
        df1, df2 = collect_slide1_slide2()
        print(f"  slide1_v2.csv : {len(df1)}행")
        print(f"  slide2_v2.csv : {len(df2)}행")

    if args.part in (0, 2):
        df_tags = collect_custom_tags()
        print(f"  app_tags.csv  : {len(df_tags)}행")
    elif args.part == 3:
        # part 3만 단독 실행 시 app_tags를 파일에서 로드
        import pandas as _pd
        df_tags = _pd.read_csv(OUT_DIR / "app_tags.csv")
        df_tags["app_id"] = df_tags["app_id"].astype(str)

    if args.part in (0, 3):
        df3 = enrich_slide3(df_tags)
        print(f"  slide3_v2.csv : {len(df3)}행")

    print("\n" + "="*60)
    print("완료!")
    print("="*60)
