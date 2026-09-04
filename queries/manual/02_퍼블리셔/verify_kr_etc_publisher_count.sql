-- ============================================================
--  KR 시장 TOP100 내 한국 퍼블리셔 — TOP5(엔씨·넥슨·넷마블·카카오·NHN) 제외 '기타 KR'의 퍼블리셔 개수
--  출처: verify/verify_kr_etc_publisher_count.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================

-- ── [1/1] ──────────────────────────
SELECT COUNT(DISTINCT publisher_name) AS pub_cnt,
       COUNT(DISTINCT unified_app_id) AS game_cnt
FROM dw_app_monthly
WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
  AND date >= '2022-01-01' AND date < '2023-01-01'
  AND (publisher_country='South Korea' OR publisher_name ILIKE '%NEXON%')
  AND publisher_name NOT IN ('NCSOFT','NC Corporation','NC','NEXON','NEXON Korea','Nexon','Netmarble','NETMARBLE','Kakao Games','KAKAO Games','NHN','NHN Corp.')
  AND publisher_name NOT ILIKE '%NCSOFT%'
  AND publisher_name NOT ILIKE '%NEXON%'
  AND publisher_name NOT ILIKE '%Netmarble%'
  AND publisher_name NOT ILIKE '%Kakao Games%'
  AND publisher_name NOT ILIKE '%NHN%'
