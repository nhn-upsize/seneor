---
name: sensor
description: Sensor Tower 모바일 게임 마켓 데이터 분석 스킬. PostgreSQL DB(AI_mobilegame)에서 TOP 100 앱/퍼블리셔 매출, 광고/오가닉 다운로드, 신규 진입 게임 등을 표준화된 조건으로 조회. 사용자가 게임 매출, 퍼블리셔 순위, 다운로드 채널, 신규 게임 진입 등을 물을 때 사용.
---

# Sensor Tower 모바일 게임 마켓 분석 스킬

## 스킬 사용 시점

사용자가 다음 주제에 대해 물으면 이 스킬의 표준 조건을 따라 답변하세요:
- 모바일 게임 매출 / 다운로드 / TOP 100
- 퍼블리셔 순위 / 퍼블리셔 국가 분석
- 광고/오가닉(paid/organic) 다운로드
- 신규 진입 게임 (연도별)
- MAU / 차트 순위

## 데이터베이스 연결

- DB: `AI_mobilegame` (PostgreSQL)
- MCP: `postgres` 서버 연결 필요
- 접속: `postgresql://postgres:upsize@<호스트>:5432/AI_mobilegame`

자세한 테이블 구조는 `reference/schema_v8.sql` 참조. 테이블별 수집 기준은 `reference/db_table_summary.md` 참조.

### 분석용 DW 테이블: `dw_app_monthly` (앱별 지표의 단일 진실 공급원)

**앱별 지표는 항상 `dw_app_monthly`를 최우선으로 사용하세요.** 특히 다음 지표는 반드시 dw 값을 먼저 읽습니다 — raw 소스 테이블을 따로 조회하지 마세요:

| 지표 | dw 컬럼 | 원칙 |
|---|---|---|
| **장르** | `genre` | **항상 단일 값 기준** (ST `Storefront Game Subcategory` 대표 태그). 여러 장르를 합치거나 categories JSONB를 다시 파싱하지 말 것 |
| **하위장르** | `sub_genre` | Role Playing 앱만 `MMORPG` / `비MMORPG` 구분. 그 외 장르는 NULL. `app_genre_override.sub_genre`에서 관리 |
| **광고유입률 (paid ratio)** | `paid_ratio`, `paid_abs`, `organic_abs`, `browser_abs` | dw의 사전 계산값 사용. `st_download_channels` 직접 조회 지양 |
| **Demographics (성별)** | `female_pct`, `male_pct` | dw에 분기→월 forward-fill됨 |
| **연령대 / 평균연령** | `avg_age_total`, `age_breakdown` (JSONB) | dw 컬럼 사용. `st_app_demographics` 직접 조회 지양 |
| **매출/다운로드/MAU** | `revenue_usd`, `units`, `mau` | 이미 USD 변환, 월·국가·OS 정규화 완료 |
| **MAU 커버리지** | `mau` | 매출 TOP 100 기준: US 100% / JP ~98.7% / KR ~90.4% (2026-04 기준). NULL은 ST 데이터 미제공 — 분석 시 "일부 KR 앱은 MAU 미공시" 명시 |
| **앱 메타 (이름/퍼블리셔/국가)** | `name`, `publisher_name`, `publisher_country` | dw 기준으로 집계, st_app_detail 재조인 불필요 |

복합 분석(매출+다운로드채널+MAU+앱메타를 함께 보는 경우)에는 **`dw_app_monthly`** 사용이 기본값입니다.
이미 모든 소스가 조인되어 있고 매출은 USD로 변환돼 있습니다.

- **Grain**: `(date, os, country, app_id)` — 월 × OS × 마켓국가 × 앱
- **포함 컬럼**: `revenue_usd`, `revenue_usd_100p`, `revenue_krw_100`, `units`, `mau`, `rank_revenue/units/mau`, `organic_abs`, `paid_abs`, `browser_abs`, `paid_ratio`, `name`, `publisher_name`, `publisher_country`, `genre`, `in_revenue_top100` / `in_units_top100` / `in_mau_top100` / `in_publisher_top100` (OS별 source flags), **`in_revenue_top100_unified_os`** (iOS+Android 합산 매출 TOP 100)
- **데이터 범위**: 2022-01 ~ 최신 수집월 (약 140,000행)
- **demographics**: 분기→월 forward-fill (female_pct, male_pct, avg_age_total, age_breakdown JSONB) — 89% 커버
- **MAU**: 3중 소스 (active_users TOP 2000 → US는 profile custom_tags fallback → 매월 ETL에서 per-app `/v1/{os}/usage/active_users`로 매출 TOP 100 NULL 보강). 매출 TOP 100 기준 평균 96.4% 커버, KR이 가장 낮음 (~90%)
- **st_master_apps / st_master_publishers 는 v7에서 삭제됨** — 월별 고유 앱 리스트가 필요하면 dw_app_monthly에서 source flags 또는 소스 테이블 UNION으로 직접 추출

