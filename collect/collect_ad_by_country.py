"""
국가별(시장 기준) 광고집행율 수집
comparison_attributes 엔드포인트를 country별로 호출해서
KR / JP / US / CN 시장 TOP 100 기준 광고집행율 수집
"""
import sys, json, time, os, re
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from pathlib import Path
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN     = os.getenv("SENSOR_TOWER_API_TOKEN")
BASE_URL  = "https://api.sensortower.com"
OUT_DIR   = Path("C:/Users/NHN/Documents/sensortower_api")
CACHE_DIR = OUT_DIR / ".cache"
CATEGORY  = 6014

session = requests.Session()
session.headers.update({"Accept": "application/json"})


def parse_pct(val) -> float | None:
    if not val:
        return None
    m = re.search(r"[\d.]+", str(val))
    return float(m.group()) if m else None


def fetch_comparison_attrs(country: str, date_str: str) -> list:
    """comparison_attributes를 특정 국가 기준으로 호출."""
    params = {
        "auth_token":          TOKEN,
        "date":                date_str,
        "comparison_attribute":"absolute",
        "measure":             "revenue",
        "time_range":          "month",
        "device_type":         "total",
        "category":            CATEGORY,
        "country":             country,   # 국가별 시장 기준
    }
    r = session.get(f"{BASE_URL}/v1/ios/sales_report_estimates_comparison_attributes",
                    params=params, timeout=20)
    if r.status_code != 200:
        print(f"    [{country} {date_str}] HTTP {r.status_code}")
        return []
    data = r.json()
    return data if isinstance(data, list) else []


def collect_country_ad_rates():
    # 수집 대상: 국가 × 최근 분기 (2025-10 ~ 2026-01, 최근 데이터)
    # 가장 최근 월부터 역순으로 시도해서 데이터 있는 것 사용
    target_countries = ["KR", "JP", "US", "CN"]
    test_dates = ["2026-01-01", "2025-10-01", "2025-07-01", "2025-04-01",
                  "2025-01-01", "2024-10-01"]

    # 먼저 API가 country 파라미터를 지원하는지 테스트
    print("=== API 테스트 (KR, 최근 월) ===")
    for d in test_dates:
        items = fetch_comparison_attrs("KR", d)
        if items:
            sample = items[0].get("custom_tags", {})
            paid_keys = [k for k in sample.keys() if "Paid" in k]
            print(f"  KR {d}: {len(items)}개 앱, paid 필드: {paid_keys[:4]}")
            print(f"  샘플 값: { {k: sample[k] for k in paid_keys[:4]} }")
            break
        time.sleep(0.5)
    else:
        print("  → 데이터 없음. country 파라미터 미지원일 수 있음.")
        return None

    # 국가별 전체 수집 (여러 날짜 중 데이터 있는 최근 것)
    rows = []
    for country in target_countries:
        print(f"\n[{country}] 수집 중...")
        country_items = []
        for d in test_dates:
            items = fetch_comparison_attrs(country, d)
            if items:
                print(f"  {d}: {len(items)}개 앱")
                country_items = items
                break
            time.sleep(0.3)

        if not country_items:
            print(f"  → {country}: 데이터 없음")
            continue

        # 앱별 paid install 추출
        disp_ww, srch_ww, disp_us, srch_us = [], [], [], []
        for item in country_items:
            ct = item.get("custom_tags", {})
            dw = parse_pct(ct.get("Paid Display Downloads % (Last Q, WW)"))
            sw = parse_pct(ct.get("Paid Search Downloads % (Last Q, WW)"))
            du = parse_pct(ct.get("Paid Display Downloads % (Last Q, US)"))
            su = parse_pct(ct.get("Paid Search Downloads % (Last Q, US)"))
            if dw is not None: disp_ww.append(dw)
            if sw is not None: srch_ww.append(sw)
            if du is not None: disp_us.append(du)
            if su is not None: srch_us.append(su)

        rows.append({
            "country":             country,
            "n_apps":              len(country_items),
            "paid_display_pct_ww": round(sum(disp_ww)/len(disp_ww), 1) if disp_ww else None,
            "paid_search_pct_ww":  round(sum(srch_ww)/len(srch_ww), 1) if srch_ww else None,
            "paid_display_pct_us": round(sum(disp_us)/len(disp_us), 1) if disp_us else None,
            "paid_search_pct_us":  round(sum(srch_us)/len(srch_us), 1) if srch_us else None,
        })
        time.sleep(0.5)

    if not rows:
        print("\n수집 실패: API가 country 파라미터 미지원")
        return None

    df = pd.DataFrame(rows)
    out = OUT_DIR / "ad_rate_by_country.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n=== 결과 ===")
    print(df.to_string(index=False))
    print(f"\n[저장] {out.name}")
    return df


if __name__ == "__main__":
    collect_country_ad_rates()
