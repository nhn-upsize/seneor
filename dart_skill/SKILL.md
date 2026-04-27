# DART 공시 재무 분석 스킬

## 스킬 사용 시점

사용자가 다음 주제에 대해 물으면 이 스킬의 표준 조건을 따라 답변하세요:
- 한국 게임사 재무제표 (매출/영업이익/순이익/자산/부채/자본)
- 인건비 / 광고비 / 비용 구조 분석
- 분기별 실적 추이
- M&A / 합병인수 / 공시 내역
- 신작 게임 정보
- DART API 계정과목 검색

## 데이터베이스 연결

- DB: `AI_mobilegame` (PostgreSQL, Sensor Tower 데이터와 동일 DB)
- MCP: `postgres` 서버 연결 사용
- 접속: `postgresql://postgres:upsize@localhost:5432/AI_mobilegame`

---

## 데이터 개요

- **출처**: DART XBRL(22~25) + DART API + 전체공시 + 수동 정리
- **대상**: 한국 게임사 30개
- **기간**: 2022~2025 (4개년)
- **단위**: 원(KRW). DB 컬럼은 모두 **원 단위 BIGINT**
- **억원 환산**: `/100000000.0`

### 회사 목록 (30개)

NHN, 골프존, 네오위즈, 넥슨게임즈, 넥슨지티, 넵튠, 넷마블, 더블유게임즈, 데브시스터즈, 드래곤플라이, 모비릭스, 미투온, 스코넥, 시프트업, 썸에이지, 액토즈소프트, 엔씨소프트, 엠게임, 웹젠, 위메이드, 위메이드맥스, 위메이드플레이, 조이시티, 카카오게임즈, 컴투스, 컴투스홀딩스, 크래프톤, 펄어비스, 플레이위드, 한빛소프트

---

## 테이블 구조 (6개)

### 1. `dart_company` — 회사 마스터

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `corp_code` (PK) | VARCHAR(20) | DART 고유번호 |
| `corp_name` | VARCHAR(100) | 회사명 |

### 2. `dart_financial_summary` — 연간 요약재무

PK: `(corp_code, fs_type, year)`

| 구분 | 컬럼명 | 한글명 |
|---|---|---|
| **핵심** | revenue | 매출액 |
| | operating_income | 영업이익 |
| | net_income | 당기순이익 |
| | pretax_income | 세전이익 |
| | eps | 기본주당이익 |
| | total_assets | 자산총계 |
| | total_liabilities | 부채총계 |
| | total_equity | 자본총계 |
| | current_assets | 유동자산 |
| | current_liabilities | 유동부채 |
| | noncurrent_liabilities | 비유동부채 |
| | tangible_assets | 유형자산 |
| | intangible_assets | 무형자산 |
| | goodwill | 영업권 |
| **현금흐름** | cash_and_equivalents | 현금및현금성자산 |
| | cf_operating | 영업현금흐름 |
| | cf_investing | 투자현금흐름 |
| | cf_financing | 재무현금흐름 |
| **비용** | cost_of_sales | 매출원가 |
| | sga_total | 판매비와관리비합계 |
| | commission_fees | 지급수수료 |
| | depreciation | 감가상각비 |
| | amortization | 무형자산상각비 |
| | rnd_expense | 연구개발비 |
| | advertising_expense | 광고선전비 |
| | income_tax | 법인세비용 |
| | finance_income | 금융수익 |
| | finance_cost | 금융비용 |
| | interest_expense | 이자비용 |
| **인건비** | labor_total | 인건비합계 |
| | labor_employee_benefit | 종업원급여합계 |
| | labor_salary | 단기급여 |
| | labor_welfare | 복리후생비 |
| | labor_retirement | 퇴직급여 |
| | labor_retirement_db | 퇴직급여DB |
| | labor_retirement_dc | 퇴직급여DC |
| | labor_stock_comp | 주식보상 |
| | labor_wage | 임금 |
| | labor_bonus | 상여 |
| | labor_consolation | 위로금 |
| **메타** | labor_source | 인건비출처 |
| | ad_source | 광고비출처 |

**참고**: 모든 회사·연도에 전 컬럼이 채워지지는 않음 (sparse). NULL은 해당 데이터 없음.

`fs_type` 값:
- `'연결'` — 연결재무제표 (자회사 포함)
- `'별도'` — 별도재무제표 (본사만)

### 3. `dart_financial_quarterly` — 분기 재무

PK: `(corp_code, fs_type, quarter)`

| 컬럼 | 설명 |
|---|---|
| quarter | `'2022Q1'` ~ `'2025Q4'` |
| revenue | 매출액 |
| operating_income | 영업이익 |
| labor_cost | 인건비 |
| advertising_expense | 광고선전비 |
| is_estimated | 추정 여부 (연간÷4 역산) |

