# -*- coding: utf-8 -*-
"""웹보드 Step 1~4 종합 재검증 (Disney Solitaire 제외)"""
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

EX = "AND name NOT ILIKE '%Disney Solitaire%'"

# =====================================================
# 1. 퍼블리셔별 연도별 매출 (NHN / 네오위즈 / Zempot / 기타)
# =====================================================
print("="*70)
print("Step 3: 퍼블리셔별 월평균 매출 (Disney 제외)")
print("="*70)

pub_groups = [
    ('NHN',      "publisher_name ILIKE '%NHN%'"),
    ('네오위즈',   "publisher_name ILIKE '%NEOWIZ%'"),
    ('Zempot',  "publisher_name ILIKE '%Zempot%'"),
    ('기타',     "publisher_name NOT ILIKE '%NHN%' AND publisher_name NOT ILIKE '%NEOWIZ%' AND publisher_name NOT ILIKE '%Zempot%'"),
]

YR = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

for gname, cond in pub_groups:
    print(f"\n{gname}:")
    for yr, m in YR.items():
        if yr == '26.1Q':
            df = "date >= '2026-01-01' AND date < '2026-04-01'"
        else:
            df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
        cur.execute(f"""
        SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 1),
               COUNT(DISTINCT unified_app_id)
        FROM dw_app_monthly
        WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
          AND genre IN ('Card','Casino','Board') {EX}
          AND {df} AND {cond}
        """)
        r = cur.fetchone()
        v, cnt = (r[0] or 0), (r[1] or 0)
        print(f"  {yr}: {v:,.1f}억 ({cnt}게임)")

# 전체 합계
print("\n전체 웹보드 합계:")
for yr, m in YR.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 1)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board') {EX} AND {df}
    """)
    v = cur.fetchone()[0] or 0
    print(f"  {yr}: {v:,.1f}억")

# =====================================================
# 2. 게임별 월평균 매출 (Step 4 7게임 기준)
# =====================================================
print("\n" + "="*70)
print("Step 4: 게임별 월평균 매출")
print("="*70)

games = [
    ('한게임 포커',          "name ILIKE '한게임 포커%' AND name NOT ILIKE '%클래식%'"),
    ('한게임 섯다&맞고',     "name ILIKE '한게임 섯다%'"),
    ('한게임포커 클래식',     "name ILIKE '한게임포커 클래식%' OR name ILIKE '한게임 포커 클래식%'"),
    ('한게임 신맞고',        "name ILIKE '한게임 신맞고%' OR name ILIKE '한게임 맞고%'"),
    ('Pmang Poker',       "name ILIKE 'Pmang Poker%' OR name ILIKE '피망 포커%'"),
    ('피망 뉴맞고',          "name ILIKE '피망 뉴맞고%' OR name ILIKE '피망 맞고%' OR name ILIKE '피망 섯다고%'"),
    ('WPL',               "name ILIKE 'WPL%'"),
]

for gname, cond in games:
    print(f"\n{gname}:")
    for yr, m in YR.items():
        if yr == '26.1Q':
            df = "date >= '2026-01-01' AND date < '2026-04-01'"
        else:
            df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
        cur.execute(f"""
        SELECT ROUND(SUM(revenue_krw_100)/100000000.0/{m}, 1)
        FROM dw_app_monthly
        WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
          AND genre IN ('Card','Casino','Board') {EX}
          AND {df} AND ({cond})
        """)
        v = cur.fetchone()[0] or 0
        print(f"  {yr}: {v:,.1f}")

# =====================================================
# 3. MAU / DL 연도별 재검증 (앱 합산 기준)
# =====================================================
print("\n" + "="*70)
print("Step 1: MAU / DL 연도별 재검증")
print("="*70)

# 방법 A: 월별 앱 합산 후 월평균
# 방법 B: 연도 누적 / 월수
print("\n방법 A: 월별 앱 합산 → 월평균")
for yr, m in YR.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    WITH mo AS (
      SELECT date, SUM(mau) u, SUM(units) d
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND genre IN ('Card','Casino','Board') {EX} AND {df}
      GROUP BY date
    )
    SELECT ROUND(AVG(u)/10000.0, 0), ROUND(AVG(d)/10000.0, 1)
    FROM mo
    """)
    r = cur.fetchone()
    print(f"  {yr}: MAU {r[0] or 0:,.0f}만 · DL {r[1] or 0:,.1f}만")

# =====================================================
# 4. 7게임별 남/녀 비중 연도별
# =====================================================
print("\n" + "="*70)
print("Step 4: 7게임 × 연도별 남/녀 비중")
print("="*70)

wb_games_cond = """(
  name ILIKE '한게임 포커%' OR name ILIKE '한게임 섯다%' OR
  name ILIKE '한게임포커 클래식%' OR name ILIKE '한게임 포커 클래식%' OR
  name ILIKE '한게임 신맞고%' OR name ILIKE '한게임 맞고%' OR
  name ILIKE 'Pmang Poker%' OR name ILIKE '피망 포커%' OR
  name ILIKE '피망 뉴맞고%' OR name ILIKE '피망 맞고%' OR name ILIKE '피망 섯다고%' OR
  name ILIKE 'WPL%'
)"""

for gname, cond in games:
    print(f"\n{gname}:")
    for yr, m in YR.items():
        if yr == '26.1Q':
            df = "date >= '2026-01-01' AND date < '2026-04-01'"
        else:
            df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
        # 월별 유저 가중 평균
        cur.execute(f"""
        SELECT ROUND(AVG(male_pct)::numeric, 1), ROUND(AVG(female_pct)::numeric, 1),
               COUNT(DISTINCT date)
        FROM dw_app_monthly
        WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
          AND genre IN ('Card','Casino','Board') {EX}
          AND {df} AND ({cond})
          AND male_pct IS NOT NULL
        """)
        r = cur.fetchone()
        mp, fp, n = r[0] or 0, r[1] or 0, r[2] or 0
        print(f"  {yr}: 남 {mp}% · 여 {fp}% (n={n})")

conn.close()
