-- ============================================================
--  KR 웹보드 (Disney Solitaire 제외) 분기별·연도별 매출 재검증
--  출처: verify/verify_wb_exclude_disney.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/1] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/3, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2022-04-01'
