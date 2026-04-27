# -*- coding: utf-8 -*-
"""
Step 4 대표 게임 8개의 월평균 매출 — 연도 전체 월수 기준으로 재계산
"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 대표 게임 8개를 unified_app_id 기반으로 식별 (26.1Q 기준 TOP 등 활용)
# 이름 매칭으로 찾기
targets = [
    ('한게임 포커', 'NHN'),
    ('한게임 섯다', 'NHN'),
    ('한게임포커 클래식', 'NHN'),
    ('한게임 신맞고', 'NHN'),
    ('Pmang Poker', 'NEOWIZ'),
    ('피망 뉴맞고', 'NEOWIZ'),
    ('WPL', 'Zempot'),
    ('Yu-Gi-Oh', 'KONAMI'),
]

# 각 게임의 unified_app_id 확보
for name_like, pub_like in targets:
    cur.execute("""
      SELECT unified_app_id, name, publisher_name
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND name ILIKE %s AND publisher_name ILIKE %s
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
      GROUP BY unified_app_id, name, publisher_name
      ORDER BY COUNT(*) DESC LIMIT 1
    """, (f'%{name_like}%', f'%{pub_like}%'))
    r = cur.fetchone()
    print(f"  {name_like} / {pub_like}: uaid={r[0] if r else None}  name={r[1][:30] if r else None}")

# 연도별 월수
yr_months = {'2022':12, '2023':12, '2024':12, '2025':12, '26.1Q':3}

# 게임별 연도별 매출합 / 전체 월수
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, unified_app_id, name, publisher_name, revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
)
SELECT yr, unified_app_id, MAX(name) AS any_name, MAX(publisher_name) AS pub,
       SUM(revenue_krw_100) AS rev, COUNT(DISTINCT date) AS appearing_months
FROM base GROUP BY yr, unified_app_id ORDER BY yr, rev DESC NULLS LAST;
""")
rows = cur.fetchall()

# 특정 8게임만 필터
want_names = ['한게임 포커', '한게임 섯다', '한게임포커 클래식', '한게임 신맞고',
              'Pmang Poker', '피망 뉴맞고', 'WPL', 'Yu-Gi-Oh']
matched = {}
for yr, uaid, name, pub, rev, months in rows:
    for w in want_names:
        if name and w in name:
            key = w
            matched.setdefault(key, {})
            months_total = yr_months[yr]
            matched[key].setdefault(yr, {})
            # 동일 게임이 여러 unified_app_id로 나올 수 있음 — 매출 큰 것 채택
            cur_best = matched[key][yr].get('rev', 0)
            if rev and float(rev) > float(cur_best or 0):
                matched[key][yr] = {
                    'rev': float(rev),
                    'months_total': months_total,
                    'appearing': months,
                    'uaid': uaid,
                    'pub': pub,
                    'name': name,
                }

print("\n[각 게임 연도별 월평균 매출 (억) — 전체 월수 기준]")
print(f"{'게임':<20}{'22':>10}{'23':>10}{'24':>10}{'25':>10}{'26.1Q':>10}")
for key in want_names:
    m = matched.get(key, {})
    vals = []
    for y in ['2022','2023','2024','2025','26.1Q']:
        d = m.get(y, {})
        if not d or not d.get('rev'):
            vals.append('-')
        else:
            eok = d['rev'] / 1e8 / d['months_total']
            vals.append(f"{eok:.1f}")
    print(f"{key[:20]:<20}" + "".join(f"{v:>10}" for v in vals))

# 합계 계산
print("\n[연도별 합계 (8게임 월평균 합)]")
for y in ['2022','2023','2024','2025','26.1Q']:
    total = 0
    for key in want_names:
        m = matched.get(key, {}).get(y, {})
        if m and m.get('rev'):
            total += m['rev'] / 1e8 / m['months_total']
    print(f"  {y}: {total:.1f} 억")

cur.close(); conn.close()
