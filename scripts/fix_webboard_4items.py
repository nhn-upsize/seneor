# -*- coding: utf-8 -*-
"""
NHN_webboard_analysis.html 4가지 수정:
1. Step 1 해석 박스 아래 / formula-box 위에 MAU & DL 스파크라인 추가
2. Step 2 SVG viewBox 확장 (24Q4/26Q1 막대 튀어나옴 해결)
3. Step 6 테이블 확장: 1~5위 + 게임명/퍼블리셔 컬럼
4. Step 6 .ins 해석 갱신 (NHN 1~3위 싹쓸이)

기준: KR · Card+Casino+Board · in_revenue_top100_unified_os=TRUE · revenue_krw_100
"""
import os, re, psycopg2

HTML = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
BACKUP = HTML + ".bak.before_4items"

# ============================================================
# 0) DB에서 데이터 재조회 (정확성 확보)
# ============================================================
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# DL 월평균 (만건)
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date, 'YYYY') END AS yr,
        date, units
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
monthly_sum AS (
    SELECT yr, date, SUM(units) AS u FROM base GROUP BY yr, date
)
SELECT yr, ROUND((AVG(u)/10000.0)::numeric, 1) FROM monthly_sum GROUP BY yr ORDER BY yr;
""")
dl_rows = dict(cur.fetchall())  # {'2022': 36.5, ..., '26.1Q': 27.6}

# 26.1Q TOP5 게임 — unified_app_id 기준 연도별 월평균 매출 (억원)
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date, 'YYYY') END AS yr,
        date, os, unified_app_id, name, publisher_name, revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
per_app_yr AS (
    SELECT yr, unified_app_id, MAX(publisher_name) AS publisher_name,
           SUM(revenue_krw_100) AS rev_sum,
           COUNT(DISTINCT date) AS months
    FROM base GROUP BY yr, unified_app_id
),
rep_name AS (
    SELECT DISTINCT ON (yr, unified_app_id) yr, unified_app_id, name
    FROM base
    ORDER BY yr, unified_app_id,
             CASE WHEN os='android' THEN 0 ELSE 1 END, date DESC
),
per_app_monthly AS (
    SELECT p.yr, p.unified_app_id, rn.name, p.publisher_name,
           p.rev_sum / NULLIF(p.months, 0) AS monthly_avg_krw
    FROM per_app_yr p JOIN rep_name rn USING (yr, unified_app_id)
    WHERE p.rev_sum IS NOT NULL
),
ranked AS (
    SELECT yr, unified_app_id, name, publisher_name, monthly_avg_krw,
           ROW_NUMBER() OVER (PARTITION BY yr ORDER BY monthly_avg_krw DESC NULLS LAST) AS rnk
    FROM per_app_monthly
)
SELECT yr, rnk, unified_app_id, name, publisher_name,
       ROUND((monthly_avg_krw / 1e8)::numeric, 1)
FROM ranked WHERE rnk <= 5
ORDER BY yr, rnk;
""")
ranked_rows = cur.fetchall()

# 26.1Q TOP5의 unified_app_id 확보
q1_top5 = [r for r in ranked_rows if r[0] == '26.1Q']
q1_ids = [r[2] for r in q1_top5]
q1_meta = [(r[3], r[4]) for r in q1_top5]   # [(name, publisher), ...]

# 해당 5개 앱의 연도별 월평균 매출
cur.execute("""
WITH base AS (
    SELECT
        CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date, 'YYYY') END AS yr,
        date, unified_app_id, revenue_krw_100
    FROM dw_app_monthly
    WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
      AND genre IN ('Card','Casino','Board')
      AND date BETWEEN '2022-01-01' AND '2026-03-01'
      AND unified_app_id = ANY(%s)
),
per_app_yr AS (
    SELECT yr, unified_app_id,
           SUM(revenue_krw_100) AS rev_sum,
           COUNT(DISTINCT date) AS months
    FROM base GROUP BY yr, unified_app_id
)
SELECT unified_app_id, yr,
       ROUND(((rev_sum / NULLIF(months,0)) / 1e8)::numeric, 1)
FROM per_app_yr ORDER BY unified_app_id, yr;
""", (q1_ids,))
app_yr = {}   # {uaid: {'2022': 39.7, ...}}
for uaid, yr, v in cur.fetchall():
    app_yr.setdefault(uaid, {})[yr] = v

