-- ============================================================
--  KR 기타 KR 퍼블 게임수 — 기존 표의 '22게임' 기준 vs DB 조회값 대조
--  출처: verify/verify_kr_etc_game_count.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/3] ──────────────────────────
SELECT COUNT(DISTINCT unified_app_id)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND date >= '2022-01-01' AND date < '2023-01-01'
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%'
OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%'
OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%')

-- ── [2/3] ──────────────────────────
WITH monthly AS (
      SELECT date, COUNT(DISTINCT unified_app_id) cnt
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND date >= '2022-01-01' AND date < '2023-01-01'
        AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
        AND NOT (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%'
OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%'
OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%')
      GROUP BY date
    )
    SELECT ROUND(AVG(cnt), 0), MIN(cnt), MAX(cnt)
    FROM monthly

-- ── [3/3] ──────────────────────────
SELECT COUNT(DISTINCT unified_app_id)
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND date = '2022-06-01'
      AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
      AND NOT (publisher_name ILIKE '%NCSOFT%' OR publisher_name ILIKE '%NC Corp%'
OR publisher_name ILIKE '%NEXON%' OR publisher_name ILIKE '%Netmarble%'
OR publisher_name ILIKE '%Kakao Games%' OR publisher_name ILIKE '%NHN%')
