# -*- coding: utf-8 -*-
"""임원 보고용 인사이트 데이터 수집"""
import psycopg2, json

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 1) KR TOP 5 퍼블리셔 매출 변화 (전후)
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date<'2025-01-01' THEN 'b' ELSE 'a' END AS p,
         date, publisher_name, revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
    AND (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NEXON%'
         OR publisher_name ILIKE '%Netmarble%' OR publisher_name ILIKE '%Kakao Games%'
         OR publisher_name ILIKE '%NHN%')
),
pub_norm AS (
  SELECT p, date,
    CASE
      WHEN publisher_name ILIKE '%NCSOFT%' THEN '엔씨소프트'
      WHEN publisher_name ILIKE '%NEXON%' THEN '넥슨'
      WHEN publisher_name ILIKE '%Netmarble%' THEN '넷마블'
      WHEN publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%KAKAO GAMES%' THEN '카카오게임즈'
      WHEN publisher_name ILIKE '%NHN%' THEN 'NHN'
    END AS pub_norm,
    revenue_krw_100 AS rev
  FROM base
),
monthly AS (
  SELECT p, date, pub_norm, SUM(rev) AS m FROM pub_norm GROUP BY p, date, pub_norm
)
SELECT p, pub_norm, ROUND((AVG(m)/1e8)::numeric, 0)
FROM monthly GROUP BY p, pub_norm ORDER BY pub_norm, p
""")
kr_top5 = {}
for p, pub, v in cur.fetchall():
    kr_top5.setdefault(pub, {})[p] = float(v) if v else 0
print("[KR TOP5 퍼블] 전/후 월평균 매출 (억)")
for pub, d in kr_top5.items():
    b = d.get('b',0); a = d.get('a',0)
    diff = a-b; pct = (diff/b*100) if b else 0
    print(f"  {pub}: {b:.0f}억 → {a:.0f}억  (Δ{diff:+.0f}, {pct:+.0f}%)")

# 2) KR 중화권 매출 절대값 / 점유율 / 대표 게임
cur.execute("""
WITH kr_total AS (
  SELECT CASE WHEN date<'2025-01-01' THEN 'b' ELSE 'a' END AS p, date,
         SUM(revenue_krw_100) AS tot
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY p, date
),
kr_cn AS (
  SELECT CASE WHEN date<'2025-01-01' THEN 'b' ELSE 'a' END AS p, date,
         SUM(revenue_krw_100) AS cn
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND (publisher_name ILIKE '%FUNFLY%' OR
         publisher_country IN ('China','Hong Kong','Taiwan','Macao'))
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY p, date
)
SELECT kt.p, ROUND((AVG(kt.tot)/1e8)::numeric, 0) AS total,
       ROUND((AVG(kc.cn)/1e8)::numeric, 0) AS cn_only
FROM kr_total kt LEFT JOIN kr_cn kc USING(p, date)
GROUP BY kt.p ORDER BY kt.p
""")
print("\n[KR 중화권 매출]")
for p, t, cn in cur.fetchall():
    print(f"  {p}: 전체 {t}억, 중화권 {cn}억 ({cn/t*100:.1f}%)")

# 3) 중화권 대표 Survival 게임 (Last War/Whiteout 등)
cur.execute("""
SELECT name, publisher_name, SUM(revenue_krw_100)/1e8 AS rev
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date BETWEEN '2025-01-01' AND '2026-03-01'
  AND (publisher_name ILIKE '%FUNFLY%' OR
       publisher_country IN ('China','Hong Kong','Taiwan','Macao'))
GROUP BY name, publisher_name
ORDER BY rev DESC LIMIT 10
""")
print("\n[KR 25~26.1Q 중화권 Top 10]")
for n, p, v in cur.fetchall():
    v_f = float(v) if v else 0
    print(f"  {(n or '-')[:35]:<37}  {(p or '-')[:20]:<22}  {v_f:>6.0f}억")

# 4) JP 자국 퍼블 하락 — 대표 게임 (전후 가장 큰 하락)
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date<'2025-01-01' THEN 'b' ELSE 'a' END AS p,
         date, name, publisher_name, revenue_krw_100
  FROM dw_app_monthly
  WHERE country='JP' AND in_revenue_top100_unified_os=TRUE
    AND publisher_country='Japan'
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
monthly AS (
  SELECT p, name, publisher_name, date, SUM(revenue_krw_100) AS m
  FROM base GROUP BY p, name, publisher_name, date
),
avg_by_period AS (
  SELECT name, publisher_name, p, AVG(m) AS avg_rev
  FROM monthly GROUP BY name, publisher_name, p
)
SELECT name, publisher_name,
  MAX(CASE WHEN p='b' THEN avg_rev END)/1e8 AS before_eok,
  MAX(CASE WHEN p='a' THEN avg_rev END)/1e8 AS after_eok
FROM avg_by_period
GROUP BY name, publisher_name
HAVING MAX(CASE WHEN p='b' THEN avg_rev END) IS NOT NULL
   AND MAX(CASE WHEN p='a' THEN avg_rev END) IS NOT NULL
ORDER BY (MAX(CASE WHEN p='a' THEN avg_rev END) - MAX(CASE WHEN p='b' THEN avg_rev END))
LIMIT 10
""")
print("\n[JP 자국 퍼블 25년 전후 매출 감소 TOP 10]")
for n, p, b, a in cur.fetchall():
    b_f = float(b or 0); a_f = float(a or 0)
    print(f"  {n[:30]:<32}  {p[:18]:<20}  {b_f:.0f}→{a_f:.0f}억 (Δ{a_f-b_f:+.0f})")

# 5) US MONOPOLY GO! 같은 메가히트 확인
cur.execute("""
SELECT name, publisher_name,
  AVG(CASE WHEN date<'2025-01-01' THEN revenue_krw_100 END)/1e8 AS b,
  AVG(CASE WHEN date>='2025-01-01' THEN revenue_krw_100 END)/1e8 AS a
FROM dw_app_monthly
WHERE country='US' AND in_revenue_top100_unified_os=TRUE
  AND date BETWEEN '2022-01-01' AND '2026-03-01'
GROUP BY name, publisher_name
HAVING AVG(revenue_krw_100)/1e8 > 500
ORDER BY a DESC NULLS LAST LIMIT 10
""")
print("\n[US TOP 10 (전후 매출 높은 순)]")
for n, p, b, a in cur.fetchall():
    b_f = float(b or 0); a_f = float(a or 0)
    print(f"  {n[:30]:<32}  {p[:18]:<20}  {b_f:.0f}→{a_f:.0f}억")

cur.close(); conn.close()