cur.close(); conn.close()

YEARS = ['2022', '2023', '2024', '2025', '26.1Q']

print("[DL 월평균 (만건)]")
for y in YEARS: print(f"  {y}: {dl_rows.get(y)}")

print("\n[26.1Q TOP5 연도별 월평균 매출]")
for (name, pub), uaid in zip(q1_meta, q1_ids):
    row = app_yr.get(uaid, {})
    vals = [row.get(y, None) for y in YEARS]
    print(f"  {name[:25]:<25} ({pub[:15]:<15}) -> {vals}")

# ============================================================
# 1) 백업 + HTML 읽기
# ============================================================
with open(HTML, 'r', encoding='utf-8') as f: html = f.read()
if not os.path.exists(BACKUP):
    with open(BACKUP, 'w', encoding='utf-8') as f: f.write(html)

orig_open = html.count('<div')
orig_close = html.count('</div>')
print(f"\n[BEFORE] <div>={orig_open}, </div>={orig_close}")

# ============================================================
# 2) 스파크라인 SVG 생성 헬퍼
# ============================================================
def spark_points(values):
    """값 배열 -> 5개 x,y 좌표 (y: 15=top, 60=bottom)"""
    xs = [20, 85, 150, 215, 280]
    vmax, vmin = max(values), min(values)
    span = vmax - vmin if vmax != vmin else 1
    ys = [round(15 + 45 * (vmax - v) / span, 1) for v in values]
    return list(zip(xs, ys)), ys

def make_spark_svg(gid, color_stroke, color_grad, values, unit_label, years=YEARS):
    pts, ys = spark_points(values)
    poly_pts = " ".join(f"{x},{y}" for x,y in pts) + f" 280,68 20,68"
    line_pts = " ".join(f"{x},{y}" for x,y in pts)
    circles = ""
    for i,(x,y) in enumerate(pts):
        if i == len(pts)-1:
            circles += f'<circle cx="{x}" cy="{y}" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>'
        else:
            circles += f'<circle cx="{x}" cy="{y}" r="4" fill="{color_stroke}"/>'
    labels = ""
    for i,(x,_y) in enumerate(pts):
        col = "#f59e0b" if i == len(pts)-1 else "#64748b"
        weight = "800" if i == len(pts)-1 else "600"
        yr_lbl = years[i] if years[i] == '26.1Q' else f"'{years[i][-2:]}"
        labels += (f'<text x="{x}" y="78" text-anchor="middle" '
                   f'style="font-size:11px;fill:{col};font-weight:{weight};'
                   f'font-family:Pretendard,-apple-system,sans-serif;">{yr_lbl}</text>')
    # 값 라벨 (데이터 포인트 위)
    value_labels = ""
    for i,((x,y),v) in enumerate(zip(pts, values)):
        col = "#f59e0b" if i == len(pts)-1 else color_stroke
        value_labels += (f'<text x="{x}" y="{y-7}" text-anchor="middle" '
                         f'style="font-size:9.5px;fill:{col};font-weight:700;'
                         f'font-family:Pretendard,-apple-system,sans-serif;">{v}</text>')
    svg = (
        f'<svg viewBox="0 0 300 85" style="width:100%;max-width:420px;height:68px;margin-top:6px;" preserveAspectRatio="none">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{color_grad}" stop-opacity="0.4"/>'
        f'<stop offset="100%" stop-color="{color_grad}" stop-opacity="0"/></linearGradient></defs>'
        f'<polygon fill="url(#{gid})" points="{poly_pts}"/>'
        f'<polyline fill="none" stroke="{color_stroke}" stroke-width="2.5" points="{line_pts}"/>'
        f'{circles}{value_labels}{labels}</svg>'
    )
    return svg

