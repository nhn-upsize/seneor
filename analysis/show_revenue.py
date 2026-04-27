import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

ios = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide3_v2.csv")
aod = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide3_rank_revenue_android.csv")
ranks = [1,10,20,50,100]

for plat, df in [("iOS", ios), ("AOS", aod)]:
    df = df.copy()
    df["revenue_m_usd"] = pd.to_numeric(df.get("revenue_m_usd",0), errors="coerce")
    if "period" not in df.columns:
        df["period"] = df["ym"].apply(lambda x: "post2025" if x >= "2025-01" else "pre2025")

    print(f"=== {plat} 국가별 ===")
    for c in ["KR","JP","US"]:
        for pk in ["pre2025","post2025"]:
            vals = []
            for r in ranks:
                s = df[(df["country"]==c)&(df["period"]==pk)&(df["rank"]==r)]
                v = s["revenue_m_usd"].mean() if len(s) else 0
                vals.append(f"{r}위={v:.2f}M")
            print(f"  {c} {pk}: " + "  ".join(vals))

    if "publisher_group" not in df.columns:
        print(f"  (publisher_group 없음)\n")
        continue
    print(f"\n=== {plat} 퍼블리셔별 ===")
    for pub in ["한국","일본","서구권","중화권"]:
        for pk in ["pre2025","post2025"]:
            vals = []
            for r in ranks:
                s = df[(df["publisher_group"]==pub)&(df["period"]==pk)&(df["rank"]==r)]
                v = s["revenue_m_usd"].mean() if len(s) else 0
                vals.append(f"{r}위={v:.2f}M")
            print(f"  {pub} {pk}: " + "  ".join(vals))
    print()
