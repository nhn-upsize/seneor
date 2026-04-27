-- ============================================================================
-- 04. 국가별 TOP 100 전체 월평균 (검증용)
-- ============================================================================
-- 용도: HTML 표 하단 "국가 전체 합계" 행 검증
-- 산식:
--   연도별: SUM(revenue) / (12 or 3)
--   기간별: SUM(revenue) / (36 or 15) — 모든 월이 데이터 포함이므로 0 합산 문제 없음
-- ============================================================================

-- [A] 연도별 월평균
SELECT
  country,
  EXTRACT(YEAR FROM date)::int AS year,
  ROUND(
    (SUM(revenue_krw_100) /
       CASE WHEN EXTRACT(YEAR FROM date) = 2026 THEN 3.0 ELSE 12.0 END
    )::numeric / 100000000, 0
  ) AS monthly_avg_eok
FROM dw_app_monthly
WHERE in_revenue_top100_unified_os = true
  AND country IN ('KR', 'JP', 'US')
  AND EXTRACT(YEAR FROM date) BETWEEN 2022 AND 2026
  AND revenue_krw_100 IS NOT NULL
GROUP BY country, EXTRACT(YEAR FROM date)
ORDER BY country, year;


-- [B] 기간별 월평균 (22~24 vs 25~26Q1)
SELECT
  country,
  ROUND(
    (SUM(CASE WHEN EXTRACT(YEAR FROM date) BETWEEN 2022 AND 2024 THEN revenue_krw_100 ELSE 0 END)
      / 36.0)::numeric / 100000000, 0
  ) AS avg_22_24_eok,
  ROUND(
    (SUM(CASE WHEN EXTRACT(YEAR FROM date) IN (2025, 2026) THEN revenue_krw_100 ELSE 0 END)
      / 15.0)::numeric / 100000000, 0
  ) AS avg_25_26q1_eok
FROM dw_app_monthly
WHERE in_revenue_top100_unified_os = true
  AND country IN ('KR', 'JP', 'US')
  AND revenue_krw_100 IS NOT NULL
GROUP BY country
ORDER BY country;

-- ----------------------------------------------------------------------------
-- 검증 규칙
-- ----------------------------------------------------------------------------
-- 표의 전 장르 월평균 합산 = 이 쿼리의 결과와 일치해야 함
-- (effective_genre 는 exhaustive + mutually exclusive 이므로 합이 국가 총계와 같음)
-- ----------------------------------------------------------------------------
-- 기대값 (2026-04 기준, 현재 dw 스냅샷):
--   KR: 22~24 avg 4,109 / 25~26Q1 avg 4,654 / 연도별 3,835→4,003→4,488→4,800→4,071
--   JP: 22~24 avg 9,306 / 25~26Q1 avg 8,969 / 연도별 9,700→9,062→9,157→9,058→8,611
--   US: 22~24 avg 16,801 / 25~26Q1 avg 19,736 / 연도별 14,687→16,355→19,360→19,999→18,686
