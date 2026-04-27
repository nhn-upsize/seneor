# -*- coding: utf-8 -*-
"""KR 웹보드 분기별 매출 검증 — Card+Casino+Board 통합 · TOP100 unified_os"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 연도별 환율
FX = {'2022':1292, '2023':1307, '2024':1364, '2025':1422, '2026':1409}

# 분기별 매출 (월평균, 웹보드 장르만)
print("=== KR 웹보드 분기별 월평균 매출 (억원) ===")
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
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0/3, 0)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date >= '{s}' AND date < '{e}'
    """)
    v = cur.fetchone()[0] or 0
    print(f"  {lbl}: {v:,.1f}")

# 22년 7월 규제 한도 상향 전후 월별 매출 (22년 월별)
print("\n=== 2022년 월별 웹보드 매출 (억원) ===")
for m in range(1, 13):
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date = '2022-{m:02d}-01'
    """)
    v = cur.fetchone()[0] or 0
    marker = '  <-- 규제 상향 (7/1부)' if m == 7 else ''
    print(f"  2022-{m:02d}: {v:,.1f}{marker}")

# 주요 게임별 22년 분기 추이 (한게임 포커·섯다맞고·포커클래식·피망포커)
print("\n=== 주요 웹보드 게임 22년 분기별 매출 (억원/월) ===")
games_q = [
    ('22.1Q', '2022-01-01', '2022-04-01'),
    ('22.2Q', '2022-04-01', '2022-07-01'),
    ('22.3Q', '2022-07-01', '2022-10-01'),
    ('22.4Q', '2022-10-01', '2023-01-01'),
]
cur.execute(f"""
SELECT name, unified_app_id FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  AND date >= '2022-01-01' AND date < '2023-01-01'
  AND (name ILIKE '%한게임%' OR name ILIKE '%섯다%' OR name ILIKE '%포커클래식%'
       OR name ILIKE '%피망%' OR name ILIKE '%윈조이%' OR name ILIKE '%WPL%')
GROUP BY name, unified_app_id
ORDER BY name
""")
games = cur.fetchall()
for name, aid in games:
    print(f"\n  {name}:")
    for lbl, s, e in games_q:
        cur.execute(f"""
        SELECT ROUND(SUM(revenue_krw_100)/100000000.0/3, 1)
        FROM dw_app_monthly
        WHERE country='KR' AND unified_app_id='{aid}'
          AND date >= '{s}' AND date < '{e}'
        """)
        v = cur.fetchone()[0] or 0
        print(f"    {lbl}: {v:,.1f}")

conn.close()
