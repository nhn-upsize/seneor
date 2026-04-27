# -*- coding: utf-8 -*-
"""3국 합산(KR+JP+US) 전체 데이터 검증"""
import psycopg2, sys
sys.stdout.reconfigure(encoding='utf-8')
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

COND = "country IN ('KR','JP','US') AND in_revenue_top100_unified_os=TRUE"

# 1. 전체 매출·MAU·ARPMAU·DL
print("=== 3국 합산 연도별 ===")
print(f"{'연도':<8}{'매출(억)':>12}{'MAU(만)':>12}{'ARPMAU(원)':>14}{'DL(만)':>10}")
rev, mau, arp, dl = {}, {}, {}, {}
for yr, m in YR_MONTHS.items():
    cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                    FROM dw_app_monthly WHERE {COND} AND {pf(yr)}""")
    rev[yr] = float(cur.fetchone()[0] or 0)
    cur.execute(f"""
    WITH mo AS (SELECT date, SUM(mau) u FROM dw_app_monthly
                WHERE {COND} AND {pf(yr)} GROUP BY date)
    SELECT ROUND(AVG(u)/10000.0, 0) FROM mo""")
    mau[yr] = float(cur.fetchone()[0] or 0)
    cur.execute(f"""
    WITH mo AS (SELECT date, SUM(revenue_krw_100) r, SUM(mau) u FROM dw_app_monthly
                WHERE {COND} AND {pf(yr)} GROUP BY date)
    SELECT ROUND(AVG(r)/NULLIF(AVG(u),0), 0) FROM mo""")
    arp[yr] = float(cur.fetchone()[0] or 0)
    cur.execute(f"""SELECT ROUND(SUM(units)/10000.0/{m}, 0)
                    FROM dw_app_monthly WHERE {COND} AND {pf(yr)}""")
    dl[yr] = float(cur.fetchone()[0] or 0)
    print(f"{yr:<8}{rev[yr]:>12,.0f}{mau[yr]:>12,.0f}{arp[yr]:>14,.0f}{dl[yr]:>10,.0f}")

print("\n전후 변화:")
for label, d in [('매출', rev), ('MAU', mau), ('ARPMAU', arp), ('DL', dl)]:
    b, a, delta, pct = ba(d)
    print(f"  {label:<7}: {b:>10,.0f} → {a:>10,.0f}  ({delta:+,.0f}, {pct:+.1f}%)")

# 2. 퍼블국적별 매출 (3국 합산)
print("\n=== 3국 합산 퍼블국적별 매출 (억) ===")
CN = "('China','Hong Kong','Taiwan','Macao','Macau','Singapore')"
groups = [
    ('KR',    "(publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%') AND publisher_name NOT ILIKE '%FUNFLY%'"),
    ('JP',    "publisher_country='Japan' AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'"),
    ('중화권',  f"(publisher_country IN {CN} OR publisher_name ILIKE '%FUNFLY%') AND publisher_name NOT ILIKE '%NEXON%'"),
    ('북미',   "publisher_country IN ('United States','Canada') AND publisher_name NOT ILIKE '%NEXON%'"),
    ('기타',   f"publisher_country IS NOT NULL AND publisher_country NOT IN ('Japan','South Korea','United States','Canada','China','Hong Kong','Taiwan','Macao','Macau') AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'"),
]
for gname, cnd in groups:
    vals = {}
    for yr, m in YR_MONTHS.items():
        cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                        FROM dw_app_monthly WHERE {COND} AND {pf(yr)} AND {cnd}""")
        vals[yr] = float(cur.fetchone()[0] or 0)
    b, a, d, p = ba(vals)
    print(f"  {gname:<5}: " + ' '.join(f'{vals[y]:>7,.0f}' for y in YR_MONTHS) + f"  {b:,.0f}→{a:,.0f} ({d:+,.0f}, {p:+.1f}%)")

# 3. 장르별 매출 (3국 합산)
print("\n=== 3국 합산 장르별 매출 (억) ===")
for g in ['Strategy','Puzzle','Role Playing','Casino','Board','Adventure','Action','Arcade','Simulation','Card','Music','Sports','Casual','Racing','Word']:
    vals = {}
    for yr, m in YR_MONTHS.items():
        cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 0)
                        FROM dw_app_monthly WHERE {COND} AND {pf(yr)} AND genre='{g}'""")
        vals[yr] = float(cur.fetchone()[0] or 0)
    b, a, dd, p = ba(vals)
    print(f"  {g:<13}: " + ' '.join(f'{vals[y]:>6,.0f}' for y in YR_MONTHS) + f"  {b:,.0f}→{a:,.0f} ({dd:+,.0f}, {p:+.1f}%)")
conn.close()
