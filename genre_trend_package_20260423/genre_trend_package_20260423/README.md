# 국가별·연도별·장르별 월평균 매출 추이 — 쿼리 & 코드 패키지

## 📦 포함 파일

| 파일 | 용도 |
|---|---|
| `01_main_query_by_country.sql` | 국가별 × 연도별 × 장르(effective_genre) × 월평균 매출 — 차트/표의 메인 데이터 소스 |
| `02_representative_games.sql` | 장르별 대표 게임 TOP 1~2 (누적 매출 기준) |
| `03_period_comparison_null_excluded.sql` | 22~24 vs 25~26Q1 월평균 비교 (진입월 수 기반, NULL 제외) |
| `04_validation_country_totals.sql` | 국가별 TOP 100 전체 월평균 (표 하단 합계 행 검증용) |
| `05_lv2_genre_distribution.sql` | lv2_genre × genre 조합별 앱 수 분포 확인 |
| `html_template.html` | HTML 대시보드 템플릿 (Chart.js 라인차트 + 탭 시스템) |

## 🎯 분석 설계 요약

### 대상
- **국가**: KR / JP / US 3개국
- **데이터 소스**: `dw_app_monthly` (Sensor Tower, NHN 내부 AI_mobilegame DB)
- **필터**: `in_revenue_top100_unified_os = true` (iOS+Android 합산 매출 TOP 100)
- **기간**: 2022 ~ 2026 Q1

### 매출 단위
- 기본 컬럼: **`revenue_krw_100`** (= `revenue_usd ÷ 0.7 × 연도별환율`)
- 센서타워 100% 보정 (÷0.7) + 한국은행 연도별 확정 환율 적용
  - 2022: 1,292 / 2023: 1,307 / 2024: 1,364 / 2025: 1,422 / 2026: 1,409 (임시)

### 장르 분류 규칙 (effective_genre)

```
1. Card·Casino·Board 장르 통합 후 lv2_genre(PvP/PvE)로만 분리
   - 'Card+Casino+Board / PvP (웹보드)'
   - 'Card+Casino+Board / PvE (카지노)'
   - 'Card+Casino+Board / 미분류'
2. Role Playing
   - KR: MMORPG / 비MMORPG 구분 유지 (+ 방치형 lv2)
   - JP/US: RPG 통합 (MMORPG·비MMORPG 구분 제거) + 방치형만 별도
3. 기타 장르: genre [/ sub_genre] [/ lv2_genre] 조합
```

### 특수 예외
- **Disney Solitaire (SuperPlay)**: ST 분류상 lv2_genre=PvE 이지만, 업무적으로 PvE에서 제외하여 CCB/미분류로 이동 (쿼리 내 name 기반 예외 처리)

### 기간 평균 계산 원칙 ⭐
- **NULL 제외, 진입월만 대상**: 해당 장르가 TOP 100에 없던 월은 분모에서 제외
- **22~24 월평균** = `AVG(month_rev) WHERE year BETWEEN 2022 AND 2024` (진입월 수가 분모)
- **25~26Q1 월평균** = `AVG(month_rev) WHERE year IN (2025, 2026)` (진입월 수가 분모)
- 이유: 런칭 전 게임을 0으로 합산하면 성장률이 과장됨

## 🔁 재실행 순서

1. **`01_main_query_by_country.sql`** 을 KR/JP/US 각각 실행 → 국가별 `(year, effective_genre, monthly_avg_eok)` 결과 확보
2. **`02_representative_games.sql`** 1회 실행 → `(country, eg)` 별 대표 게임 1~2개 확보
3. **`03_period_comparison_null_excluded.sql`** 1회 실행 → 22~24 vs 25~26Q1 평균 확보
4. **`04_validation_country_totals.sql`** 1회 실행 → 표 하단 합계 행 검증
5. `html_template.html` 의 하드코딩 데이터(`makeChart('chart-xx', [...])` 및 `<tr>` 행)에 위 결과 반영

## 📊 최신 결과 파일 위치

`../genre_trend_3countries_20260423_1622.html` (Disney Solitaire PvE 제외 반영 버전)

## ⚠️ 주의사항

- 월 데이터가 매월 추가되므로 쿼리 재실행 시 숫자는 달라질 수 있음
- `dw_app_monthly` 는 매월 ETL 후 갱신되며 MAU·demographics 는 보강 로직 포함
- 대표 게임은 누적 매출 기준이라 연도별 1위와 다를 수 있음
- Disney Solitaire 예외는 수동 규칙 — 향후 유사 사례(Solitaire 류가 PvE로 자동 분류되는 케이스) 발견 시 쿼리 내 예외 패턴 확장 필요
