# -*- coding: utf-8 -*-
"""
신규 진입 탭 리디자인용 전체 데이터 추출 (OS 통합 + 25년 전후)
- Section 1: 국가별 3개월 생존율 (전/후 비교)
- Section 2: 국가별 생존 vs 미생존 광고집행률 (전/후)
- Section 3: 퍼블리셔 국적별 3개월 생존율 (전/후)
- Section 4: 퍼블리셔별 생존 vs 미생존 광고집행률 (전/후)
- Section 5: 국가별 M+1~M+12 잔존율 (전/후, OS 통합)
- Section 6: 퍼블리셔별 M+1~M+12 잔존율 (전/후, OS 통합)
"""
import psycopg2, json
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# ============================================================
# 공통 CTE: OS 통합 신규 진입 게임 추출
#   - in_revenue_top100_unified_os=TRUE 에 최초 진입한 월
#   - 1월 진입 제외 (전년도 잔류 혼입 방지)
#   - 진입월이 2022-02 ~ 2026-01 사이
# ============================================================
COMMON_CTE = """
WITH monthly AS (
    SELECT DISTINCT country, unified_app_id, date
    FROM dw_app_monthly
    WHERE in_revenue_top100_unified_os = TRUE
      AND country IN ('KR','JP','US')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
first_entry AS (
    SELECT country, unified_app_id, MIN(date) AS entry_date
    FROM monthly GROUP BY country, unified_app_id
),
new_entries AS (
    SELECT fe.country, fe.unified_app_id, fe.entry_date,
           CASE WHEN fe.entry_date < '2025-01-01' THEN 'before' ELSE 'after' END AS period
    FROM first_entry fe
    WHERE EXTRACT(MONTH FROM fe.entry_date) <> 1
      AND fe.entry_date >= '2022-02-01'
      AND fe.entry_date <= '2026-03-01'
)
"""

# ============================================================
# Section 1: 국가별 3개월 생존율 (전/후)
# ============================================================
sql1 = COMMON_CTE + """
, survival AS (
    SELECT ne.country, ne.period, ne.unified_app_id,
           EXISTS(
               SELECT 1 FROM monthly m
               WHERE m.country=ne.country AND m.unified_app_id=ne.unified_app_id
                 AND m.date = ne.entry_date + INTERVAL '3 months'
           ) AS survived
    FROM new_entries ne
    WHERE ne.entry_date + INTERVAL '3 months' <= '2026-03-01'
)
SELECT country, period, COUNT(*) AS total,
       SUM(CASE WHEN survived THEN 1 ELSE 0 END) AS surv,
       ROUND(SUM(CASE WHEN survived THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 1) AS rate
FROM survival GROUP BY country, period ORDER BY country, period;
"""
cur.execute(sql1)
s1 = cur.fetchall()
print("=== [Section 1] 국가별 3개월 생존율 (전/후, OS통합) ===")
print(f"{'국가':<6}{'기간':<10}{'진입':>6}{'생존':>6}{'생존율':>8}")
for country, period, total, surv, rate in s1:
    print(f"{country:<6}{period:<10}{total:>6}{surv:>6}{float(rate):>7.1f}%")

# ============================================================
# Section 2: 국가별 생존 vs 미생존 광고집행률 (전/후)
# 각 신규진입 게임의 진입후 3개월간 평균 paid_ratio
# ============================================================
sql2 = COMMON_CTE + """
, survival AS (
    SELECT ne.country, ne.period, ne.unified_app_id, ne.entry_date,
           EXISTS(
               SELECT 1 FROM monthly m
               WHERE m.country=ne.country AND m.unified_app_id=ne.unified_app_id
                 AND m.date = ne.entry_date + INTERVAL '3 months'
           ) AS survived
    FROM new_entries ne
    WHERE ne.entry_date + INTERVAL '3 months' <= '2026-03-01'
),
paid_per_game AS (
    SELECT s.country, s.period, s.survived, s.unified_app_id,
           AVG(d.paid_ratio) AS avg_paid
    FROM survival s
    JOIN dw_app_monthly d
      ON d.country=s.country
     AND d.unified_app_id=s.unified_app_id
     AND d.date BETWEEN s.entry_date AND s.entry_date + INTERVAL '3 months'
    WHERE d.paid_ratio IS NOT NULL
    GROUP BY s.country, s.period, s.survived, s.unified_app_id
)
SELECT country, period, survived,
       ROUND((AVG(avg_paid)*100)::numeric, 1) AS avg_paid_pct,
       COUNT(*) AS n
FROM paid_per_game GROUP BY country, period, survived
ORDER BY country, period, survived DESC;
"""
cur.execute(sql2)
s2 = cur.fetchall()
print("\n=== [Section 2] 국가별 생존/미생존 광고집행률 (전/후, OS통합) ===")
print(f"{'국가':<6}{'기간':<10}{'생존':<6}{'광고%':>8}{'n':>6}")
for country, period, survived, pct, n in s2:
    print(f"{country:<6}{period:<10}{'Y' if survived else 'N':<6}{float(pct):>7.1f}%{n:>6}")

