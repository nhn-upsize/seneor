# -*- coding: utf-8 -*-
"""
Step 3 퍼블리셔별 월평균 매출/점유율 불일치 진단
- 각 연도 NHN / 네오위즈 / Zempot / 기타 월평균 매출(억)과 합계 비교
- 점유율이 어떤 분모로 계산되었는지 검증
"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

print("="*80)
print("[Card+Casino+Board · KR · in_revenue_top100_unified_os=TRUE 기준]")
print("="*80)

# 연도별 전체 월평균 매출 (억원)
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
monthly AS (SELECT yr, date, SUM(revenue_krw_100) AS m FROM base GROUP BY yr, date)
SELECT yr, ROUND((AVG(m)/1e8)::numeric, 1) AS total_eok
FROM monthly GROUP BY yr ORDER BY yr;
""")
total_by_yr = {r[0]: float(r[1]) for r in cur.fetchall()}
print("\n[전체 월평균 매출 (억원)]")
for y,v in total_by_yr.items(): print(f"  {y}: {v}억")

# 퍼블리셔 그룹별 월평균 매출
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date,
        CASE
            WHEN publisher_name ILIKE '%NHN%' THEN 'NHN'
            WHEN publisher_name ILIKE '%NEOWIZ%' THEN '네오위즈'
            WHEN publisher_name ILIKE '%Zempot%' OR publisher_name ILIKE '%ZEMPOT%' THEN 'Zempot'
            ELSE '기타'
        END AS pub_grp,
        revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
monthly AS (SELECT yr, pub_grp, date, SUM(revenue_krw_100) AS m FROM base GROUP BY yr, pub_grp, date)
SELECT yr, pub_grp, ROUND((AVG(m)/1e8)::numeric, 1) AS eok
FROM monthly GROUP BY yr, pub_grp ORDER BY yr, pub_grp;
""")
pub_rows = cur.fetchall()
pub_map = {}
for yr,g,v in pub_rows:
    pub_map.setdefault(yr,{})[g] = float(v) if v is not None else 0.0

print("\n[퍼블리셔별 월평균 매출 (억) + 개별 점유율 = 퍼블리셔매출/총매출]")
print(f"{'YR':<8}{'NHN':>10}{'네오':>10}{'Zempot':>10}{'기타':>10}{'합':>10}{'총':>10}{'합-총':>10}")
for yr in ['2022','2023','2024','2025','26.1Q']:
    row = pub_map.get(yr, {})
    nhn, neo, zem, etc = row.get('NHN',0), row.get('네오위즈',0), row.get('Zempot',0), row.get('기타',0)
    s = nhn+neo+zem+etc
    t = total_by_yr.get(yr,0)
    print(f"{yr:<8}{nhn:>10.1f}{neo:>10.1f}{zem:>10.1f}{etc:>10.1f}{s:>10.1f}{t:>10.1f}{s-t:>10.1f}")

print("\n[개별 점유율 (퍼블리셔매출/총매출) %]")
print(f"{'YR':<8}{'NHN':>10}{'네오':>10}{'Zempot':>10}{'기타':>10}{'합':>10}")
for yr in ['2022','2023','2024','2025','26.1Q']:
    row = pub_map.get(yr, {})
    t = total_by_yr.get(yr,0)
    if t == 0: continue
    nhn_p = row.get('NHN',0)/t*100
    neo_p = row.get('네오위즈',0)/t*100
    zem_p = row.get('Zempot',0)/t*100
    etc_p = row.get('기타',0)/t*100
    print(f"{yr:<8}{nhn_p:>10.1f}{neo_p:>10.1f}{zem_p:>10.1f}{etc_p:>10.1f}{nhn_p+neo_p+zem_p+etc_p:>10.1f}")

cur.close(); conn.close()
