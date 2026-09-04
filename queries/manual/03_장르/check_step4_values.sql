-- ============================================================
--  Step 4 대표 게임 8개의 월평균 매출 — 연도 전체 월수 기준으로 재계산
--  출처: verify/check_step4_values.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/1] ──────────────────────────
SELECT unified_app_id, name, publisher_name
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND name ILIKE %s AND publisher_name ILIKE %s
  AND date BETWEEN '2022-01-01' AND '2026-03-01'
GROUP BY unified_app_id, name, publisher_name
ORDER BY COUNT(*) DESC LIMIT 1
