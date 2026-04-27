"""
Slide 1 & 2 — KR/JP/CN(중화권) 데이터 수집
중화권 = CN + HK + TW + MO 합산 → 레이블은 CN으로 통일
"""
import sys, json, hashlib
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
import requests, os
from dotenv import load_dotenv
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DEFAULT_COUNTRIES, expand_country, is_target_country

load_dotenv()
TOKEN = os.getenv("SENSOR_TOWER_API_TOKEN")
CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
session = requests.Session()
session.headers.update({"Accept": "application/json"})

MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

# KR, JP, CN(중화권) — US는 Slide 1/2에서 제외
COUNTRIES = ["KR", "JP", "CN"]
CATEGORY  = 6014
CHART_TYPE = "topgrossingapplications"


def load_ranking(country_code, date_str):
    """단일 국가코드(예: CN, HK, TW, MO)로 랭킹 조회 (캐시 활용)."""
    params = {"category": CATEGORY, "chart_type": CHART_TYPE,
              "date": date_str, "country": country_code}
    h = hashlib.md5(json.dumps({"path": "/v1/ios/ranking", "params": params},
                                sort_keys=True).encode()).hexdigest()
    f = CACHE_DIR / f"{h}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8")).get("ranking", [])
    r = session.get("https://api.sensortower.com/v1/ios/ranking",
                    params={"auth_token": TOKEN, **params}, timeout=15)
    data = r.json()
    f.write_text(json.dumps(data), encoding="utf-8")
    return data.get("ranking", []) if isinstance(data, dict) else []


def load_ranking_for_label(label, date_str):
    """
    분석 레이블(KR/JP/CN 등) → 해당하는 모든 국가코드 조회 후 합산.
    CN이면 CN+HK+TW+MO 랭킹을 모두 합쳐서 반환 (중복 app_id는 set으로 처리).
    """
    codes = expand_country(label)
    merged = set()
    for code in codes:
        merged.update(load_ranking(code, date_str))
    return list(merged)


def get_app_details(app_ids):
    """앱 상세 (release_date 포함), 100개씩."""
    results = {}
    for i in range(0, len(app_ids), 100):
        chunk = app_ids[i:i+100]
        r = session.get("https://api.sensortower.com/v1/ios/apps",
            params={"auth_token": TOKEN, "app_ids": ",".join(str(x) for x in chunk)},
            timeout=20)
        raw = r.json() if r.status_code == 200 else []
        items = raw if isinstance(raw, list) else raw.get("apps", [])
        for app in items:
            if isinstance(app, dict):
                results[app["app_id"]] = app
    return results


def get_retention(app_ids, label, year):
    """
    분석 레이블(KR/JP/CN)에 해당하는 모든 국가코드의 잔존율 조회.
    CN이면 CN+HK+TW+MO 각각 조회 후 app_data를 합산.
    """
    end = "2026-03-31" if year == 2026 else f"{year}-12-31"
    codes = expand_country(label)
    all_app_data = []

    for code in codes:
        r = session.get("https://api.sensortower.com/v1/ios/usage/retention",
            params={"auth_token": TOKEN,
                    "app_ids": ",".join(str(x) for x in app_ids),
                    "start_date": f"{year}-01-01", "end_date": end,
                    "country": code, "retention_days": "1,7,14,30"},
            timeout=30)
        if r.status_code == 200:
            data = r.json()
            all_app_data.extend(data.get("app_data", []))

    return {"app_data": all_app_data}


# ── MAIN ────────────────────────────────────────────────────────
slide1_rows = []
slide2_rows = []

for label in COUNTRIES:
    codes = expand_country(label)
    print(f"\n{'='*40}")
    if len(codes) > 1:
        print(f"[{label}] 중화권 통합 수집: {codes}")
    else:
        print(f"[{label}] 데이터 수집 시작")
    print(f"{'='*40}")

    # 1) 월별 랭킹 — 레이블에 해당하는 모든 국가코드 합산
    months_in_chart = {}
    for dt in MONTHS:
        ym = dt.strftime("%Y-%m")
        for app_id in load_ranking_for_label(label, dt.strftime("%Y-%m-%d")):
            months_in_chart.setdefault(int(app_id), set()).add(ym)

    all_ids = list(months_in_chart.keys())
    print(f"  전체 차트 앱: {len(all_ids)}개 ({'+'.join(codes)} 합산)")

    # 2) 앱 상세 (release_date)
    print(f"  앱 상세 조회 중...")
    details = get_app_details(all_ids)

    # 3) Slide 1: 생존/탈락 분류
    for app_id, months_set in months_in_chart.items():
        info = details.get(app_id, {})
        rd = info.get("release_date", "")
        if not rd:
            continue
        first_month = min(months_set)
        release_ym = rd[:7]
        if release_ym != first_month:
            continue  # 신규 진입 게임만
        slide1_rows.append({
            "country": label,          # CN으로 통일 표시
            "app_id": app_id,
            "name": info.get("name", ""),
            "release_date": rd[:10],
            "first_chart_month": first_month,
            "months_in_chart": len(months_set),
            "survived_3m": len(months_set) >= 3,
        })

    country_s1 = [r for r in slide1_rows if r["country"] == label]
    survived = sum(1 for r in country_s1 if r["survived_3m"])
    churned  = sum(1 for r in country_s1 if not r["survived_3m"])
    print(f"  [{label}] 신규 진입: {len(country_s1)}개 → 생존 {survived} / 탈락 {churned}")

    # 4) Slide 2: 연도별 잔존율
    new_by_year = {}
    for r in country_s1:
        yr = r["release_date"][:4]
        new_by_year.setdefault(yr, []).append(r["app_id"])

    for year in range(2022, 2027):
        ids = new_by_year.get(str(year), [])[:50]
        if not ids:
            continue
        print(f"  {label} {year}년 잔존율 조회 ({len(ids)}개, {'+'.join(codes)})...", flush=True)
        data = get_retention(ids, label, year)

        # 같은 app_id가 여러 국가에서 올 수 있으므로 평균 처리
        ret_by_app = {}
        for item in data.get("app_data", []):
            ret = item.get("corrected_retention", [])
            aid = item.get("app_id")
            if aid not in ret_by_app:
                ret_by_app[aid] = []
            ret_by_app[aid].append(ret)

        for aid, rets in ret_by_app.items():
            # 여러 국가 잔존율 → 평균
            def avg_idx(idx):
                vals = [r[idx] for r in rets if len(r) > idx]
                return round(sum(vals) / len(vals) * 100, 1) if vals else None

            slide2_rows.append({
                "country": label,
                "year": year,
                "app_id": aid,
                "d1":  avg_idx(0),
                "d7":  avg_idx(6),
                "d14": avg_idx(13),
                "d30": avg_idx(29),
            })

print("\n완료, 저장 중...")

# 저장
out = Path("C:/Users/NHN/Documents/sensortower_api")

df1 = pd.DataFrame(slide1_rows)
df1.to_csv(out / "slide1_classification_all.csv", index=False)
print(f"Slide1 저장: {len(df1)}행")
print(df1.groupby(["country", "survived_3m"]).size().reset_index(name="count").to_string(index=False))

df2 = pd.DataFrame(slide2_rows)
if not df2.empty:
    summary2 = df2.groupby(["country", "year"])[["d1", "d7", "d14", "d30"]].mean().round(1).reset_index()
    summary2.to_csv(out / "slide2_retention_all.csv", index=False)
    print(f"\nSlide2 저장: {len(summary2)}행")
    print(summary2.to_string(index=False))