# ============================================================
# Section 3: 퍼블리셔 국적별 3개월 생존율 (전/후)
# ============================================================
sql3 = COMMON_CTE + """
, pub_meta AS (
    SELECT DISTINCT ON (unified_app_id) unified_app_id, publisher_name, publisher_country
    FROM dw_app_monthly
    WHERE in_revenue_top100_unified_os=TRUE AND publisher_country IS NOT NULL
    ORDER BY unified_app_id, date DESC
),
grouped AS (
    SELECT ne.country, ne.period, ne.unified_app_id, ne.entry_date,
           CASE
               WHEN pm.publisher_name ILIKE '%NEXON%' THEN 'KR'
               WHEN pm.publisher_name ILIKE '%FUNFLY%' THEN '중화권'
               WHEN pm.publisher_country IN ('South Korea') THEN 'KR'
               WHEN pm.publisher_country IN ('Japan') THEN 'JP'
               WHEN pm.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
               WHEN pm.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
               ELSE '기타'
           END AS pub_grp
    FROM new_entries ne
    LEFT JOIN pub_meta pm ON pm.unified_app_id = ne.unified_app_id
    WHERE ne.entry_date + INTERVAL '3 months' <= '2026-03-01'
),
survival AS (
    SELECT g.*,
           EXISTS(
               SELECT 1 FROM monthly m
               WHERE m.country=g.country AND m.unified_app_id=g.unified_app_id
                 AND m.date = g.entry_date + INTERVAL '3 months'
           ) AS survived
    FROM grouped g
)
SELECT pub_grp, period, COUNT(*) AS total,
       SUM(CASE WHEN survived THEN 1 ELSE 0 END) AS surv,
       ROUND(SUM(CASE WHEN survived THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 1) AS rate
FROM survival WHERE pub_grp IS NOT NULL
GROUP BY pub_grp, period
ORDER BY pub_grp, period;
"""
cur.execute(sql3)
s3 = cur.fetchall()
print("\n=== [Section 3] 퍼블리셔 국적별 3개월 생존율 (전/후) ===")
print(f"{'그룹':<8}{'기간':<10}{'진입':>6}{'생존':>6}{'생존율':>8}")
for grp, period, total, surv, rate in s3:
    print(f"{grp:<8}{period:<10}{total:>6}{surv:>6}{float(rate):>7.1f}%")

# ============================================================
# Section 4: 퍼블리셔별 생존/미생존 광고집행률 (전/후)
# ============================================================
sql4 = COMMON_CTE + """
, pub_meta AS (
    SELECT DISTINCT ON (unified_app_id) unified_app_id, publisher_name, publisher_country
    FROM dw_app_monthly
    WHERE in_revenue_top100_unified_os=TRUE AND publisher_country IS NOT NULL
    ORDER BY unified_app_id, date DESC
),
grouped AS (
    SELECT ne.country, ne.period, ne.unified_app_id, ne.entry_date,
           CASE
               WHEN pm.publisher_name ILIKE '%NEXON%' THEN 'KR'
               WHEN pm.publisher_name ILIKE '%FUNFLY%' THEN '중화권'
               WHEN pm.publisher_country IN ('South Korea') THEN 'KR'
               WHEN pm.publisher_country IN ('Japan') THEN 'JP'
               WHEN pm.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
               WHEN pm.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
               ELSE '기타'
           END AS pub_grp
    FROM new_entries ne
    LEFT JOIN pub_meta pm ON pm.unified_app_id = ne.unified_app_id
    WHERE ne.entry_date + INTERVAL '3 months' <= '2026-03-01'
),
survival AS (
    SELECT g.*,
           EXISTS(
               SELECT 1 FROM monthly m
               WHERE m.country=g.country AND m.unified_app_id=g.unified_app_id
                 AND m.date = g.entry_date + INTERVAL '3 months'
           ) AS survived
    FROM grouped g
),
paid_per_game AS (
    SELECT s.pub_grp, s.period, s.survived, s.unified_app_id, s.country,
           AVG(d.paid_ratio) AS avg_paid
    FROM survival s
    JOIN dw_app_monthly d
      ON d.country=s.country AND d.unified_app_id=s.unified_app_id
     AND d.date BETWEEN s.entry_date AND s.entry_date + INTERVAL '3 months'
    WHERE d.paid_ratio IS NOT NULL AND s.pub_grp IS NOT NULL
    GROUP BY s.pub_grp, s.period, s.survived, s.unified_app_id, s.country
)
SELECT pub_grp, period, survived,
       ROUND((AVG(avg_paid)*100)::numeric, 1) AS pct,
       COUNT(*) AS n
FROM paid_per_game GROUP BY pub_grp, period, survived
ORDER BY pub_grp, period, survived DESC;
"""
cur.execute(sql4)
s4 = cur.fetchall()
print("\n=== [Section 4] 퍼블리셔별 생존/미생존 광고집행률 (전/후) ===")
print(f"{'그룹':<8}{'기간':<10}{'생존':<6}{'광고%':>8}{'n':>6}")
for grp, period, survived, pct, n in s4:
    print(f"{grp:<8}{period:<10}{'Y' if survived else 'N':<6}{float(pct):>7.1f}%{n:>6}")

