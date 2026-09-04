-- ============================================================
--  SELECT date, country, os, name, publisher_name, revenue_krw_100,
--  출처: verify/query_wpl_check.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/2] ──────────────────────────
SELECT date, country, os, name, publisher_name, revenue_krw_100,
       in_revenue_top100_unified_os, genre
FROM dw_app_monthly
WHERE country='KR'
  AND (publisher_name ILIKE '%Zempot%' OR name ILIKE '%WPL%' OR name ILIKE '%윈조이%')
  AND date >= '2026-01-01'
ORDER BY date, os;

-- ── [2/2] ──────────────────────────
SELECT date, os, name, revenue_krw_100, in_revenue_top100_unified_os
FROM dw_app_monthly
WHERE country='KR'
  AND name ILIKE '%클래식%' AND publisher_name='NHN Corp.'
  AND date >= '2026-01-01'
ORDER BY date, os;
