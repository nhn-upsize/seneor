# DB 테이블 수집 기준 (v6)

대상 DB: `AI_mobilegame` (PostgreSQL)
기간: 2022-01 ~ 2026-03 (51개월)
카테고리: game (서브장르 추가예정)

## 파이프라인 구조

### 마스터 파이프라인 (월별 TOP 100 → 마스터 → 앱 상세/채널)

| 테이블 | 수집 기준 | TOP | 분류 축 | 월당 행수 | 누적(51개월) | API |
|---|---|---|---|---|---|---|
| **st_top_apps_downloads_revenue** | 매출 TOP 100 + 다운로드 TOP 100 (각각 별도 호출) | 100 | 월별 × OS(android,ios) × 마켓국가(US,KR,JP) × game × measure(revenue,units) | 1,200 | 61,200 | `/v1/{os}/sales_report_estimates_comparison_attributes` |
| **st_app_profile** | sales_report 응답의 custom_tags JSONB 저장 (리텐션, ARPDAU, 광고집행 여부 등) | 전부 | 월별 × OS × 고유 app_id (sales_report에서 자동 수집) | ~839 | ~42,782 | (sales_report에 포함) |
| **st_top_publishers** | 매출 TOP 100만 (다운로드 제외) | 100 | 월별 × OS × 마켓국가(US,KR,JP) × game × measure(revenue) | 600 | 30,600 | `/v1/{os}/top_and_trending/publishers` |
| **st_top_publishers_apps** | TOP 100 퍼블리셔의 하위 앱 (API 응답 내 포함) | 전부 | st_top_publishers 종속 | ~5,814 | ~296,532 | (publishers에 포함) |
| **st_top_apps_active_users** | MAU TOP 100 (DAU/WAU 제외) | 100 | 월별 × OS × 마켓국가(US,KR,JP) × game × measure(MAU) | 600 | 30,600 | `/v1/{os}/top_and_trending/active_users` |

### 마스터 레지스트리 (내부 빌드, API 호출 없음)

| 테이블 | 수집 기준 | 월당 고유 | 누적 |
|---|---|---|---|
| **st_master_apps** | sources: revenue_top100 + units_top100 + mau_top100 + publisher_apps (4개 소스 UNION) | ~2,210 | 9,556 |
| **st_master_publishers** | sources: revenue_top100 (1개 소스) | ~441 | 1,107 |

### 마스터 기반 파생 (API 호출)

| 테이블 | 수집 기준 | 누적 | API |
|---|---|---|---|
| **st_app_detail** | st_master_apps의 app_id로 앱 메타정보 (호출 시점 스냅샷) | ~9,556 (1회 스냅샷) | `/v1/{os}/apps` |
| **st_download_channels** | st_app_detail의 unified_app_id로 Paid/Organic 월별 집계 | ~497,915 | `/v1/{os}/downloads_by_sources` |

### 독립 파이프라인 (마스터와 무관)

| 테이블 | 수집 기준 | TOP | 월당 | 누적 | API |
|---|---|---|---|---|---|
| **st_top_charts** | 매월 1일 기준 차트 순위 TOP 100 (free/paid/grossing) | 100 | 1,800 | 91,800 | `/v1/{os}/ranking` |
| **st_store_summary** | 카테고리 × 마켓국가(US,KR,JP,WW) 전체 집계 | - | 8 | 408 | `/v1/{os}/store_summary` |
| **st_games_breakdown** | 게임 장르 × 마켓국가(US,KR,JP,WW) 전체 집계 | - | 8 | 408 | `/v1/{os}/games_breakdown` |

### 보류

| 테이블 | 상태 | 이유 |
|---|---|---|
| **st_app_demographics** | 보류 | API가 quarterly/all_time만 지원, 월별 수집 불가 |
| **st_demographics_baseline** | 보류 | 동일 |

## 중요 사항

### 매출 단위
- 모든 `revenue_*` 필드는 **센트(cents) 단위**
- USD 변환: `revenue_absolute / 100.0`

### 국가 체계
- **마켓국가** (판매 국가): `st_top_*` 테이블의 `country` — 한국/일본/미국 시장 구분
- **퍼블리셔 국가** (법인 소재지): `st_app_detail.publisher_country` — 5개 그룹으로 집계 (JP/KR/중화권/북미/기타)

### 카테고리 (iOS ↔ Android 통합)
DB 저장 시 Android 스타일로 통일:
- `game` = 게임 전체
- `game_action`, `game_puzzle`, ... 서브장르 17개

iOS API 호출 시에는 숫자 코드 사용 (6014, 7001~7018) 후 DB 저장 전 변환.

### 자동화
- 마스터 테이블(`st_master_*`)은 `app_detail` 또는 `download_channels` 실행 시 **자동 재빌드**
- 수동 빌드: `psql -f build_master.sql`

## 기간 범위
- 수집 완료: **2022-01 ~ 2026-03** (51개월)
- 월 데이터는 `YYYY-MM-01` 형식 (해당 월 전체 집계)
- `st_top_charts`만 해당 월 1일 시점 스냅샷
