-- ============================================================
--  step3_US
--  자동 생성 — report_pipeline/queries.py  (직접 수정 금지)
--
--  기간   : 완전연도 2022, 2023, 2024, 2025 + 부분 26.1H(2026-01-01~, 6개월)
--           전 36개월 / 후 18개월
--  월평균 : 달력 개월수 고정 분모 (활동월 수 아님)
--  매출   : revenue_krw_100 (환율 반영 완료)
--  국적   : NEXON→KR · FUNFLY→중화권 / 중화권=China/Hong Kong/Taiwan/Macao
--
--  기간을 바꾸려면 report_pipeline/config.py 의 PERIOD 블록을 고치고
--  python -m report_pipeline.dump_sql 을 다시 실행하세요.
-- ============================================================

WITH base AS (
  SELECT EXTRACT(YEAR FROM (date AT TIME ZONE 'Asia/Seoul'))::int AS yr, (date AT TIME ZONE 'Asia/Seoul') AS d, revenue_krw_100 AS krw,
         COALESCE(lv2_genre, genre) AS eg
  FROM dw_app_monthly
  WHERE country='US' AND in_revenue_top100_unified_os=TRUE
)
SELECT eg,
  ROUND(SUM(krw) FILTER (WHERE yr=2022)/12/1e8) AS y22,
  ROUND(SUM(krw) FILTER (WHERE yr=2023)/12/1e8) AS y23,
  ROUND(SUM(krw) FILTER (WHERE yr=2024)/12/1e8) AS y24,
  ROUND(SUM(krw) FILTER (WHERE yr=2025)/12/1e8) AS y25,
  ROUND(SUM(krw) FILTER (WHERE d>='2026-01-01' AND d<'2026-07-01')/6/1e8) AS h_partial,
  ROUND(SUM(krw) FILTER (WHERE yr IN (2022,2023,2024))/36/1e8) AS pre,
  ROUND((SUM(krw) FILTER (WHERE yr IN (2025))+COALESCE(SUM(krw) FILTER (WHERE d>='2026-01-01' AND d<'2026-07-01'),0))/18/1e8) AS post,
  ROUND((SUM(krw) FILTER (WHERE yr IN (2025))+COALESCE(SUM(krw) FILTER (WHERE d>='2026-01-01' AND d<'2026-07-01'),0))/18/1e8 - SUM(krw) FILTER (WHERE yr IN (2022,2023,2024))/36/1e8) AS chg
FROM base
GROUP BY eg
ORDER BY post DESC NULLS LAST;
