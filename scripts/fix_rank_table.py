# -*- coding: utf-8 -*-
"""
'국가별 매출 순위별 월평균 규모' 테이블의 하드코딩 수치를 현재 DB 기준으로 재계산 후 교체.

공식 (HTML 기재와 동일):
- unified TOP100 (in_revenue_top100_unified_os=TRUE)
- 연간 순위 = SUM(revenue_krw_100) 내림차순
- 월평균 = 연매출 / 등장월수
- 대상: 1/10/20/50/100위 × KR/JP/US × 22/23/24/25/26.1Q
"""
import re, psycopg2

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 연도별 월수 (26.1Q = 3)
PERIODS = [
    ('2022', '2022-01-01', '2022-12-01', 12),
    ('2023', '2023-01-01', '2023-12-01', 12),
    ('2024', '2024-01-01', '2024-12-01', 12),
    ('2025', '2025-01-01', '2025-12-01', 12),
    ('26.1Q', '2026-01-01', '2026-03-01', 3),
]
COUNTRIES = ['KR', 'JP', 'US']
RANKS = [1, 10, 20, 50, 100]

# {country: {period: {rank: value_eok}}}
data = {c: {p[0]: {} for p in PERIODS} for c in COUNTRIES}

for p_label, start, end, _months in PERIODS:
    cur.execute("""
    WITH app_year AS (
        SELECT country, unified_app_id,
               SUM(revenue_krw_100) AS yr_rev,
               COUNT(DISTINCT date) AS months_in
        FROM dw_app_monthly
        WHERE in_revenue_top100_unified_os=TRUE
          AND country IN ('KR','JP','US')
          AND date BETWEEN %s AND %s
        GROUP BY country, unified_app_id
    ),
    ranked AS (
        SELECT country, yr_rev / NULLIF(months_in, 0) AS monthly_avg,
               ROW_NUMBER() OVER (PARTITION BY country ORDER BY yr_rev DESC NULLS LAST) AS r
        FROM app_year
        WHERE yr_rev IS NOT NULL
    )
    SELECT country, r, ROUND((monthly_avg/1e8)::numeric, 0) AS eok
    FROM ranked WHERE r IN (1,10,20,50,100)
    ORDER BY country, r;
    """, (start, end))
    for country, r, eok in cur.fetchall():
        data[country][p_label][int(r)] = int(eok) if eok is not None else None

cur.close(); conn.close()

# 출력
print('[현재 DB 기준 재계산 결과]')
for c in COUNTRIES:
    print(f"\n{c}:")
    for p_label, _, _, _ in PERIODS:
        print(f"  {p_label}: {data[c][p_label]}")

# ============================================================
# HTML 교체 — 각 국가 테이블의 <tbody>...</tbody> 재생성
# ============================================================
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
o_open = html.count('<div'); o_close = html.count('</div>')

def fmt(v):
    if v is None: return '-'
    return f"{v:,}"

def make_tbody(country):
    rows = []
    for rank in RANKS:
        extra = ' style="border-top:2px solid #93c5fd;"' if (rank==100 and country=='KR') else \
                (' style="border-top:2px solid #fca5a5;"' if (rank==100 and country=='JP') else \
                (' style="border-top:2px solid #d8b4fe;"' if (rank==100 and country=='US') else ''))
        cells = [f'<td style="padding:4px 6px;font-weight:600;">{rank}위</td>']
        for p_label, _, _, _ in PERIODS:
            v = data[country][p_label].get(rank)
            is_26 = (p_label == '26.1Q')
            style = 'padding:4px 6px;background:#fef3c7;' if is_26 else 'padding:4px 6px;'
            cells.append(f'<td class="num" style="{style}">{fmt(v)}</td>')
        rows.append(f'              <tr{extra}>' + ''.join(cells) + '</tr>')
    return '\n'.join(rows)

# KR 교체
KR_TBODY_RE = re.compile(
    r'(🇰🇷 KR 한국.*?<tbody>\n)(.*?)(\n            </tbody>)',
    re.DOTALL
)
# 이모지가 &#x1F1F0;&#x1F1F7; 로 escape 되어있음
KR_ANCHOR_RE = re.compile(
    r'(&#x1F1F0;&#x1F1F7; KR 한국.*?<tbody>\n)(.*?)(\n            </tbody>)',
    re.DOTALL
)
JP_ANCHOR_RE = re.compile(
    r'(&#x1F1EF;&#x1F1F5; JP 일본.*?<tbody>\n)(.*?)(\n            </tbody>)',
    re.DOTALL
)
US_ANCHOR_RE = re.compile(
    r'(&#x1F1FA;&#x1F1F8; US 미국.*?<tbody>\n)(.*?)(\n            </tbody>)',
    re.DOTALL
)

