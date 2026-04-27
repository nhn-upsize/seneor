-- ============================================================
-- Sensor Tower Market Analysis API - DB Schema (v7)
-- 대상 DB: PostgreSQL
-- 수정일: 2026-04-10
-- v7: v6 대비 변경사항
--     - st_master_apps / st_master_publishers 제거 (누적 레지스트리 불필요)
--     - dw_app_monthly 분석용 DW 테이블 신규 추가
--       (월 × OS × 국가 × 앱 grain, revenue USD 변환, source flags, demographics 포함)
--     - collect_app_detail / collect_demographics / collect_download_channels 은
--       월별 TOP100 소스 UNION 으로 직접 app_id 추출하도록 변경 (ETL 코드 참조)
--     - 매출은 센트(cents) 단위로 저장 (dw_app_monthly.revenue_usd만 USD)
-- ============================================================

-- ============================================================
-- 0. 공통 테이블
-- ============================================================

-- 게임 카테고리 참조 테이블 (게임 + 서브장르만)
CREATE TABLE IF NOT EXISTS st_game_category_ref (
    category_code   VARCHAR(50)  PRIMARY KEY,
    display_name_en VARCHAR(100) NOT NULL,
    display_name_ko VARCHAR(100) NOT NULL,
    is_parent       BOOLEAN      NOT NULL DEFAULT FALSE
);

INSERT INTO st_game_category_ref (category_code, display_name_en, display_name_ko, is_parent) VALUES
('game',                   'Games (All)',    '게임 전체',       TRUE),
('game_action',            'Action',         '액션',           FALSE),
('game_adventure',         'Adventure',      '어드벤처',       FALSE),
('game_arcade',            'Arcade',         '아케이드',       FALSE),
('game_board',             'Board',          '보드',           FALSE),
('game_card',              'Card',           '카드',           FALSE),
('game_casino',            'Casino',         '카지노',         FALSE),
('game_casual',            'Casual',         '캐주얼',         FALSE),
('game_educational',       'Educational',    '교육(게임)',     FALSE),
('game_music',             'Music',          '음악(게임)',     FALSE),
('game_puzzle',            'Puzzle',         '퍼즐',           FALSE),
('game_racing',            'Racing',         '레이싱',         FALSE),
('game_role_playing',      'Role Playing',   'RPG',            FALSE),
('game_simulation',        'Simulation',     '시뮬레이션',     FALSE),
('game_sports',            'Sports',         '스포츠(게임)',   FALSE),
('game_strategy',          'Strategy',       '전략',           FALSE),
('game_trivia',            'Trivia',         '퀴즈',           FALSE),
('game_word',              'Word',           '워드',           FALSE)
ON CONFLICT (category_code) DO NOTHING;

-- API 수집 이력 추적
CREATE TABLE IF NOT EXISTS st_collection_log (
    id              BIGSERIAL PRIMARY KEY,
    endpoint        VARCHAR(100) NOT NULL,
    os              VARCHAR(10)  NOT NULL,
    params          JSONB        NOT NULL,
    collected_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    status          VARCHAR(20)  NOT NULL DEFAULT 'success',
    error_message   TEXT,
    record_count    INTEGER
);

-- ============================================================
-- 0-1. 앱 프로필 (sales_report의 custom_tags 월별 저장)
-- ============================================================
CREATE TABLE IF NOT EXISTS st_app_profile (
    id              BIGSERIAL PRIMARY KEY,
    os              VARCHAR(10)  NOT NULL,
    app_id          VARCHAR(200) NOT NULL,
    collected_date  DATE         NOT NULL,
    custom_tags     JSONB        NOT NULL,
    collected_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    UNIQUE (os, app_id, collected_date)
);

CREATE INDEX IF NOT EXISTS idx_app_profile_app ON st_app_profile (app_id, collected_date DESC);
CREATE INDEX IF NOT EXISTS idx_app_profile_tags ON st_app_profile USING GIN (custom_tags);

-- ============================================================
-- (v7에서 제거됨) 0-2. 마스터 레지스트리
-- st_master_apps / st_master_publishers 는 v7에서 삭제되었습니다.
-- 월별 TOP100 고유 앱 리스트가 필요하면 소스 테이블 UNION 을 직접 쿼리하거나
-- dw_app_monthly 테이블을 참조하세요.
-- ============================================================

