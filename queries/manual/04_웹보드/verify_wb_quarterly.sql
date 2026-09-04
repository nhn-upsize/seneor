-- ============================================================
--  KR 웹보드 분기별 매출 검증 — Card+Casino+Board 통합 · TOP100 unified_os
--  출처: verify/verify_wb_quarterly.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/3] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/3, 0)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  AND date >= '2022-01-01' AND date < '2022-04-01'

-- ── [2/3] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  AND date = '2022-01-01'

-- ── [3/3] ──────────────────────────
SELECT name, unified_app_id FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board')
  AND date >= '2022-01-01' AND date < '2023-01-01'
  AND (name ILIKE '%한게임%' OR name ILIKE '%섯다%' OR name ILIKE '%포커클래식%'
       OR name ILIKE '%피망%' OR name ILIKE '%윈조이%' OR name ILIKE '%WPL%')
GROUP BY name, unified_app_id
ORDER BY name
