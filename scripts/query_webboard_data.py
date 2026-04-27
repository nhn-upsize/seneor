# -*- coding: utf-8 -*-
"""
Webboard 분석용 데이터 조회:
1) KR Card+Casino+Board 장르, in_revenue_top100_unified_os=TRUE 기준
   연도별 월평균 다운로드 (22/23/24/25/26.1Q)
2) 연도별 순위별(1~5위) 월평균 매출 (revenue_krw_100) + 게임명/퍼블리셔
"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# ============================================================
# 1) 연도별 월평균 다운로드 (units)
#    Card+Casino+Board, KR, in_revenue_top100_unified_os=TRUE
# ============================================================
print("=" * 70)
print("[1] 웹보드 연도별 월평균 다운로드 (만건)")
print("=" * 70)

sql_dl = """
WITH base AS (
    SELECT
        CASE
            WHEN date >= '2026-01-01' THEN '26.1Q'
            ELSE TO_CHAR(date, 'YYYY')
        END AS yr,
        date,
        units
    FROM dw_app_monthly
    WHERE country = 'KR'
      AND in_revenue_top100_unified_os = TRUE
      AND genre IN ('Card', 'Casino', 'Board')
      AND date >= '2022-01-01'
      AND date <= '2026-03-01'
),
monthly_sum AS (
    SELECT yr, date, SUM(units) AS monthly_units
    FROM base
    GROUP BY yr, date
)
SELECT yr,
       ROUND(AVG(monthly_units)::numeric / 10000.0, 1) AS monthly_avg_units_10k
FROM monthly_sum
GROUP BY yr
ORDER BY yr;
"""
cur.execute(sql_dl)
dl_rows = cur.fetchall()
for r in dl_rows:
    print(f"  {r[0]}: {r[1]} 만건/월")

# ============================================================
# 2) 연도별 순위별 매출 TOP5
# ============================================================
print()
print("=" * 70)
print("[2] 연도별 순위별 월평균 매출 (억원) + 게임명/퍼블리셔")
print("=" * 70)

sql_rank = """
WITH base AS (
    SELECT
        CASE
            WHEN date >= '2026-01-01' THEN '26.1Q'
            ELSE TO_CHAR(date, 'YYYY')
        END AS yr,
        date, os, unified_app_id, name, publisher_name, revenue_krw_100
    FROM dw_app_monthly
    WHERE country = 'KR'
      AND in_revenue_top100_unified_os = TRUE
      AND genre IN ('Card', 'Casino', 'Board')
      AND date >= '2022-01-01'
      AND date <= '2026-03-01'
),
-- unified_app_id 기준으로 OS 통합 (android+ios 이름이 달라도 같은 앱)
per_app_yr AS (
    SELECT yr, unified_app_id,
           MAX(publisher_name) AS publisher_name,
           SUM(revenue_krw_100) AS rev_sum,
           COUNT(DISTINCT date) AS months
    FROM base
    GROUP BY yr, unified_app_id
),
-- 대표 이름: android 우선 (없으면 ios)
rep_name AS (
    SELECT DISTINCT ON (yr, unified_app_id)
           yr, unified_app_id, name
    FROM base
    ORDER BY yr, unified_app_id,
             CASE WHEN os='android' THEN 0 ELSE 1 END,
             date DESC
),
per_app_monthly AS (
    SELECT p.yr, p.unified_app_id, rn.name, p.publisher_name,
           p.rev_sum / NULLIF(p.months, 0) AS monthly_avg_krw
    FROM per_app_yr p
    JOIN rep_name rn USING (yr, unified_app_id)
),
ranked AS (
    SELECT yr, name, publisher_name, monthly_avg_krw,
           ROW_NUMBER() OVER (PARTITION BY yr ORDER BY monthly_avg_krw DESC NULLS LAST) AS rnk
    FROM per_app_monthly
    WHERE monthly_avg_krw IS NOT NULL
)
SELECT yr, rnk, name, publisher_name,
       ROUND((monthly_avg_krw / 1e8)::numeric, 1) AS monthly_avg_eok
FROM ranked
WHERE rnk <= 5
ORDER BY yr, rnk;
"""
cur.execute(sql_rank)
rows = cur.fetchall()
current_yr = None
for yr, rnk, name, pub, eok in rows:
    if yr != current_yr:
        print(f"\n  -- {yr} --")
        current_yr = yr
    print(f"    {rnk}위  {eok}억  {name}  ({pub})")

cur.close()
conn.close()
