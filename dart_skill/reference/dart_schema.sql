-- dart_ 테이블 스키마: 한국게임사 DART 공시 데이터
-- DB: AI_mobilegame
-- 생성일: 2026-04-13

-- 1. 회사 마스터
CREATE TABLE IF NOT EXISTS dart_company (
    corp_code   VARCHAR(20) PRIMARY KEY,
    corp_name   VARCHAR(100) NOT NULL
);

-- 2. 연간 요약재무
CREATE TABLE IF NOT EXISTS dart_financial_summary (
    corp_code           VARCHAR(20) NOT NULL REFERENCES dart_company(corp_code),
    fs_type             VARCHAR(10) NOT NULL,  -- '연결' / '별도'
    year                SMALLINT    NOT NULL,
    -- 핵심 재무
    revenue             BIGINT,     -- 매출액
    operating_income    BIGINT,     -- 영업이익
    net_income          BIGINT,     -- 당기순이익
    pretax_income       BIGINT,     -- 세전이익
    eps                 BIGINT,     -- 기본주당이익
    total_assets        BIGINT,     -- 자산총계
    total_liabilities   BIGINT,     -- 부채총계
    total_equity        BIGINT,     -- 자본총계
    current_assets      BIGINT,     -- 유동자산
    current_liabilities BIGINT,     -- 유동부채
    noncurrent_liabilities BIGINT,  -- 비유동부채
    tangible_assets     BIGINT,     -- 유형자산
    intangible_assets   BIGINT,     -- 무형자산
    goodwill            BIGINT,     -- 영업권
    -- 현금흐름
    cash_and_equivalents BIGINT,    -- 현금및현금성자산
    cf_operating        BIGINT,     -- 영업현금흐름
    cf_investing        BIGINT,     -- 투자현금흐름
    cf_financing        BIGINT,     -- 재무현금흐름
    -- 손익 항목
    cost_of_sales       BIGINT,     -- 매출원가
    sga_total           BIGINT,     -- 판매비와관리비합계
    commission_fees     BIGINT,     -- 지급수수료
    depreciation        BIGINT,     -- 감가상각비
    amortization        BIGINT,     -- 무형자산상각비
    rnd_expense         BIGINT,     -- 연구개발비
    advertising_expense BIGINT,     -- 광고선전비
    income_tax          BIGINT,     -- 법인세비용
    finance_income      BIGINT,     -- 금융수익
    finance_cost        BIGINT,     -- 금융비용
    interest_expense    BIGINT,     -- 이자비용
    -- 인건비 상세
    labor_total         BIGINT,     -- 인건비합계
    labor_employee_benefit BIGINT,  -- 인건비_종업원급여합계
    labor_salary        BIGINT,     -- 인건비_단기급여
    labor_welfare       BIGINT,     -- 인건비_복리후생비
    labor_retirement    BIGINT,     -- 인건비_퇴직급여
    labor_retirement_db BIGINT,     -- 인건비_퇴직급여DB
    labor_retirement_dc BIGINT,     -- 인건비_퇴직급여DC
    labor_stock_comp    BIGINT,     -- 인건비_주식보상
    labor_wage          BIGINT,     -- 인건비_임금
    labor_bonus         BIGINT,     -- 인건비_상여
    labor_consolation   BIGINT,     -- 인건비_위로금
    -- 메타
    labor_source        VARCHAR(200),  -- _인건비출처
    ad_source           VARCHAR(200),  -- _광고비출처
    PRIMARY KEY (corp_code, fs_type, year)
);

-- 3. 분기 재무
CREATE TABLE IF NOT EXISTS dart_financial_quarterly (
    corp_code           VARCHAR(20) NOT NULL REFERENCES dart_company(corp_code),
    fs_type             VARCHAR(10) NOT NULL,  -- '연결'
    quarter             VARCHAR(10) NOT NULL,  -- '2022Q1' 등
    revenue             BIGINT,     -- 매출액
    operating_income    BIGINT,     -- 영업이익
    labor_cost          BIGINT,     -- 인건비
    advertising_expense BIGINT,     -- 광고선전비
    is_estimated        BOOLEAN DEFAULT FALSE, -- _추정 여부
    PRIMARY KEY (corp_code, fs_type, quarter)
);

-- 4. API 전체 계정과목
CREATE TABLE IF NOT EXISTS dart_financial_account (
    id                  SERIAL PRIMARY KEY,
    corp_code           VARCHAR(20) NOT NULL REFERENCES dart_company(corp_code),
    year                SMALLINT    NOT NULL,
    fs_type             VARCHAR(10) NOT NULL,  -- '연결' / '별도'
    account_name        VARCHAR(200),   -- 계정명
    account_code        VARCHAR(200),   -- 코드
    amount_current      BIGINT,         -- 당기
    amount_previous     BIGINT,         -- 전기
    amount_before_prev  BIGINT          -- 전전기
);
CREATE INDEX IF NOT EXISTS idx_dart_fa_corp_year
    ON dart_financial_account(corp_code, year, fs_type);

-- 5. 공시목록
CREATE TABLE IF NOT EXISTS dart_disclosure (
    id                  SERIAL PRIMARY KEY,
    corp_code           VARCHAR(20)  NOT NULL REFERENCES dart_company(corp_code),
    receipt_no          VARCHAR(30),            -- 접수번호 (합병인수 등은 NULL)
    category            VARCHAR(30)  NOT NULL,  -- 사업보고서, 배당 등
    disclosure_date     VARCHAR(10),            -- 날짜 (YYYYMMDD)
    title               VARCHAR(500),           -- 제목
    detail              JSONB                   -- 상세 (합병비율 등, 접수번호 없는 건은 원본 전체)
);
CREATE INDEX IF NOT EXISTS idx_dart_disc_corp ON dart_disclosure(corp_code);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dart_disc_uq
    ON dart_disclosure(corp_code, receipt_no) WHERE receipt_no IS NOT NULL AND receipt_no != '';

-- 6. 신작정보
CREATE TABLE IF NOT EXISTS dart_new_game (
    id                  SERIAL PRIMARY KEY,
    corp_code           VARCHAR(20)  NOT NULL REFERENCES dart_company(corp_code),
    game_name           VARCHAR(200) NOT NULL,  -- 게임명
    game_type           VARCHAR(50),            -- 구분 (출시작/개발중 등)
    release_date        VARCHAR(200),           -- 출시일
    platform            VARCHAR(200),           -- 플랫폼
    genre               VARCHAR(200),           -- 장르
    performance         TEXT,                   -- 성과
    service_status      VARCHAR(100)            -- 서비스상태
);
CREATE INDEX IF NOT EXISTS idx_dart_ng_corp
    ON dart_new_game(corp_code);