**주의사항**:
- 분기 데이터는 DART XBRL 분기/반기보고서에서 당분기(3개월) 수치를 직접 추출. Q4는 연간 사업보고서 수치에서 Q1~Q3 합을 차감하여 역산
- `is_estimated = true`인 경우 XBRL 미제공으로 연간 총합을 4등분한 추정치. 해당 기업: 시프트업(2022~2024년 일부 분기)
- 현재 연결 기준만 수록
- 분기별 인건비/광고선전비는 별도 정리한 엑셀 데이터 반영. 연간 수치는 분기 합산으로 대체

**회사별 예외사항**:
- **카카오게임즈 2024년**: 연중 연결범위 변경으로 분기 XBRL과 사업보고서 수치가 불일치하여, 사업보고서 기준 수치로 수동 반영
- **조이시티 2025년**: 연간 매출액 원본 데이터 오류로 분기 합산 기준(1,404억)으로 수정
- **데브시스터즈, 조이시티, 스코넥**: XBRL에 `ifrs-full:Revenue` 태그가 없어 `ifrs-full:GrossProfit`(영업수익) 태그를 매출액으로 사용
- **분기재무 수록 범위**: 현재 26개 게임사 수록. 해외 공시 기업(넥슨, 그라비티) 등은 추후 추가 예정

### 4. `dart_financial_account` — API 전체 계정과목

PK: `id` (SERIAL) / INDEX: `(corp_code, year, fs_type)`

| 컬럼 | 설명 |
|---|---|
| account_name | 계정명 (한글) |
| account_code | DART 계정 코드 |
| amount_current | 당기 금액 |
| amount_previous | 전기 금액 |
| amount_before_prev | 전전기 금액 |

- DART `fnlttSinglAcntAll` API의 전체 계정과목 (~39,700건)
- 요약재무에 없는 세부 항목을 검색할 때 사용

### 5. `dart_disclosure` — 공시목록

PK: `id` (SERIAL) / INDEX: `(corp_code)`, UNIQUE: `(corp_code, receipt_no)` WHERE NOT NULL

| 컬럼 | 설명 |
|---|---|
| receipt_no | 접수번호 (합병인수 등 일부 NULL) |
| category | 공시 카테고리 |
| disclosure_date | 날짜 (YYYYMMDD) |
| title | 제목 |
| detail | 상세 (JSONB, 합병비율·인수금액 등) |

카테고리 목록 (12개):
`사업보고서`, `분기반기`, `주주총회`, `자기주식`, `합병인수`, `잠정실적`, `배당`, `임원변경`, `유상증자`, `전환사채`, `최대주주변경`, `기타`

**합병인수 카테고리 특이사항**: 접수번호 없이 detail JSONB에 `대상회사`, `인수시기`, `인수금액`, `지분율`, `인수배경`, `인수후현황` 등이 저장된 건이 있음 (DART 공시가 아닌 수동 정리 데이터)

### 6. `dart_new_game` — 신작정보

PK: `id` (SERIAL) / INDEX: `(corp_code)`

| 컬럼 | 설명 |
|---|---|
| game_name | 게임명 |
| game_type | 구분 (출시작/개발중 등) |
| release_date | 출시일 |
| platform | 플랫폼 |
| genre | 장르 |
| performance | 성과 |
| service_status | 서비스상태 |

---

## 표준 조건 (필수 준수)

### 1. 금액 단위

- DB 값은 **원(KRW)** 단위 BIGINT
- 응답 시 **억원으로 환산**: `/ 100000000.0`
- 표시: `1,234억원` 또는 소수점 필요 시 `1,234.5억원`

### 2. 기본 재무제표 유형

- 사용자가 명시하지 않으면 **연결(`'연결'`)** 기준으로 응답
- 별도 재무제표는 사용자가 "별도" 또는 "본사만"이라고 요청할 때만 사용

### 3. 비율 계산

자주 쓰는 비율:
```sql
-- 영업이익률
ROUND(operating_income * 100.0 / NULLIF(revenue, 0), 1)
-- 순이익률
ROUND(net_income * 100.0 / NULLIF(revenue, 0), 1)
-- 부채비율
ROUND(total_liabilities * 100.0 / NULLIF(total_equity, 0), 1)
-- 인건비율
ROUND(labor_total * 100.0 / NULLIF(revenue, 0), 1)
-- 광고비율
ROUND(advertising_expense * 100.0 / NULLIF(revenue, 0), 1)
-- ROE
ROUND(net_income * 100.0 / NULLIF(total_equity, 0), 1)
```

