-- ============================================================================
-- 03. 기간 비교 — 22~24 vs 25~26Q1 월평균 (NULL 제외)
-- ============================================================================
-- 용도: HTML 표의 "22~24 월평균 / 25~26Q1 월평균 / Δ" 컬럼
-- 핵심 규칙: 해당 장르가 TOP 100에 진입한 월만 대상으로 평균
--            → 런칭 전/이탈 월은 NULL 처리, 분모에서 제외 (0 합산 금지)
-- 실행: country = 'KR' / 'JP' / 'US' 로 각각 한 번씩 실행
-- ============================================================================

WITH base AS (
  SELECT
    country,
    EXTRACT(YEAR FROM date)::int AS year,
    TO_CHAR(date, 'YYYY-MM') AS month,
    CASE
      WHEN name ILIKE '%Disney Solitaire%' AND genre IN ('Card','Casino','Board')
        THEN 'Card+Casino+Board / 미분류'
      WHEN genre IN ('Card','Casino','Board') AND lv2_genre = 'PvP'
        THEN 'Card+Casino+Board / PvP (웹보드)'
      WHEN genre IN ('Card','Casino','Board') AND lv2_genre = 'PvE'
        THEN 'Card+Casino+Board / PvE (카지노)'
      WHEN genre IN ('Card','Casino','Board')
        THEN 'Card+Casino+Board / 미분류'
      WHEN country IN ('JP','US') AND genre = 'Role Playing' AND lv2_genre = '방치형'
        THEN 'Role Playing / 방치형'
      WHEN country IN ('JP','US') AND genre = 'Role Playing'
        THEN 'Role Playing'
      WHEN sub_genre IS NOT NULL AND lv2_genre IS NOT NULL
        THEN genre || ' / ' || sub_genre || ' / ' || lv2_genre
      WHEN sub_genre IS NOT NULL
        THEN genre || ' / ' || sub_genre
      WHEN lv2_genre IS NOT NULL
        THEN genre || ' / ' || lv2_genre
      ELSE genre
    END AS effective_genre,
    SUM(revenue_krw_100) AS month_rev
  FROM dw_app_monthly
  WHERE in_revenue_top100_unified_os = true
    AND country = 'KR'            -- ⭐ 여기를 JP / US 로 바꿔가며 3회 실행
    AND EXTRACT(YEAR FROM date) BETWEEN 2022 AND 2026
    AND revenue_krw_100 IS NOT NULL
  GROUP BY 1, 2, 3, 4
)
SELECT
  effective_genre,
  COUNT(CASE WHEN year BETWEEN 2022 AND 2024 THEN 1 END) AS months_22_24,
  ROUND(
    (AVG(CASE WHEN year BETWEEN 2022 AND 2024 THEN month_rev END))::numeric
      / 100000000, 0
  ) AS avg_22_24_eok,
  COUNT(CASE WHEN year IN (2025, 2026) THEN 1 END) AS months_25_26q1,
  ROUND(
    (AVG(CASE WHEN year IN (2025, 2026) THEN month_rev END))::numeric
      / 100000000, 0
  ) AS avg_25_26q1_eok,
  -- 변화율 (%) — 분자/분모 둘 다 있을 때만
  CASE
    WHEN AVG(CASE WHEN year BETWEEN 2022 AND 2024 THEN month_rev END) IS NULL
      OR AVG(CASE WHEN year IN (2025, 2026) THEN month_rev END) IS NULL
    THEN NULL
    ELSE ROUND(
      (AVG(CASE WHEN year IN (2025, 2026) THEN month_rev END)
        / AVG(CASE WHEN year BETWEEN 2022 AND 2024 THEN month_rev END) - 1
      )::numeric * 100, 0
    )
  END AS change_pct
FROM base
GROUP BY effective_genre
ORDER BY avg_25_26q1_eok DESC NULLS LAST;

-- ----------------------------------------------------------------------------
-- 핵심 포인트
-- ----------------------------------------------------------------------------
-- • AVG(CASE WHEN ... THEN month_rev END) = NULL 자동 제외, 실제 값 있는 월만 평균
-- • 분모가 들쭉날쭉 → 진입월 수(m22_24, m25_26q1)를 함께 출력해 해석 시 참고
-- • months_22_24 = 0 이면 그 장르는 22~24 기간에 TOP 100 미진입 = 신규 장르
-- • months_25_26q1 = 0 이면 이탈 (25년 이후 TOP 100 소멸)
-- • 국가 전체 합계(04번 쿼리) 는 모든 월이 데이터를 포함하므로 NULL 제외 결과와 동일
