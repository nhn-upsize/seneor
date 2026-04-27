"""
iOS + AOS 순위별 월평균 매출 재수집
- comparison_attributes 캐시 활용 (국가별 TOP100 + revenue_absolute)
- 순위 1,10,20,50,100위
"""
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import pandas as pd

CACHE_DIR = Path("C:/Users/NHN/Documents/sensortower_api/.cache")
OUT_DIR = Path("C:/Users/NHN/Documents/sensortower_api")

CHINESE = {"CN","HK","TW","MO"}
NA_CODES = {"US","CA"}
_NM = {"SOUTH KOREA":"한국","KOREA":"한국","JAPAN":"일본","CHINA":"중화권","HONG KONG":"중화권","TAIWAN":"중화권","MACAU":"중화권","UNITED STATES":"북미","CANADA":"북미"}
def classify(raw):
    if not raw: return "기타"
    u = str(raw).strip().upper()
    for k,v in _NM.items():
        if k in u: return v
    if u in CHINESE: return "중화권"
    if u in NA_CODES: return "북미"
    if u in {"JP","JPN"}: return "일본"
    if u in {"KR","KOR"}: return "한국"
    return "기타"

# comparison_attributes 캐시에서 전체 추출
rows = []
for f in sorted(CACHE_DIR.iterdir()):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(d, list) or len(d) < 50: continue
        if not isinstance(d[0], dict) or "custom_tags" not in d[0]: continue
        if "revenue_absolute" not in d[0]: continue

        aid0 = str(d[0].get("app_id", ""))
        plat = "ios" if aid0.isdigit() else "android"

        for rank_idx, app in enumerate(d, 1):
            ct = app.get("custom_tags", {})
            pc = str(ct.get("Publisher Country", "") or "")
            rev = app.get("revenue_absolute", 0) or 0
            units = app.get("units_absolute", 0) or 0

            rows.append({
                "country": app.get("country", ""),
                "platform": plat,
                "ym": (app.get("date", "")[:7]),
                "rank": rank_idx,
                "app_id": str(app.get("app_id", "")),
                "publisher_country": pc,
                "publisher_group": classify(pc),
                "revenue_usd": rev / 100,
                "downloads": units,
                "period": "post2025" if (app.get("date","")[:7]) >= "2025-01" else "pre2025",
            })
    except:
        pass

df = pd.DataFrame(rows)
print(f"총 추출: {len(df)}행")
print(f"플랫폼: {df['platform'].value_counts().to_dict()}")

# 순위별 매출 CSV 저장
ranks = [1, 10, 20, 50, 100]
df_ranks = df[df["rank"].isin(ranks)]
df_ranks["revenue_m_usd"] = (df_ranks["revenue_usd"] / 1_000_000).round(3)

# iOS
ios_rev = df_ranks[df_ranks["platform"] == "ios"].copy()
ios_rev.to_csv(OUT_DIR / "slide3_v2.csv", index=False)
print(f"\niOS 매출: {len(ios_rev)}행")

# AOS
aod_rev = df_ranks[df_ranks["platform"] == "android"].copy()
aod_rev.to_csv(OUT_DIR / "slide3_rank_revenue_android.csv", index=False)
print(f"AOS 매출: {len(aod_rev)}행")

# 검증
print("\n=== 검증: 순위별 매출 (1위 > 10위 > ... 순서 확인) ===")
for plat in ["ios", "android"]:
    for c in ["KR", "JP", "US"]:
        sub = df_ranks[(df_ranks["platform"]==plat)&(df_ranks["country"]==c)]
        line = f"  {plat} {c}:"
        for r in ranks:
            s = sub[sub["rank"]==r]
            v = s["revenue_m_usd"].mean() if len(s) else 0
            line += f"  {r}위={v:.1f}M"
        print(line)
