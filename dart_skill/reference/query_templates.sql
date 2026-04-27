-- =============================================
-- DART 공시 재무 데이터 자주 쓰는 쿼리 템플릿
-- DB: AI_mobilegame / 테이블: dart_*
-- =============================================

-- Q1: 특정 회사 연간 재무 요약 (연결 기준)
SELECT
    c.corp_name,
    s.year,
    s.revenue / 100000000.0 AS "매출액(억원)",
    s.operating_income / 100000000.0 AS "영업이익(억원)",
    s.net_income / 100000000.0 AS "순이익(억원)",
    s.total_assets / 100000000.0 AS "자산(억원)",
    s.total_equity / 100000000.0 AS "자본(억원)",
    s.labor_total / 100000000.0 AS "인건비(억원)",
    s.advertising_expense / 100000000.0 AS "광고비(억원)"
FROM dart_financial_summary s
JOIN dart_company c ON c.corp_code = s.corp_code
WHERE c.corp_name = '넷마블'
  AND s.fs_type = '연결'
ORDER BY s.year;

-- Q2: 전체 게임사 매출 순위 (특정 연도, 연결 기준)
SELECT
    c.corp_name,
    s.revenue / 100000000.0 AS "매출액(억원)",
    s.operating_income / 100000000.0 AS "영업이익(억원)",
    ROUND(s.operating_income * 100.0 / NULLIF(s.revenue, 0), 1) AS "영업이익률(%)",
    s.net_income / 100000000.0 AS "순이익(억원)"
FROM dart_financial_summary s
JOIN dart_company c ON c.corp_code = s.corp_code
WHERE s.year = 2025 AND s.fs_type = '연결'
ORDER BY s.revenue DESC;

-- Q3: 분기별 매출/영업이익 추이 (특정 회사)
SELECT
    c.corp_name,
    q.quarter,
    q.revenue / 100000000.0 AS "매출액(억원)",
    q.operating_income / 100000000.0 AS "영업이익(억원)",
    q.labor_cost / 100000000.0 AS "인건비(억원)",
    q.advertising_expense / 100000000.0 AS "광고비(억원)",
    q.is_estimated AS "추정여부"
FROM dart_financial_quarterly q
JOIN dart_company c ON c.corp_code = q.corp_code
WHERE c.corp_name = '크래프톤'
ORDER BY q.quarter;

-- Q4: 인건비 상세 비교 (전체 게임사, 특정 연도)
SELECT
    c.corp_name,
    s.labor_total / 100000000.0 AS "인건비합계(억원)",
    s.labor_salary / 100000000.0 AS "단기급여(억원)",
    s.labor_welfare / 100000000.0 AS "복리후생(억원)",
    s.labor_retirement / 100000000.0 AS "퇴직급여(억원)",
    s.labor_stock_comp / 100000000.0 AS "주식보상(억원)",
    ROUND(s.labor_total * 100.0 / NULLIF(s.revenue, 0), 1) AS "인건비율(%)"
FROM dart_financial_summary s
JOIN dart_company c ON c.corp_code = s.corp_code
WHERE s.year = 2025 AND s.fs_type = '연결' AND s.labor_total IS NOT NULL
ORDER BY s.labor_total DESC;

-- Q5: 광고비 비중 비교 (전체 게임사)
SELECT
    c.corp_name,
    s.year,
    s.advertising_expense / 100000000.0 AS "광고비(억원)",
    s.revenue / 100000000.0 AS "매출액(억원)",
    ROUND(s.advertising_expense * 100.0 / NULLIF(s.revenue, 0), 1) AS "광고비율(%)"
FROM dart_financial_summary s
JOIN dart_company c ON c.corp_code = s.corp_code
WHERE s.fs_type = '연결' AND s.advertising_expense IS NOT NULL
ORDER BY s.year, s.advertising_expense DESC;

-- Q6: M&A / 합병인수 공시 조회
SELECT
    c.corp_name,
    d.disclosure_date,
    d.title,
    d.detail
FROM dart_disclosure d
JOIN dart_company c ON c.corp_code = d.corp_code
WHERE d.category = '합병인수'
ORDER BY c.corp_name, d.disclosure_date;

-- Q7: 특정 회사 전체 공시 이력
SELECT
    d.category,
    d.disclosure_date,
    d.title,
    d.receipt_no
FROM dart_disclosure d
JOIN dart_company c ON c.corp_code = d.corp_code
WHERE c.corp_name = '엔씨소프트'
ORDER BY d.disclosure_date DESC;

-- Q8: 신작 게임 현황 (전체)
SELECT
    c.corp_name,
    g.game_name,
    g.game_type,
    g.release_date,
    g.platform,
    g.genre,
    g.service_status
FROM dart_new_game g
JOIN dart_company c ON c.corp_code = g.corp_code
ORDER BY c.corp_name, g.release_date;

-- Q9: 연도별 영업이익률 변화 (전체)
SELECT
    c.corp_name,
    s.year,
    ROUND(s.operating_income * 100.0 / NULLIF(s.revenue, 0), 1) AS "영업이익률(%)",
    ROUND(s.net_income * 100.0 / NULLIF(s.revenue, 0), 1) AS "순이익률(%)"
FROM dart_financial_summary s
JOIN dart_company c ON c.corp_code = s.corp_code
WHERE s.fs_type = '연결'
ORDER BY c.corp_name, s.year;

-- Q10: DART API 전체 계정과목에서 특정 항목 검색
SELECT
    c.corp_name,
    a.year,
    a.fs_type,
    a.account_name,
    a.account_code,
    a.amount_current / 100000000.0 AS "당기(억원)"
FROM dart_financial_account a
JOIN dart_company c ON c.corp_code = a.corp_code
WHERE a.account_name LIKE '%연구개발%'
  AND a.fs_type = '연결'
ORDER BY c.corp_name, a.year;
