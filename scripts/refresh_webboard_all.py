# -*- coding: utf-8 -*-
"""
웹보드 심층분석 전체 수치 재계산 (Card+Casino+Board 장르 필터, 현재 DB 기준).
원펀맨/솔라리바이벌/월드크러쉬/하이큐 FLY HIGH 는 Role Playing으로 재분류됐기에 자동 제외됨.
"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# ---------- 1) Step 1: 시장 전체 월평균 매출/MAU/ARPMAU ----------
print("="*70)
print("[Step 1] KR Card+Casino+Board 시장 월평균 매출 + MAU + ARPMAU")
print("="*70)
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, SUM(revenue_krw_100) AS m_rev, SUM(mau) AS m_mau
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY yr, date
)
SELECT yr,
       ROUND((AVG(m_rev)/1e8)::numeric, 1) AS rev_eok,
       ROUND((AVG(m_mau)/10000.0)::numeric, 0) AS mau_man,
       ROUND((AVG(m_rev)/NULLIF(AVG(m_mau),0))::numeric, 0) AS arpmau
FROM base GROUP BY yr ORDER BY yr;
""")
step1 = {r[0]: (float(r[1]), int(r[2]), int(r[3]) if r[3] else 0) for r in cur.fetchall()}
for y in YEARS:
    r,m,a = step1[y]
    print(f"  {y}: {r}억/월  MAU {m}만  ARPMAU {a:,}원")

# ---------- 2) Step 2: 분기별 매출 추이 ----------
print("\n"+"="*70)
print("[Step 2] 분기별 매출 (17분기)")
print("="*70)
cur.execute("""
WITH base AS (
  SELECT date, SUM(revenue_krw_100) AS m
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY date
)
SELECT EXTRACT(YEAR FROM date)::int AS y,
       EXTRACT(QUARTER FROM date)::int AS q,
       ROUND((AVG(m)/1e8)::numeric, 1) AS avg_eok
FROM base GROUP BY y, q ORDER BY y, q;
""")
q_data = [(f'{y}', f'Q{q}', float(v)) for y,q,v in cur.fetchall()]
for row in q_data: print(f"  {row[0]}-{row[1]}: {row[2]}억")

# ---------- 3) Step 3: 퍼블리셔별 월평균 매출 (전체 월수 기준) ----------
print("\n"+"="*70)
print("[Step 3] 퍼블리셔 그룹별 월평균 매출 + 점유율")
print("="*70)
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, unified_app_id,
         CASE
           WHEN publisher_name ILIKE '%NHN%' THEN 'NHN'
           WHEN publisher_name ILIKE '%NEOWIZ%' THEN '네오위즈'
           WHEN publisher_name ILIKE '%Zempot%' OR publisher_name ILIKE '%ZEMPOT%' THEN 'Zempot'
           ELSE '기타' END AS pub_grp,
         revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
)
SELECT yr, pub_grp, SUM(revenue_krw_100) AS rev_sum,
       COUNT(DISTINCT unified_app_id) AS n_apps
FROM base GROUP BY yr, pub_grp ORDER BY yr, pub_grp;
""")
s3 = {}
for yr, grp, rev, n in cur.fetchall():
    eok = float(rev)/1e8/YR_MONTHS[yr] if rev else 0
    s3.setdefault(yr,{})[grp] = {'eok': eok, 'games': n}

for y in YEARS:
    row = s3[y]
    total = sum(d['eok'] for d in row.values())
    print(f"\n  {y} (합계 {total:.1f}억):")
    for g in ['NHN','네오위즈','Zempot','기타']:
        d = row.get(g, {'eok':0,'games':0})
        share = d['eok']/total*100 if total else 0
        print(f"    {g:<8} {d['eok']:>6.1f}억 ({share:.1f}%) · {d['games']}게임")

# ---------- 4) Step 4: 대표 게임 8개 연도별 월평균 ----------
print("\n"+"="*70)
print("[Step 4] 대표 게임별 월평균 매출")
print("="*70)
GAMES = [
    ('한게임 포커',          ['한게임 포커'], '%NHN%'),
    ('한게임 섯다&맞고',     ['한게임 섯다'], '%NHN%'),
    ('한게임포커 클래식',    ['한게임포커 클래식','한게임 포커 클래식'], '%NHN%'),
    ('한게임 신맞고',        ['한게임 신맞고'], '%NHN%'),
    ('Pmang Poker',          ['Pmang Poker'], '%NEOWIZ%'),
    ('피망 뉴맞고',          ['피망 뉴맞고','Pmang Gostop'], '%NEOWIZ%'),
    ('WPL (윈조이 포커)',    ['WPL','윈조이 포커 리그'], '%Zempot%'),
    ('Yu-Gi-Oh! Master Duel',['Yu-Gi-Oh'], '%KONAMI%'),
]
step4 = {}
for name, pats, pub in GAMES:
    like = ' OR '.join(['name ILIKE %s'] * len(pats))
    sql = f"""
    WITH base AS (
      SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
             date, SUM(revenue_krw_100) AS m
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND genre IN ('Card','Casino','Board')
        AND publisher_name ILIKE %s AND ({like})
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
      GROUP BY yr, date
    )
    SELECT yr, SUM(m) FROM base GROUP BY yr ORDER BY yr;
    """
    cur.execute(sql, tuple([pub] + [f'%{p}%' for p in pats]))
    rows = {}
    for yr, tot in cur.fetchall():
        rows[yr] = float(tot)/1e8/YR_MONTHS[yr] if tot else 0
    step4[name] = rows
    print(f"  {name}: " + ' / '.join(f'{rows.get(y,0):.1f}' for y in YEARS))

# ---------- 5) Step 6: 연도별 순위별 TOP5 ----------
print("\n"+"="*70)
print("[Step 6] 연도별 TOP5 게임")
print("="*70)
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, os, unified_app_id, name, publisher_name, revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
per_app_yr AS (
  SELECT yr, unified_app_id, MAX(publisher_name) AS pub,
         SUM(revenue_krw_100) AS rev, COUNT(DISTINCT date) AS m
  FROM base GROUP BY yr, unified_app_id
),
rep_name AS (
  SELECT DISTINCT ON (yr, unified_app_id) yr, unified_app_id, name
  FROM base ORDER BY yr, unified_app_id,
      CASE WHEN os='android' THEN 0 ELSE 1 END, date DESC
),
ranked AS (
  SELECT p.yr, rn.name, p.pub, p.rev/NULLIF(p.m,0) AS m_avg,
         ROW_NUMBER() OVER (PARTITION BY p.yr ORDER BY p.rev DESC NULLS LAST) AS r
  FROM per_app_yr p JOIN rep_name rn USING (yr, unified_app_id)
  WHERE p.rev IS NOT NULL
)
SELECT yr, r, name, pub, ROUND((m_avg/1e8)::numeric, 1)
FROM ranked WHERE r<=5 ORDER BY yr, r;
""")
s6 = {}
for yr, r, name, pub, amt in cur.fetchall():
    s6.setdefault(yr,{})[int(r)] = (name, pub, float(amt))
for y in YEARS:
    print(f"\n  {y}:")
    for r in range(1,6):
        if r in s6[y]:
            n,p,a = s6[y][r]
            print(f"    {r}위 {a}억 {n[:25]} ({p[:15]})")

import json
out = {'step1':step1,'step2':q_data,'step3':s3,'step4':step4,'step6':s6}
with open(r'C:\Users\NHN\Documents\sensortower_api\scripts\webboard_refresh.json','w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)

cur.close(); conn.close()
print("\n[saved] webboard_refresh.json")
