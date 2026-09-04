-- ============================================================
--  KR TOP100 내 한국 퍼블리셔 — TOP5 제외한 중소 퍼블의 정확한 개수
--  출처: verify/verify_kr_etc_pub_v2.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/4] ──────────────────────────
SELECT COUNT(DISTINCT publisher_name) pub_cnt,
       COUNT(DISTINCT unified_app_id) game_cnt
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2022-01-01' AND date < '2023-01-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
  AND NOT (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%' OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%' OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%')

-- ── [2/4] ──────────────────────────
SELECT COUNT(DISTINCT publisher_name)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2022-01-01' AND date < '2023-01-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')

-- ── [3/4] ──────────────────────────
SELECT COUNT(DISTINCT publisher_name)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2022-01-01' AND date < '2023-01-01'
  AND (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%' OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%' OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%')

-- ── [4/4] ──────────────────────────
SELECT publisher_name, COUNT(DISTINCT unified_app_id) game_cnt
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2025-01-01' AND date < '2026-01-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
  AND NOT (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%' OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%' OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%')
GROUP BY publisher_name
ORDER BY game_cnt DESC, publisher_name