# ============================================================
# Section 5: 국가별 M+1 ~ M+12 잔존율 (전/후, OS통합)
# ============================================================
print("\n=== [Section 5] 국가별 M+K 잔존율 (전/후, OS통합) ===")
retention_country = {}  # {country: {'before': [m+1..m+12], 'after': [...]}}
for country in ['KR','JP','US']:
    retention_country[country] = {'before': [], 'after': []}
    for period in ['before', 'after']:
        for k in range(1, 13):
            cur.execute(COMMON_CTE + """
            SELECT
                ROUND(SUM(CASE WHEN EXISTS(
                    SELECT 1 FROM monthly m
                    WHERE m.country=ne.country AND m.unified_app_id=ne.unified_app_id
                      AND m.date = ne.entry_date + (%s::int || ' months')::interval
                ) THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1) AS rate
            FROM new_entries ne
            WHERE ne.country=%s AND ne.period=%s
              AND ne.entry_date + (%s::int || ' months')::interval <= '2026-03-01';
            """, (k, country, period, k))
            rate = cur.fetchone()[0]
            retention_country[country][period].append(float(rate) if rate is not None else 0.0)
    print(f"  {country} before M+1~12: {retention_country[country]['before']}")
    print(f"  {country} after  M+1~12: {retention_country[country]['after']}")

# ============================================================
# Section 6: 퍼블리셔별 M+1 ~ M+12 잔존율 (전/후)
# ============================================================
print("\n=== [Section 6] 퍼블리셔별 M+K 잔존율 (전/후, OS통합) ===")
retention_pub = {}
for grp in ['KR','JP','중화권','북미']:
    retention_pub[grp] = {'before': [], 'after': []}
    for period in ['before', 'after']:
        for k in range(1, 13):
            cur.execute(COMMON_CTE + """
            , pub_meta AS (
                SELECT DISTINCT ON (unified_app_id) unified_app_id, publisher_name, publisher_country
                FROM dw_app_monthly
                WHERE in_revenue_top100_unified_os=TRUE AND publisher_country IS NOT NULL
                ORDER BY unified_app_id, date DESC
            ),
            grouped AS (
                SELECT ne.*, CASE
                   WHEN pm.publisher_name ILIKE '%%NEXON%%' THEN 'KR'
                   WHEN pm.publisher_name ILIKE '%%FUNFLY%%' THEN '중화권'
                   WHEN pm.publisher_country IN ('South Korea') THEN 'KR'
                   WHEN pm.publisher_country IN ('Japan') THEN 'JP'
                   WHEN pm.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
                   WHEN pm.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
                   ELSE '기타' END AS pub_grp
                FROM new_entries ne
                LEFT JOIN pub_meta pm ON pm.unified_app_id = ne.unified_app_id
            )
            SELECT
                ROUND(SUM(CASE WHEN EXISTS(
                    SELECT 1 FROM monthly m
                    WHERE m.country=g.country AND m.unified_app_id=g.unified_app_id
                      AND m.date = g.entry_date + (%s::int || ' months')::interval
                ) THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100, 1)
            FROM grouped g
            WHERE g.pub_grp=%s AND g.period=%s
              AND g.entry_date + (%s::int || ' months')::interval <= '2026-03-01';
            """, (k, grp, period, k))
            rate = cur.fetchone()[0]
            retention_pub[grp][period].append(float(rate) if rate is not None else 0.0)
    print(f"  {grp} before: {retention_pub[grp]['before']}")
    print(f"  {grp} after:  {retention_pub[grp]['after']}")

# 저장
out = {
    'section1': [{'country':c,'period':p,'total':t,'surv':s,'rate':float(r)} for c,p,t,s,r in s1],
    'section2': [{'country':c,'period':p,'survived':sv,'pct':float(pc),'n':n} for c,p,sv,pc,n in s2],
    'section3': [{'pub_grp':g,'period':p,'total':t,'surv':s,'rate':float(r)} for g,p,t,s,r in s3],
    'section4': [{'pub_grp':g,'period':p,'survived':sv,'pct':float(pc),'n':n} for g,p,sv,pc,n in s4],
    'section5': retention_country,
    'section6': retention_pub,
}
with open(r'C:\Users\NHN\Documents\sensortower_api\scripts\newgame_data_v2.json','w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n[저장] newgame_data_v2.json")
cur.close(); conn.close()
