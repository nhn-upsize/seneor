import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

ios = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide1_v2.csv")
aod = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide1_v2_android.csv")
ios_ad = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/newgame_ad_rates.csv")
cr = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/chart_retention_newentry.csv")
ios_rev = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide3_v2.csv")
aod_rev = pd.read_csv("C:/Users/NHN/Documents/sensortower_api/slide3_rank_revenue_android.csv")

ios_m = ios.merge(ios_ad[["app_id","total_ww"]], on="app_id", how="left")
ios_m["has_ad"] = ios_m["total_ww"].fillna(0) > 0

PRE=33; POST=13
CTR=["KR","JP","US"]; PUB=["한국","일본","북미","중화권","기타"]
LBL=["M+1","M+2","M+3","M+6","M+12"]
RANKS=[1,10,20,50,100]

md = []
md.append("# 모바일 게임 시장 분석 보고서")
md.append("## 매출 TOP 100 신규진입 게임 기준 (2022~2026.Q1)\n")
md.append("---\n## 분석 기준\n")
md.append("| 항목 | 내용 |")
md.append("|------|------|")
md.append("| 대상 | 매출 TOP 100 (App Store / Google Play) |")
md.append("| 신규진입 정의 | 각 연도 1월 TOP100을 기준선, 2~12월 중 처음 진입한 게임 |")
md.append("| 분석 기간 | pre2025: 2022~2024 각 2~12월 (33개월) / post2025: 2025.2~2026.3 (13개월) |")
md.append("| 3개월 생존 | 첫 진입월 +3개월 시점에 TOP100 존재 여부 |")
md.append("| 차트 잔존율 | 신규진입 게임이 M+N 시점에 TOP100에 남아있는 비율 |")
md.append("| n (게임수) | 월평균 (총 게임수 / 해당 기간 개월수) |")
md.append("| 생존율 | 전체 기간 누적 비율 (총 생존수 / 총 신규진입수) |")
md.append("| 광고집행율 | 월별 비율의 평균, iOS만 (AOS는 Sensor Tower 커버리지 한계) |")
md.append("| 랭킹 기준일 | 매월 1일 |")
md.append("| 소표본 | n < 50인 경우 참고 수준 |")
md.append("| 출처 | Sensor Tower API |\n")

# 1
md.append("---\n## 1. 신규 게임 3개월 생존율 - 국가별\n")
md.append("| 국가 | 플랫폼 | 기간 | 신규진입(총) | 월평균 | 생존수 | 생존율 |")
md.append("|:----:|:------:|:----:|:----------:|:------:|:------:|:------:|")
for p,df in [("iOS",ios),("AOS",aod)]:
    for c in CTR:
        for pk in ["pre2025","post2025"]:
            s=df[(df["country"]==c)&(df["period"]==pk)]; t=len(s); sv=int(s["survived_3m"].sum())
            r=sv/t*100 if t else 0; m=PRE if pk=="pre2025" else POST
            n=" *" if t<50 else ""
            md.append(f"| {c} | {p} | {pk} | {t} | {t/m:.1f} | {sv} | **{r:.1f}%**{n} |")
md.append("\n**해석:** 2025년 이후 대부분 시장에서 생존율 하락. KR이 iOS 31->24%, AOS 39->22%로 가장 큰 낙폭. US AOS만 유일하게 39->41%로 상승.")
md.append("\n**인사이트:** 한국 시장의 경쟁 강도가 가장 높으며, 미국 AOS는 상대적으로 신규 진입 기회가 남아있는 시장.\n")

# 2
md.append("---\n## 2. 광고 집행율 - 국가별 (3개월 생존 vs 미생존)\n")
md.append("> iOS 기준 / 월평균 광고집행율 / AOS는 Sensor Tower 광고 커버리지 한계로 생략\n")
md.append("| 국가 | 기간 | 생존 광고율 | 미생존 광고율 | 생존 n | 미생존 n |")
md.append("|:----:|:----:|:---------:|:----------:|:------:|:--------:|")
for c in CTR:
    for pk in ["pre2025","post2025"]:
        sub=ios_m[(ios_m["country"]==c)&(ios_m["period"]==pk)&(ios_m["total_ww"].notna())]
        sv=sub[sub["survived_3m"]==True]; ch=sub[sub["survived_3m"]==False]
        smo=sv.groupby("first_chart_month")["has_ad"].mean()*100
        cmo=ch.groupby("first_chart_month")["has_ad"].mean()*100
        rs=smo.mean() if len(smo) else 0; rc=cmo.mean() if len(cmo) else 0
        md.append(f"| {c} | {pk} | **{rs:.1f}%** | {rc:.1f}% | {len(sv)} | {len(ch)} |")
md.append("\n**해석:** KR/JP에서 생존 게임의 광고집행율(11~16%)이 미생존(1~6%) 대비 확연히 높음. US는 생존/미생존 격차가 적음.")
md.append("\n**인사이트:** 한국/일본 시장에서는 Paid UA 투자가 초기 생존과 강한 상관관계. 미국은 오가닉 유입 비중이 높아 광고 외 요인이 중요.\n")

