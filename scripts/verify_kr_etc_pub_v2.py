# -*- coding: utf-8 -*-
"""KR TOP100 내 한국 퍼블리셔 — TOP5 제외한 중소 퍼블의 정확한 개수
unified_os=TRUE 기준 (iOS+Android 합산)
'게임수' = 해당 연도에 TOP100 진입한 고유 unified_app_id 개수
'퍼블수' = 해당 연도에 TOP100 진입한 고유 publisher_name 개수
"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# TOP5 퍼블리셔 이름 패턴 (통합된 이름들)
TOP5_PATTERNS = [
    "publisher_name ILIKE '%NCSOFT%'",
    "publisher_name ILIKE '%NC Corp%'",
    "publisher_name ILIKE '%NEXON%'",
    "publisher_name ILIKE '%Netmarble%'",
    "publisher_name ILIKE '%Kakao Games%'",
    "publisher_name ILIKE '%NHN%'",
]
TOP5_COND = ' OR '.join(TOP5_PATTERNS)

YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

print(f"\n{'연도':<8}{'전체 KR':<12}{'TOP5 퍼블수':<14}{'기타 KR 퍼블수':<18}{'기타 KR 게임수':<18}")
for yr, months in YR_MONTHS.items():
    if yr == '26.1Q':
        df = "date >= '2026-01-01' AND date < '2026-04-01'"
    else:
        df = f"date >= '{yr}-01-01' AND date < '{int(yr)+1}-01-01'"

    # 기타 KR (TOP5 외)
    cur.execute(f"""
    SELECT COUNT(DISTINCT publisher_name) pub_cnt,
           COUNT(DISTINCT unified_app_id) game_cnt
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {df}
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT ({TOP5_COND})
    """)
    etc = cur.fetchone()

    # 전체 KR 퍼블 수
    cur.execute(f"""
    SELECT COUNT(DISTINCT publisher_name)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {df}
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
    """)
    total_kr_pub = cur.fetchone()[0]

    # TOP5 퍼블 수
    cur.execute(f"""
    SELECT COUNT(DISTINCT publisher_name)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND {df}
      AND ({TOP5_COND})
    """)
    top5_cnt = cur.fetchone()[0]

    print(f"{yr:<8}{total_kr_pub:<12}{top5_cnt:<14}{etc[0]:<18}{etc[1]:<18}")

# 실제 기타 KR 퍼블리셔 이름 목록 (25년)
print("\n=== 25년 기타 KR 퍼블리셔 전체 목록 ===")
cur.execute(f"""
SELECT publisher_name, COUNT(DISTINCT unified_app_id) game_cnt
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2025-01-01' AND date < '2026-01-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
  AND NOT ({TOP5_COND})
GROUP BY publisher_name
ORDER BY game_cnt DESC, publisher_name
""")
rows = cur.fetchall()
for i, (name, cnt) in enumerate(rows, 1):
    print(f"  {i:>3}. {name} ({cnt}게임)")
print(f"\n총 {len(rows)}개 퍼블리셔")

conn.close()