# ============================================================
# 3) Step 1: 스파크라인 2개 추가 (해석 박스 뒤 / formula-box 앞)
# ============================================================
mau_values = [200, 128, 100, 99, 135]
dl_values = [dl_rows[y] for y in YEARS]
dl_values_f = [float(v) for v in dl_values]

mau_svg = make_spark_svg("wb-mau-grad", "#f59e0b", "#f59e0b", mau_values, "만명")
dl_svg = make_spark_svg("wb-dl-grad", "#3b82f6", "#3b82f6", dl_values_f, "만건")

sparkline_block = (
    '\n    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">'
    '<div>'
    '<div style="font-size:0.72rem;color:#64748b;font-weight:600;padding:4px 8px;border-left:2px solid #f59e0b;">'
    '📉 월평균 MAU 추이 (만명) — 활성 유저</div>'
    f'{mau_svg}'
    '</div>'
    '<div>'
    '<div style="font-size:0.72rem;color:#64748b;font-weight:600;padding:4px 8px;border-left:2px solid #3b82f6;">'
    '📥 월평균 다운로드 추이 (만건) — 신규 유입</div>'
    f'{dl_svg}'
    '</div>'
    '</div>\n    '
)

# Step 1의 formula-box 앞에 삽입 — 해당 step-body 범위 내에서만
# step-body 블록 중 첫 번째(Step 1) 안의 formula-box를 찾는다.
STEP1_FORMULA_MARK = '<div class="formula-box">\n      <strong>📐 정의/공식</strong><br>\n      • 대상: KR 시장 내'
if STEP1_FORMULA_MARK not in html:
    raise RuntimeError("Step 1 formula-box 앵커를 찾지 못함")
html = html.replace(STEP1_FORMULA_MARK, sparkline_block + STEP1_FORMULA_MARK, 1)

# ============================================================
# 4) Step 2: SVG viewBox 확장 (상단 clipping 해결)
# ============================================================
# viewBox="0 0 900 240" -> viewBox="0 -30 900 270"
# y 범위를 -30..240 으로 확장해서 26Q1의 y=-21, 값 라벨 y=-26 포함
OLD_VBOX = 'viewBox="0 0 900 240" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;"'
NEW_VBOX = 'viewBox="0 -30 900 270" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;"'
if OLD_VBOX not in html:
    raise RuntimeError("Step 2 SVG viewBox 앵커 못 찾음")
html = html.replace(OLD_VBOX, NEW_VBOX, 1)

# ============================================================
# 5) Step 6: 테이블 확장 (순위 3행 -> 5행 + 게임명/퍼블리셔 컬럼)
# ============================================================
def _fmt(v):
    if v is None: return '-'
    return f"{v}"

def _cls(v_prev, v_cur, last=False):
    if v_prev is None or v_cur is None: return ""
    if v_cur > v_prev: return " up"
    if v_cur < v_prev: return " dn"
    return ""

# 5개 행 구성 (26.1Q TOP5 게임 기준, 연도별 값 표시)
# 퍼블리셔명 단축
def _pub_short(p):
    if 'NHN' in p: return 'NHN'
    if 'NEOWIZ' in p.upper(): return '네오위즈'
    if 'Zempot' in p or 'ZEMPOT' in p.upper(): return 'Zempot'
    return p

def _name_short(n):
    # 긴 이름 축약
    if n.startswith('한게임포커 클래식'): return '한게임포커 클래식'
    if n.startswith('WPL'): return 'WPL (윈조이 포커)'
    if n.startswith('Pmang Poker'): return 'Pmang Poker'
    return n

