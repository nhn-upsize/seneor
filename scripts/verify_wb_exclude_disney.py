# -*- coding: utf-8 -*-
"""KR 웹보드 (Disney Solitaire 제외) 분기별·연도별 매출 재검증"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

EXCLUDE = "AND name NOT ILIKE '%Disney Solitaire%'"

# 분기별
print("=== 분기별 월평균 매출 (Disney Solitaire 제외) ===")
quarters = [
    ('22.1Q', '2022-01-01', '2022-04-01'),
    ('22.2Q', '2022-04-01', '2022-07-01'),
    ('22.3Q', '2022-07-01', '2022-10-01'),
    ('22.4Q', '2022-10-01', '2023-01-01'),
    ('23.1Q', '2023-01-01', '2023-04-01'),
    ('23.2Q', '2023-04-01', '2023-07-01'),
    ('23.3Q', '2023-07-01', '2023-10-01'),
    ('23.4Q', '2023-10-01', '2024-01-01'),
    ('24.1Q', '2024-01-01', '2024-04-01'),
    ('24.2Q', '2024-04-01', '2024-07-01'),
    ('24.3Q', '2024-07-01', '2024-10-01'),
    ('24.4Q', '2024-10-01', '2025-01-01'),
    ('25.1Q', '2025-01-01', '2025-04-01'),
    ('25.2Q', '2025-04-01', '2025-07-01'),
    ('25.3Q', '2025-07-01', '2025-10-01'),
    ('25.4Q', '2025-10-01', '2026-01-01'),
    ('26.1Q', '2026-01-01', '2026-04-01'),
]
for lbl, s, e in quarters:
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0/3, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      {EXCLUDE}
      AND date >= '{s}' AND date < '{e}'
    """)
    v = cur.fetchone()[0] or 0
    print(f"  {lbl}: {v:,.1f}")

# 연도별
print("\n=== 연도별 월평균 매출 ===")
YR = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}
for yr, months in YR.items():
    if yr=='26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{months}, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      {EXCLUDE} AND {df}
    """)
    v = cur.fetchone()[0] or 0
    print(f"  {yr}: {v:,.1f}")

# 전후 비교
print("\n=== 25년 전후 (전 22~24 vs 후 25~26.1Q) ===")
cur.execute(f"""
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/36, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  {EXCLUDE}
  AND date >= '2022-01-01' AND date < '2025-01-01'
""")
b = cur.fetchone()[0] or 0
cur.execute(f"""
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/15, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  {EXCLUDE}
  AND date >= '2025-01-01' AND date < '2026-04-01'
""")
a = cur.fetchone()[0] or 0
print(f"  전: {b}억 / 후: {a}억 / 변화 {a-b:+,.1f}억 ({(a-b)/b*100:+.1f}%)")

# 22년 월별 (규제 이벤트 검증)
print("\n=== 22년 월별 ===")
for m in range(1, 13):
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      {EXCLUDE}
      AND date = '2022-{m:02d}-01'
    """)
    v = cur.fetchone()[0] or 0
    print(f"  2022-{m:02d}: {v:,.1f}")

conn.close()