단, raw 소스 테이블 직접 조회가 더 적합한 경우도 있습니다:
- `st_top_charts`: 스토어 차트 순위 (topgrossing 등) — dw에 미포함
- `st_store_summary` / `st_games_breakdown`: 카테고리/장르 단위 전체 집계 — dw에 미포함
- 센트(cents) 원본 값이 필요한 경우

---

## 표준 집계 조건 (필수 준수)

### 1. "TOP 100" 용어 해석

| 사용자 요청 | 해석 | 사용 테이블 |
|---|---|---|
| "TOP 100 뽑아줘" | **월별 매출 기준** TOP 100 (iOS+Android 합산) | `dw_app_monthly` WHERE `in_revenue_top100_unified_os = true` |
| "OS별 TOP 100 뽑아줘" | **월별 매출 기준** OS별 각각 TOP 100 | `st_top_apps_downloads_revenue` (measure='revenue') |
| "스토어 기준 월별 TOP 100" | 매월 1일자 스토어 매출 차트 TOP 100 | `st_top_charts` (chart_type='topgrossing', rank ≤ 100) |
| "다운로드 TOP 100" | 월별 다운로드 기준 TOP 100 | `st_top_apps_downloads_revenue` (measure='units') |
| "MAU TOP 100" | 월별 MAU 기준 TOP 100 | `st_top_apps_active_users` (measure='MAU') |
| "퍼블리셔 TOP 100" | 월별 매출 기준 퍼블리셔 TOP 100 | `st_top_publishers` (measure='revenue') |

**매출 TOP 100 요청 시 반드시 `dw_app_monthly.in_revenue_top100_unified_os = true`를 사용하세요.** 이 컬럼은 월별 × 국가별로 iOS+Android 합산 매출 기준 TOP 100이 `true`로 표시됩니다. OS별 각각의 TOP 100이 아닌 **통합 TOP 100**이 기본값입니다.

```sql
-- 매출 TOP 100 기본 쿼리
SELECT unified_app_id, name, country,
       SUM(revenue_krw_100) AS total_krw
FROM dw_app_monthly
WHERE in_revenue_top100_unified_os = true
  AND date = '2026-03-01'
GROUP BY unified_app_id, name, country
ORDER BY total_krw DESC;
```

**응답 시 반드시 어떤 기준으로 집계했는지 명시하세요.**

예: "2026년 3월 매출 기준 TOP 100 앱입니다 (iOS+Android 합산, dw_app_monthly.in_revenue_top100_unified_os 기준)"

### 2. 매출 단위 변환 & 100% 보정

**센서타워 매출은 실제의 약 70% 추정치**이므로 100% 보정 컬럼을 제공합니다. 집계·보고는 기본적으로 **100p 기준**을 사용하세요.

#### 단위 체계

| 컬럼/값 | 의미 | 위치 |
|---|---|---|
| `revenue_absolute`, `revenue_delta` 등 | 센트(cents) 단위, ST 추정치(70%) | raw st_* 테이블 |
| `revenue_usd` | USD, ST 추정치(70%) | dw_app_monthly |
| **`revenue_usd_100p`** | USD, **100% 보정** (= revenue_usd / 0.7) | dw_app_monthly ⭐ |
| **`revenue_krw_100`** | KRW, **100% 보정 + 연도별 환율 적용** (= revenue_usd / 0.7 × 연도환율) | dw_app_monthly ⭐⭐ |

#### 연도별 환율 (`fx_rate_yearly` 테이블)

| 연도 | USD/KRW | 기준 |
|---|---:|---|
| 2022 | 1,292 | 한국은행 확정치 |
| 2023 | 1,307 | 한국은행 확정치 |
| 2024 | 1,364 | 한국은행 확정치 |
| 2025 | 1,422 | 한국은행 확정치 |
| 2026 | 1,409 | 임시 |

