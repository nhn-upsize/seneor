# -*- coding: utf-8 -*-
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()
for yr, months in {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}.items():
    if yr=='26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT ROUND(SUM(units)/10000.0/{months}, 0)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE AND {df}
    """)
    v = cur.fetchone()[0] or 0
    print(f"{yr}: {v:,.0f} 만건/월")
conn.close()
