# -*- coding: utf-8 -*-
"""기타 KR 퍼블리셔 수 — 월평균 기준 (기존 게임수와 동일 집계 방식)
정규화(raw 이름 통일) 후 월평균
"""
import psycopg2, re

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

TOP5_COND = """publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%'
OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%'
OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%'"""

def normalize(name):
    n = name.upper()
    n = re.sub(r"\b(CO\.?\s*,?\s*LTD\.?|CORP\.?|INC\.?|CORPORATION|LTD\.?|STUDIO|\(.*\)|CO\.?)\s*$", "", n).strip()
    n = re.sub(r"\s*,\s*$", "", n).strip()
    n = re.sub(r"[.,]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

print(f"{'연도':<8}{'월평균 퍼블 (raw)':<20}{'월평균 퍼블 (정규화)':<22}{'월평균 게임':<14}")
for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT date, publisher_name, unified_app_id
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {df}
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT ({TOP5_COND})
    """)
    rows = cur.fetchall()
    # 월별 집계
    by_month = {}
    for d, pname, aid in rows:
        by_month.setdefault(d, {'raw_pubs':set(), 'norm_pubs':set(), 'games':set()})
        by_month[d]['raw_pubs'].add(pname)
        by_month[d]['norm_pubs'].add(normalize(pname))
        by_month[d]['games'].add(aid)
    if not by_month:
        continue
    n_months = len(by_month)
    raw_avg = sum(len(m['raw_pubs']) for m in by_month.values()) / n_months
    norm_avg = sum(len(m['norm_pubs']) for m in by_month.values()) / n_months
    game_avg = sum(len(m['games']) for m in by_month.values()) / n_months
    print(f"{yr:<8}{raw_avg:<20.1f}{norm_avg:<22.1f}{game_avg:<14.1f}")

conn.close()
