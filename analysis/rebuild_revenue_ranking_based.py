"""
순위별 매출 재수집 — Ranking API(공식 순위) + comparison_attributes(매출) 결합
- 순위: Ranking API (App Store/Google Play 공식)
- 매출: comparison_attributes 캐시에서 app_id 매칭
"""
import sys, json, hashlib
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from datetime import date
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


# === 1단계: comparison_attributes 캐시에서 전체 매출 맵 구축 ===
print("1) comparison_attributes 캐시에서 매출 맵 구축...")
# key: (country, ym, app_id) → revenue_usd, downloads, publisher_country
rev_map = {}

for f in sorted(CACHE_DIR.iterdir()):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(d, list) or len(d) < 50: continue
        if not isinstance(d[0], dict) or "custom_tags" not in d[0]: continue
        if "revenue_absolute" not in d[0]: continue

        for app in d:
            country = app.get("country", "")
            ym = (app.get("date", "")[:7])
            aid = str(app.get("app_id", ""))
            rev = app.get("revenue_absolute", 0) or 0
            units = app.get("units_absolute", 0) or 0
            ct = app.get("custom_tags", {})
            pc = str(ct.get("Publisher Country", "") or "")

            key = (country, ym, aid)
            rev_map[key] = {"revenue_usd": rev / 100, "downloads": units, "publisher_country": pc}
    except:
        pass

print(f"   매출 맵: {len(rev_map)}개 항목")


# === 2단계: Ranking API에서 순위별 app_id + 매출 매칭 ===
print("\n2) Ranking API 순위 + 매출 매칭...")
RANKS = [1, 10, 20, 50, 100]
rows = []

# iOS
for label in ["KR", "JP", "US"]:
    codes = expand_country(label) if label == "CN" else [label]
    for dt in MONTHS:
        ym = dt.strftime("%Y-%m")
        date_str = dt.strftime("%Y-%m-%d")

        # iOS ranking
        ranking = load_ranking_ios(label, date_str)
        for rank in RANKS:
            if rank - 1 < len(ranking):
                aid = ranking[rank - 1]
                key = (label, ym, aid)
                rev_info = rev_map.get(key, {})
                rev_usd = rev_info.get("revenue_usd", 0)
                dl = rev_info.get("downloads", 0)
                pc = rev_info.get("publisher_country", "")

                rows.append({
                    "country": label, "platform": "ios", "ym": ym,
                    "rank": rank, "app_id": aid,
                    "publisher_country": pc, "publisher_group": classify(pc),
                    "revenue_usd": rev_usd,
                    "revenue_m_usd": round(rev_usd / 1_000_000, 3),
                    "downloads": dl,
                    "period": "post2025" if ym >= "2025-01" else "pre2025",
                })

# AOS
for country in ["KR", "JP", "US"]:
    for dt in MONTHS:
        ym = dt.strftime("%Y-%m")
        date_str = dt.strftime("%Y-%m-%d")

        ranking = load_ranking_android(country, date_str)
        for rank in RANKS:
            if rank - 1 < len(ranking):
                aid = ranking[rank - 1]
                key = (country, ym, aid)
                rev_info = rev_map.get(key, {})
                rev_usd = rev_info.get("revenue_usd", 0)
                dl = rev_info.get("downloads", 0)
                pc = rev_info.get("publisher_country", "")

                rows.append({
                    "country": country, "platform": "android", "ym": ym,
                    "rank": rank, "app_id": aid,
                    "publisher_country": pc, "publisher_group": classify(pc),
                    "revenue_usd": rev_usd,
                    "revenue_m_usd": round(rev_usd / 1_000_000, 3),
                    "downloads": dl,
                    "period": "post2025" if ym >= "2025-01" else "pre2025",
                })

df = pd.DataFrame(rows)

# 매출 매칭률 확인
matched = (df["revenue_usd"] > 0).sum()
print(f"   총 행: {len(df)}, 매출 매칭: {matched} ({matched/len(df)*100:.0f}%)")

# 저장
ios_df = df[df["platform"] == "ios"]
aod_df = df[df["platform"] == "android"]
ios_df.to_csv(OUT_DIR / "data" / "slide3_v2.csv", index=False)
aod_df.to_csv(OUT_DIR / "data" / "slide3_rank_revenue_android.csv", index=False)
print(f"\n   iOS: {len(ios_df)}행 → data/slide3_v2.csv")
print(f"   AOS: {len(aod_df)}행 → data/slide3_rank_revenue_android.csv")

# 검증
print("\n=== 검증: 순위별 매출 (1위 > 10위 > ... 순서) ===")
for plat in ["ios", "android"]:
    for c in ["KR", "JP", "US"]:
        sub = df[(df["platform"] == plat) & (df["country"] == c)]
        line = f"  {plat} {c}:"
        for r in RANKS:
            s = sub[sub["rank"] == r]
            v = s["revenue_m_usd"].mean() if len(s) else 0
            line += f"  {r}위={v:.1f}M"
        print(line)

# KR iOS 2025-01 1위 확인
print("\n=== KR iOS 2025-01 1위 ===")
s = df[(df["platform"]=="ios")&(df["country"]=="KR")&(df["ym"]=="2025-01")&(df["rank"]==1)]
if len(s):
    print(f"  app_id: {s.iloc[0]['app_id']} (리니지M=1474589366?)")
    print(f"  매출: ${s.iloc[0]['revenue_m_usd']:.2f}M")
