# -*- coding: utf-8 -*-
"""KR 웹보드 — KR 퍼블리셔 기준 월별/분기별 재검증"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 분기별 - KR 퍼블만
print("=== 분기별 (KR 퍼블만) ===")
quarters = [
    ('22.1Q', '2022-01-01', '2022-04-01'),
    ('22.2Q', '2022-04-01', '2022-07-01'),
    ('22.3Q', '2022-07-01', '2022-10-01'),
    ('22.4Q', '2022-10-01', '2023-01-01'),
]
for lbl, s, e in quarters:
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0/3, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND (publisher_country='South Korea')
      AND date >= '{s}' AND date < '{e}'
    """)
    v = cur.fetchone()[0] or 0
    print(f"  {lbl}: {v:,.1f}")

# 월별 - KR 퍼블만
print("\n=== 22년 월별 (KR 퍼블만) ===")
for m in range(1, 13):
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND (publisher_country='South Korea')
      AND date = '2022-{m:02d}-01'
    """)
    v = cur.fetchone()[0] or 0
    print(f"  2022-{m:02d}: {v:,.1f}")

conn.close()
