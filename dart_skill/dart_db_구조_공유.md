# 한국게임사 DART 공시 DB

## 원본 JSON 구조

**파일**: `한국게임사_풀DB_v2.json`
**파일 크기**: 10.8 MB / **회사 수**: 30개 / **데이터 범위**: 2022~2025 (4개년)

### 최상위 구조

```json
{
  "_메타": { ... },           // 메타데이터
  "NHN": { ... },            // 회사별 데이터 (30개)
  "넷마블": { ... },
  ...
}
```

### 회사별 하위 구조 (7개 키)

| 키 | 설명 | 구조 |
|---|---|---|
| `corp_code` | DART 고유번호 | `string` |
| `요약재무` | 연간 핵심 재무제표 | `{연결/별도} → {연도} → {항목: 금액}` |
| `API재무계정` | DART API 전체 계정과목 | `{연도} → {연결/별도} → [{계정명, 코드, 당기, 전기, 전전기}]` |
| `재무비율` | 부채비율/ROE 등 | 현재 전 회사 **빈 객체** |
| `공시목록` | 카테고리별 공시 | `{카테고리} → [{날짜, 제목, 접수번호, ?상세}]` |
| `신작정보` | 신규 게임 정보 | `[{게임명, 구분, 출시일, 플랫폼, 장르, 성과, 서비스상태}]` |
| `분기재무` | 분기별 재무 | `{연결} → {2022Q1~2025Q4} → {매출액, 영업이익, 인건비, 광고선전비}` |

### 세부 필드

**요약재무** — 연도별 최대 ~40개 필드:
- 핵심: 매출액, 영업이익, 당기순이익, 자산/부채/자본총계
- 현금흐름: 영업/투자/재무현금흐름, 현금및현금성자산
- 비용상세: 인건비(합계 + 단기급여/복리후생/퇴직급여DB·DC/주식보상 등 9항목), 광고선전비, 지급수수료, 매출원가, 감가상각비, 연구개발비
- 기타: 금융수익/비용, EPS, 유동자산/부채, 유형/무형자산, 영업권

**공시목록** — 12개 카테고리:
- 사업보고서, 분기반기, 주주총회, 자기주식, 합병인수, 잠정실적, 배당, 임원변경, 유상증자, 전환사채, 최대주주변경, 기타

### 데이터 규모

| 데이터 | 총 건수 |
|---|---:|
| API재무계정 레코드 | ~39,700건 |
| 공시 건수 | ~5,400건 |
| 신작정보 | 176건 |
| 분기재무 (30사 × 16분기) | ~480건 |

---

## PostgreSQL 테이블 설계

**DB**: `AI_mobilegame` / **접두사**: `dart_` (Sensor Tower `st_`와 구분)

| 테이블 | PK | 적재 건수 |
|---|---|---:|
| `dart_company` | `corp_code` | 30 |
| `dart_financial_summary` | `corp_code, fs_type, year` | 229 |
| `dart_financial_quarterly` | `corp_code, fs_type, quarter` | 464 |
| `dart_financial_account` | `id` (SERIAL) | 39,734 |
| `dart_disclosure` | `id` (SERIAL) | 5,374 |
| `dart_new_game` | `id` (SERIAL) | 176 |

### `dart_financial_summary` 컬럼 (40개)

금액 단위: 원(KRW). 억원 환산 시 `/100000000`

| 구분 | 컬럼 |
|---|---|
| **핵심 재무 (14)** | revenue, operating_income, net_income, pretax_income, eps, total_assets, total_liabilities, total_equity, current_assets, current_liabilities, noncurrent_liabilities, tangible_assets, intangible_assets, goodwill |
| **현금흐름 (4)** | cash_and_equivalents, cf_operating, cf_investing, cf_financing |
| **비용 항목 (11)** | cost_of_sales, sga_total, commission_fees, depreciation, amortization, rnd_expense, advertising_expense, income_tax, finance_income, finance_cost, interest_expense |
| **인건비 상세 (11)** | labor_total, labor_employee_benefit, labor_salary, labor_welfare, labor_retirement, labor_retirement_db, labor_retirement_dc, labor_stock_comp, labor_wage, labor_bonus, labor_consolation |
| **메타 (2)** | labor_source, ad_source |

> 회사·연도마다 채워진 필드가 다름 (sparse). NULL = 해당 데이터 미공시.
