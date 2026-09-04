-- ============================================================
--  Webboard 분석용 데이터 조회:
--  출처: verify/query_webboard_data.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/2] ──────────────────────────
WITH base AS (
    SELECT
        CASE
            WHEN date >= '2026-01-01' THEN '26.1Q'
            ELSE TO_CHAR(date, 'YYYY')
        END AS yr,
        date,
        units
    FROM dw_app_monthly
    WHERE country = 'KR'
      AND in_revenue_top100_unified_os = TRUE
      AND genre IN ('Card', 'Casino', 'Board')
      AND date >= '2022-01-01'
      AND date <= '2026-03-01'
),
monthly_sum AS (
    SELECT yr, date, SUM(units) AS monthly_units
    FROM base
    GROUP BY yr, date
)
SELECT yr,
       ROUND(AVG(monthly_units)::numeric / 10000.0, 1) AS monthly_avg_units_10k
FROM monthly_sum
GROUP BY yr
ORDER BY yr;

-- ── [2/2] ──────────────────────────
WITH base AS (
    SELECT
        CASE
            WHEN date >= '2026-01-01' THEN '26.1Q'
            ELSE TO_CHAR(date, 'YYYY')
        END AS yr,
        date, os, unified_app_id, name, publisher_name, revenue_krw_100
    FROM dw_app_monthly
    WHERE country = 'KR'
      AND in_revenue_top100_unified_os = TRUE
      AND genre IN ('Card', 'Casino', 'Board')
      AND date >= '2022-01-01'
      AND date <= '2026-03-01'
),
-- unified_app_id 기준으로 OS 통합 (android+ios 이름이 달라도 같은 앱)
per_app_yr AS (
    SELECT yr, unified_app_id,
           MAX(publisher_name) AS publisher_name,
           SUM(revenue_krw_100) AS rev_sum,
           COUNT(DISTINCT date) AS months
    FROM base
    GROUP BY yr, unified_app_id
),
-- 대표 이름: android 우선 (없으면 ios)
rep_name AS (
    SELECT DISTINCT ON (yr, unified_app_id)
           yr, unified_app_id, name
    FROM base
    ORDER BY yr, unified_app_id,
             CASE WHEN os='android' THEN 0 ELSE 1 END,
             date DESC
),
per_app_monthly AS (
    SELECT p.yr, p.unified_app_id, rn.name, p.publisher_name,
           p.rev_sum / NULLIF(p.months, 0) AS monthly_avg_krw
    FROM per_app_yr p
    JOIN rep_name rn USING (yr, unified_app_id)
),
ranked AS (
    SELECT yr, name, publisher_name, monthly_avg_krw,
           ROW_NUMBER() OVER (PARTITION BY yr ORDER BY monthly_avg_krw DESC NULLS LAST) AS rnk
    FROM per_app_monthly
    WHERE monthly_avg_krw IS NOT NULL
)
SELECT yr, rnk, name, publisher_name,
       ROUND((monthly_avg_krw / 1e8)::numeric, 1) AS monthly_avg_eok
FROM ranked
WHERE rnk <= 5
ORDER BY yr, rnk;
