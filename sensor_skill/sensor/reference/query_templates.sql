-- ============================================================
-- Sensor Tower 게임 분석 쿼리 템플릿
-- 사용 시 {year}, {month}, {date} 등 플레이스홀더 치환
-- ============================================================


-- ============================================================
-- Q1: 특정 월 매출 기준 TOP 100 (국가/OS별, 게임 전체)
-- ============================================================
WITH revenue_ranked AS (
    SELECT
        country, os, app_id,
        revenue_absolute / 100.0 AS revenue_usd,
        units_absolute AS downloads,
        ROW_NUMBER() OVER (PARTITION BY country, os ORDER BY revenue_absolute DESC) AS rank
    FROM st_top_apps_downloads_revenue
    WHERE date = '{year}-{month}-01'
      AND measure = 'revenue'
      AND category = 'game'
)
SELECT rank, country, os, app_id,
       ROUND(revenue_usd::numeric, 2) AS revenue_usd, downloads
FROM revenue_ranked
WHERE rank <= 100
ORDER BY country, os, rank;


-- ============================================================
-- Q2: 퍼블리셔 매출 TOP N + 국가 그룹화 (넥슨 예외 처리)
-- ============================================================
WITH pub_revenue AS (
    SELECT
        t.publisher_id, t.publisher_name, t.country AS market_country,
        SUM(t.revenue_absolute) / 100.0 AS revenue_usd,
        SUM(t.units_absolute) AS downloads
    FROM st_top_publishers t
    WHERE t.date = '{year}-{month}-01'
      AND t.category = 'game'
      AND t.measure = 'revenue'
    GROUP BY t.publisher_id, t.publisher_name, t.country
),
pub_with_country AS (
    SELECT
        p.*,
        d.publisher_country,
        CASE
            WHEN p.publisher_name ILIKE '%NEXON%' THEN 'KR'
            WHEN d.publisher_country = 'South Korea' THEN 'KR'
            WHEN d.publisher_country = 'Japan' THEN 'JP'
            WHEN d.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
            WHEN d.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
            ELSE '기타'
        END AS pub_group
    FROM pub_revenue p
    LEFT JOIN LATERAL (
        SELECT publisher_country FROM st_app_detail a
        WHERE a.publisher_id = p.publisher_id
        ORDER BY a.collected_date DESC LIMIT 1
    ) d ON TRUE
)
SELECT pub_group, publisher_name,
       ROUND(SUM(revenue_usd)::numeric, 2) AS revenue_usd,
       SUM(downloads) AS downloads
FROM pub_with_country
GROUP BY pub_group, publisher_name
ORDER BY revenue_usd DESC
LIMIT 100;


-- ============================================================
-- Q3: 퍼블리셔 국가 그룹별 매출 합계
-- ============================================================
WITH pub_with_group AS (
    SELECT
        t.publisher_id, t.publisher_name,
        t.revenue_absolute,
        CASE
            WHEN t.publisher_name ILIKE '%NEXON%' THEN 'KR'
            WHEN d.publisher_country = 'South Korea' THEN 'KR'
            WHEN d.publisher_country = 'Japan' THEN 'JP'
            WHEN d.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
            WHEN d.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
            ELSE '기타'
        END AS pub_group
    FROM st_top_publishers t
    LEFT JOIN LATERAL (
        SELECT publisher_country FROM st_app_detail a
        WHERE a.publisher_id = t.publisher_id
        ORDER BY a.collected_date DESC LIMIT 1
    ) d ON TRUE
    WHERE t.date = '{year}-{month}-01'
      AND t.category = 'game'
      AND t.measure = 'revenue'
)
SELECT pub_group,
       COUNT(DISTINCT publisher_id) AS pub_count,
       ROUND((SUM(revenue_absolute)/100.0)::numeric, 2) AS total_revenue_usd
FROM pub_with_group
GROUP BY pub_group
ORDER BY total_revenue_usd DESC;


-- ============================================================
-- Q4-A: 신규 진입 게임 — 방법 1 (매출 기준 TOP 100)
-- 특정 연도 1월에는 없다가 2~12월 중 처음 진입한 게임
-- ============================================================
WITH jan_apps AS (
    SELECT DISTINCT os, country, app_id
    FROM st_top_apps_downloads_revenue
    WHERE measure = 'revenue' AND category = 'game'
      AND date = '{year}-01-01'
),
rest AS (
    SELECT DISTINCT ON (os, country, app_id)
        os, country, app_id, date
    FROM st_top_apps_downloads_revenue
    WHERE measure = 'revenue' AND category = 'game'
      AND date BETWEEN '{year}-02-01' AND '{year}-12-01'
    ORDER BY os, country, app_id, date
)
SELECT os, country,
       COUNT(*) AS new_entries,
       ROUND((COUNT(*)/11.0)::numeric, 1) AS avg_per_month
FROM rest r
WHERE NOT EXISTS (
    SELECT 1 FROM jan_apps j
    WHERE j.os=r.os AND j.country=r.country AND j.app_id=r.app_id
)
GROUP BY os, country
ORDER BY os, country;


