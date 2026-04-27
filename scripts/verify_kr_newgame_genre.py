# -*- coding: utf-8 -*-
"""KR TOP100 신규 진입 — 퍼블국적 × 장르(RPG vs 비RPG) 연도별 진입 수"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 중화권 국가 정의
CN_COUNTRIES = "('China','Hong Kong','Taiwan','Singapore')"

for pub_group, cond in [
    ('KR 퍼블', f"(publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')"),
    ('중화권',  f"publisher_country IN {CN_COUNTRIES}"),
]:
    print(f"\n=== {pub_group} · 연도별 신규 진입 수 (장르별) ===")
    # 연도별 첫 진입월 기준
    sql = f"""
    WITH first_entry AS (
      SELECT unified_app_id,
             MIN(date) AS first_date,
             (ARRAY_AGG(genre ORDER BY date))[1] AS genre0
      FROM dw_app_monthly
      WHERE country='KR'
        AND in_revenue_top100_unified_os=TRUE
        AND {cond}
      GROUP BY unified_app_id
    )
    SELECT EXTRACT(YEAR FROM first_date)::int AS yr,
           CASE
             WHEN genre0 ILIKE '%MMORPG%' OR genre0 ILIKE '%Role%' OR genre0 ILIKE '%RPG%' THEN 'RPG'
             WHEN genre0 ILIKE '%Strategy%' THEN 'Strategy'
             WHEN genre0 ILIKE '%Casual%' OR genre0 ILIKE '%Puzzle%' OR genre0 ILIKE '%Arcade%' THEN 'Casual'
             ELSE '기타'
           END AS g,
           COUNT(*) cnt
    FROM first_entry
    WHERE first_date >= '2022-01-01' AND first_date < '2026-01-01'
    GROUP BY yr, g
    ORDER BY yr, g
    """
    cur.execute(sql)
    data = {}
    for yr, g, cnt in cur.fetchall():
        data.setdefault(yr, {})[g] = cnt
    for yr in sorted(data.keys()):
        parts = [f"{k}:{v}" for k, v in data[yr].items()]
        total = sum(data[yr].values())
        avg = total/12
        print(f"  {yr}: {', '.join(parts)} · 합{total}개 · 월평균 {avg:.1f}")

conn.close()
