# NHN 모바일 게임 시장 분석

KR·JP·US 3개국 모바일 게임 시장을 **분기 단위로 분석·발행**하는 저장소입니다.
Board/Casino/Card 외 신규 장르 출시 및 해외 진출 검토가 목적입니다.

보고서는 GitHub Pages로 발행되며, **전달할 링크는 이 문서가 아니라 메신저로 공유합니다.**
여기에는 발행·유지보수 규칙만 둡니다.

---

## 저장소 구조

```
seneor/
├── index.html      최신 분기로 보내는 리다이렉트 (Pages 랜딩)
├── reports.html    전체 분기 목록
├── 26Y1Q/          분기별 산출물 — 폴더 하나 = 분기 하나
├── 26Y2Q/          index.html(본편) · summary.html(요약본)
│
├── CLAUDE.md       작업 규칙 요약 (고치기 전에 읽을 것)
├── docs/
│   └── QUARTERLY.md    ★ 분기 보고서 작업 가이드
├── report_pipeline/    기간 연장 재생성 (config 단일출처 + 자기정합 검증기)
│
├── src/            재사용 라이브러리 (API 클라이언트·설정)
├── collect/        Sensor Tower API 수집
├── build/          보고서·슬라이드 생성
├── verify/         집계 검증 쿼리 (분기마다 재실행)
│
├── queries/ · genre_trend_package_20260423/    분석용 SQL
└── sensor_skill/ · dart_skill/                 DB 조회 스킬 정의
```

| 주소 | 가리키는 곳 |
|---|---|
| `/seneor/` | 최신 분기 보고서. **분기마다 대상이 바뀝니다** |
| `/seneor/reports.html` | 전체 분기 목록. 주소 고정 |
| `/seneor/26Y2Q/` | 특정 분기 고정 주소 |

**밖으로 링크를 공유할 때는 `/26Y2Q/` 형식을 쓰세요.** 루트는 다음 분기가 나오면 대상이 바뀝니다.
`#tab-country-deep` · `#tab-webboard` · `#tab-newgame` · `#tab-criteria` 를 붙이면 특정 탭이 바로 열립니다.

---

## 새 분기를 추가할 때

새 분기는 **새로 만드는 게 아니라 기간을 연장하는 것**입니다. 프레임은 그대로 두고
`report_pipeline/config.py` 의 PERIOD 블록만 바꿔 데이터를 재산출합니다.
집계 기준·검증 절차·자주 나는 실수는 **[docs/QUARTERLY.md](docs/QUARTERLY.md)** 에 있습니다.
**작업 전에 반드시 읽으세요.**

발행 단계는 다음 4가지입니다.

1. `26Y3Q/` 폴더에 본편 `index.html`, 요약본 `summary.html` 을 넣습니다.
2. 각 `<title>` 을 `26년 3분기 시장 분석 보고서 — NHN 모바일 게임 시장 분석` 형식으로 맞춥니다.
3. **루트 `index.html` 의 리다이렉트 경로 두 줄**(`meta refresh` · `link rel=canonical`)을
   새 폴더로 바꿉니다. ← **빼먹으면 루트가 계속 이전 분기를 가리킵니다.**
4. `reports.html` 맨 위에 분기 블록을 추가하고 `최신` 배지를 옮깁니다.

파일을 옮기거나 이름을 바꾸면 옛 주소는 404가 됩니다. **밖에 공유된 적 있는 주소라면**
리다이렉트 stub(`meta refresh` 한 줄)을 그 경로에 남기세요. 현재 남아 있는 stub은 없습니다.

### 용어 규칙

이름이 갈라지지 않도록 **아래 표기만** 사용합니다.

| 대상 | 표기 | 쓰지 않는 표현 |
|---|---|---|
| 분기 — 폴더·파일 | `26Y2Q` | `26Q2`, `2026Q2` |
| 분기 — 화면·문서명 | `26년 2분기` | `2Q`, `1Q vs 2Q`, `26년 상반기` |
| 문서① 4탭 본편 | `26년 2분기 시장 분석 보고서` | 종합, 대시보드 |
| 문서② 1장 요약 | `26년 2분기 요약본` | 요약, 흐름 분석 |

파일명은 문서 종류만 나타냅니다(`index.html` / `summary.html`). 분기는 폴더가, 버전은 git이 관리합니다.

---

## 실행 환경

```bash
pip install -r requirements.txt
cp .env.example .env     # 값을 채운 뒤 사용
```

접속 정보는 **코드에 넣지 않습니다.** `.env` 에 `SENSOR_TOWER_API_TOKEN` 과
`AI_MOBILEGAME_DSN`(PostgreSQL 접속 문자열) 두 개를 넣으세요. `.env` 는 커밋되지 않습니다.

```bash
python collect/collect_all_v2.py       # API 수집
python build/build_exec_report.py      # 보고서 생성
python verify/verify_all_sum.py        # 집계 검증 (개별 쿼리)
python -m report_pipeline.validate     # HTML 자기정합성 — 발행 전 필수, ✅ 0건까지
```

스크립트는 저장소 루트에서 실행하는 것을 전제로 합니다.

### 커밋하지 않는 것

`.env` · `data/` `data_raw/` `output/` `reports/` `*.csv` `*.xlsx`(**Sensor Tower 라이선스 데이터**) ·
`__pycache__/` `.cache/`. 발행할 HTML은 `reports/` 가 아니라 **분기 폴더에 직접** 넣어야 커밋됩니다.

---

## 분석 기준 (요약)

**분석 프레임워크 A~G** — ⒜시장 흐름 ⒝수익 구조 ⒞유저 프로필 ⒟경쟁 환경 ⒠출시 조건
⒡출시 후 생존 ⒢재무 역량(DART). 데이터는 Sensor Tower API + DART 공시(한국 게임사 30개),
PostgreSQL `AI_mobilegame` 에 적재.

**집계 표준**

- 매출 TOP100 · OS 통합(`unified_os`) 기준, `dw_app_monthly` 중심
- 퍼블리셔 국적 5그룹 — KR / JP / 중화권 / 북미 / 기타
- **NEXON은 JP 등록이지만 KR로 강제 분류**
- **중화권 = China·Hong Kong·Taiwan·Macao 만. 싱가포르 제외**
- 매출은 `revenue_usd_100p`(스토어 수수료 포함 Gross), 환율은 연도별 평균 적용

**주의**

- 성별·연령은 **WW 기준 스냅샷 1회분** — 국가별 분리도, 시계열 추적도 불가
- `st_store_summary` 는 **Android만** — iOS 점유율 산출 불가
- DART 재무는 **연결재무** — 게임 외 사업 매출 포함(NHN 결제/클라우드 등)

> 해당 분기의 정확한 집계 기준은 보고서 **④데이터 기준·집계 명세** 탭에 있습니다.
> 이 요약과 다르면 **보고서 쪽이 맞습니다.**

---

## 히스토리

| 시기 | 작업 |
|---|---|
| 2026-04 | 분석 프레임워크 설계(A~G), 26년 1분기 보고서 발행 |
| 2026-07 | 26년 2분기 보고서·요약본 발행 |
| 2026-09 | 분기 폴더 체계·용어 규칙 도입, 스크립트 정리, 인증 정보 환경변수 전환 |