**원화 집계는 `revenue_krw_100`을 사용**하면 연도별 환율이 자동 반영됩니다 (월 데이터의 해당 연도 환율). 이 컬럼이 원칙적인 기본값.

#### 응답 규칙

- **기본 보고는 `revenue_krw_100` 컬럼 사용** — 연도별 환율 + 100% 보정이 자동 적용됨
- 여러 연도를 합산하는 경우에도 `SUM(revenue_krw_100)`로 정확 (각 월이 해당 연도 환율로 변환됨)
- 사용자가 특정 환율을 지시한 경우만 `revenue_usd_100p × 지정환율`로 수동 계산
- 표시 형식: `1,703,903,673원 (연도별 한국은행 환율 + 센서타워 100% 보정 적용)`
- 표일 경우 표 상단/하단에 **"연도별 환율(2022:1,292 / 2023:1,307 / 2024:1,364 / 2025:1,422 / 2026:1,409) + 센서타워 100% 보정(÷0.7) 적용"** 한 번만 표기
- 필요 시 70% 기준도 병기: `100% 환산 17.0억원 / ST 추정치(70%) 11.9억원`

#### raw 테이블 직접 조회 시 (표준 공식)

raw `st_*` 테이블에는 100% 보정 컬럼이 없으므로 **매번 아래 공식을 쿼리에 포함**하세요. 별도 뷰는 만들지 않는 정책입니다 (dw 우선 원칙 유지).

**대상 테이블**: `st_top_apps_downloads_revenue`, `st_top_publishers`, `st_top_publishers_apps`, `st_games_breakdown`, `st_store_summary`, `st_app_detail.last_month_revenue`

**표준 공식 (항상 이 패턴 사용)**:
```sql
SELECT
    t.revenue_absolute / 100.0                AS revenue_usd,       -- ST 원본 (70%)
    t.revenue_absolute / 70.0                 AS revenue_usd_100p,  -- USD 100% 보정
    t.revenue_absolute / 70.0 * fx.rate_krw   AS revenue_krw_100p   -- ⭐ 기본값 (원화 100%)
FROM <매출테이블> t
JOIN fx_rate_yearly fx ON fx.year = EXTRACT(YEAR FROM t.date)::int
```

**주의**:
- `st_app_detail.last_month_revenue`는 단일 컬럼이라 별도 date 컬럼 기준으로 환율 적용 필요 (보통 최근 month 기준)
- `st_games_breakdown`, `st_store_summary`의 `revenue` 컬럼도 동일하게 `/70.0 * fx.rate_krw` 적용
- **컬럼 별칭은 반드시 `revenue_krw_100p` / `revenue_usd_100p`** (dw와 동일 네이밍)

단, **앱별 분석은 `dw_app_monthly.revenue_krw_100` 우선 사용** (스킬 §앱별 지표는 dw 우선 원칙).

### 3. 기본 기간

- 기본값: **월(month)**
- `date_granularity=monthly`, `time_range='month'` 사용
- 월 데이터는 `YYYY-MM-01` 형식으로 저장 (해당 월 전체 집계)

### 4. 기본 마켓 국가 (3개)

사용자가 국가를 명시하지 않으면:
- **KR** (한국)
- **JP** (일본)
- **US** (미국)

이 3개 국가별로 각각 집계하고 함께 표시.

### 5. 퍼블리셔 국가 그룹핑 (5개 그룹)

퍼블리셔 국가별 집계 시 반드시 다음 5개 그룹으로 분류:

| 그룹 | 포함 국가 (`st_app_detail.publisher_country`) |
|---|---|
| **JP (일본)** | Japan |
| **KR (한국)** | South Korea |
| **중화권** | China, Hong Kong, Taiwan, Macao |
| **북미** | US, USA, United States, Canada |
| **기타** | Finland, Singapore, Turkey, Israel, United Kingdom, Switzerland, Cyprus, Ireland, Sweden, 나머지 국가 전부 |

### 6. 특수 케이스 (퍼블리셔 국가 강제 재분류)

퍼블리셔 국가 그룹 집계 시, 아래 퍼블리셔는 `publisher_country` 값과 무관하게 지정 그룹으로 강제 분류:

| 퍼블리셔 | ST 등록 국가 | 강제 분류 | 판별 조건 |
|---|---|---|---|
| **NEXON** | Japan | **KR** | `publisher_name ILIKE '%NEXON%'` |
| **FUNFLY** | Singapore | **중화권** | `publisher_name ILIKE '%FUNFLY%'` |

