-- ============================================================
-- 블루오션 장르 식별 쿼리
-- 조건: 매출 규모 + 낮은 HHI(경쟁 분산) + 높은 YoY 성장률
-- 테이블: dw_app_monthly
-- 기간: 최근 1년(2025-04 ~ 2026-03) vs 전년(2024-04 ~ 2025-03)
-- 범위: 전체 국가, 전체 OS 합산
-- ============================================================

WITH recent AS (
    -- 최근 1년: 장르별 · 앱별 매출 합산
    SELECT
        genre,
        app_id,
        SUM(revenue_usd)  AS app_rev
    FROM dw_app_monthly
    WHERE date BETWEEN '2025-04-01' AND '2026-03-01'
      AND genre IS NOT NULL
    GROUP BY genre, app_id
),
prev AS (
    -- 전년 동기: 장르별 총 매출
    SELECT
        genre,
        SUM(revenue_usd)  AS total_rev
    FROM dw_app_monthly
    WHERE date BETWEEN '2024-04-01' AND '2025-03-01'
      AND genre IS NOT NULL
    GROUP BY genre
),
genre_stats AS (
    -- 장르별 매출 합계 + 게임 수 + HHI 계산
    SELECT
        r.genre,
        SUM(r.app_rev)                                      AS total_rev,
        COUNT(DISTINCT r.app_id)                             AS game_count,
        -- HHI = 각 게임의 점유율(%) 제곱 합
        ROUND(
            SUM(
                POWER(r.app_rev / NULLIF(SUM(r.app_rev) OVER (PARTITION BY r.genre), 0) * 100, 2)
            )
        , 0)                                                 AS hhi
    FROM recent r
    GROUP BY r.genre
),
final AS (
    SELECT
        gs.genre,
        ROUND(gs.total_rev, 0)                               AS recent_rev_usd,
        gs.game_count,
        gs.hhi,
        CASE
            WHEN gs.hhi < 1500 THEN 'Low (경쟁적)'
            WHEN gs.hhi < 2500 THEN 'Mid (중간)'
            ELSE 'High (과점)'
        END                                                   AS hhi_grade,
        ROUND(p.total_rev, 0)                                AS prev_rev_usd,
        CASE
            WHEN p.total_rev > 0
            THEN ROUND((gs.total_rev - p.total_rev) / p.total_rev * 100, 1)
            ELSE NULL
        END                                                   AS yoy_growth_pct
    FROM genre_stats gs
    LEFT JOIN prev p ON p.genre = gs.genre
)
SELECT
    genre                                                     AS "장르",
    TO_CHAR(recent_rev_usd, 'FM999,999,999,999')             AS "최근1년 매출(USD)",
    game_count                                                AS "게임수",
    hhi                                                       AS "HHI",
    hhi_grade                                                 AS "집중도",
    TO_CHAR(COALESCE(prev_rev_usd, 0), 'FM999,999,999,999')  AS "전년 매출(USD)",
    COALESCE(yoy_growth_pct || '%', 'N/A')                    AS "YoY 성장률",
    -- 블루오션 스코어: 매출 큰데 + HHI 낮고 + 성장률 높은 장르일수록 높음
    CASE
        WHEN hhi IS NOT NULL AND yoy_growth_pct IS NOT NULL
        THEN ROUND(
            (PERCENT_RANK() OVER (ORDER BY recent_rev_usd)      * 40)  -- 매출 규모 40%
          + (PERCENT_RANK() OVER (ORDER BY hhi DESC)            * 30)  -- HHI 낮을수록 30%
          + (PERCENT_RANK() OVER (ORDER BY yoy_growth_pct)      * 30)  -- 성장률 30%
        , 1)
        ELSE NULL
    END                                                       AS "블루오션 점수"
FROM final
ORDER BY "블루오션 점수" DESC NULLS LAST;
