# -*- coding: utf-8 -*-
"""MAU / ARPMAU 연도별 검증 (KR, JP, US)"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

for country in ['KR','JP','US']:
    print(f"\n=== {country} (TOP100 unified_os) ===")
    for yr, months in YR_MONTHS.items():
        if yr == '26.1Q':
            date_filter = "date >= '2026-01-01' AND date < '2026-04-01'"
        else:
            date_filter = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
        sql = f"""
        WITH m AS (
          SELECT date,
                 SUM(revenue_krw_100) AS rev,
                 SUM(mau) AS mau_sum
          FROM dw_app_monthly
          WHERE country='{country}'
            AND in_revenue_top100_unified_os=TRUE
            AND {date_filter}
          GROUP BY date
        )
        SELECT ROUND(AVG(mau_sum)/10000.0, 0) AS mau_만,
               ROUND(AVG(rev)/NULLIF(AVG(mau_sum),0), 0) AS arpmau_원
        FROM m
        """
        cur.execute(sql)
        r = cur.fetchone()
        mau = r[0] if r and r[0] else 0
        arp = r[1] if r and r[1] else 0
        print(f"  {yr}: MAU {mau:>6,.0f}만 · ARPMAU {arp:>7,.0f}원")

conn.close()