> 쿼리에서는 CASE 문 맨 위에 이 두 규칙을 먼저 적용한 뒤, 그 다음에 `publisher_country` 기반 일반 분류를 적용해야 합니다 (§Q4 템플릿 참조).

### 7. 광고 집행률 (Paid vs Organic)

**중요**: Sensor Tower의 `Advertised on Any Network` 태그는 "광고 집행 여부"만 알려주므로 부정확합니다.

광고 집행 정도를 집계할 때는 **paid/organic 다운로드 절대값**을 사용:
- 출처: `st_download_channels` (unified_app_id 기반)
- `paid_abs` = 유료 광고 다운로드 (paid_display + paid_search)
- `organic_abs` = 오가닉 다운로드 (organic_browse + organic_search)
- `browser_abs` = 브라우저 유입

**"광고 유입"의 정의**: `paid` 채널로 분류된 다운로드만 포함.

광고 집행률 계산 예:
```sql
paid_abs / (organic_abs + paid_abs + browser_abs) AS paid_ratio
```

### 8. 신규 진입 게임 집계 (필수 질문)

**"2022~2024년 TOP 100 신규 진입"** 같은 요청을 받으면, 반드시 **어떤 방법**으로 집계할지 사용자에게 먼저 질문하세요:

#### 방법 1: 매출 기준 TOP 100 (`st_top_apps_downloads_revenue`)
- 각 연도 **1월에는 TOP 100에 없다가**, 같은 연도 **2~12월 중 처음 진입**한 게임
- 월별 평균 = 해당 게임 수 / 11 (2~12월)
- SQL 예시:
```sql
WITH jan_apps AS (
    SELECT DISTINCT os, country, app_id
    FROM st_top_apps_downloads_revenue
    WHERE measure='revenue' AND category='game'
      AND date = '2023-01-01'
),
rest AS (
    SELECT DISTINCT ON (os, country, app_id) os, country, app_id, date
    FROM st_top_apps_downloads_revenue
    WHERE measure='revenue' AND category='game'
      AND date BETWEEN '2023-02-01' AND '2023-12-01'
    ORDER BY os, country, app_id, date
)
SELECT COUNT(*) / 11.0 AS avg_per_month
FROM rest r
WHERE NOT EXISTS (SELECT 1 FROM jan_apps j
                  WHERE j.os=r.os AND j.country=r.country AND j.app_id=r.app_id);
```

#### 방법 2: 스토어 매출 기준 TOP 100 (`st_top_charts`, topgrossing)
- 위와 동일하지만 `st_top_charts`에서 `chart_type='topgrossing'`, `rank <= 100` 사용
- 매월 1일자 스토어 차트 기준

**반드시 응답 전에 사용자에게 어느 방법을 원하는지 물어보세요.**

### 9. Demographics (성별/연령대)

- 출처: `st_app_demographics` (분기 단위 수집, Q1 2022 ~ Q1 2026, 17분기)
- `dw_app_monthly`에는 분기→월 forward-fill로 포함 (`female_pct`, `male_pct`, `avg_age_total`, `age_breakdown` JSONB)
- 커버리지: 약 89% (일부 앱은 Sensor Tower에 demographics 데이터 없음)
- `age_breakdown` JSONB 구조: `{"female_0": 0.02, "female_18": 0.13, "female_25": 0.12, ..., "male_55": 0.03}`
- 연령 구간: 0~17 / 18~24 / 25~34 / 35~44 / 45~54 / 55+ (여성/남성 각각)
- `st_demographics_baseline`: 국가별 전체 인구 베이스라인 (앱 수치와 비교용, 102행)

---

## 응답 원칙