# 3
md.append("---\n## 3. 신규 게임 3개월 생존율 - 퍼블리셔별\n")
md.append("| 퍼블리셔 | 플랫폼 | 기간 | 신규진입(총) | 월평균 | 생존수 | 생존율 |")
md.append("|:--------:|:------:|:----:|:----------:|:------:|:------:|:------:|")
for p,df in [("iOS",ios),("AOS",aod)]:
    for pub in PUB:
        for pk in ["pre2025","post2025"]:
            s=df[(df["publisher_group"]==pub)&(df["period"]==pk)]; t=len(s); sv=int(s["survived_3m"].sum())
            r=sv/t*100 if t else 0; m=PRE if pk=="pre2025" else POST
            n=" *" if t<50 else ""
            md.append(f"| {pub} | {p} | {pk} | {t} | {t/m:.1f} | {sv} | **{r:.1f}%**{n} |")
md.append("\n> * 소표본(n<50) 참고 수준\n")
md.append("**해석:** 기타(핀란드/영국/이스라엘 등)가 iOS 42%, AOS 59%로 최고 생존율. 중화권 iOS 36%, 북미 iOS 29%. 한국은 AOS post2025 19%로 최하위.")
md.append("\n**인사이트:** 기타 그룹에 Supercell(핀란드)/King(스웨덴)/Playrix(아일랜드) 등 글로벌 강자 포함. 중화권은 물량 공세, 북미는 안정적 생존. 한국 퍼블리셔 개선 시급.")
md.append("\n> 기타 = Finland, Singapore, Turkey, Israel, UK, Switzerland, Cyprus, Ireland, Sweden 등\n")

# 4
md.append("---\n## 4. 광고 집행율 - 퍼블리셔별 (3개월 생존 vs 미생존)\n")
md.append("> iOS 기준\n")
md.append("| 퍼블리셔 | 기간 | 생존 광고율 | 미생존 광고율 | 생존 n | 미생존 n |")
md.append("|:--------:|:----:|:---------:|:----------:|:------:|:--------:|")
for pub in PUB:
    for pk in ["pre2025","post2025"]:
        sub=ios_m[(ios_m["publisher_group"]==pub)&(ios_m["period"]==pk)&(ios_m["total_ww"].notna())]
        sv=sub[sub["survived_3m"]==True]; ch=sub[sub["survived_3m"]==False]
        smo=sv.groupby("first_chart_month")["has_ad"].mean()*100
        cmo=ch.groupby("first_chart_month")["has_ad"].mean()*100
        rs=smo.mean() if len(smo) else 0; rc=cmo.mean() if len(cmo) else 0
        md.append(f"| {pub} | {pk} | **{rs:.1f}%** | {rc:.1f}% | {len(sv)} | {len(ch)} |")
md.append("\n**해석:** 생존 게임의 광고집행율이 퍼블리셔 유형과 무관하게 미생존 대비 높은 경향.")
md.append("\n**인사이트:** Paid UA는 퍼블리셔 규모/국적과 관계없이 초기 생존의 공통 요소. 다만 광고만으로 생존이 보장되지는 않음.\n")

# 5
md.append("---\n## 5. 차트 잔존율 M+1~M+12 - 국가별\n")
md.append("> 신규진입 게임이 M+N 시점에 매출 TOP100에 남아있는 비율\n")
md.append("| 국가 | 플랫폼 | 기간 | n | 월평균 | M+1 | M+2 | M+3 | M+6 | M+12 |")
md.append("|:----:|:------:|:----:|:--:|:----:|:---:|:---:|:---:|:---:|:----:|")
for pl in ["ios","android"]:
    for c in CTR:
        for pk in ["pre2025","post2025"]:
            s=cr[(cr["platform"]==pl)&(cr["country"]==c)&(cr["period"]==pk)]
            m=PRE if pk=="pre2025" else POST; pn="iOS" if pl=="ios" else "AOS"
            vs=" | ".join([f"**{s[l].mean()*100:.0f}%**" if len(s) else "-" for l in LBL])
            n=" *" if len(s)<50 else ""
            md.append(f"| {c} | {pn} | {pk} | {len(s)} | {len(s)/m:.1f} | {vs} |{n}")
md.append("\n> * 소표본(n<50) 참고 수준\n")
md.append("**해석:** pre2025에서 M+12 잔존율이 JP/US 29~32%로 양호했으나, post2025에서 전 시장 4~12%로 급락. KR이 가장 낮음(4%).")
md.append("\n**인사이트:** 2025년 이후 신규 게임의 1년 후 TOP100 잔존이 극히 어려워짐. 기존 상위 게임의 방어력이 강화되고 있음을 시사.")
md.append("\n> **주의:** post2025의 M+6은 61%, M+12는 21%의 게임만 판정 기간이 충분함 (데이터 끝: 2026.03). 실제 잔존율은 더 높을 수 있음.\n")

