-- ============================================================
--  KR Strategy / 중화권 Strategy / KR MMORPG 연도별 월평균 매출 검증
--  출처: verify/verify_kr_strategy.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/2] ──────────────────────────
SELECT DISTINCT publisher_country, COUNT(*) cnt
FROM dw_app_monthly
WHERE country='KR' AND genre ILIKE '%strategy%'
  AND in_revenue_top100_unified_os=TRUE
GROUP BY publisher_country ORDER BY cnt DESC LIMIT 20

-- ── [2/2] ──────────────────────────
SELECT DISTINCT genre, COUNT(*) cnt
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
GROUP BY genre ORDER BY cnt DESC LIMIT 20
