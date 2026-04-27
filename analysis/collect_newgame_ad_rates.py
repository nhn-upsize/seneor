"""
신규 게임 광고집행율 수집:
  slide2_v2.csv 의 (country, year) 조합별로 comparison_attributes API 호출
  → 해당 시점 TOP 앱 중 신규게임 app_id 와 매칭 → 광고집행율 추출
  → newgame_ad_rates.csv 저장
"""
import sys, os, time, re
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from pathlib import Path
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN    = os.getenv("SENSOR_TOWER_API_TOKEN")
BASE_URL = "https://api.sensortower.com"
BASE     = Path("C:/Users/NHN/Documents/sensortower_api")
CATEGORY = 6014

session = requests.Session()
session.headers.update({"Accept": "application/json"})


def parse_pct(val):
    if not val:
        return None
    m = re.search(r"[\d.]+", str(val))
    return float(m.group()) if m else None


def fetch_attrs(country: str, date_str: str) -> dict:
    """국가+날짜 기준 comparison_attributes 호출 → {app_id: {disp_ww, srch_ww}} 반환"""
    params = {
        "auth_token":          TOKEN,
        "date":                date_str,
        "comparison_attribute":"absolute",
        "measure":             "revenue",
        "time_range":          "month",
        "device_type":         "total",
        "category":            CATEGORY,
        "country":             country,
    }
    try:
        r = session.get(
            f"{BASE_URL}/v1/ios/sales_report_estimates_comparison_attributes",
            params=params, timeout=20
        )
    except Exception as e:
        print(f"    요청 오류: {e}")
        return {}

    if r.status_code != 200:
        print(f"    [{country} {date_str}] HTTP {r.status_code}")
        return {}

    data = r.json()
    items = data if isinstance(data, list) else []
    result = {}
    for item in items:
        aid = item.get("app_id")
        ct  = item.get("custom_tags", {})
        result[aid] = {
            "paid_display_pct_ww": parse_pct(ct.get("Paid Display Downloads % (Last Q, WW)")),
            "paid_search_pct_ww":  parse_pct(ct.get("Paid Search Downloads % (Last Q, WW)")),
            "paid_display_pct_us": parse_pct(ct.get("Paid Display Downloads % (Last Q, US)")),
            "paid_search_pct_us":  parse_pct(ct.get("Paid Search Downloads % (Last Q, US)")),
        }
    return result


def main():
    # 신규 게임 목록 (publisher_group 포함)
    s2 = pd.read_csv(BASE / "slide2_v2.csv")
    # slide1_classification_all로 first_chart_month 보완
    clf = pd.read_csv(BASE / "slide1_classification_all.csv")

    # 기준: slide2_v2.csv의 각 행(country × app_id × year)별로 수집 날짜 설정
    # year별로 대표 날짜 매핑 (해당 연도 중반)
    year_to_dates = {
        2022: ["2022-07-01", "2022-04-01", "2022-10-01", "2022-01-01"],
        2023: ["2023-07-01", "2023-04-01", "2023-10-01", "2023-01-01"],
        2024: ["2024-07-01", "2024-04-01", "2024-10-01", "2024-01-01"],
        2025: ["2025-07-01", "2025-04-01", "2026-01-01", "2025-10-01"],
    }

    # 수집할 (country, year) 조합
    combos = s2[["country","year"]].drop_duplicates().values.tolist()
    print(f"수집 대상: {len(combos)}개 (country × year) 조합\n")

    # API 호출 → 캐시
    cache = {}   # (country, year) → {app_id: attrs}
    for country, year in combos:
        key = (country, year)
        dates = year_to_dates.get(int(year), [f"{year}-07-01"])
        found = {}
        for d in dates:
            print(f"  [{country} {year}] 날짜 {d} 호출...")
            found = fetch_attrs(country, d)
            if found:
                print(f"    → {len(found)}개 앱 수신")
                break
            time.sleep(0.4)
        if not found:
            print(f"    → 데이터 없음")
        cache[key] = found
        time.sleep(0.5)

    # 매칭: slide2_v2의 각 행에 광고집행율 붙이기
    rows = []
    for _, row in s2.iterrows():
        country = row["country"]
        year    = int(row["year"])
        app_id  = row["app_id"]
        period  = row["period"]
        pub_grp = row.get("publisher_group", "")

        attrs = cache.get((country, year), {}).get(app_id, {})
        disp_ww = attrs.get("paid_display_pct_ww")
        srch_ww = attrs.get("paid_search_pct_ww")
        disp_us = attrs.get("paid_display_pct_us")
        srch_us = attrs.get("paid_search_pct_us")

        rows.append({
            "country":             country,
            "year":                year,
            "period":              period,
            "app_id":              app_id,
            "publisher_group":     pub_grp,
            "paid_display_pct_ww": disp_ww,
            "paid_search_pct_ww":  srch_ww,
            "paid_display_pct_us": disp_us,
            "paid_search_pct_us":  srch_us,
        })

    df = pd.DataFrame(rows)

    # 광고 데이터 있는 것만 확인
    has_data = df["paid_display_pct_ww"].notna()
    print(f"\n매칭 결과: {has_data.sum()}/{len(df)} 행에 광고 데이터 있음")

    # 퍼블리셔별 × 기간별 집계
    df["total_ww"] = df["paid_display_pct_ww"].fillna(0) + df["paid_search_pct_ww"].fillna(0)
    summary_pub = (
        df[has_data]
        .groupby(["publisher_group","period"])
        .agg(n=("app_id","count"),
             display_ww=("paid_display_pct_ww","mean"),
             search_ww=("paid_search_pct_ww","mean"),
             total_ww=("total_ww","mean"))
        .round(1)
    )
    print("\n=== 퍼블리셔별 × 기간별 광고집행율 ===")
    print(summary_pub.to_string())

    # 국가별 × 기간별 집계
    summary_ctr = (
        df[has_data]
        .groupby(["country","period"])
        .agg(n=("app_id","count"),
             display_ww=("paid_display_pct_ww","mean"),
             search_ww=("paid_search_pct_ww","mean"),
             total_ww=("total_ww","mean"))
        .round(1)
    )
    print("\n=== 국가별 × 기간별 광고집행율 ===")
    print(summary_ctr.to_string())

    # 저장
    out = BASE / "newgame_ad_rates.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n[저장] {out.name}  ({len(df)}행)")


if __name__ == "__main__":
    main()