-- ============================================================
-- 1. 앱 상세정보 (/v1/{os}/apps)
--    월별 TOP100 소스 UNION 에서 수집된 app_id로 조회
-- ============================================================
CREATE TABLE IF NOT EXISTS st_app_detail (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,
    app_id              VARCHAR(200) NOT NULL,
    country             VARCHAR(50)  NOT NULL DEFAULT 'US',
    name                VARCHAR(500),
    publisher_name      VARCHAR(300),
    publisher_id        VARCHAR(200),
    publisher_country   VARCHAR(50),
    categories          JSONB,                  -- [6014, 7001] 등 카테고리 코드 배열
    release_date        TIMESTAMPTZ,
    updated_date        TIMESTAMPTZ,
    rating              NUMERIC(6,4),
    global_rating_count BIGINT,
    rating_count        BIGINT,
    price               NUMERIC(10,2),
    in_app_purchases    BOOLEAN,
    content_rating      VARCHAR(50),
    icon_url            TEXT,
    url                 TEXT,
    bundle_id           VARCHAR(300),
    description         TEXT,
    subtitle            TEXT,
    last_month_downloads    BIGINT,             -- humanized_worldwide_last_month_downloads.downloads
    last_month_revenue      BIGINT,             -- humanized_worldwide_last_month_revenue.revenue
    unified_app_id      VARCHAR(100),           -- unified app_id (플랫폼 통합 ID)
    collected_date      DATE         NOT NULL,
    collected_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    UNIQUE (os, app_id, country, collected_date)
);

CREATE INDEX IF NOT EXISTS idx_app_detail_app ON st_app_detail (app_id, collected_date DESC);
CREATE INDEX IF NOT EXISTS idx_app_detail_categories ON st_app_detail USING GIN (categories);
CREATE INDEX IF NOT EXISTS idx_app_detail_publisher ON st_app_detail (publisher_id);
CREATE INDEX IF NOT EXISTS idx_app_detail_unified ON st_app_detail (unified_app_id);

-- ============================================================
-- 2. Top Charts (GET /v1/{os}/ranking)
-- ============================================================
CREATE TABLE IF NOT EXISTS st_top_charts (
    id              BIGSERIAL PRIMARY KEY,
    os              VARCHAR(10)  NOT NULL,
    category        VARCHAR(50)  NOT NULL,
    chart_type      VARCHAR(30)  NOT NULL,
    country         VARCHAR(5)   NOT NULL,
    date            DATE         NOT NULL,
    rank            INTEGER      NOT NULL,
    app_id          VARCHAR(200) NOT NULL,
    collected_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    UNIQUE (os, category, chart_type, country, date, rank)
);

CREATE INDEX IF NOT EXISTS idx_top_charts_app ON st_top_charts (app_id, date);
CREATE INDEX IF NOT EXISTS idx_top_charts_date ON st_top_charts (date, os, country);

-- ============================================================
-- 3. Top Apps by Downloads & Revenue
--    (GET /v1/{os}/sales_report_estimates_comparison_attributes)
--    매출은 센트(cents) 단위
-- ============================================================
CREATE TABLE IF NOT EXISTS st_top_apps_downloads_revenue (
    id                          BIGSERIAL PRIMARY KEY,
    os                          VARCHAR(10)  NOT NULL,
    category                    VARCHAR(50)  NOT NULL,
    country                     VARCHAR(5),
    regions                     TEXT,
    date                        DATE         NOT NULL,
    end_date                    DATE,
    time_range                  VARCHAR(10)  NOT NULL,
    comparison_attribute        VARCHAR(20)  NOT NULL,
    measure                     VARCHAR(10)  NOT NULL,
    device_type                 VARCHAR(10),
    app_id                      VARCHAR(200) NOT NULL,

    current_units_value         BIGINT,
    units_absolute              BIGINT,
    comparison_units_value      BIGINT,
    units_delta                 BIGINT,
    units_transformed_delta     NUMERIC(20,5),

    current_revenue_value       BIGINT,
    revenue_absolute            BIGINT,
    comparison_revenue_value    BIGINT,
    revenue_delta               BIGINT,
    revenue_transformed_delta   NUMERIC(20,5),

    absolute                    BIGINT,
    delta                       BIGINT,
    transformed_delta           NUMERIC(20,5),

    collected_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, category, country, date, time_range, measure, app_id)
);

CREATE INDEX IF NOT EXISTS idx_downloads_revenue_app ON st_top_apps_downloads_revenue (app_id, date);
CREATE INDEX IF NOT EXISTS idx_downloads_revenue_date ON st_top_apps_downloads_revenue (date, os, country);

