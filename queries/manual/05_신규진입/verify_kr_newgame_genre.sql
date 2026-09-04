-- ============================================================
--  KR TOP100 신규 진입 — 퍼블국적 × 장르(RPG vs 비RPG) 연도별 진입 수
--  출처: verify/verify_kr_newgame_genre.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/2] ──────────────────────────
WITH first_entry AS (
  SELECT unified_app_id,
         MIN(date) AS first_date,
         (ARRAY_AGG(genre ORDER BY date))[1] AS genre0
  FROM dw_app_monthly
  WHERE country='KR'
    AND in_revenue_top100_unified_os=TRUE
    AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
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

-- ── [2/2] ──────────────────────────
WITH first_entry AS (
  SELECT unified_app_id,
         MIN(date) AS first_date,
         (ARRAY_AGG(genre ORDER BY date))[1] AS genre0
  FROM dw_app_monthly
  WHERE country='KR'
    AND in_revenue_top100_unified_os=TRUE
    AND (publisher_country IN ('China','Hong Kong','Taiwan','Macao','Macau') OR publisher_name ILIKE '%FUNFLY%')
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
