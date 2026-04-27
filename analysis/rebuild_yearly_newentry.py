"""
신규진입 기준 변경: 각 연도별 1월 TOP100 = 기준선, 2월부터 신규진입 판정
- 각 연도 1월 제외, 2~12월만 집계
- pre2025 (2022~2024 각 2~12월) vs post2025 (2025 2~12월 + 2026 2~3월) 월평균
"""
import sys, json, hashlib, time, os, requests
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd

TOKEN = "ST0_g63UDQaD_YGooSG75BhhRdA"
BASE_URL = "https://api.sensortower.com"
CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
OUT_DIR = Path("C:/Users/NHN/Documents/sensortower_api")
session = requests.Session()
session.headers.update({"Accept": "application/json"})

sys.path.insert(0, str(OUT_DIR))
from config import expand_country

MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES_IOS = ["KR", "JP", "US", "CN"]
COUNTRIES_AOS = ["KR", "JP", "US"]
YEARS = [2022, 2023, 2024, 2025, 2026]

CHINESE = {"CN","HK","TW","MO"}
NA_CODES = {"US","CA"}
_NM = {"SOUTH KOREA":"한국","KOREA":"한국","JAPAN":"일본","CHINA":"중화권","HONG KONG":"중화권","TAIWAN":"중화권","MACAU":"중화권","UNITED STATES":"북미","CANADA":"북미"}

def classify(raw):
    if not raw: return "기타"
    u = str(raw).strip().upper()
    for k, v in _NM.items():
        if k in u: return v
    if u in CHINESE: return "중화권"
    if u in NA_CODES: return "북미"
    if u in {"JP","JPN"}: return "일본"
    if u in {"KR","KOR"}: return "한국"
    return "기타"


def cached_json(path, params):
    safe = {k: v for k, v in params.items() if k != "auth_token"}
    h = hashlib.md5(json.dumps({"path": path, "params": safe}, sort_keys=True).encode()).hexdigest()
    f = CACHE_DIR / f"{h}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return None


def load_ranking_ios(country_code, date_str):
    data = cached_json("/v1/ios/ranking", {"category": 6014, "chart_type": "topgrossingapplications", "date": date_str, "country": country_code})
    if not data: return []
    ranking = data.get("ranking", []) if isinstance(data, dict) else data
    return [str(x) for x in ranking[:100]]


def load_ranking_android(country, date_str):
    data = cached_json("/v1/android/ranking", {"category": "game", "chart_type": "topgrossing", "date": date_str, "country": country, "limit": 100})
    if not data: return []
    ranking = data.get("ranking", data) if isinstance(data, dict) else data
    return [str(a) if isinstance(a, str) else str(a.get("app_id","")) for a in ranking][:100]


def fetch_details(platform, app_ids):
    results = {}
    for i in range(0, len(app_ids), 100):
        chunk = app_ids[i:i+100]
        r = session.get(f"{BASE_URL}/v1/{platform}/apps",
                        params={"auth_token": TOKEN, "app_ids": ",".join(chunk)}, timeout=30)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 10)))
            r = session.get(f"{BASE_URL}/v1/{platform}/apps",
                            params={"auth_token": TOKEN, "app_ids": ",".join(chunk)}, timeout=30)
        if r.status_code == 200:
            items = r.json() if isinstance(r.json(), list) else r.json().get("apps", [])
            for app in items:
                aid = str(app.get("app_id") or app.get("package_name", ""))
                pc = app.get("publisher_country", "") or app.get("canonical_country", "") or ""
                results[aid] = {"pc": pc, "name": app.get("name",""), "pub_name": app.get("publisher_name","")}
        time.sleep(0.15)
    return results


CHECK_OFFSETS = [1, 2, 3, 6, 12]
CHECK_LABELS = ["M+1", "M+2", "M+3", "M+6", "M+12"]


def check_survived_b(first_month, ranking_sets, label, aid):
    """M+3 시점 TOP100 존재 여부"""
    try:
        fm_dt = datetime.strptime(first_month, "%Y-%m")
        m3 = (fm_dt + relativedelta(months=3)).strftime("%Y-%m")
        return aid in ranking_sets.get((label, m3), set())
    except:
        return False