-- ============================================================
-- 4. Top Apps by Active Users
--    (GET /v1/{os}/top_and_trending/active_users)
-- ============================================================
CREATE TABLE IF NOT EXISTS st_top_apps_active_users (
    id                          BIGSERIAL PRIMARY KEY,
    os                          VARCHAR(10)  NOT NULL,
    category                    VARCHAR(50)  NOT NULL,
    country                     VARCHAR(5),
    regions                     TEXT,
    date                        DATE         NOT NULL,
    time_range                  VARCHAR(10)  NOT NULL,
    comparison_attribute        VARCHAR(20)  NOT NULL,
    measure                     VARCHAR(10)  NOT NULL,
    device_type                 VARCHAR(10),
    app_id                      VARCHAR(200) NOT NULL,

    users_absolute              BIGINT,
    users_delta                 BIGINT,
    users_transformed_delta     NUMERIC(20,5),
    users_market_share          NUMERIC(15,13),

    collected_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, category, country, date, time_range, measure, app_id)
);

CREATE INDEX IF NOT EXISTS idx_active_users_app ON st_top_apps_active_users (app_id, date);
CREATE INDEX IF NOT EXISTS idx_active_users_date ON st_top_apps_active_users (date, os, country);

-- ============================================================
-- 5. Top App Publishers
--    (GET /v1/{os}/top_and_trending/publishers)
--    매출은 센트(cents) 단위
-- ============================================================
CREATE TABLE IF NOT EXISTS st_top_publishers (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,
    category            VARCHAR(50)  NOT NULL,
    country             VARCHAR(5),
    date                DATE         NOT NULL,
    end_date            DATE,
    time_range          VARCHAR(10)  NOT NULL,
    comparison_attribute VARCHAR(20) NOT NULL,
    measure             VARCHAR(10)  NOT NULL,
    device_type         VARCHAR(10),
    publisher_id        VARCHAR(200) NOT NULL,
    publisher_name      VARCHAR(300),

    units_absolute      BIGINT,
    units_delta         BIGINT,
    revenue_absolute    BIGINT,
    revenue_delta       BIGINT,

    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, category, country, date, time_range, measure, publisher_id)
);

CREATE INDEX IF NOT EXISTS idx_top_publishers_date ON st_top_publishers (date, os, country);

CREATE TABLE IF NOT EXISTS st_top_publishers_apps (
    id                          BIGSERIAL PRIMARY KEY,
    publisher_record_id         BIGINT REFERENCES st_top_publishers(id) ON DELETE CASCADE,
    app_id                      VARCHAR(200) NOT NULL,
    publisher_id                VARCHAR(200) NOT NULL,

    units_absolute              BIGINT,
    units_delta                 BIGINT,
    units_transformed_delta     NUMERIC(20,5),
    revenue_absolute            BIGINT,
    revenue_delta               BIGINT,
    revenue_transformed_delta   NUMERIC(20,5),

    collected_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pub_apps_publisher ON st_top_publishers_apps (publisher_record_id);
CREATE INDEX IF NOT EXISTS idx_pub_apps_app ON st_top_publishers_apps (app_id);

-- ============================================================
-- 6. Store Summary (카테고리 단위 집계)
--    (GET /v1/{os}/store_summary)
--    매출은 센트(cents) 단위
-- ============================================================
CREATE TABLE IF NOT EXISTS st_store_summary (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,
    category            VARCHAR(50)  NOT NULL,
    country             VARCHAR(5)   NOT NULL,
    date                DATE         NOT NULL,
    date_granularity    VARCHAR(15)  NOT NULL,

    units               BIGINT,
    revenue             BIGINT,

    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, category, country, date, date_granularity)
);

CREATE INDEX IF NOT EXISTS idx_store_summary_date ON st_store_summary (date, os, category);

-- ============================================================
-- 7. Games Breakdown (게임 카테고리별 집계)
--    (GET /v1/{os}/games_breakdown)
--    매출은 센트(cents) 단위
-- ============================================================
CREATE TABLE IF NOT EXISTS st_games_breakdown (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,
    category            VARCHAR(50)  NOT NULL,
    country             VARCHAR(5)   NOT NULL,
    date                DATE         NOT NULL,
    date_granularity    VARCHAR(15)  NOT NULL,

    units               BIGINT,
    revenue             BIGINT,

    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, category, country, date, date_granularity)
);

CREATE INDEX IF NOT EXISTS idx_games_breakdown_date ON st_games_breakdown (date, os, category);

