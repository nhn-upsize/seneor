# -*- coding: utf-8 -*-
import psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 1) Zempot / WPL 찾기 — 26.1Q
cur.execute("""
SELECT date, country, os, name, publisher_name, revenue_krw_100,
       in_revenue_top100_unified_os, genre
FROM dw_app_monthly
WHERE country='KR'
  AND (publisher_name ILIKE '%Zempot%' OR name ILIKE '%WPL%' OR name ILIKE '%윈조이%')
  AND date >= '2026-01-01'
ORDER BY date, os;
""")
print("[WPL/Zempot 검색]")
for r in cur.fetchall():
    print(f"  {r[0]} {r[1]}/{r[2]:<7} {str(r[3])[:35]:<35}  {str(r[4])[:20]:<20}  rev={r[5]}  unified={r[6]}  genre={r[7]}")

# 2) 한게임포커 클래식 OS별
print("\n[한게임포커 클래식 26.1Q OS별]")
cur.execute("""
SELECT date, os, name, revenue_krw_100, in_revenue_top100_unified_os
FROM dw_app_monthly
WHERE country='KR'
  AND name ILIKE '%클래식%' AND publisher_name='NHN Corp.'
  AND date >= '2026-01-01'
ORDER BY date, os;
""")
for r in cur.fetchall():
    print(f"  {r[0]} {r[1]:<8} {str(r[2])[:40]:<40}  rev={r[3]}  unified={r[4]}")

cur.close(); conn.close()
