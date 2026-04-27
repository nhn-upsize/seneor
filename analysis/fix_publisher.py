import sys, json, time, os, requests
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import pandas as pd

TOKEN = "ST0_g63UDQaD_YGooSG75BhhRdA"
BASE = "https://api.sensortower.com"
session = requests.Session()
session.headers.update({"Accept": "application/json"})

CHINESE = {"CN","HK","TW","MO"}
WESTERN = {"US","CA","GB","DE","FR","FI","SE","NO","DK","NL","BE","CH","AT","AU","NZ","IE","IT","ES","PT","RU","PL","CZ","HU","RO","UA","GR","TR","IL","ZA","BR","MX","AR","CO","CL","PE"}
_NM = {"SOUTH KOREA":"한국","KOREA":"한국","JAPAN":"일본","CHINA":"중화권","HONG KONG":"중화권","TAIWAN":"중화권","MACAU":"중화권","UNITED STATES":"서구권","UNITED KINGDOM":"서구권","CANADA":"서구권","AUSTRALIA":"서구권","GERMANY":"서구권","FRANCE":"서구권"}
def classify(raw):
    if not raw: return "기타"
    u = str(raw).strip().upper()
    for k,v in _NM.items():
        if k in u: return v
    if u in CHINESE: return "중화권"
    if u in WESTERN: return "서구권"
    if u in {"JP","JPN"}: return "일본"
    if u in {"KR","KOR"}: return "한국"
    return "기타"

def fetch(platform, ids):
    r = {}
    for i in range(0, len(ids), 100):
        c = ids[i:i+100]
        resp = session.get(f"{BASE}/v1/{platform}/apps", params={"auth_token": TOKEN, "app_ids": ",".join(c)}, timeout=30)
        if resp.status_code == 429:
            time.sleep(int(resp.headers.get("Retry-After", 10)))
            resp = session.get(f"{BASE}/v1/{platform}/apps", params={"auth_token": TOKEN, "app_ids": ",".join(c)}, timeout=30)
        if resp.status_code == 200:
            for a in (resp.json() if isinstance(resp.json(), list) else resp.json().get("apps", [])):
                aid = str(a.get("app_id") or a.get("package_name",""))
                r[aid] = a.get("publisher_country","") or a.get("canonical_country","") or ""
        time.sleep(0.2)
        if (i//100+1) % 5 == 0: print(f"  {platform}: {i+100}/{len(ids)}")
    return r

BD = Path("C:/Users/NHN/Documents/sensortower_api")
ios = pd.read_csv(BD/"slide1_v2.csv"); aod = pd.read_csv(BD/"slide1_v2_android.csv")

print("iOS...")
d1 = fetch("ios", list(ios["app_id"].astype(str).unique()))
print(f"  {len(d1)}개")
print("AOS...")
d2 = fetch("android", list(aod["app_id"].astype(str).unique()))
print(f"  {len(d2)}개")

for fn, df, det in [("slide1_v2.csv",ios,d1),("slide1_v2_android.csv",aod,d2)]:
    for i,row in df.iterrows():
        a=str(row["app_id"])
        if a in det and det[a]:
            df.at[i,"publisher_country"]=det[a]; df.at[i,"publisher_group"]=classify(det[a])
    df.to_csv(BD/fn, index=False)
    g=df["publisher_group"].value_counts()
    print(f"{fn}: {g.to_dict()}")

ad = {**d1, **d2}
cr = pd.read_csv(BD/"chart_retention_newentry.csv")
for i,row in cr.iterrows():
    a=str(row["app_id"])
    if a in ad and ad[a]: cr.at[i,"publisher_group"]=classify(ad[a])
cr.to_csv(BD/"chart_retention_newentry.csv", index=False)
print(f"chart_ret: 기타={len(cr[cr['publisher_group']=='기타'])}")
print("Done!")
