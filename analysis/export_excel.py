import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

BD = "C:/Users/NHN/Documents/sensortower_api"
ios = pd.read_csv(f"{BD}/slide1_v2.csv")
aod = pd.read_csv(f"{BD}/slide1_v2_android.csv")
ios_ad = pd.read_csv(f"{BD}/newgame_ad_rates.csv")
cr = pd.read_csv(f"{BD}/chart_retention_newentry.csv")
ios_rev = pd.read_csv(f"{BD}/slide3_v2.csv")
aod_rev = pd.read_csv(f"{BD}/slide3_rank_revenue_android.csv")

ios_m = ios.merge(ios_ad[["app_id","total_ww"]], on="app_id", how="left")
ios_m["has_ad"] = ios_m["total_ww"].fillna(0) > 0

PRE=33; POST=13
C=["KR","JP","US"]; P=["한국","일본","북미","중화권","기타"]
rc=["M+1","M+2","M+3","M+6","M+12"]
ranks=[1,10,20,50,100]

with pd.ExcelWriter(f"{BD}/Slides_14_21_RawData_v3.xlsx", engine="openpyxl") as w:
    # S14
    rows=[]
    for pl,df in [("iOS",ios),("AOS",aod)]:
        for c in C:
            for pk in ["pre2025","post2025"]:
                s=df[(df["country"]==c)&(df["period"]==pk)]; t=len(s); sv=int(s["survived_3m"].sum())
                m=PRE if pk=="pre2025" else POST
                rows.append({"플랫폼":pl,"국가":c,"기간":pk,"총게임수":t,"월평균":round(t/m,1),"생존수":sv,"생존율":round(sv/t*100,1) if t else 0})
    pd.DataFrame(rows).to_excel(w, sheet_name="S14_생존율_국가별", index=False)

    # S15
    rows=[]
    for c in C:
        for pk in ["pre2025","post2025"]:
            sub=ios_m[(ios_m["country"]==c)&(ios_m["period"]==pk)&(ios_m["total_ww"].notna())]
            sv=sub[sub["survived_3m"]==True]; ch=sub[sub["survived_3m"]==False]
            smo=sv.groupby("first_chart_month")["has_ad"].mean()*100
            cmo=ch.groupby("first_chart_month")["has_ad"].mean()*100
            rows.append({"플랫폼":"iOS","국가":c,"기간":pk,"생존_광고율":round(smo.mean(),1) if len(smo) else 0,"미생존_광고율":round(cmo.mean(),1) if len(cmo) else 0,"생존n":len(sv),"미생존n":len(ch)})
    pd.DataFrame(rows).to_excel(w, sheet_name="S15_광고율_국가별", index=False)

    # S16
    rows=[]
    for pl,df in [("iOS",ios),("AOS",aod)]:
        for pub in P:
            for pk in ["pre2025","post2025"]:
                s=df[(df["publisher_group"]==pub)&(df["period"]==pk)]; t=len(s); sv=int(s["survived_3m"].sum())
                m=PRE if pk=="pre2025" else POST
                rows.append({"플랫폼":pl,"퍼블리셔":pub,"기간":pk,"총게임수":t,"월평균":round(t/m,1),"생존수":sv,"생존율":round(sv/t*100,1) if t else 0})
    pd.DataFrame(rows).to_excel(w, sheet_name="S16_생존율_퍼블리셔별", index=False)

    # S17
    rows=[]
    for pub in P:
        for pk in ["pre2025","post2025"]:
            sub=ios_m[(ios_m["publisher_group"]==pub)&(ios_m["period"]==pk)&(ios_m["total_ww"].notna())]
            sv=sub[sub["survived_3m"]==True]; ch=sub[sub["survived_3m"]==False]
            smo=sv.groupby("first_chart_month")["has_ad"].mean()*100
            cmo=ch.groupby("first_chart_month")["has_ad"].mean()*100
            rows.append({"플랫폼":"iOS","퍼블리셔":pub,"기간":pk,"생존_광고율":round(smo.mean(),1) if len(smo) else 0,"미생존_광고율":round(cmo.mean(),1) if len(cmo) else 0,"생존n":len(sv),"미생존n":len(ch)})
    pd.DataFrame(rows).to_excel(w, sheet_name="S17_광고율_퍼블리셔별", index=False)

    # S18
    rows=[]
    for pl in ["ios","android"]:
        for c in C:
            for pk in ["pre2025","post2025"]:
                s=cr[(cr["platform"]==pl)&(cr["country"]==c)&(cr["period"]==pk)]
                m=PRE if pk=="pre2025" else POST
                row={"플랫폼":"iOS" if pl=="ios" else "AOS","국가":c,"기간":pk,"총n":len(s),"월평균":round(len(s)/m,1)}
                for lbl in rc: row[lbl]=f"{s[lbl].mean()*100:.1f}%" if len(s) else "-"
                rows.append(row)
    pd.DataFrame(rows).to_excel(w, sheet_name="S18_잔존율_국가별", index=False)

    # S19
    rows=[]
    for pl in ["ios","android"]:
        for pub in P:
            for pk in ["pre2025","post2025"]:
                s=cr[(cr["platform"]==pl)&(cr["publisher_group"]==pub)&(cr["period"]==pk)]
                m=PRE if pk=="pre2025" else POST
                row={"플랫폼":"iOS" if pl=="ios" else "AOS","퍼블리셔":pub,"기간":pk,"총n":len(s),"월평균":round(len(s)/m,1)}
                for lbl in rc: row[lbl]=f"{s[lbl].mean()*100:.1f}%" if len(s) else "-"
                rows.append(row)
    pd.DataFrame(rows).to_excel(w, sheet_name="S19_잔존율_퍼블리셔별", index=False)

    # S20
    rows=[]
    for pl,df in [("iOS",ios_rev),("AOS",aod_rev)]:
        df=df.copy(); df["revenue_m_usd"]=pd.to_numeric(df.get("revenue_m_usd",0),errors="coerce")
        for c in C:
            for pk in ["pre2025","post2025"]:
                row={"플랫폼":pl,"국가":c,"기간":pk}
                for r in ranks:
                    s=df[(df["country"]==c)&(df["period"]==pk)&(df["rank"]==r)]
                    row[f"{r}위"]=round(s["revenue_m_usd"].mean(),2) if len(s) else 0
                rows.append(row)
    pd.DataFrame(rows).to_excel(w, sheet_name="S20_매출_국가별", index=False)

    # S21
    rows=[]
    for pl,df in [("iOS",ios_rev),("AOS",aod_rev)]:
        df=df.copy(); df["revenue_m_usd"]=pd.to_numeric(df.get("revenue_m_usd",0),errors="coerce")
        if "publisher_group" not in df.columns: continue
        for pub in P:
            for pk in ["pre2025","post2025"]:
                row={"플랫폼":pl,"퍼블리셔":pub,"기간":pk}
                for r in ranks:
                    s=df[(df["publisher_group"]==pub)&(df["period"]==pk)&(df["rank"]==r)]
                    row[f"{r}위"]=round(s["revenue_m_usd"].mean(),2) if len(s) else 0
                rows.append(row)
    pd.DataFrame(rows).to_excel(w, sheet_name="S21_매출_퍼블리셔별", index=False)

print("Done: Slides_14_21_RawData_v3.xlsx")