### 4. NULL 처리

- 회사마다 채워진 필드가 다름 (sparse 데이터)
- 비율 계산 시 반드시 `NULLIF(분모, 0)` 사용
- 결과에 NULL이 많으면 "해당 데이터 미공시"로 안내

### 5. 분기 데이터 주의

- `is_estimated = true`이면 "추정치(연간÷4)" 표시
- Q4 역산 데이터는 오차 가능성 있음을 안내

---

## Sensor Tower 교차 분석

Sensor Tower 데이터(`st_*` 테이블, `/sensor` 스킬)와 DART 데이터를 함께 볼 때:

- **매출 단위 주의**: st_ 테이블은 **USD 센트**, dart_ 테이블은 **KRW 원**
- **집계 단위 차이**: st_는 앱 단위, dart_는 회사(법인) 단위
- **매핑 테이블**: `dart_st_publisher_map`으로 조인 (corp_code ↔ publisher_name)
- 비교 시 반드시 단위 차이와 집계 범위 차이를 명시

### 매핑 테이블: `dart_st_publisher_map`

PK: `(corp_code, publisher_name)`

ST의 같은 퍼블리셔가 여러 이름으로 등록되어 있어 1:N 매핑. 조인 예시:
```sql
SELECT c.corp_name, d.publisher_name, ...
FROM dart_st_publisher_map m
JOIN dart_company c ON c.corp_code = m.corp_code
JOIN dw_app_monthly d ON d.publisher_name = m.publisher_name
WHERE ...
```

### 매핑 현황 (30개사)

| DART 회사명 | ST publisher_name | 비고 |
|---|---|---|
| NHN | NHN Corp. | |
| 골프존 | GOLFZON Corp. | |
| 네오위즈 | NEOWIZ / NEOWIZ corp | |
| 넥슨게임즈 | - | 해외 퍼블리셔, DART 데이터 없음 |
| 넥슨지티 | - | 해외 퍼블리셔, DART 데이터 없음 |
| 넵튠 | Neptune Company / Neptune Corp. | |
| 넷마블 | Netmarble / Netmarble Corporation | |
| 더블유게임즈 | DoubleUGames / DoubleUGames Co., Ltd. | |
| 데브시스터즈 | Devsisters / Devsisters Corporation | |
| 드래곤플라이 | DRAGONFLY GF CO., LTD. | |
| 모비릭스 | mobirix / MOBIRIX | |
| 미투온 | - | ST 미등록 |
| 스코넥 | - | ST 미등록 |
| 시프트업 | - | 개발사 (퍼블리싱: Level Infinite) |
| 썸에이지 | - | ST 미등록 |
| 액토즈소프트 | - | ST 미등록 |
| 엔씨소프트 | NC Corporation / NCSOFT | |
| 엠게임 | Mgame / MGAME Corp. | |
| 웹젠 | Webzen Inc. / WEBZEN INC. | |
| 위메이드 | Wemade Co., Ltd / Wemade Co., Ltd. | |
| 위메이드맥스 | Wemade Max Co., Ltd. | |
| 위메이드플레이 | Wemade Connect / Wemade Connect Co., Ltd. / Wemade Play Co.,Ltd. | 구 위메이드커넥트 |
| 조이시티 | JOYCITY Corp / JOYCITY Corp. | |
| 카카오게임즈 | Kakao Games Corp. | |
| 컴투스 | Com2uS / Com2uS Corp. / Com2uS Japan Inc. | |
| 컴투스홀딩스 | Com2uS Holdings | |
| 크래프톤 | KRAFTON Inc / KRAFTON, Inc. | |
| 펄어비스 | PEARL ABYSS / Pearl Abyss Corp. | |
| 플레이위드 | PLAYWITH Inc / PlaywithKorea Inc. | |
| 한빛소프트 | HanbitSoft Inc / hanbitsoft inc. | |

- **매핑 완료**: 23개사 (ST publisher_name 42건)
- **매핑 불가**: 7개사 (넥슨게임즈, 넥슨지티, 미투온, 스코넥, 시프트업, 썸에이지, 액토즈소프트)

---

## 응답 원칙

1. **억원 환산**: 모든 금액은 억원으로 변환해서 표시
2. **연결 기본**: 재무제표 유형은 연결이 기본
3. **기준 명시**: 어떤 테이블/연도/fs_type으로 뽑았는지 명시
4. **NULL 안내**: 데이터 없는 항목은 "미공시"로 표기
5. **추정 표시**: 분기 추정치는 반드시 표시

---

## 참고 파일

- `reference/dart_schema.sql` — DB 스키마 DDL
- `reference/query_templates.sql` — 자주 쓰는 쿼리 모음
