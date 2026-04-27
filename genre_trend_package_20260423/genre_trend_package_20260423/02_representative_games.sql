-- ============================================================================
-- 02. 장르별 대표 게임 TOP 1~2 (누적 매출 기준)
-- ============================================================================
-- 용도: HTML 표의 "대표 게임" 컬럼
-- 출력: (country, effective_genre, top_games) — 상위 1~2개 게임을 " · " 로 연결
-- ============================================================================

WITH app_genre AS (
  SELECT
    country,
    unified_app_id,
    -- 게임명 우선순위: 한국어(가-힣) → 영어 → 일본어(ぁ-ヿ)
    (ARRAY_AGG(name ORDER BY
        CASE WHEN name ~ '[가-힣]' THEN 0
             WHEN name ~ '[ぁ-ヿ]' THEN 2
             ELSE 1 END
      ))[1] AS display_name,
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
    SUM(revenue_krw_100) AS total_rev
  FROM dw_app_monthly
  WHERE in_revenue_top100_unified_os = true
    AND country IN ('KR','JP','US')
    AND EXTRACT(YEAR FROM date) BETWEEN 2022 AND 2026
    AND revenue_krw_100 IS NOT NULL
  GROUP BY country, unified_app_id,
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
    END
),
ranked AS (
  SELECT country, effective_genre, display_name, total_rev,
    ROW_NUMBER() OVER (
      PARTITION BY country, effective_genre
      ORDER BY total_rev DESC
    ) AS rn
  FROM app_genre
)
SELECT
  country,
  effective_genre,
  STRING_AGG(display_name, ' · ' ORDER BY rn) AS top_games
FROM ranked
WHERE rn <= 2
GROUP BY country, effective_genre
ORDER BY country, effective_genre;

-- ----------------------------------------------------------------------------
-- 핵심 포인트
-- ----------------------------------------------------------------------------
-- • unified_app_id: iOS·Android 동일 게임 통합 키
-- • ROW_NUMBER() OVER (PARTITION BY country, effective_genre ORDER BY total_rev DESC)
--   → 장르별 누적 매출 순위
-- • STRING_AGG(... ORDER BY rn) 으로 1~2위 연결
-- • 누적 기간: 2022~2026 Q1 전체
