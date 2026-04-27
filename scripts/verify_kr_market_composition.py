# -*- coding: utf-8 -*-
"""KR 시장 — 퍼블 국적별 월평균 매출 연도별"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

CN = "('China','Hong Kong','Taiwan','Singapore')"
NA = "('United States','Canada')"

groups = [
    ('KR 퍼블', f"(publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')"),
    ('중화권',  f"publisher_country IN {CN} AND publisher_name NOT ILIKE '%NEXON%'"),
    ('북미',    f"publisher_country IN {NA}"),
    ('기타',    f"publisher_country IS NOT NULL AND publisher_country NOT IN {CN} AND publisher_country NOT IN {NA} AND publisher_country!='South Korea' AND publisher_name NOT ILIKE '%NEXON%'"),
]

print(f"\n{'구분':<10}" + ''.join(f"{y:>10}" for y in YR_MONTHS))
for gname, cond in groups:
    vals = []
    for yr, months in YR_MONTHS.items():
        if yr == '26.1Q':
            date_filter = "date >= '2026-01-01' AND date < '2026-04-01'"
        else:
            date_filter = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
        sql = f"""
        SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{months}, 0)
        FROM dw_app_monthly
        WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
          AND {date_filter}
          AND {cond}
        """
        cur.execute(sql)
        v = cur.fetchone()[0] or 0
        vals.append(v)
    print(f"{gname:<10}" + ''.join(f"{v:>10,.0f}" for v in vals))

# 전체
print(f"\n{'전체':<10}", end='')
for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        date_filter = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        date_filter = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{months}, 0)
                    FROM dw_app_monthly
                    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE AND {date_filter}""")
    print(f"{cur.fetchone()[0] or 0:>10,.0f}", end='')
print()

conn.close()
