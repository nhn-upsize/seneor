# -*- coding: utf-8 -*-
"""JP 시장 전체 수치 검증"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

def period_filter(yr):
    if yr == '26.1Q':
        return "date >= '2026-01-01' AND date < '2026-04-01'"
    return f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"

def before_after(values):
    """전=22~24 월평균, 후=25~26.1Q 월평균"""
    before = (values['2022']+values['2023']+values['2024'])/3
    after = (values['2025']*12 + values['26.1Q']*3)/15
    return before, after, after-before, (after-before)/before*100 if before else 0

# 1. 전체 매출
print("=== JP 전체 월평균 매출 (억) ===")
rev = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                    FROM dw_app_monthly
                    WHERE country='JP' AND in_revenue_top100_unified_os=TRUE AND {period_filter(yr)}""")
    rev[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {rev[yr]:,.0f}억")
b,a,d,p = before_after(rev)
print(f"  전후: {b:,.0f} → {a:,.0f} ({d:+,.0f}억, {p:+.1f}%)")

# 2. MAU
print("\n=== JP MAU (만명) ===")
mau = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""
    WITH mo AS (SELECT date, SUM(mau) s FROM dw_app_monthly
                WHERE country='JP' AND in_revenue_top100_unified_os=TRUE AND {period_filter(yr)}
                GROUP BY date)
    SELECT ROUND(AVG(s)/10000.0, 0) FROM mo""")
    mau[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {mau[yr]:,.0f}만")
b,a,d,p = before_after(mau)
print(f"  전후: {b:,.0f} → {a:,.0f} ({d:+,.0f}만, {p:+.1f}%)")

# 3. ARPMAU
print("\n=== JP ARPMAU (원/MAU) ===")
arp = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""
    WITH mo AS (SELECT date, SUM(revenue_krw_100) r, SUM(mau) u FROM dw_app_monthly
                WHERE country='JP' AND in_revenue_top100_unified_os=TRUE AND {period_filter(yr)}
                GROUP BY date)
    SELECT ROUND(AVG(r)/NULLIF(AVG(u),0), 0) FROM mo""")
    arp[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {arp[yr]:,.0f}원")
b,a,d,p = before_after(arp)
print(f"  전후: {b:,.0f} → {a:,.0f} ({d:+,.0f}원, {p:+.1f}%)")

# 4. DL
print("\n=== JP DL (만건) ===")
dl = {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""SELECT ROUND(SUM(units)/10000.0/{m}, 0)
                    FROM dw_app_monthly
                    WHERE country='JP' AND in_revenue_top100_unified_os=TRUE AND {period_filter(yr)}""")
    dl[yr] = cur.fetchone()[0] or 0
    print(f"  {yr}: {dl[yr]:,.0f}만")
b,a,d,p = before_after(dl)
print(f"  전후: {b:,.0f} → {a:,.0f} ({d:+,.0f}만, {p:+.1f}%)")

# 5. 퍼블국적별 매출
print("\n=== JP 퍼블국적별 월평균 매출 (억) ===")
CN = "('China','Hong Kong','Taiwan','Macao','Macau','Singapore')"
groups = [
    ('JP',   f"publisher_country='Japan' AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'"),
    ('중화권', f"(publisher_country IN {CN} OR publisher_name ILIKE '%FUNFLY%') AND publisher_name NOT ILIKE '%NEXON%'"),
    ('KR',   f"publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%'"),
    ('북미',  f"publisher_country IN ('United States','Canada') AND publisher_name NOT ILIKE '%NEXON%'"),
    ('기타',  f"publisher_country IS NOT NULL AND publisher_country NOT IN ('Japan','South Korea','United States','Canada','China','Hong Kong','Taiwan','Macao','Macau') AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'"),
]
for gname, cond in groups:
    vals = {}
    for yr, m in YR_MONTHS.items():
        cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                        FROM dw_app_monthly
                        WHERE country='JP' AND in_revenue_top100_unified_os=TRUE
                          AND {period_filter(yr)} AND {cond}""")
        vals[yr] = cur.fetchone()[0] or 0
    b,a,d,p = before_after(vals)
    print(f"  {gname:<6}: " + ' '.join(f'{vals[y]:>5,.0f}' for y in YR_MONTHS) + f"  전후 {b:,.0f}→{a:,.0f} ({d:+.0f}, {p:+.1f}%)")

# 6. 장르별 매출
print("\n=== JP 장르별 월평균 매출 (억) — 주요 장르만 ===")
genres = ['Strategy','Arcade','Simulation','Card','Puzzle','Action','Sports','Role Playing','Adventure','Music']
for g in genres:
    vals = {}
    for yr, m in YR_MONTHS.items():
        cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                        FROM dw_app_monthly
                        WHERE country='JP' AND in_revenue_top100_unified_os=TRUE
                          AND {period_filter(yr)} AND genre='{g}'""")
        vals[yr] = cur.fetchone()[0] or 0
    b,a,d,p = before_after(vals)
    print(f"  {g:<13}: " + ' '.join(f'{vals[y]:>5,.0f}' for y in YR_MONTHS) + f"  전후 {b:,.0f}→{a:,.0f} ({d:+.0f}억, {p:+.1f}%)")

conn.close()
