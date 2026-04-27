# -*- coding: utf-8 -*-
"""웹보드 7게임 연령/성별/MAU/다운로드 연도별 비교 데이터 추출"""
import psycopg2, json
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

GAMES = [
    ('한게임 포커',         ['한게임 포커'],            '%NHN%'),
    ('한게임 섯다&맞고',    ['한게임 섯다'],            '%NHN%'),
    ('한게임포커 클래식',   ['한게임포커 클래식'],      '%NHN%'),
    ('한게임 신맞고',       ['한게임 신맞고'],          '%NHN%'),
    ('Pmang Poker',         ['Pmang Poker'],            '%NEOWIZ%'),
    ('피망 뉴맞고',         ['피망 뉴맞고','Pmang Gostop'], '%NEOWIZ%'),
    ('WPL (윈조이 포커 리그)', ['WPL','윈조이 포커 리그'], '%Zempot%'),
]
YEARS = ['2022','2023','2024','2025','26.1Q']

result = {}
for label, pats, pub in GAMES:
    like = ' OR '.join(['name ILIKE %s'] * len(pats))
    sql = f"""
    WITH base AS (
      SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
             date, mau, units, avg_age_total, female_pct, male_pct, revenue_krw_100
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND genre IN ('Card','Casino','Board')
        AND publisher_name ILIKE %s AND ({like})
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
    )
    SELECT yr,
      ROUND(AVG(avg_age_total)::numeric, 1) AS age,
      ROUND((AVG(female_pct)*100)::numeric, 1) AS f_pct,
      ROUND((AVG(male_pct)*100)::numeric, 1) AS m_pct,
      ROUND((AVG(mau)/10000.0)::numeric, 1) AS mau_man,
      ROUND((AVG(units)/10000.0)::numeric, 1) AS dl_man
    FROM base GROUP BY yr ORDER BY yr;
    """
    cur.execute(sql, tuple([pub] + [f'%{p}%' for p in pats]))
    result[label] = {}
    for yr, age, f, m, mau, dl in cur.fetchall():
        result[label][yr] = {
            'age': float(age) if age else None,
            'f_pct': float(f) if f else None,
            'm_pct': float(m) if m else None,
            'mau_man': float(mau) if mau else None,
            'dl_man': float(dl) if dl else None,
        }

# 출력
for label in result:
    print(f"\n=== {label} ===")
    for y in YEARS:
        d = result[label].get(y, {})
        age = f"{d.get('age')}세" if d.get('age') else '-'
        gen = f"M{d.get('m_pct'):.0f}/F{d.get('f_pct'):.0f}" if d.get('m_pct') else '-'
        mau = f"{d.get('mau_man'):.1f}만" if d.get('mau_man') else '-'
        dl = f"{d.get('dl_man'):.1f}만" if d.get('dl_man') else '-'
        print(f"  {y}: 연령 {age} / 성비 {gen} / MAU {mau} / DL {dl}")

with open(r'C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json','w',encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\n[saved]")

cur.close(); conn.close()