# 한 번만 (첫 번째 매칭 = '국가별 매출 순위별 월평균 규모' 테이블 — 두 번째는 80/20 집중도로 동일 이모지 사용)
# 안전하게 step-q 텍스트로 범위 찾아서 그 안에서만 교체
target_header = '국가별 매출 순위별 월평균 규모'
target_start = html.find(target_header)
target_end = html.find('매출 집중도 분석 &mdash; 80/20 법칙')
if target_start == -1 or target_end == -1:
    raise RuntimeError('Target range not found')
section = html[target_start:target_end]

for country, regex in [('KR', KR_ANCHOR_RE), ('JP', JP_ANCHOR_RE), ('US', US_ANCHOR_RE)]:
    new_body = make_tbody(country)
    m = regex.search(section)
    if not m:
        raise RuntimeError(f'{country} tbody 매칭 실패')
    section = section[:m.start()] + m.group(1) + new_body + m.group(3) + section[m.end():]

html = html[:target_start] + section + html[target_end:]

# step-a 해석도 최신 값 기반으로 갱신
kr_100_all = [data['KR'][p[0]].get(100) for p in PERIODS if p[0] != '26.1Q']
kr_20_all = [data['KR'][p[0]].get(20) for p in PERIODS if p[0] != '26.1Q']
us_100_all = [data['US'][p[0]].get(100) for p in PERIODS if p[0] != '26.1Q']

# 간단히 최신값만 반영
us_100_latest = data['US']['2025'].get(100)
kr_20_latest = data['KR']['2025'].get(20)

# ins 문구 업데이트
US_100_MIN = min(v for v in us_100_all if v is not None)
US_100_MAX = max(v for v in us_100_all if v is not None)
KR_20_MIN = min(v for v in kr_20_all if v is not None)
KR_20_MAX = max(v for v in kr_20_all if v is not None)
JP_1_22 = data['JP']['2022'].get(1)
JP_1_25 = data['JP']['2025'].get(1)

old_ins_re = re.compile(
    r'<div class="ins"[^>]*><strong>핵심:</strong> US 100위\([^)]*\) &asymp; KR 20위\([^)]*\)[^<]*<strong>[^<]*</strong>[^<]*</div>',
    re.DOTALL
)
new_ins = (f'<div class="ins" style="margin-top:14px;"><strong>핵심:</strong> '
           f'US 100위({US_100_MIN}~{US_100_MAX}억) &asymp; KR 20위({KR_20_MIN}~{KR_20_MAX}억) 수준. '
           f'<strong>US 시장은 100위권에서도 KR 상위권 매출을 기록</strong> &mdash; '
           f'NHN 웹보드가 US 진출 시 중위권만 안착해도 KR 대비 3~4배 매출 잠재력. '
           f'JP는 1위가 22년 {JP_1_22}억&rarr;25년 {JP_1_25}억으로 축소, 정체 시장 확인.</div>')
if old_ins_re.search(html):
    html = old_ins_re.sub(new_ins, html, count=1)

# step-a도 갱신
old_stepa = (r'<div class="step-a">US 100위\(68억\) &asymp; KR 20위\(62억\)\. '
             r'US 시장의 두께가 KR·JP 대비 압도적 &mdash; NHN 진출 시 '
             r'<strong>중위권만 해도 KR 상위권 매출</strong></div>')
new_stepa = (f'<div class="step-a">US 100위({US_100_MIN}~{US_100_MAX}억) &asymp; '
             f'KR 20위({KR_20_MIN}~{KR_20_MAX}억). '
             f'US 시장의 두께가 KR·JP 대비 압도적 — NHN 진출 시 '
             f'<strong>중위권만 해도 KR 상위권 매출</strong></div>')
html = re.sub(old_stepa, new_stepa, html, count=1)

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)

n_open = html.count('<div'); n_close = html.count('</div>')
print(f"\n<div> {o_open}→{n_open}, </div> {o_close}→{n_close}  {'✅' if n_open==n_close else '❌'}")
print("[DONE]", MAIN)
