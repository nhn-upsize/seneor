# queries/ — 쿼리 지도

26년 1·2분기 보고서 수치를 뽑은 쿼리 전부와, **3분기에 뭘 어떻게 바꾸는지** 정리한 문서입니다.

```
queries/
├── generated/26.1H/    보고서 본체 SQL 13개 — 자동 생성 (손으로 고치지 말 것)
└── manual/             파이프라인이 커버하지 않는 섹션 22개 — 손으로 유지
    ├── 01_시장총계/
    ├── 02_퍼블리셔/
    ├── 03_장르/
    ├── 04_웹보드/
    └── 05_신규진입/
```

집계 표준은 **[`../docs/QUARTERLY.md`](../docs/QUARTERLY.md)** 에 있습니다. 쿼리를 새로 쓰거나 고치기 전에 읽으세요.

---

## 1. 보고서 본체 — `generated/` (자동)

`report_pipeline/queries.py` 가 `config.py` 기준으로 생성합니다. 기간·환율·국적 분류·장르 매핑이
전부 한 곳에서 나오므로 규칙이 쿼리마다 갈라지지 않습니다.

| 파일 | 내용 |
|---|---|
| `step1_{KR,JP,US}.sql` | 국가별 총매출·MAU·DL 추이 |
| `step2_{KR,JP,US}.sql` | 퍼블리셔 국적별 (KR/JP/중화권/북미/기타) |
| `step3_{KR,JP,US}.sql` | 장르별 |
| `step4_{KR,JP,US}.sql` | 퍼블리셔 국적 × 장르 |
| `combined_genre.sql` | 3국 합산 장르 |

### 3분기 절차

**① `report_pipeline/config.py` 의 PERIOD 블록만 수정**

```python
PARTIAL = {"label": "26.1~3Q", "start": "2026-01-01",
           "end_exclusive": "2026-10-01", "months": 9}
POST    = {"full_years": [2025], "include_partial": True, "months": 21}  # 12 + 9
FULL_YEARS = [2022, 2023, 2024, 2025]   # 그대로
```

**② 다시 덤프**

```bash
python -m report_pipeline.dump_sql
```

→ `queries/generated/26.1~3Q/` 에 13개가 새로 생깁니다. 이전 분기 폴더는 남습니다.

**③ 그 SQL을 DB에 실행해 값을 얻고 HTML 갱신** — 수기 추정 금지.

> `generated/` 안의 파일을 손으로 고치면 다음 덤프 때 덮어써집니다.
> 쿼리 로직을 바꿔야 하면 `report_pipeline/queries.py` 를 고치세요.

---

## 2. 나머지 섹션 — `manual/` (수동)

`verify/*.py` 안에 파이썬 f-string으로 조립돼 있던 SQL을 **실행 시점에 가로채 파일로 뽑은 것**입니다.
자리표시자가 없는 완성된 쿼리라 DB 툴에 그대로 붙여 넣으면 됩니다.
스크립트 1개 = 파일 1개이고, 파일 안에서 `-- ── [n/m] ──` 주석으로 쿼리를 구분했습니다.

| 폴더 | 파일 | 내용 |
|---|---|---|
| **01_시장총계** | `verify_all_sum.sql` | 3국 합산 매출·MAU·ARPMAU·DL 연도별 |
| | `verify_jp_all.sql` · `verify_us_all.sql` | JP·US 시장 전체 수치 |
| | `verify_kr_dl.sql` | KR 다운로드 |
| | `verify_mau_arpmau.sql` | 3국 MAU·ARPMAU |
| **02_퍼블리셔** | `verify_kr_top5.sql` | KR TOP5 퍼블리셔 연도별 월평균 매출 |
| | `verify_kr_market_composition.sql` | KR 퍼블 국적별 구성 |
| | `verify_kr_etc_*.sql` (4) | 기타 KR 퍼블 게임수·퍼블수 (정규화 전후 버전들) |
| | `check_publisher_share.sql` | 중화권 침투 점유율 |
| **03_장르** | `verify_kr_strategy.sql` | KR/중화권 Strategy, KR MMORPG |
| | `check_step4_values.sql` | 국적×장르 교차 검증 |
| **04_웹보드** | `verify_wb_quarterly.sql` | KR 웹보드 분기별 매출 (Card+Casino+Board 통합) |
| | `verify_wb_all4.sql` | 웹보드 Step1~4 종합 |
| | `verify_wb_exclude_disney.sql` | Disney Solitaire 제외 재검증 |
| | `verify_wb_kr_pub.sql` | KR 퍼블리셔 기준 |
| | `query_webboard_data.sql` · `query_wpl_check.sql` | 웹보드 원자료 조회 |
| **05_신규진입** | `verify_kr_newgame_genre.sql` | KR TOP100 신규 진입, 국적×장르 연도별 |

### 3분기에 할 일

**기간이 쿼리 안에 하드코딩돼 있습니다.** 날짜를 직접 늘려야 합니다.

- 대부분 `date >= '2026-01-01' AND date < '2026-04-01'` 형태 → 끝 날짜를 `2026-10-01` 로
- `verify_wb_quarterly.sql` 은 분기 목록이 26.1Q에서 끝남 → 26.2Q·26.3Q 추가
- 신규 진입은 `first_date < '2026-01-01'` 범위 확인

**정본은 `verify/*.py` 입니다.** `manual/` 은 읽고 붙여넣기 쉬우라고 뽑아둔 사본입니다.
파이썬을 고쳤으면 아래를 다시 돌려 사본을 갱신하세요 — 둘이 갈라지면 안 됩니다.

```bash
python -m report_pipeline.extract_manual_sql
```

(DB 접속 없이 동작합니다. 가짜 커서를 물려 실행하면서 최종 SQL만 가로챕니다.)

---

## 3. 장르 추이 — `../genre_trend_package_20260423/`

장르별 매출 추이 전용 쿼리 5개(+README)가 별도 폴더에 있습니다.
`effective_genre` 커스텀 분류, Disney Solitaire 예외, NULL 제외 평균 등 장르 분석 표준이 여기 있습니다.
**기간이 하드코딩**돼 있어 3분기에 쓰려면 날짜를 직접 고쳐야 합니다.

---

## 자주 어긋나는 기준

- **중화권 = China · Hong Kong · Taiwan · Macao 만. 싱가포르는 절대 포함하지 않음**
  (예외는 FUNFLY 강제분류 하나. 2026-09에 `config.py` 와 verify 스크립트 5개에서
  싱가포르가 들어가 있던 것을 수정했습니다 — `manual/` 은 수정 후 기준으로 추출됨)
- **NEXON → KR** 강제분류
- **월평균 분모 = 달력 개월수 고정** (활동월 수 아님)
- **연평균은 월별 SUM 후 평균** — `GROUP BY name` + `AVG` 는 OS 이중 카운트로 50% 오류
- 매출은 `revenue_krw_100` (환율 반영 완료 컬럼)
