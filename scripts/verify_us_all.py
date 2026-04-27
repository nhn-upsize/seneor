# -*- coding: utf-8 -*-
"""US 시장 전체 수치 검증"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

def pf(yr):
    if yr == '26.1Q':
        return "date >= '2026-01-01' AND date < '2026-04-01'"
    return f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"

def ba(v):
    vv = {k: float(x or 0) for k,x in v.items()}
    b = (vv['2022']+vv['2023']+vv['2024'])/3
    a = (vv['2025']*12 + vv['26.1Q']*3)/15
    return b, a, a-b, (a-b)/b*100 if b else 0

print("=== US 전체 매출 (억) ===")
rev = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                    FROM dw_app_monthly
                    WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND {pf(yr)}""")
    rev[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {rev[yr]:,.0f}")
b,a,d,p = ba(rev)
print(f"  전후: {b:,.0f} -> {a:,.0f} ({d:+,.0f}, {p:+.1f}%)")

print("\n=== US MAU (만명) ===")
mau = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""
    WITH mo AS (SELECT date, SUM(mau) s FROM dw_app_monthly
                WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND {pf(yr)}
                GROUP BY date)
    SELECT ROUND(AVG(s)/10000.0, 0) FROM mo""")
    mau[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {mau[yr]:,.0f}")
b,a,d,p = ba(mau)
print(f"  전후: {b:,.0f} -> {a:,.0f} ({d:+,.0f}, {p:+.1f}%)")

print("\n=== US ARPMAU (원) ===")
arp = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""
    WITH mo AS (SELECT date, SUM(revenue_krw_100) r, SUM(mau) u FROM dw_app_monthly
                WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND {pf(yr)}
                GROUP BY date)
    SELECT ROUND(AVG(r)/NULLIF(AVG(u),0), 0) FROM mo""")
    arp[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {arp[yr]:,.0f}")
b,a,d,p = ba(arp)
print(f"  전후: {b:,.0f} -> {a:,.0f} ({d:+,.0f}, {p:+.1f}%)")

print("\n=== US DL (만건) ===")
dl = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""SELECT ROUND(SUM(units)/10000.0/{m}, 0)
                    FROM dw_app_monthly
                    WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND {pf(yr)}""")
    dl[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {dl[yr]:,.0f}")
b,a,d,p = ba(dl)
print(f"  전후: {b:,.0f} -> {a:,.0f} ({d:+,.0f}, {p:+.1f}%)")

print("\n=== US 퍼블국적별 (억) ===")
CN = "('China','Hong Kong','Taiwan','Macao','Macau','Singapore')"
groups = [
    ('북미',  f"publisher_country IN ('United States','Canada') AND publisher_name NOT ILIKE '%NEXON%'"),
    ('중화권', f"(publisher_country IN {CN} OR publisher_name ILIKE '%FUNFLY%') AND publisher_name NOT ILIKE '%NEXON%'"),
    ('기타',  f"publisher_country IS NOT NULL AND publisher_country NOT IN ('Japan','South Korea','United States','Canada','China','Hong Kong','Taiwan','Macao','Macau') AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'"),
    ('JP',   f"publisher_country='Japan' AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'"),
    ('KR',   f"publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%'"),
]
for g, c in groups:
    v = {}
    for yr, m in YR_MONTHS.items():
        cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND {pf(yr)} AND {c}""")
        v[yr] = cur.fetchone()[0] or 0
    b,a,d,p = ba(v)
    print(f"  {g:<5}: " + ' '.join(f'{v[y]:>6,.0f}' for y in YR_MONTHS) + f"  {b:,.0f}->{a:,.0f} ({d:+.0f}, {p:+.1f}%)")

print("\n=== US 장르별 (억) ===")
genres = ['Strategy','Puzzle','Action','Casino','Simulation','Role Playing','Adventure','Sports','Arcade','Card','Word','Board','Trivia','Music','Racing']
for g in genres:
    v = {}
    for yr, m in YR_MONTHS.items():
        cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND {pf(yr)} AND genre='{g}'""")
        v[yr] = cur.fetchone()[0] or 0
    b,a,d,p = ba(v)
    print(f"  {g:<13}: " + ' '.join(f'{v[y]:>5,.0f}' for y in YR_MONTHS) + f"  {b:,.0f}->{a:,.0f} ({d:+.0f}, {p:+.1f}%)")

conn.close()
