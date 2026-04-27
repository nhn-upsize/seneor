# NHN 모바일 게임 신규 출시 검토 — 시장 분석 프로젝트

## 프로젝트 개요

| 항목 | 내용 |
|---|---|
| **목적** | NHN의 Board/Casino/Card 외 신규 장르 출시 및 해외(US) 진출 검토를 위한 데이터 기반 시장 분석 |
| **분석 기간** | 2022-01 ~ 2026-02 (약 4년 2개월) |
| **대상 시장** | KR (한국), JP (일본), US (미국) |
| **데이터 소스** | Sensor Tower API + DART 공시 (한국 게임사 30개) |
| **DB** | PostgreSQL `AI_mobilegame` (10.77.13.162:5432) |
| **작성일** | 2026-04-14 ~ 15 |

---

## 최종 산출물

### 보고용 (이사님 전달)

| 파일 | 설명 |
|---|---|
| **`NHN_market_analysis.html`** | **통합 보고서 (파일 1개)** — 3개 탭으로 구성, 브라우저에서 바로 열림, DB 불필요 |

탭 구성:
1. **한국 시장 인사이트** — 시장 변화 요약, 4년 추이, 성장/하락 영역, NHN 전략 방향
2. **A~G 분석 트리 & 결과** — 7단계 분석 프레임워크 + 아코디언 형태 분석 결과
3. **데이터 기준 명세** — 테이블별 기준, 집계 방식, 주의사항

### 내부 보관용

| 파일 | 설명 |
|---|---|
| `analysis_queries.sql` | A~G 전체 쿼리 30개 (DB 재실행용) |
| `analysis_results.json` | 전체 결과 데이터 JSON (DB 없이 데이터 확인용) |
| `market_research_mindmap.html` | 메인 분석 (통합 전 개별 파일) |
| `kr_market_insight.html` | 한국 시장 인사이트 (통합 전 개별 파일) |
| `data_criteria.html` | 데이터 기준 명세 (통합 전 개별 파일) |
| `layout_sample.html` | 레이아웃 비교 샘플 (탭 vs 아코디언) |

---

## 분석 프레임워크 (A~G 7단계)

```
A. 시장 전체 흐름 → B. 수익 구조 → C. 유저 프로필 → D. 경쟁 환경
    → E. 출시 조건 → F. 출시 후 생존 → G. 재무 역량 (DART)
```

| 단계 | 질문 | 핵심 결론 |
|---|---|---|
| **A** | 시장이 어디로 가고 있나? | KR +14% 유일 성장, JP -15% 하락, US $12B 압도적 |
| **B** | 어디에 돈이 되는가? | KR RPG 44% 편중, US Casino+Card+Board $2.8B |
| **C** | 유저는 누구인가? | Board/Casino/Card 55+ 고연령, Puzzle 95% 여성 |
| **D** | 경쟁 상황은? | KR 퍼블 66%→50%, 중화권 22%→30% 상승 |
| **E** | 성공하려면? | Puzzle 6M생존 77% 최고, US iOS TOP100 월 $1.5M |
| **F** | 출시 후 생존은? | Casino US 38.4개월 최장수, RPG 8.6개월 최단 |
| **G** | 재무 체력은? | NHN 현금 1.56조 1위, 넷마블 광고비 20% vs NHN 3.5% |

---

## 주요 데이터 테이블

| 테이블 | 용도 | Grain |
|---|---|---|
| `dw_app_monthly` | DW 통합 (매출+DL+MAU+UA+앱메타) | 월 × OS × 국가 × 앱 |
| `st_top_publishers` | 퍼블리셔 매출/DL TOP100 | 월 × OS × 국가 × 퍼블리셔 |
| `st_app_profile` | 앱 프로필 (성별/연령/리텐션 등) | 수집일 × OS × 앱 |
| `st_store_summary` | 스토어 전체 매출 (Android만) | 월 × OS × 국가 |
| `dart_financial_summary` | 한국 게임사 연간 재무 | 회사 × 회계유형 × 연도 |
| `dart_new_game` | 한국 게임사 신작 | 회사 × 게임 |
| `dart_disclosure` | 한국 게임사 공시 | 회사 × 공시 |