-- ============================================================
-- 8. Download Channels (GET /v1/{os}/downloads_by_sources)
--    유료/오가닉 다운로드 채널 월별 집계
--    ※ unified app_id 기반 (플랫폼 통합)
-- ============================================================
CREATE TABLE IF NOT EXISTS st_download_channels (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,   -- ios, android, unified
    unified_app_id      VARCHAR(100) NOT NULL,   -- unified app_id
    country             VARCHAR(5)   NOT NULL,
    date                DATE         NOT NULL,
    date_granularity    VARCHAR(15)  NOT NULL DEFAULT 'monthly',

    -- 절대값 (다운로드 수)
    organic_abs             BIGINT,          -- organic_browse + organic_search 합계 (legacy)
    organic_browse_abs      BIGINT,          -- 오가닉 브라우즈
    organic_search_abs      BIGINT,          -- 오가닉 검색
    browser_abs             BIGINT,          -- 브라우저 유입
    paid_abs                BIGINT,          -- 유료 광고
    paid_search_abs         BIGINT,          -- 유료 검색

    -- 비율
    organic_frac            NUMERIC(10,6),
    organic_browse_frac     NUMERIC(10,6),
    organic_search_frac     NUMERIC(10,6),
    browser_frac            NUMERIC(10,6),
    paid_frac               NUMERIC(10,6),
    paid_search_frac        NUMERIC(10,6),

    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, unified_app_id, country, date, date_granularity)
);

CREATE INDEX IF NOT EXISTS idx_dl_channels_app ON st_download_channels (unified_app_id, date);
CREATE INDEX IF NOT EXISTS idx_dl_channels_date ON st_download_channels (date, country);

-- ============================================================
-- 9. App Demographics (/v1/{os}/usage/demographics)
--    성별/연령대 분포
--    ※ date_granularity: all_time, quarterly
--    ※ confidence: 1~10+ (10+=높음, <=3=낮음)
-- ============================================================
CREATE TABLE IF NOT EXISTS st_app_demographics (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,
    app_id              VARCHAR(200) NOT NULL,
    country             VARCHAR(10)  NOT NULL,    -- 'WW' 또는 국가 코드
    date                DATE         NOT NULL,
    end_date            DATE,
    date_granularity    VARCHAR(15)  NOT NULL,    -- all_time, quarterly
    confidence          INTEGER,                  -- 1~10+ (데이터 신뢰도)

    -- 성별 합계
    female              NUMERIC(10,6),
    male                NUMERIC(10,6),
    average_age_total   NUMERIC(10,4),

    -- 성별 x 연령대 분포 (비율)
    female_0            NUMERIC(10,6),            -- 여성 18세 미만
    female_18           NUMERIC(10,6),            -- 여성 18~24
    female_25           NUMERIC(10,6),            -- 여성 25~34
    female_35           NUMERIC(10,6),            -- 여성 35~44
    female_45           NUMERIC(10,6),            -- 여성 45~54
    female_55           NUMERIC(10,6),            -- 여성 55+
    male_0              NUMERIC(10,6),            -- 남성 18세 미만
    male_18             NUMERIC(10,6),            -- 남성 18~24
    male_25             NUMERIC(10,6),            -- 남성 25~34
    male_35             NUMERIC(10,6),            -- 남성 35~44
    male_45             NUMERIC(10,6),            -- 남성 45~54
    male_55             NUMERIC(10,6),            -- 남성 55+

    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, app_id, country, date, date_granularity)
);

CREATE INDEX IF NOT EXISTS idx_demographics_app ON st_app_demographics (app_id, date);
CREATE INDEX IF NOT EXISTS idx_demographics_date ON st_app_demographics (date, os, country);

-- 국가별 베이스라인 인구 분포 (앱 비교용)
CREATE TABLE IF NOT EXISTS st_demographics_baseline (
    id                  BIGSERIAL PRIMARY KEY,
    os                  VARCHAR(10)  NOT NULL,
    country             VARCHAR(10)  NOT NULL,
    date                DATE         NOT NULL,
    date_granularity    VARCHAR(15)  NOT NULL,

    female_0            NUMERIC(10,6),
    female_18           NUMERIC(10,6),
    female_25           NUMERIC(10,6),
    female_35           NUMERIC(10,6),
    female_45           NUMERIC(10,6),
    female_55           NUMERIC(10,6),
    male_0              NUMERIC(10,6),
    male_18             NUMERIC(10,6),
    male_25             NUMERIC(10,6),
    male_35             NUMERIC(10,6),
    male_45             NUMERIC(10,6),
    male_55             NUMERIC(10,6),

    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (os, country, date, date_granularity)
);