# 6
md.append("---\n## 6. 차트 잔존율 M+1~M+12 - 퍼블리셔별\n")
md.append("| 퍼블리셔 | 플랫폼 | 기간 | n | 월평균 | M+1 | M+2 | M+3 | M+6 | M+12 |")
md.append("|:--------:|:------:|:----:|:--:|:----:|:---:|:---:|:---:|:---:|:----:|")
for pl in ["ios","android"]:
    for pub in PUB:
        for pk in ["pre2025","post2025"]:
            s=cr[(cr["platform"]==pl)&(cr["publisher_group"]==pub)&(cr["period"]==pk)]
            m=PRE if pk=="pre2025" else POST; pn="iOS" if pl=="ios" else "AOS"
            vs=" | ".join([f"**{s[l].mean()*100:.0f}%**" if len(s) else "-" for l in LBL])
            n=" *" if len(s)<50 else ""
            md.append(f"| {pub} | {pn} | {pk} | {len(s)} | {len(s)/m:.1f} | {vs} |{n}")
md.append("\n> * 소표본(n<50) 참고 수준\n")
md.append("**해석:** 기타 그룹이 M+12 iOS 29%, AOS 27%로 최고. 일본 iOS 25%, AOS 23%. 한국 iOS 16%, AOS 15%로 최하위.")
md.append("\n**인사이트:** 기타(Supercell/King/Playrix 등 유럽 강자)와 일본의 장기 잔존이 압도적. 한국 퍼블리셔는 M+3 이후 급감 — 라이브서비스 강화 필요.")
md.append("\n> **주의:** post2025의 M+6은 61%, M+12는 21%의 게임만 판정 기간이 충분함. 실제 잔존율은 더 높을 수 있음.\n")

# 7
md.append("---\n## 7. 순위별 월평균 매출 - 국가별\n")
md.append("| 국가 | 플랫폼 | 기간 | 1위 | 10위 | 20위 | 50위 | 100위 |")
md.append("|:----:|:------:|:----:|:---:|:----:|:----:|:----:|:-----:|")
for p,df in [("iOS",ios_rev),("AOS",aod_rev)]:
    df=df.copy(); df["revenue_m_usd"]=pd.to_numeric(df.get("revenue_m_usd",0),errors="coerce")
    if "period" not in df.columns: df["period"]=df["ym"].apply(lambda x:"post2025" if x>="2025-01" else "pre2025")
    for c in CTR:
        for pk in ["pre2025","post2025"]:
            vs=[]
            for r in RANKS:
                s=df[(df["country"]==c)&(df["period"]==pk)&(df["rank"]==r)]
                v=s["revenue_m_usd"].mean() if len(s) else 0; vs.append(f"**${v:.1f}M**")
            md.append(f"| {c} | {p} | {pk} | {' | '.join(vs)} |")
md.append("\n**해석:** AOS 기준 US 1위 월매출 $28~39M으로 KR($17~22M), JP($8~18M) 대비 압도적. 50위 이하에서는 격차가 $1~2M 수준으로 급감.")
md.append("\n**인사이트:** 미국 시장의 상위권 매출 규모가 독보적이며, TOP 10 진입이 수익성의 결정적 분기점.\n")

# 8
md.append("---\n## 8. 순위별 월평균 매출 - 퍼블리셔별\n")
md.append("| 퍼블리셔 | 플랫폼 | 기간 | 1위 | 10위 | 20위 | 50위 | 100위 |")
md.append("|:--------:|:------:|:----:|:---:|:----:|:----:|:----:|:-----:|")
for p,df in [("iOS",ios_rev),("AOS",aod_rev)]:
    df=df.copy(); df["revenue_m_usd"]=pd.to_numeric(df.get("revenue_m_usd",0),errors="coerce")
    if "period" not in df.columns: df["period"]=df["ym"].apply(lambda x:"post2025" if x>="2025-01" else "pre2025")
    if "publisher_group" not in df.columns: continue
    for pub in PUB:
        for pk in ["pre2025","post2025"]:
            vs=[]
            for r in RANKS:
                s=df[(df["publisher_group"]==pub)&(df["period"]==pk)&(df["rank"]==r)]
                v=s["revenue_m_usd"].mean() if len(s) else 0; vs.append(f"**${v:.1f}M**")
            md.append(f"| {pub} | {p} | {pk} | {' | '.join(vs)} |")
md.append("\n**해석:** 북미 퍼블리셔가 iOS 1위 매출에서 압도적. 중화권은 iOS 상위권 강세, AOS에서는 한국/일본과 유사.")
md.append("\n**인사이트:** 북미 퍼블리셔(미국/캐나다)가 매출 규모 1위. 기타 그룹에도 Supercell 등 고매출 퍼블리셔 포함.\n")
md.append("\n---\n*Generated: 2026-04-07 / Sensor Tower API / 매출 TOP 100 기준*\n")

with open("C:/Users/NHN/Documents/sensortower_api/MobileGame_Analysis_Report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"Done: MobileGame_Analysis_Report.md ({len(md)} lines)")