---

## 데이터 제약사항

| 제약 | 영향 |
|---|---|
| 성별/연령 = **WW(글로벌) 기준만** | 국가별 분리 불가. Asia 56%, 북미 25%, 유럽 15% |
| 성별/연령 = **스냅샷 1회분** | 시계열 변화 추적 불가 |
| st_store_summary = **Android만** | iOS HHI 산출 불가 |
| NEXON = JP 등록 | **KR 퍼블리셔로 강제 분류**하여 집계 |
| DART 재무 = **연결재무** | 게임 외 사업 매출 포함 (NHN 결제/클라우드 등) |
| 분석 제외 태그 8개 | 여성시장추이, 유저고령화, R&D투자, 인당매출 등 |

---

## 퍼블리셔 분류 기준

### 국적 5개 그룹
| 그룹 | 포함 국가 |
|---|---|
| KR | South Korea + NEXON(JP 등록이지만 KR 강제) |
| JP | Japan |
| 중화권 | China, Hong Kong, Taiwan, Macao |
| 북미 | US, USA, United States, Canada |
| 기타 | 나머지 전부 |

### 경쟁사 분석 대상 (D2)
Supercell, NEXON, Cygames, Netmarble, Level Infinite, Kakao Games, SQUARE ENIX, NHN Corp., NCSOFT, Habby, NHN PlayArt, Com2uS, KRAFTON, Wemade 등 16개사

### DART 재무 분석 대상 (G)
NHN, 넥슨, 넷마블, 크래프톤, 카카오게임즈, 엔씨소프트, 컴투스 (7개사)

---

## 핵심 결론: NHN 전략 방향

1. **Puzzle 최우선 확장** — KR 4년 +257%, 장수(JP 27.6개월), 유저 유사(35+). 이미 3개 개발 중
2. **US Card/Board 진출** — NHN 핵심 역량의 US 시장 $2.8B (KR의 17배)
3. **Strategy 검토** — 3국 최고 성장(KR +261%). 중화권 경쟁 치열
4. **오가닉/IP 강화** — NHN Paid 28.5%, Casino/Card 오가닉 63% 활용
5. **현금 1.56조 활용** — 7개사 중 현금 1위

---

## 프로젝트 히스토리

| 날짜 | 작업 |
|---|---|
| 2026-04-14 | 분석 프레임워크 설계 (A~G 7단계), HTML 트리 생성 |
| 2026-04-14 | DB 쿼리 추출 (30개), dw_app_monthly + DART 테이블 |
| 2026-04-14 | 하단 분석 결과 카드 22개 생성, N/A 12개→8개 태그 처리 |
| 2026-04-14 | kr_market_insight.html 생성 (한국 시장 인사이트) |
| 2026-04-14 | data_criteria.html 생성 (데이터 기준 명세) |
| 2026-04-14 | 아코디언 레이아웃으로 전면 재구성 |
| 2026-04-14 | 연간 기준('22→'25) 통일, 4년 추이 바차트 추가 |
| 2026-04-15 | 3개 HTML → NHN_market_analysis.html 탭 방식 통합 |

---

## 재현 방법

### HTML 보고서만 보는 경우
`NHN_market_analysis.html`을 브라우저에서 열면 됨 (DB 불필요)

### 데이터를 다시 뽑는 경우
```bash
# 1. DB 접속
psql -h 10.77.13.162 -U postgres -d AI_mobilegame

# 2. 쿼리 실행
\i analysis_queries.sql

# 3. 또는 MCP postgres 연결
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame
```

### 결과 데이터만 확인
`analysis_results.json` 파일 참조 (A~G 섹션별 구조화된 JSON)
