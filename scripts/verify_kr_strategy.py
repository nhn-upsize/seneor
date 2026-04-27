# -*- coding: utf-8 -*-
"""KR Strategy / 중화권 Strategy / KR MMORPG 연도별 월평균 매출 검증"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# 먼저 publisher_country 값 확인
cur.execute("""
SELECT DISTINCT publisher_country, COUNT(*) cnt
FROM dw_app_monthly
WHERE country='KR' AND genre ILIKE '%strategy%'
  AND in_revenue_top100_unified_os=TRUE
GROUP BY publisher_country ORDER BY cnt DESC LIMIT 20
""")
print("=== publisher_country 분포 (KR × Strategy) ===")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}건")

# 장르 값 확인
cur.execute("""
SELECT DISTINCT genre, COUNT(*) cnt
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
GROUP BY genre ORDER BY cnt DESC LIMIT 20
""")
print("\n=== genre 분포 (KR TOP100) ===")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}건")

conn.close()
