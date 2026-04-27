# -*- coding: utf-8 -*-
"""KR 기타 KR 퍼블 게임수 — 기존 표의 '22게임' 기준 vs DB 조회값 대조
기존 표는 TOP100 내 연도별로 일정 시점의 고유 게임수인지 확인
"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

TOP5_COND = """publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%'
OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%'
OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%'"""

print("\n=== 방법 A: 연도 내 TOP100 한번이라도 진입한 고유 게임수 ===")
YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}
for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT COUNT(DISTINCT unified_app_id)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {df}
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT ({TOP5_COND})
    """)
    print(f"  {yr}: {cur.fetchone()[0]}개")

print("\n=== 방법 B: 월평균 (해당 연도 각 월 평균 게임수) ===")
for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    WITH monthly AS (
      SELECT date, COUNT(DISTINCT unified_app_id) cnt
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND {df}
        AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
        AND NOT ({TOP5_COND})
      GROUP BY date
    )
    SELECT ROUND(AVG(cnt), 0), MIN(cnt), MAX(cnt)
    FROM monthly
    """)
    r = cur.fetchone()
    print(f"  {yr}: 월평균 {r[0]}개 (최소 {r[1]}, 최대 {r[2]})")

print("\n=== 방법 C: 특정 월 기준 스냅샷 (예: 각 연도 6월) ===")
for yr in ['2022','2023','2024','2025']:
    cur.execute(f"""
    SELECT COUNT(DISTINCT unified_app_id)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND date = '{yr}-06-01'
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT ({TOP5_COND})
    """)
    print(f"  {yr}-06: {cur.fetchone()[0]}개")
cur.execute(f"""
SELECT COUNT(DISTINCT unified_app_id)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date = '2026-02-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
  AND NOT ({TOP5_COND})
""")
print(f"  2026-02: {cur.fetchone()[0]}개")

conn.close()
