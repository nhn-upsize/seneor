-- ============================================================
--  웹보드 Step 1~4 종합 재검증 (Disney Solitaire 제외)
--  출처: verify/verify_wb_all4.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1),
       COUNT(DISTINCT unified_app_id)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND publisher_name ILIKE '%NHN%'

-- ── [2/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1),
       COUNT(DISTINCT unified_app_id)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND publisher_name NOT ILIKE '%NHN%' AND publisher_name NOT ILIKE '%NEOWIZ%' AND publisher_name NOT ILIKE '%Zempot%'

-- ── [3/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%' AND date >= '2022-01-01' AND date < '2023-01-01'

-- ── [4/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '한게임 포커%' AND name NOT ILIKE '%클래식%')

-- ── [5/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '한게임 섯다%')

-- ── [6/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '한게임포커 클래식%' OR name ILIKE '한게임 포커 클래식%')

-- ── [7/12] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 1)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '피망 뉴맞고%' OR name ILIKE '피망 맞고%' OR name ILIKE '피망 섯다고%')

-- ── [8/12] ──────────────────────────
WITH mo AS (
  SELECT date, SUM(mau) u, SUM(units) d
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%' AND date >= '2022-01-01' AND date < '2023-01-01'
  GROUP BY date
)
SELECT ROUND(AVG(u)/10000.0, 0), ROUND(AVG(d)/10000.0, 1)
FROM mo

-- ── [9/12] ──────────────────────────
SELECT ROUND(AVG(male_pct)::numeric, 1), ROUND(AVG(female_pct)::numeric, 1),
       COUNT(DISTINCT date)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '한게임 포커%' AND name NOT ILIKE '%클래식%')
  AND male_pct IS NOT NULL

-- ── [10/12] ──────────────────────────
SELECT ROUND(AVG(male_pct)::numeric, 1), ROUND(AVG(female_pct)::numeric, 1),
       COUNT(DISTINCT date)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '한게임 섯다%')
  AND male_pct IS NOT NULL

-- ── [11/12] ──────────────────────────
SELECT ROUND(AVG(male_pct)::numeric, 1), ROUND(AVG(female_pct)::numeric, 1),
       COUNT(DISTINCT date)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '한게임포커 클래식%' OR name ILIKE '한게임 포커 클래식%')
  AND male_pct IS NOT NULL

-- ── [12/12] ──────────────────────────
SELECT ROUND(AVG(male_pct)::numeric, 1), ROUND(AVG(female_pct)::numeric, 1),
       COUNT(DISTINCT date)
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND genre IN ('Card','Casino','Board') AND name NOT ILIKE '%Disney Solitaire%'
  AND date >= '2022-01-01' AND date < '2023-01-01' AND (name ILIKE '피망 뉴맞고%' OR name ILIKE '피망 맞고%' OR name ILIKE '피망 섯다고%')
  AND male_pct IS NOT NULL
