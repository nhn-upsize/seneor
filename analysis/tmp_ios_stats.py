import sys
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
from pathlib import Path
BASE = Path("C:/Users/NHN/Documents/sensortower_api")

df = pd.read_csv(BASE / "slide1_v2.csv")
print("iOS total rows:", len(df))
grp = df.groupby(["country","period"])["survived_3m"].agg(["sum","count"])
grp["rate_pct"] = (grp["sum"]/grp["count"]*100).round(1)
print()
print("iOS 국가별 x period:")
print(grp.to_string())
grp2 = df.groupby(["publisher_group","period"])["survived_3m"].agg(["sum","count"])
grp2["rate_pct"] = (grp2["sum"]/grp2["count"]*100).round(1)
print()
print("iOS 퍼블리셔별 x period:")
print(grp2.to_string())
