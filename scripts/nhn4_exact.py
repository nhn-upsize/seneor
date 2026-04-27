# -*- coding: utf-8 -*-
import psycopg2
conn = psycopg2.connect('postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame')
cur = conn.cursor()

games = [
    ('한게임 포커',         '한게임 포커'),
    ('한게임 섯다&맞고',    '한게임 섯다'),
    ('한게임포커 클래식',   '한게임포커 클래식'),
    ('한게임 신맞고',       '한게임 신맞고'),
]
yr_months = {'2024':12, '2025':12, '26.1Q':3}

print('[KR · in_revenue_top100_unified_os=TRUE · Card+Casino+Board · dw_app_monthly.revenue_krw_100]')
print('연도별 환율(24:1,364 / 25:1,422 / 26:1,409) + 센서타워 100% 보정(÷0.7) 적용')
print('=' * 110)
print(f"{'게임':<22}{'2024 월평균 (원)':>28}{'2025 월평균 (원)':>28}{'26.1Q 월평균 (원)':>28}")
print('-' * 110)

sql_tpl = """
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, SUM(revenue_krw_100) AS m
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND publisher_name ILIKE 'PCT_NHN_PCT'
      AND name ILIKE 'PCT_NAME_PCT'
      AND date BETWEEN '2024-01-01' AND '2026-03-01'
    GROUP BY yr, date
)
SELECT yr, SUM(m) AS total FROM base GROUP BY yr ORDER BY yr;
"""

for label, pat in games:
    sql = sql_tpl.replace('PCT_NHN_PCT', '%NHN%').replace('PCT_NAME_PCT', f'%{pat}%')
    cur.execute(sql)
    rows = dict(cur.fetchall())
    line = f"{label:<22}"
    for yr in ['2024','2025','26.1Q']:
        tot = rows.get(yr)
        if tot is not None:
            avg = float(tot) / yr_months[yr]
            line += f"{int(avg):>24,}원"
        else:
            line += f"{'-':>28}"
    print(line)

# 합계
print('-' * 110)
sql_tot = """
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, SUM(revenue_krw_100) AS m
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND publisher_name ILIKE '%NHN%'
      AND (name ILIKE '%한게임 포커%' OR name ILIKE '%한게임 섯다%'
           OR name ILIKE '%한게임포커 클래식%' OR name ILIKE '%한게임 신맞고%')
      AND date BETWEEN '2024-01-01' AND '2026-03-01'
    GROUP BY yr, date
)
SELECT yr, SUM(m) FROM base GROUP BY yr ORDER BY yr;
"""
cur.execute(sql_tot)
totals = dict(cur.fetchall())
line = f"{'NHN 4종 합계':<22}"
for yr in ['2024','2025','26.1Q']:
    tot = totals.get(yr)
    if tot is not None:
        avg = float(tot) / yr_months[yr]
        line += f"{int(avg):>24,}원"
    else:
        line += f"{'-':>28}"
print(line)

cur.close(); conn.close()
