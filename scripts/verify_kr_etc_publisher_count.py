# -*- coding: utf-8 -*-
"""KR 시장 TOP100 내 한국 퍼블리셔 — TOP5(엔씨·넥슨·넷마블·카카오·NHN) 제외 '기타 KR'의 퍼블리셔 개수"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

TOP5 = "('NCSOFT','NC Corporation','NC','NEXON','NEXON Korea','Nexon','Netmarble','NETMARBLE','Kakao Games','KAKAO Games','NHN','NHN Corp.')"

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        date_filter = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        date_filter = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT COUNT(DISTINCT publisher_name) AS pub_cnt,
           COUNT(DISTINCT unified_app_id) AS game_cnt
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {date_filter}
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND publisher_name NOT IN {TOP5}
      AND publisher_name NOT ILIKE '%NCSOFT%'
      AND publisher_name NOT ILIKE '%NEXON%'
      AND publisher_name NOT ILIKE '%Netmarble%'
      AND publisher_name NOT ILIKE '%Kakao Games%'
      AND publisher_name NOT ILIKE '%NHN%'
    """)
    r = cur.fetchone()
    print(f"{yr}: 퍼블리셔 {r[0]}개 · 게임 {r[1]}개")

conn.close()