-- ============================================================
-- 뷰
-- ============================================================

-- 앱 리텐션 뷰 (custom_tags 기반)
CREATE OR REPLACE VIEW v_app_retention AS
SELECT
    app_id, os, collected_date,
    custom_tags->>'Day 1 Retention (Latest Available, US)'   AS d1_retention_us,
    custom_tags->>'Day 7 Retention (Latest Available, US)'   AS d7_retention_us,
    custom_tags->>'Day 30 Retention (Latest Available, US)'  AS d30_retention_us,
    custom_tags->>'ARPDAU (Last Month, WW)'                  AS arpdau_ww,
    custom_tags->>'Advertised on Any Network'                 AS advertised
FROM st_app_profile;

-- 앱 engagement 뷰 (custom_tags 기반)
CREATE OR REPLACE VIEW v_app_engagement AS
SELECT
    app_id, os, collected_date,
    custom_tags->>'Last 30 Days Average DAU (US)'   AS avg_dau_us,
    custom_tags->>'Last 30 Days Average DAU (WW)'   AS avg_dau_ww,
    custom_tags->>'Last Month Average MAU (US)'     AS avg_mau_us,
    custom_tags->>'Last Month Average MAU (WW)'     AS avg_mau_ww,
    custom_tags->>'Predominant Age (Last Quarter, US)' AS predominant_age_us,
    custom_tags->>'Genders (Last Quarter, US)'         AS gender_us
FROM st_app_profile;

-- Store Summary / Games Breakdown 매출 달러 변환 뷰
CREATE OR REPLACE VIEW v_store_summary_usd AS
SELECT
    os, category, country, date, date_granularity,
    units,
    revenue / 100.0 AS revenue_usd
FROM st_store_summary;

CREATE OR REPLACE VIEW v_games_breakdown_usd AS
SELECT
    os, category, country, date, date_granularity,
    units,
    revenue / 100.0 AS revenue_usd
FROM st_games_breakdown;

-- ============================================================
-- 14. dw_app_monthly — 분석용 월별 앱 DW 테이블 (v7 신규)
--     Grain: (date, os, country, app_id)
--     - 매출/다운로드/MAU/채널/demographics 전부 조인된 wide 테이블
--     - revenue_usd 는 cents 에서 USD 로 변환
--     - source flags (in_*_top100) 로 어느 TOP100 에 들었는지 추적
--     - build_dw_app_monthly.sql 로 UPSERT 빌드 (API 호출 없음)
-- ============================================================
CREATE TABLE IF NOT EXISTS dw_app_monthly (
    date              DATE         NOT NULL,
    os                VARCHAR(16)  NOT NULL,
    country           VARCHAR(8)   NOT NULL,
    app_id            VARCHAR(128) NOT NULL,

    unified_app_id    VARCHAR(128),

    name              VARCHAR(512),
    publisher_id      VARCHAR(128),
    publisher_name    VARCHAR(255),
    publisher_country VARCHAR(64),
    genre             VARCHAR(64),
    release_date      DATE,

    revenue_usd       NUMERIC(18, 2),
    units             BIGINT,
    rank_revenue      INT,
    rank_units        INT,

    mau               BIGINT,
    rank_mau          INT,

    organic_abs       BIGINT,
    paid_abs          BIGINT,
    browser_abs       BIGINT,
    paid_ratio        NUMERIC(6, 4),

    demographics_quarter DATE,
    female_pct        NUMERIC(5, 2),
    male_pct          NUMERIC(5, 2),
    avg_age_total     NUMERIC(5, 2),
    age_breakdown     JSONB,

    in_revenue_top100   BOOLEAN DEFAULT FALSE,
    in_units_top100     BOOLEAN DEFAULT FALSE,
    in_mau_top100       BOOLEAN DEFAULT FALSE,
    in_publisher_top100 BOOLEAN DEFAULT FALSE,

    updated_at        TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (date, os, country, app_id)
);

CREATE INDEX IF NOT EXISTS idx_dw_pub_country ON dw_app_monthly (publisher_country, date, os);
CREATE INDEX IF NOT EXISTS idx_dw_unified     ON dw_app_monthly (unified_app_id, date);
CREATE INDEX IF NOT EXISTS idx_dw_publisher   ON dw_app_monthly (publisher_id, date);
CREATE INDEX IF NOT EXISTS idx_dw_date_os     ON dw_app_monthly (date, os);
