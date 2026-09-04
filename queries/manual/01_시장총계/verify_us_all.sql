-- ============================================================
--  US 시장 전체 수치 검증
--  출처: verify/verify_us_all.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                    FROM dw_app_monthly
                    WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND date >= '2022-01-01' AND date < '2023-01-01'

-- ── [2/10] ──────────────────────────
WITH mo AS (SELECT date, SUM(mau) s FROM dw_app_monthly
            WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND date >= '2022-01-01' AND date < '2023-01-01'
            GROUP BY date)
SELECT ROUND(AVG(s)/10000.0, 0) FROM mo

-- ── [3/10] ──────────────────────────
WITH mo AS (SELECT date, SUM(revenue_krw_100) r, SUM(mau) u FROM dw_app_monthly
            WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND date >= '2022-01-01' AND date < '2023-01-01'
            GROUP BY date)
SELECT ROUND(AVG(r)/NULLIF(AVG(u),0), 0) FROM mo

-- ── [4/10] ──────────────────────────
SELECT ROUND(SUM(units)/10000.0/12, 0)
                    FROM dw_app_monthly
                    WHERE country='US' AND in_revenue_top100_unified_os=TRUE AND date >= '2022-01-01' AND date < '2023-01-01'

-- ── [5/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND date >= '2022-01-01' AND date < '2023-01-01' AND publisher_country IN ('United States','Canada') AND publisher_name NOT ILIKE '%NEXON%'

-- ── [6/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND date >= '2022-01-01' AND date < '2023-01-01' AND (publisher_country IN ('China','Hong Kong','Taiwan','Macao','Macau') OR publisher_name ILIKE '%FUNFLY%') AND publisher_name NOT ILIKE '%NEXON%'

-- ── [7/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND date >= '2022-01-01' AND date < '2023-01-01' AND publisher_country IS NOT NULL AND publisher_country NOT IN ('Japan','South Korea','United States','Canada','China','Hong Kong','Taiwan','Macao','Macau') AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'

-- ── [8/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND date >= '2022-01-01' AND date < '2023-01-01' AND publisher_country='Japan' AND publisher_name NOT ILIKE '%NEXON%' AND publisher_name NOT ILIKE '%FUNFLY%'

-- ── [9/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND date >= '2022-01-01' AND date < '2023-01-01' AND publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%'

-- ── [10/10] ──────────────────────────
SELECT ROUND(SUM(revenue_krw_100)/100000000.0/12, 0)
                        FROM dw_app_monthly
                        WHERE country='US' AND in_revenue_top100_unified_os=TRUE
                          AND date >= '2022-01-01' AND date < '2023-01-01' AND genre='Strategy'
