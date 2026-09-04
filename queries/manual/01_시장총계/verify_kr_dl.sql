-- ============================================================
--  SELECT ROUND(SUM(units)/10000.0/{months}, 0)
--  출처: verify/verify_kr_dl.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/1] ──────────────────────────
SELECT ROUND(SUM(units)/10000.0/12, 0)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE AND date >= '2022-01-01' AND date < '2023-01-01'