def process_platform(platform, countries, load_fn, details_api_path):
    print(f"\n{'='*50}")
    print(f"  {platform.upper()} 처리")
    print(f"{'='*50}")

    # 1) 전체 월별 TOP100 세트 구축
    ranking_sets = {}  # (label, ym) -> set
    for label in countries:
        if platform == "ios":
            codes = expand_country(label)
        else:
            codes = [label]
        for dt in MONTHS:
            ym = dt.strftime("%Y-%m")
            if platform == "ios":
                merged = []
                seen = set()
                for code in codes:
                    for aid in load_fn(code, dt.strftime("%Y-%m-%d")):
                        if aid not in seen:
                            seen.add(aid)
                            merged.append(aid)
                ranking_sets[(label, ym)] = set(merged[:100])
            else:
                ranking_sets[(label, ym)] = set(load_fn(label, dt.strftime("%Y-%m-%d"))[:100])

    # 2) 연도별 신규진입 판정 (1월=기준선, 2월부터 신규)
    new_entries = []  # (label, aid, first_chart_month)
    app_all_months = {}  # (label, aid) -> set of all ym appeared

    for label in countries:
        for year in YEARS:
            # 해당 연도 1월 = 기준선
            jan_ym = f"{year}-01"
            seen_this_year = set(ranking_sets.get((label, jan_ym), set()))

            # 해당 연도 가용 월 (2월~)
            year_months = []
            for dt in MONTHS:
                if dt.year == year and dt.month >= 2:
                    year_months.append(dt)

            for dt in year_months:
                ym = dt.strftime("%Y-%m")
                top100 = ranking_sets.get((label, ym), set())
                for aid in top100:
                    if aid not in seen_this_year:
                        new_entries.append((label, aid, ym))
                        seen_this_year.add(aid)
                    # 전체 등장 월 추적
                    app_all_months.setdefault((label, aid), set()).add(ym)

            # 1월도 전체 등장 월에는 추가 (잔존율 체크용)
            for aid in ranking_sets.get((label, jan_ym), set()):
                app_all_months.setdefault((label, aid), set()).add(jan_ym)

    print(f"  신규진입 게임: {len(new_entries)}개")

    # 3) 앱 상세 조회
    unique_ids = list(set(aid for _, aid, _ in new_entries))
    print(f"  고유 앱: {len(unique_ids)}개, 상세 조회 중...")
    details = fetch_details(platform if platform != "ios" else "ios", unique_ids)
    print(f"  상세: {len(details)}개")

    # 4) 행 생성
    rows = []
    for label, aid, first_month in new_entries:
        info = details.get(aid, {})
        pc = info.get("pc", "")
        survived = check_survived_b(first_month, ranking_sets, label, aid)
        period = "post2025" if first_month >= "2025-01" else "pre2025"

        row = {
            "country": label,
            "app_id": aid,
            "name": info.get("name", ""),
            "publisher_name": info.get("pub_name", ""),
            "publisher_country": pc,
            "publisher_group": classify(pc),
            "first_chart_month": first_month,
            "months_in_chart": len(app_all_months.get((label, aid), set())),
            "survived_3m": survived,
            "period": period,
        }
        if platform == "android":
            row["platform"] = "android"

        # 차트 잔존율
        try:
            fm_dt = datetime.strptime(first_month, "%Y-%m")
            for offset, lbl in zip(CHECK_OFFSETS, CHECK_LABELS):
                target_ym = (fm_dt + relativedelta(months=offset)).strftime("%Y-%m")
                row[lbl] = 1 if aid in ranking_sets.get((label, target_ym), set()) else 0
        except:
            for lbl in CHECK_LABELS:
                row[lbl] = 0

        rows.append(row)

    df = pd.DataFrame(rows)

    # 요약
    for ctr in countries:
        for pk in ["pre2025", "post2025"]:
            sub = df[(df["country"] == ctr) & (df["period"] == pk)]
            if len(sub):
                m = sub["first_chart_month"].nunique()
                avg = len(sub) / m if m else 0
                sr = sub["survived_3m"].mean() * 100
                print(f"  {ctr} {pk}: n={len(sub)} ({m}개월, 월평균 {avg:.1f}개) 생존율={sr:.1f}%")

    return df


def main():
    df_ios = process_platform("ios", COUNTRIES_IOS, load_ranking_ios, "ios")
    df_ios.to_csv(OUT_DIR / "slide1_v2.csv", index=False)
    print(f"\n  저장: slide1_v2.csv ({len(df_ios)}행)")

    df_aod = process_platform("android", COUNTRIES_AOS, load_ranking_android, "android")
    df_aod.to_csv(OUT_DIR / "slide1_v2_android.csv", index=False)
    print(f"\n  저장: slide1_v2_android.csv ({len(df_aod)}행)")

    # 차트 잔존율
    df_ios["platform"] = "ios"
    cols = ["platform", "country", "app_id", "first_chart_month", "period", "publisher_group"] + CHECK_LABELS
    cr = pd.concat([df_ios[cols], df_aod[cols]], ignore_index=True)
    cr.to_csv(OUT_DIR / "chart_retention_newentry.csv", index=False)
    print(f"\n  차트 잔존율: {len(cr)}행")

    # 검증
    jp_feb = df_aod[(df_aod["country"] == "JP") & (df_aod["first_chart_month"] == "2022-02")]
    print(f"\n  검증: JP AOS 2022-02 = {len(jp_feb)}개 (센서타워: 24개)")


if __name__ == "__main__":
    main()
