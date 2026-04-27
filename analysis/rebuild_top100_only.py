"""
TOP 100만 사용하여 전체 데이터 재계산
- slide1_v2.csv (iOS 신규진입 + 생존율 + 차트잔존율)
- slide1_v2_android.csv (AOS 동일)
- chart_retention_newentry.csv (차트 잔존율)
"""
import sys, json, hashlib
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd

CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
OUT_DIR = Path("C:/Users/NHN/Documents/sensortower_api")
sys.path.insert(0, str(OUT_DIR))
from config import expand_country

MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES_IOS = ["KR", "JP", "US", "CN"]
COUNTRIES_AOS = ["KR", "JP", "US"]

CHINESE = {"CN","HK","TW","MO"}
WESTERN = {"US","CA","GB","DE","FR","FI","SE","NO","DK","NL","BE","CH","AT","AU","NZ","IE","IT","ES","PT","RU","PL","CZ","HU","RO","UA","GR","TR","IL","ZA","BR","MX","AR","CO","CL","PE"}
_NAME_MAP = {"SOUTH KOREA":"한국","KOREA":"한국","JAPAN":"일본","CHINA":"중화권","HONG KONG":"중화권","TAIWAN":"중화권","MACAU":"중화권","UNITED STATES":"서구권","UNITED KINGDOM":"서구권","CANADA":"서구권","AUSTRALIA":"서구권","GERMANY":"서구권","FRANCE":"서구권"}

def classify(raw):
    if not raw: return "기타"
    u = str(raw).strip().upper()
    for k, v in _NAME_MAP.items():
        if k in u: return v
    if u in CHINESE: return "중화권"
    if u in WESTERN: return "서구권"
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
    items = [str(a) if isinstance(a, str) else str(a.get("app_id","")) for a in ranking]
    return items[:100]


def get_details(path, app_ids):
    results = {}
    for i in range(0, len(app_ids), 100):
        chunk = app_ids[i:i+100]
        data = cached_json(path, {"app_ids": ",".join(str(x) for x in chunk)})
        if not data: continue
        items = data if isinstance(data, list) else data.get("apps", [])
        for app in items:
            if isinstance(app, dict):
                aid = str(app.get("app_id") or app.get("package_name",""))
                if aid: results[aid] = app
    return results


CHECK_OFFSETS = [1, 2, 3, 6, 12]
CHECK_LABELS = ["M+1", "M+2", "M+3", "M+6", "M+12"]


def check_survived_b(months_set):
    first = min(months_set)
    try:
        fm_dt = datetime.strptime(first, "%Y-%m")
        m3 = (fm_dt + relativedelta(months=3)).strftime("%Y-%m")
        return m3 in months_set
    except:
        return False


def process_platform(platform, countries, load_fn, details_path):
    print(f"\n{'='*50}")
    print(f"  {platform.upper()} 처리 (TOP 100 only)")
    print(f"{'='*50}")

    ranking_sets = {}  # (label, ym) -> set
    app_months = {}    # (label, aid) -> set of ym

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
                top100 = merged[:100]
            else:
                top100 = load_fn(label, dt.strftime("%Y-%m-%d"))[:100]

            ranking_sets[(label, ym)] = set(top100)
            for aid in top100:
                app_months.setdefault((label, aid), set()).add(ym)

    all_ids = list(set(aid for (_, aid) in app_months.keys()))
    print(f"  고유 앱: {len(all_ids)}개")
    details = get_details(details_path, all_ids)
    print(f"  상세 캐시: {len(details)}개")

    rows = []
    for (label, aid), months_set in app_months.items():
        info = details.get(aid, {})
        pc = info.get("publisher_country", "") or info.get("canonical_country", "") or ""
        first_month = min(months_set)
        survived = check_survived_b(months_set)

        row = {
            "country": label,
            "app_id": aid,
            "name": info.get("name", ""),
            "publisher_name": info.get("publisher_name", ""),
            "publisher_country": pc,
            "publisher_group": classify(pc),
            "release_date": (info.get("release_date", "") or "")[:10],
            "first_chart_month": first_month,
            "months_in_chart": len(months_set),
            "survived_3m": survived,
            "period": "post2025" if first_month >= "2025-01" else "pre2025",
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

    # 요약 출력
    for ctr in countries:
        for pk in ["pre2025", "post2025"]:
            sub = df[(df["country"] == ctr) & (df["period"] == pk)]
            if len(sub):
                sr = sub["survived_3m"].mean() * 100
                n_months = sub["first_chart_month"].nunique()
                n_mo = round(len(sub) / n_months) if n_months else 0
                print(f"  {ctr} {pk}: n={len(sub)} (월평균 {n_mo}개) 생존율={sr:.1f}%")

    return df


def main():
    # iOS
    df_ios = process_platform("ios", COUNTRIES_IOS, load_ranking_ios, "/v1/ios/apps")
    df_ios.to_csv(OUT_DIR / "slide1_v2.csv", index=False)
    print(f"\n  저장: slide1_v2.csv ({len(df_ios)}행)")

    # AOS
    df_aod = process_platform("android", COUNTRIES_AOS, load_ranking_android, "/v1/android/apps")
    df_aod.to_csv(OUT_DIR / "slide1_v2_android.csv", index=False)
    print(f"\n  저장: slide1_v2_android.csv ({len(df_aod)}행)")

    # 차트 잔존율 통합
    df_ios["platform"] = "ios"
    cols = ["platform", "country", "app_id", "first_chart_month", "period", "publisher_group"] + CHECK_LABELS
    chart_ret = pd.concat([df_ios[cols], df_aod[cols]], ignore_index=True)
    chart_ret.to_csv(OUT_DIR / "chart_retention_newentry.csv", index=False)
    print(f"\n  차트 잔존율: chart_retention_newentry.csv ({len(chart_ret)}행)")

    # 검증
    jp_feb = df_aod[(df_aod["country"] == "JP") & (df_aod["first_chart_month"] == "2022-02")]
    print(f"\n  검증: JP AOS 2022-02 신규진입: {len(jp_feb)}개 (센서타워 사이트: 24개)")


if __name__ == "__main__":
    main()