-- ============================================================
-- Q4-B: 신규 진입 게임 — 방법 2 (스토어 차트 기준, topgrossing)
-- 매월 1일 기준 TOP 100 차트에 신규 진입한 게임
-- ============================================================
WITH jan_apps AS (
    SELECT DISTINCT os, country, app_id
    FROM st_top_charts
    WHERE chart_type = 'topgrossing' AND category = 'game'
      AND date = '{year}-01-01' AND rank <= 100
),
rest AS (
    SELECT DISTINCT ON (os, country, app_id)
        os, country, app_id, date
    FROM st_top_charts
    WHERE chart_type = 'topgrossing' AND category = 'game'
      AND rank <= 100
      AND date BETWEEN '{year}-02-01' AND '{year}-12-01'
    ORDER BY os, country, app_id, date
)
SELECT os, country,
       COUNT(*) AS new_entries,
       ROUND((COUNT(*)/11.0)::numeric, 1) AS avg_per_month
FROM rest r
WHERE NOT EXISTS (
    SELECT 1 FROM jan_apps j
    WHERE j.os=r.os AND j.country=r.country AND j.app_id=r.app_id
)
GROUP BY os, country
ORDER BY os, country;


-- ============================================================
-- Q5: 앱별 Paid vs Organic 다운로드 비율 (특정 월)
-- ============================================================
SELECT
    d.os, d.name AS app_name, d.publisher_name,
    dc.country, dc.organic_abs, dc.paid_abs, dc.browser_abs,
    ROUND((dc.paid_abs::numeric / NULLIF(dc.organic_abs + dc.paid_abs + dc.browser_abs, 0) * 100), 2) AS paid_ratio_pct
FROM st_download_channels dc
JOIN st_app_detail d ON d.unified_app_id = dc.unified_app_id AND d.os = dc.os
WHERE dc.date = '{year}-{month}-01'
  AND dc.os IN ('android','ios')
ORDER BY dc.paid_abs DESC NULLS LAST
LIMIT 100;


-- ============================================================
-- Q6: 특정 퍼블리셔의 앱 목록 + 장르
-- ============================================================
SELECT
    d.os, d.app_id, d.name, d.publisher_name,
    d.categories, d.rating, d.release_date
FROM st_app_detail d
WHERE d.publisher_name ILIKE '%{publisher}%'
ORDER BY d.os, d.publisher_name, d.name;


-- ============================================================
-- Q7: 특정 월 퍼블리셔별 장르 비중 (매출 가중)
-- ============================================================
WITH pub_apps AS (
    SELECT
        p.publisher_name, p.publisher_id,
        pa.app_id, p.os,
        pa.revenue_absolute AS app_revenue
    FROM st_top_publishers p
    JOIN st_top_publishers_apps pa ON pa.publisher_record_id = p.id
    WHERE p.date = '{year}-{month}-01'
      AND p.category = 'game'
      AND p.measure = 'revenue'
),
app_genres AS (
    SELECT
        pa.publisher_name, pa.publisher_id, pa.app_id, pa.app_revenue,
        COALESCE(
            (SELECT g.elem FROM jsonb_array_elements_text(d.categories) AS g(elem)
             WHERE g.elem LIKE 'game_%' LIMIT 1),
            'game_other'
        ) AS genre
    FROM pub_apps pa
    LEFT JOIN LATERAL (
        SELECT * FROM st_app_detail a
        WHERE a.app_id = pa.app_id AND a.os = pa.os
        ORDER BY a.collected_date DESC LIMIT 1
    ) d ON TRUE
)
SELECT
    publisher_name, genre,
    ROUND((SUM(app_revenue)/100.0)::numeric, 2) AS genre_revenue_usd,
    ROUND((100.0 * SUM(app_revenue) / NULLIF(SUM(SUM(app_revenue)) OVER (PARTITION BY publisher_name), 0))::numeric, 1) AS pct
FROM app_genres
GROUP BY publisher_name, genre
ORDER BY publisher_name, genre_revenue_usd DESC;


-- ============================================================
-- Q8: 월별 시계열 매출 (특정 앱)
-- ============================================================
SELECT
    date, os, country,
    revenue_absolute / 100.0 AS revenue_usd,
    units_absolute AS downloads
FROM st_top_apps_downloads_revenue
WHERE app_id = '{app_id}'
  AND measure = 'revenue'
  AND category = 'game'
  AND date BETWEEN '{start_date}' AND '{end_date}'
ORDER BY date, os, country;


-- ============================================================
-- Q9: 카테고리별 전체 시장 규모 (store_summary/games_breakdown)
-- ============================================================
-- 마켓 전체
SELECT os, country, date,
       units, revenue / 100.0 AS revenue_usd
FROM st_store_summary
WHERE date = '{year}-{month}-01'
ORDER BY os, country;

-- 장르별
SELECT os, country, date, category,
       units, revenue / 100.0 AS revenue_usd
FROM st_games_breakdown
WHERE date = '{year}-{month}-01'
ORDER BY os, country, category;