1. **기준 명시**: 모든 집계 결과에 어떤 테이블/기준으로 뽑았는지 명시
2. **매출 KRW 환산 표시 + 100% 보정**: 기본은 `revenue_krw_100` 컬럼 사용 (= revenue_usd / 0.7 × 연도별 환율). 환율과 "센서타워 100% 보정 적용" 명시. 사용자가 특정 환율 지시한 경우만 `revenue_usd_100p × 지정환율`로 수동 계산
3. **국가 그룹화**: 퍼블리셔 국가는 5개 그룹으로 집계
4. **넥슨·FUNFLY 예외**: NEXON→KR, FUNFLY→중화권 강제
5. **광고 집행**: paid_abs 기반, organic과 비교
6. **신규 진입**: 방법 1 or 2 질문 후 집계
7. **앱별 지표는 dw 우선**: 장르·광고유입률·demographics·연령은 `dw_app_monthly` 컬럼을 먼저 사용. 특히 **장르는 항상 단일 값 (dw.genre) 기준**이며 categories JSONB를 재파싱하지 않음
8. **Role Playing 세분류**: RPG 분석 시 `sub_genre` 컬럼으로 MMORPG와 비MMORPG 구분 가능. "RPG 매출" 요청 시 MMORPG/비MMORPG 별도 집계 또는 합산 여부 확인

---

## 자주 쓰는 쿼리 템플릿

### Q1: 특정 월 매출 TOP 100 (국가/OS별) — 원화 100% 보정

```sql
WITH revenue_ranked AS (
    SELECT
        t.country, t.os, t.app_id,
        t.revenue_absolute / 70.0 * fx.rate_krw AS revenue_krw_100p,
        t.units_absolute AS downloads,
        ROW_NUMBER() OVER (PARTITION BY t.country, t.os ORDER BY t.revenue_absolute DESC) AS rank
    FROM st_top_apps_downloads_revenue t
    JOIN fx_rate_yearly fx ON fx.year = EXTRACT(YEAR FROM t.date)::int
    WHERE t.date = '2026-03-01'
      AND t.measure = 'revenue'
      AND t.category = 'game'
)
SELECT rank, country, os, app_id,
       ROUND(revenue_krw_100p::numeric, 0) AS revenue_krw_100p, downloads
FROM revenue_ranked
WHERE rank <= 100
ORDER BY country, os, rank;
```

### Q2: 퍼블리셔 매출 TOP 10 + 장르 비중

`reference/query_templates.sql` 참조.

### Q3: 신규 진입 게임 (매출 기준)

```sql
WITH jan_apps AS (
    SELECT DISTINCT os, country, app_id
    FROM st_top_apps_downloads_revenue
    WHERE measure='revenue' AND category='game' AND date='{year}-01-01'
),
new_entries AS (
    SELECT DISTINCT os, country, app_id
    FROM st_top_apps_downloads_revenue
    WHERE measure='revenue' AND category='game'
      AND date BETWEEN '{year}-02-01' AND '{year}-12-01'
)
SELECT os, country, COUNT(*) AS new_count, ROUND(COUNT(*)/11.0, 1) AS avg_per_month
FROM new_entries n
WHERE NOT EXISTS (
    SELECT 1 FROM jan_apps j 
    WHERE j.os=n.os AND j.country=n.country AND j.app_id=n.app_id
)
GROUP BY os, country;
```

### Q4: 퍼블리셔 국가 그룹 매출 — 원화 100% 보정

```sql
SELECT
    CASE
        WHEN d.publisher_name ILIKE '%NEXON%' THEN 'KR'
        WHEN d.publisher_name ILIKE '%FUNFLY%' THEN '중화권'
        WHEN d.publisher_country IN ('South Korea') THEN 'KR'
        WHEN d.publisher_country IN ('Japan') THEN 'JP'
        WHEN d.publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
        WHEN d.publisher_country IN ('US','USA','United States','Canada') THEN '북미'
        ELSE '기타'
    END AS pub_group,
    SUM(t.revenue_absolute / 70.0 * fx.rate_krw) AS total_revenue_krw_100p
FROM st_top_publishers t
JOIN fx_rate_yearly fx ON fx.year = EXTRACT(YEAR FROM t.date)::int
LEFT JOIN LATERAL (
    SELECT * FROM st_app_detail a WHERE a.publisher_id=t.publisher_id
    ORDER BY a.collected_date DESC LIMIT 1
) d ON TRUE
WHERE t.date = '2026-03-01' AND t.category = 'game' AND t.measure='revenue'
GROUP BY pub_group
ORDER BY total_revenue_krw_100p DESC;
```

---

## 참고 파일

- `reference/schema_v8.sql` — DB 스키마 전체 (v8: master 제거 + dw_app_monthly + demographics 수집 완료)
- `reference/db_table_summary.md` — 테이블별 수집 기준 상세
- `reference/etl_flow.pptx` — 수집 파이프라인 흐름도
- `reference/query_templates.sql` — 자주 쓰는 쿼리 모음