# NHN 1~3위 로우 하이라이트
rows_html = []
for idx, (uaid, (name, pub)) in enumerate(zip(q1_ids, q1_meta)):
    rnk = idx + 1
    vals = [app_yr.get(uaid, {}).get(y) for y in YEARS]
    is_nhn = 'NHN' in pub
    row_cls = ' class="nhn-row"' if is_nhn else ''
    name_cls = ' class="nhn"' if is_nhn else ''
    tds = []
    for i, v in enumerate(vals):
        is_last = (i == len(vals) - 1)
        prev = vals[i-1] if i > 0 else None
        cls = _cls(prev, v, is_last)
        td_base = "num col26" if is_last else "num"
        strong_open = "<strong>" if is_last else ""
        strong_close = "</strong>" if is_last else ""
        tds.append(f'<td class="{td_base}{cls}">{strong_open}{_fmt(v)}{strong_close}</td>')
    rows_html.append(
        f'        <tr{row_cls}>'
        f'<td><strong>{rnk}위</strong></td>'
        f'<td{name_cls}>{_name_short(name)}</td>'
        f'<td>{_pub_short(pub)}</td>'
        f'{"".join(tds)}</tr>'
    )

new_table_body = (
    '    <table>\n'
    '      <thead>\n'
    '        <tr><th>순위</th><th>게임명 (26.1Q 기준)</th><th>퍼블리셔</th>'
    '<th class="num">\'22</th><th class="num">\'23</th><th class="num">\'24</th>'
    '<th class="num">\'25</th><th class="num col26">\'26.1Q</th></tr>\n'
    '      </thead>\n'
    '      <tbody>\n'
    + '\n'.join(rows_html) + '\n'
    '      </tbody>\n'
    '    </table>'
)

# 기존 Step 6 테이블 교체
OLD_STEP6_TABLE_RE = re.compile(
    r'    <table>\s*\n'
    r'      <thead>\s*\n'
    r'        <tr><th>순위</th><th class="num">\'22</th>.*?</thead>\s*\n'
    r'      <tbody>.*?</tbody>\s*\n'
    r'    </table>',
    re.DOTALL
)
m = OLD_STEP6_TABLE_RE.search(html)
if not m:
    raise RuntimeError("Step 6 기존 테이블 매칭 실패")
html = html[:m.start()] + new_table_body + html[m.end():]

# Step 6 .ins 해석 갱신
OLD_INS = ('<div class="ins"><strong>핵심:</strong> <strong>1~3위 = 100억/월 이상</strong>을 차지. '
           '5위도 10억 수준이나 26.1Q 18.5억으로 급등. '
           '<strong>"웹보드 시장은 몇 개의 절대 강자가 대부분을 차지하는 극단적 집중 구조"</strong> — '
           'NHN이 1~3위를 모두 차지할 경우 시장 90% 지배 가능.</div>')
NEW_INS = ('<div class="ins"><strong>핵심:</strong> <strong class="nhn">NHN이 1~3위를 싹쓸이</strong> '
           '(한게임 포커 44.3억 + 한게임포커 클래식 42.6억 + 한게임 섯다&맞고 37.3억 = 124억원). '
           '4~5위는 18~19억대로 1~3위 대비 2배 이상 격차 — <strong>"상위 3개 게임이 시장의 63% 차지"</strong>. '
           '신흥 Zempot WPL(5위, 18.5억)이 NHN 최하위 라인(한게임 신맞고 10억)을 추월하며 '
           '경쟁 압박 확대 중.</div>')
if OLD_INS not in html:
    raise RuntimeError("Step 6 .ins 앵커 매칭 실패")
html = html.replace(OLD_INS, NEW_INS, 1)

# ============================================================
# 6) 저장 + div 밸런스 검증
# ============================================================
with open(HTML, 'w', encoding='utf-8') as f: f.write(html)

new_open = html.count('<div')
new_close = html.count('</div>')
print(f"\n[AFTER] <div>={new_open}, </div>={new_close}  delta={new_open-new_close}")
print(f"[DIFF]  added {new_open-orig_open} <div>, {new_close-orig_close} </div>")
if new_open == new_close:
    print("  ✅ div 밸런스 OK")
else:
    print("  ❌ div 불균형!")

print("\n[DONE] 저장:", HTML)
print("[BACKUP]", BACKUP)
