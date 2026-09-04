-- ============================================================
--  Step 3 퍼블리셔별 월평균 매출/점유율 불일치 진단
--  출처: verify/check_publisher_share.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/2] ──────────────────────────
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
monthly AS (SELECT yr, date, SUM(revenue_krw_100) AS m FROM base GROUP BY yr, date)
SELECT yr, ROUND((AVG(m)/1e8)::numeric, 1) AS total_eok
FROM monthly GROUP BY yr ORDER BY yr;

-- ── [2/2] ──────────────────────────
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date,
        CASE
            WHEN publisher_name ILIKE '%NHN%' THEN 'NHN'
            WHEN publisher_name ILIKE '%NEOWIZ%' THEN '네오위즈'
            WHEN publisher_name ILIKE '%Zempot%' OR publisher_name ILIKE '%ZEMPOT%' THEN 'Zempot'
            ELSE '기타'
        END AS pub_grp,
        revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
monthly AS (SELECT yr, pub_grp, date, SUM(revenue_krw_100) AS m FROM base GROUP BY yr, pub_grp, date)
SELECT yr, pub_grp, ROUND((AVG(m)/1e8)::numeric, 1) AS eok
FROM monthly GROUP BY yr, pub_grp ORDER BY yr, pub_grp;
