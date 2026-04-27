"""
SLIDE 3: 국가×순위별 월 매출 — 메모리 처리 버전

핵심:
- 랭킹: 캐시에서 로드 (CN은 CN+HK+TW+MO 합산)
- 매출: 10개씩 배치 × 1년 단위 조회 → 메모리에서 즉시 필터 → 캐시 저장 안 함
- 중화권(CN) = CN+HK+TW+MO 통합, 레이블은 CN으로 표시
"""
import sys, json, hashlib, time, requests, os
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DEFAULT_COUNTRIES, expand_country

load_dotenv()
TOKEN = os.getenv("SENSOR_TOWER_API_TOKEN")
CACHE_DIR = Path('C:/Users/NHN/Documents/sensortower_api/.cache')

MONTHS = []
d = date(2022, 1, 1)
while d <= date(2026, 3, 1):
    MONTHS.append(d)
    d += relativedelta(months=1)

COUNTRIES    = DEFAULT_COUNTRIES   # ["KR", "JP", "US", "CN"]
TARGET_RANKS = [1, 10, 20, 50, 100]
CATEGORY, CHART_TYPE = 6014, "topgrossingapplications"
session = requests.Session()
session.headers.update({"Accept": "application/json"})


def load_ranking_cached(country_code, date_str):
    """단일 국가코드 랭킹 조회 (캐시 활용)."""
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
    f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data.get("ranking", []) if isinstance(data, dict) else []


def load_ranking_for_label(label, date_str):
    """
    분석 레이블(KR/JP/US/CN) → 해당 국가코드 합산 랭킹.
    CN이면 CN+HK+TW+MO 4개국 TOP200을 합쳐서 중복 제거 후 반환.
    """
    codes = expand_country(label)
    merged = []
    seen = set()
    for code in codes:
        for app_id in load_ranking_cached(code, date_str):
            if app_id not in seen:
                seen.add(app_id)
                merged.append(app_id)
    return merged


def fetch_batch_revenue(app_ids, country_codes, year):
    """
    10개 앱, 1년치 매출 → country_codes에 해당하는 행만 즉시 추출.
    CN이면 CN+HK+TW+MO 모두 합산.
    캐시 저장 안 함 (수MB ~ 수십MB 방지).
    Returns: {(app_id, ym): revenue_usd}
    """
    end = "2026-03-31" if year == 2026 else f"{year}-12-31"
    r = session.get(
        "https://api.sensortower.com/v1/ios/sales_report_estimates",
        params={"auth_token": TOKEN,
                "app_ids": ",".join(str(x) for x in app_ids),
                "start_date": f"{year}-01-01",
                "end_date": end,
                "granularity": "monthly"},
        timeout=30,
    )
    result = {}
    if r.status_code != 200:
        return result
    for item in r.json():
        if item.get("cc") not in country_codes:   # 중화권이면 4개국 모두 포함
            continue
        key = (int(item["aid"]), item["d"][:7])
        result[key] = result.get(key, 0) + item.get("ar", 0) / 100
    return result


def fetch_slide3():
    rows = []

    for label in COUNTRIES:
        codes = expand_country(label)
        if len(codes) > 1:
            print(f"\n[{label}] 중화권 통합 수집: {codes}")
        else:
            print(f"\n[{label}] 랭킹 로드...")

        # 1) 랭킹 캐시 로드 (중화권은 4개국 합산)
        ranking_map = {}
        for dt in MONTHS:
            ym = dt.strftime("%Y-%m")
            ranking_map[ym] = load_ranking_for_label(label, dt.strftime("%Y-%m-%d"))

        # 2) 타겟 앱 확정
        targets = []
        for dt in MONTHS:
            ym = dt.strftime("%Y-%m")
            rl = ranking_map.get(ym, [])
            for rank in TARGET_RANKS:
                if rank - 1 < len(rl):
                    targets.append((ym, rank, int(rl[rank - 1])))

        unique_ids = list({t[2] for t in targets})
        print(f"  고유 앱 {len(unique_ids)}개 ({'+'.join(codes)} 합산)")

        # 3) 10개씩 × 연도별 매출 조회 (중화권은 4개국 합산)
        rev_map = {}
        BATCH = 10
        years = list(range(2022, 2027))
        total_batches = (len(unique_ids) // BATCH + 1) * len(years)
        n = 0
        for year in years:
            for i in range(0, len(unique_ids), BATCH):
                chunk = unique_ids[i:i+BATCH]
                batch_rev = fetch_batch_revenue(chunk, codes, year)
                rev_map.update(batch_rev)
                n += 1
                if n % 5 == 0:
                    print(f"  {label} {year}: [{n}/{total_batches}] 완료")
                time.sleep(0.3)

        # 4) 결합 (country 레이블은 CN으로 통일)
        for ym, rank, app_id in targets:
            rows.append({
                "country":     label,          # CN으로 통일
                "ym":          ym,
                "rank":        rank,
                "app_id":      app_id,
                "revenue_usd": rev_map.get((app_id, ym), 0),
            })
        print(f"  [{label}] 완료")

    df = pd.DataFrame(rows)
    df["revenue_m_usd"] = (df["revenue_usd"] / 1_000_000).round(3)
    return df


if __name__ == "__main__":
    print("SLIDE 3 데이터 수집 시작")
    print("중화권(CN) = CN + HK + TW + MO 통합")
    df = fetch_slide3()

    out = Path(__file__).parent.parent / "slide3_rank_revenue.csv"
    df.to_csv(out, index=False)
    print(f"\n저장 완료: {out} ({len(df)}행)")

    df["year"] = df["ym"].str[:4]
    summary = df.groupby(["country", "rank", "year"])["revenue_m_usd"].mean().round(3).reset_index()
    print("\n국가×순위별 연평균 월매출 (백만 USD):")
    print(summary.to_string(index=False))
