# report_pipeline — sensor_dashboard 보고서 자동화 (쿼리팩 + 검증기)

기간만 늘려서 보고서를 재생성할 때, **① 수치는 한 곳(설정)에서 재산출**하고
**② HTML의 "안 바뀐 곳/서로 안 맞는 곳"을 자동으로 잡아내기** 위한 파이프라인.

이번(2026-07) 세션에서 겪은 문제 — *같은 숫자가 카드·배너·표·해설 5~6곳에 복제돼
하나 고칠 때 나머지를 놓침* — 을 구조적으로 막는다.

```
report_pipeline/
├── config.py     ← ★ 다음 업데이트 때 여기만 수정 (기간·환율·규칙의 단일 출처)
├── queries.py    ← 쿼리 팩: config 기준으로 각 섹션 SQL 생성 (규칙 중복 제거)
├── validate.py   ← 검증기: HTML 자기정합성 전수검사 (DB 불필요)
└── README.md
```

---

## 핵심 규칙 (이미 표준화됨)
- 매출 = `dw_app_monthly.revenue_krw_100` (환율 반영 완료 컬럼 — 쿼리에서 환율계산 불필요)
- **월평균 분모 = 달력 개월수 고정** (÷활동월 아님): 연 12 · 26.1H 6 · 전 36 · 후 18
  → 장르/국적 각 행의 합이 합계와 정확히 일치 (자기정합)
- 국적: NEXON→KR · FUNFLY→중화권 / effective_genre: KR만 sub로 RPG 분리

---

## 다음 업데이트 절차 (예: 26.1H → 26년 연간)

1. **`config.py` 수정** — `PARTIAL` / `POST` / `FULL_YEARS` 만 바꾼다.
   (예: 26년 하반기 데이터 적재 후 → `FULL_YEARS`에 2026 추가, `PARTIAL`을 27.1H로)

2. **쿼리 팩 실행 → 수치 확보.** 두 가지 방법:
   - (권장) **Claude 세션에서**: "report_pipeline로 기간 갱신해줘" →
     Claude가 `queries.all_queries()`의 각 SQL을 postgres(MCP)로 실행해 값을 뽑고
     HTML을 갱신. 값은 전부 이 쿼리에서 나오므로 재조회·수기추정 불필요.
   - (독립 실행) psycopg2 + DB 접속정보가 있으면 각 SQL을 직접 실행:
     ```
     python -c "from report_pipeline import queries as Q; print(Q.step3_genre('KR'))"
     ```
     생성 SQL은 세션에서 검증됨 — KR Step3 등 대시보드 값을 그대로 재현.

3. **HTML 반영 후 반드시 검증기 실행:**
   ```
   python -m report_pipeline.validate
   ```
   - `✅ 불일치 0건` → 자기정합 통과 (배포 OK)
   - `❌ …` → 그 목록이 곧 "안 바뀐 곳" — 0건 될 때까지 수정 후 재실행

---

## 검증기가 잡는 것 (CHECKS)
- **[C1] Step2 국적별 표: 메인 == TOP5 + 기타** (22·23·24·25·부분·전·후 전 컬럼)
  → 이번 세션의 KR 메인 26.1H 1,822 오류(정답 1,885, TOP5+기타)를 -63 차이로 잡아냄.
  허용오차 `max(12, 0.5%)` — 반올림·파이프라인 노이즈(±수억)는 통과.
- **[C2] 한눈에 카드 전→후 == 해당국 헤드라인 전→후** (카드 미갱신 드리프트)

새 불변식은 `validate.py`의 `CHECKS` 리스트에 함수 하나 추가하면 확장됨
(예: Step3 장르행 합==합계, Step4 조합 임계, 배너/step-a 상호일치 등).

---

## 한계 / 다음 단계
- 현재 Step2 국적 매출표는 일부 파이프라인(china_share) 산물이라 라이브 쿼리와
  ±수억 노이즈가 있음(허용오차로 통과 처리). 완전 일치를 원하면 Step2도
  queries.step2_nationality 로 통일 필요.
- 검증기는 "자기정합"(HTML 내부 일관성)까지. "DB 최신값과 일치"까지 보려면
  report_data.json(쿼리팩 출력)과 대조하는 [C3] 데이터검증을 추가하면 됨.
- 완전 자동생성(HTML 템플릿화)은 별도 대규모 작업 — 필요 시 진행.
