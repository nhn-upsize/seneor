# -*- coding: utf-8 -*-
"""KR TOP5 퍼블리셔 연도별 월평균 매출 검증
unified_os=TRUE, country_code='KR', revenue_krw_100 기준
"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 퍼블리셔 이름 패턴
publishers = {
    '넥슨': ['NEXON', 'nexon'],
    '넷마블': ['Netmarble', 'NETMARBLE'],
    '카카오게임즈': ['Kakao Games', 'KAKAO'],
    'NHN': ['NHN'],
    '엔씨소프트': ['NCSOFT', 'NC'],
}

# 연도별 월수
YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

for pub_name, patterns in publishers.items():
    like_clause = ' OR '.join([f"publisher_name ILIKE '%{p}%'" for p in patterns])
    print(f"\n=== {pub_name} ===")
    for yr, months in YR_MONTHS.items():
        if yr == '26.1Q':
            date_filter = "date >= '2026-01-01' AND date < '2026-04-01'"
        else:
            date_filter = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"

        sql = f"""
        SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{months}, 0) as monthly_avg_억
        FROM dw_app_monthly
        WHERE country='KR'
          AND in_revenue_top100_unified_os=TRUE
          AND {date_filter}
          AND ({like_clause})
        """
        cur.execute(sql)
        r = cur.fetchone()
        val = r[0] if r and r[0] else 0
        print(f"  {yr}: {val:.0f}억/월")

conn.close()
