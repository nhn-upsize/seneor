-- ============================================================================
-- 01. 국가별 × 연도별 × 장르별 월평균 매출 (메인 쿼리)
-- ============================================================================
-- 용도: HTML 대시보드의 차트/표 핵심 데이터
-- 단위: 억원 (monthly_avg_eok)
-- 실행: country = 'KR' / 'JP' / 'US' 로 각각 한 번씩 실행
-- ============================================================================

WITH base AS (
  SELECT
    country,
    EXTRACT(YEAR FROM date)::int AS year,
    TO_CHAR(date, 'YYYY-MM') AS month,
    CASE
      -- Card+Casino+Board 3장르 통합 후 lv2_genre(PvP/PvE)로만 분리
      -- 단, Disney Solitaire 는 PvE에서 제외하여 미분류로 이동 (업무적 예외)
      WHEN name ILIKE '%Disney Solitaire%' AND genre IN ('Card','Casino','Board')
        THEN 'Card+Casino+Board / 미분류'
      WHEN genre IN ('Card','Casino','Board') AND lv2_genre = 'PvP'
        THEN 'Card+Casino+Board / PvP (웹보드)'
      WHEN genre IN ('Card','Casino','Board') AND lv2_genre = 'PvE'
        THEN 'Card+Casino+Board / PvE (카지노)'
      WHEN genre IN ('Card','Casino','Board')
        THEN 'Card+Casino+Board / 미분류'

      -- JP/US 의 Role Playing: MMORPG/비MMORPG 구분 제거, 방치형만 분리
      WHEN country IN ('JP','US') AND genre = 'Role Playing' AND lv2_genre = '방치형'
        THEN 'Role Playing / 방치형'
      WHEN country IN ('JP','US') AND genre = 'Role Playing'
        THEN 'Role Playing'

      -- KR 은 기존 genre / sub_genre / lv2_genre 3단 결합 유지
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
  year,
  effective_genre,
  ROUND(
    (SUM(month_rev) / CASE WHEN year = 2026 THEN 3.0 ELSE 12.0 END)::numeric
      / 100000000, 0
  ) AS monthly_avg_eok
FROM base
GROUP BY year, effective_genre
ORDER BY year, monthly_avg_eok DESC;

-- ----------------------------------------------------------------------------
-- 핵심 포인트
-- ----------------------------------------------------------------------------
-- • revenue_krw_100 = revenue_usd ÷ 0.7 × 연도별환율 (dw 사전 계산값)
-- • in_revenue_top100_unified_os: iOS+Android 합산 매출 TOP 100 플래그
-- • 2026 은 Q1(3개월)만 있으므로 ÷3, 나머지 연도는 ÷12
-- • / 100000000 로 원화 → 억원 변환
-- • 이 쿼리는 월별 데이터를 합산하여 연간 월평균을 계산함 (단순 산술평균)
-- • 기간 비교(22~24 vs 25~26Q1)는 03번 쿼리 사용 — NULL 제외 로직이 다름
