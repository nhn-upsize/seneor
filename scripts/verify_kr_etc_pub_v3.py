# -*- coding: utf-8 -*-
"""퍼블리셔 이름 정규화 후 정확한 기타 KR 퍼블 개수"""
import psycopg2, re

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

TOP5_COND = """publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%'
OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%'
OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%'"""

def normalize(name):
    """퍼블리셔 이름 정규화"""
    n = name.upper()
    # 꼬리 접미사 제거
    n = re.sub(r"\b(CO\.?\s*,?\s*LTD\.?|CORP\.?|INC\.?|CORPORATION|LTD\.?|STUDIO|\(.*\)|CO\.?)\s*$", "", n).strip()
    n = re.sub(r"\s*,\s*$", "", n).strip()
    n = re.sub(r"[.,]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

print(f"\n{'연도':<8}{'raw 퍼블수':<14}{'정규화 후 퍼블수':<18}{'게임수':<10}")
for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"
    cur.execute(f"""
    SELECT DISTINCT publisher_name, unified_app_id
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {df}
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT ({TOP5_COND})
    """)
    rows = cur.fetchall()
    raw_pubs = set(r[0] for r in rows)
    norm_pubs = set(normalize(r[0]) for r in rows)
    games = set(r[1] for r in rows)
    print(f"{yr:<8}{len(raw_pubs):<14}{len(norm_pubs):<18}{len(games):<10}")

# 25년 정규화된 최종 리스트
print("\n=== 25년 정규화된 기타 KR 퍼블리셔 (실제 독립 퍼블) ===")
cur.execute(f"""
SELECT DISTINCT publisher_name, unified_app_id, name
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2025-01-01' AND date < '2026-01-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
  AND NOT ({TOP5_COND})
""")
rows = cur.fetchall()
grouped = {}
for pname, aid, game_name in rows:
    norm = normalize(pname)
    grouped.setdefault(norm, {'games':set(), 'raw_names':set()})
    grouped[norm]['games'].add(game_name)
    grouped[norm]['raw_names'].add(pname)

sorted_list = sorted(grouped.items(), key=lambda x: (-len(x[1]['games']), x[0]))
for i, (norm, info) in enumerate(sorted_list, 1):
    raws = ' | '.join(sorted(info['raw_names']))
    games = ', '.join(sorted(info['games'])[:3])
    print(f"  {i:>2}. {norm} ({len(info['games'])}게임) [{raws}]")
print(f"\n총 {len(grouped)}개 정규화 퍼블리셔")

conn.close()
