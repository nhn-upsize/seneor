# -*- coding: utf-8 -*-
"""
NHN_webboard_analysis.html 2차 수정:
1) Step 2 SVG: 막대 잘림 해결(Y 스케일 재조정) + 색상 단순화(NHN 블루 + 26.1Q 주황)
2) Step 6 테이블: 26.1Q 고정 TOP5 → 연도×순위 매트릭스(각 연도마다 다른 TOP5 게임명 표기)
"""
import os, re, psycopg2

HTML = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
BACKUP = HTML + ".bak.before_v2"

# ============================================================
# 0) DB에서 연도별 TOP5 재조회 (unified_app_id 기준)
# ============================================================
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()
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
           SUM(revenue_krw_100) AS rev_sum, COUNT(DISTINCT date) AS months
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
           p.rev_sum / NULLIF(p.months,0) AS monthly_avg_krw
    FROM per_app_yr p JOIN rep_name rn USING (yr, unified_app_id)
    WHERE p.rev_sum IS NOT NULL
),
ranked AS (
    SELECT yr, name, publisher_name, monthly_avg_krw,
           ROW_NUMBER() OVER (PARTITION BY yr ORDER BY monthly_avg_krw DESC NULLS LAST) AS rnk
    FROM per_app_monthly
)
SELECT yr, rnk, name, publisher_name, ROUND((monthly_avg_krw/1e8)::numeric, 1)
FROM ranked WHERE rnk <= 5 ORDER BY yr, rnk;
""")
rows = cur.fetchall()
cur.close(); conn.close()

# {yr: {rnk: (name, pub, amount)}}
YEARS = ['2022', '2023', '2024', '2025', '26.1Q']
yr_top5 = {y: {} for y in YEARS}
for yr, rnk, name, pub, amt in rows:
    yr_top5[yr][rnk] = (name, pub, float(amt))

print("[연도별 TOP5 확인]")
for y in YEARS:
    print(f"  {y}:")
    for r in range(1, 6):
        if r in yr_top5[y]:
            n, p, a = yr_top5[y][r]
            print(f"    {r}위  {a}억  {n[:25]}  ({p[:15]})")

# ============================================================
# 1) 백업 + HTML 읽기
# ============================================================
with open(HTML, 'r', encoding='utf-8') as f: html = f.read()
if not os.path.exists(BACKUP):
    with open(BACKUP, 'w', encoding='utf-8') as f: f.write(html)
orig_open = html.count('<div'); orig_close = html.count('</div>')
print(f"\n[BEFORE] <div>={orig_open}, </div>={orig_close}")

# ============================================================
# 2) Step 2 SVG 전체 재생성 — Y 스케일 재조정 + 단색화
# ============================================================
# 17분기 데이터 (22Q1 ~ 26Q1)
bars = [
    ('2022', 'Q1', 156.5), ('2022', 'Q2', 121.4), ('2022', 'Q3', 136.9), ('2022', 'Q4', 133.2),
    ('2023', 'Q1', 167.6), ('2023', 'Q2', 127.6), ('2023', 'Q3', 122.8), ('2023', 'Q4', 153.7),
    ('2024', 'Q1', 155.1), ('2024', 'Q2', 141.4), ('2024', 'Q3', 164.5), ('2024', 'Q4', 172.8),
    ('2025', 'Q1', 168.0), ('2025', 'Q2', 153.5), ('2025', 'Q3', 164.0), ('2025', 'Q4', 165.1),
    ('26.1Q', 'Q1', 196.2),
]
# Y 스케일: value * 0.75, baseline y=195 — 최대 196.2 → 높이 147.2, 상단 y=47.8 (라벨 y=42 까지 여유)
SCALE = 0.75
BASE_Y = 195
BAR_W = 30
# X 좌표 분배: 연도 사이 간격 주기
# 2022: x=72/107/142/177 (간격 35), 연도 간 gap ~10
year_gap = 10
year_x_start = {}
year_x_start['2022'] = 72
year_x_start['2023'] = year_x_start['2022'] + 4*35 + year_gap  # 222
year_x_start['2024'] = year_x_start['2023'] + 4*35 + year_gap  # 372
year_x_start['2025'] = year_x_start['2024'] + 4*35 + year_gap  # 522
year_x_start['26.1Q'] = year_x_start['2025'] + 4*35 + year_gap  # 672

COLOR_BAR = '#bfdbfe'     # 연한 파랑 (일반 분기)
COLOR_Q1 = '#0085ca'      # NHN 블루 (Q1 성수기 강조)
COLOR_26 = '#f59e0b'      # 26.1Q 주황 하이라이트
COLOR_26_TEXT = '#b45309'

def bar_xy(year, qi):
    """year: '2022'~'26.1Q', qi: 0~3 (Q1~Q4)"""
    return year_x_start[year] + qi * 35

# SVG 빌드
svg_parts = [
    '<svg viewBox="0 0 900 230" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;">',
    '  <!-- Y축 눈금 -->',
    f'  <text x="55" y="{BASE_Y - 200*SCALE + 3}" text-anchor="end" font-size="9" fill="#94a3b8">200</text>',
    f'  <text x="55" y="{BASE_Y - 150*SCALE + 3}" text-anchor="end" font-size="9" fill="#94a3b8">150</text>',
    f'  <text x="55" y="{BASE_Y - 100*SCALE + 3}" text-anchor="end" font-size="9" fill="#94a3b8">100</text>',
    f'  <text x="55" y="{BASE_Y - 50*SCALE + 3}" text-anchor="end" font-size="9" fill="#94a3b8">50</text>',
    f'  <line x1="60" y1="{BASE_Y - 200*SCALE}" x2="880" y2="{BASE_Y - 200*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y - 150*SCALE}" x2="880" y2="{BASE_Y - 150*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y - 100*SCALE}" x2="880" y2="{BASE_Y - 100*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y - 50*SCALE}" x2="880" y2="{BASE_Y - 50*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y}" x2="880" y2="{BASE_Y}" stroke="#cbd5e1"/>',
    '',
    '  <!-- 막대들 -->',
]

# 연도별 Q 인덱스 매핑
cur_year = None
q_idx = 0
for (yr, q, v) in bars:
    if yr != cur_year:
        cur_year = yr
        q_idx = 0
    x = bar_xy(yr, q_idx) if yr != '26.1Q' else year_x_start['26.1Q']
    w = BAR_W if yr != '26.1Q' else 35
    h = v * SCALE
    y = BASE_Y - h
    # 색상: Q1 = NHN 블루, 그 외 Q = 연한 파랑, 26.1Q = 주황
    if yr == '26.1Q':
        fill, txt_fill = COLOR_26, COLOR_26_TEXT
    elif q == 'Q1':
        fill, txt_fill = COLOR_Q1, COLOR_Q1
    else:
        fill, txt_fill = COLOR_BAR, '#64748b'
    svg_parts.append(f'  <rect x="{x}" y="{y:.1f}" width="{w}" height="{h:.1f}" fill="{fill}" rx="2"/>')
    svg_parts.append(
        f'  <text x="{x + w/2}" y="{y - 5:.1f}" text-anchor="middle" '
        f'font-size="{"10" if yr=="26.1Q" else "9"}" fill="{txt_fill}" '
        f'font-weight="{"800" if yr=="26.1Q" else "700"}">{int(round(v))}</text>'
    )
    q_idx += 1

# 연도 라벨 + 분기 라벨
svg_parts.append('')
svg_parts.append('  <!-- 연도 라벨 -->')
year_label_map = [
    ('2022', year_x_start['2022'] + 2*35 - 0),
    ('2023', year_x_start['2023'] + 2*35 - 0),
    ('2024', year_x_start['2024'] + 2*35 - 0),
    ('2025', year_x_start['2025'] + 2*35 - 0),
    ('26.1Q', year_x_start['26.1Q'] + 35/2),
]
for yname, xc in year_label_map:
    col = '#f59e0b' if yname == '26.1Q' else '#64748b'
    fw = '800' if yname == '26.1Q' else '600'
    svg_parts.append(
        f'  <text x="{xc}" y="212" text-anchor="middle" font-size="11" fill="{col}" font-weight="{fw}">{yname}</text>'
    )

# 분기 라벨 (Q1~Q4 each year)
svg_parts.append('  <!-- 분기 라벨 -->')
for yr in ['2022', '2023', '2024', '2025']:
    for i, q in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        xc = year_x_start[yr] + i*35 + BAR_W/2
        svg_parts.append(
            f'  <text x="{xc}" y="225" text-anchor="middle" font-size="8" fill="#94a3b8">{q}</text>'
        )
# 26.1Q
svg_parts.append(
    f'  <text x="{year_x_start["26.1Q"] + 35/2}" y="225" text-anchor="middle" font-size="8" fill="#f59e0b" font-weight="700">Q1</text>'
)

# 범례 (간소)
svg_parts.append('')
svg_parts.append('  <!-- 범례(간소) -->')
svg_parts.append(f'  <rect x="700" y="8" width="10" height="10" fill="{COLOR_Q1}" rx="1"/><text x="715" y="17" font-size="9" fill="#475569">Q1 성수기</text>')
svg_parts.append(f'  <rect x="790" y="8" width="10" height="10" fill="{COLOR_26}" rx="1"/><text x="805" y="17" font-size="9" fill="#475569">26.1Q</text>')
svg_parts.append('</svg>')

new_svg = '    ' + '\n    '.join(svg_parts)

# 기존 Step 2 SVG 블록 치환
OLD_SVG_RE = re.compile(
    r'    <svg viewBox="0 -30 900 270".*?</svg>',
    re.DOTALL
)
if not OLD_SVG_RE.search(html):
    # fallback: 혹시 viewBox가 원복되어 있으면
    OLD_SVG_RE = re.compile(r'    <svg viewBox="0 0 900 240".*?</svg>', re.DOTALL)
m = OLD_SVG_RE.search(html)
if not m:
    raise RuntimeError("Step 2 SVG 매칭 실패")
html = html[:m.start()] + new_svg + html[m.end():]

# ============================================================
# 3) Step 6 테이블 재구성 — 연도×순위 매트릭스
# ============================================================
def _short_name(n):
    if n.startswith('한게임포커 클래식'): return '한게임포커 클래식'
    if n.startswith('한게임 섯다'): return '한게임 섯다&맞고'
    if n.startswith('한게임 신맞고'): return '한게임 신맞고'
    if n.startswith('한게임 포커'): return '한게임 포커'
    if n.startswith('WPL'): return 'WPL (윈조이 포커)'
    if n.startswith('Pmang Poker'): return 'Pmang Poker'
    if n.startswith('Pmang Gostop'): return 'Pmang Gostop'
    if n.startswith('원펀맨'): return '원펀맨 (영웅의 길)'
    if n.startswith('솔라'): return '솔라 리바이벌'
    if n.startswith('투에이스') or '2ACE' in n.upper(): return '투에이스(2ACE) 포커'
    if 'Yu-Gi-Oh' in n: return '유희왕 마스터 듀얼'
    if n.startswith('피망 포커'): return '피망 포커'
    if n.startswith('피망 뉴맞고'): return '피망 뉴맞고'
    # 일반: 맨 앞 20자
    return n[:18]

def _pub_short(p):
    if 'NHN' in p: return 'NHN'
    if 'NEOWIZ' in p.upper(): return '네오위즈'
    if 'Zempot' in p or 'ZEMPOT' in p.upper(): return 'Zempot'
    if 'KONAMI' in p.upper(): return 'Konami'
    if 'NATASKY' in p.upper(): return 'Natasky'
    if 'UJOY' in p.upper(): return 'Ujoy'
    if '2ACE' in p.upper(): return '2ACE'
    return p[:10]

def _is_nhn(p): return 'NHN' in p

# 헤더
thead = (
    '      <thead>\n'
    '        <tr>'
    '<th style="width:58px;">순위</th>'
    '<th class="num">\'22</th>'
    '<th class="num">\'23</th>'
    '<th class="num">\'24</th>'
    '<th class="num">\'25</th>'
    '<th class="num col26">\'26.1Q</th>'
    '</tr>\n'
    '      </thead>'
)

# 각 셀: 게임명(작게) + 금액(크게)
def cell(yr, rnk):
    if rnk not in yr_top5[yr]:
        return '<td class="num">-</td>'
    name, pub, amt = yr_top5[yr][rnk]
    sn = _short_name(name)
    sp = _pub_short(pub)
    nhn = _is_nhn(pub)
    is_26 = (yr == '26.1Q')
    td_cls = 'num col26' if is_26 else 'num'
    name_color = '#0085ca' if nhn else '#64748b'
    amt_color = '#0085ca' if nhn else '#1e293b'
    amt_weight = '800' if nhn else '700'
    return (
        f'<td class="{td_cls}" style="padding:6px 8px;">'
        f'<div style="font-size:0.7rem;color:{name_color};font-weight:{"700" if nhn else "500"};line-height:1.25;text-align:right;">{sn}</div>'
        f'<div style="font-size:0.68rem;color:#94a3b8;line-height:1.15;text-align:right;">{sp}</div>'
        f'<div style="font-size:0.88rem;color:{amt_color};font-weight:{amt_weight};line-height:1.3;margin-top:2px;text-align:right;">{amt}<span style="font-size:0.65rem;color:#94a3b8;font-weight:500;"> 억</span></div>'
        f'</td>'
    )

tbody_rows = []
for rnk in range(1, 6):
    cells = ''.join(cell(y, rnk) for y in YEARS)
    tbody_rows.append(
        f'        <tr><td><strong>{rnk}위</strong></td>{cells}</tr>'
    )

tbody = '      <tbody>\n' + '\n'.join(tbody_rows) + '\n      </tbody>'

new_table = (
    '    <table>\n'
    + thead + '\n'
    + tbody + '\n'
    '    </table>'
)

# 기존 Step 6 테이블 치환 (v1에서 이미 5행으로 바뀐 상태)
OLD_STEP6_RE = re.compile(
    r'    <table>\s*\n'
    r'      <thead>\s*\n'
    r'        <tr><th>순위</th>.*?</thead>\s*\n'
    r'      <tbody>.*?</tbody>\s*\n'
    r'    </table>',
    re.DOTALL
)
m2 = OLD_STEP6_RE.search(html)
if not m2:
    raise RuntimeError("Step 6 테이블 매칭 실패")
html = html[:m2.start()] + new_table + html[m2.end():]

# Step 6 .ins 해석 갱신 — 연도별 변화 반영
OLD_INS_PAT = re.compile(r'<div class="ins"><strong>핵심:</strong>[^<]*<strong class="nhn">NHN이 1~3위를 싹쓸이</strong>.*?</div>', re.DOTALL)
NEW_INS = ('<div class="ins"><strong>핵심:</strong> '
           '매년 TOP5 구성이 달라지며 <strong class="nhn">NHN 게임이 점점 상위를 점령</strong> — '
           '22년 2/3위(한게임 포커·클래식) → 23년 1~3위 싹쓸이 → 26.1Q에도 1~3위 유지. '
           '4위는 Pmang Poker(네오위즈)가 4년째 고정, 5위는 매년 교체 '
           '(22년 솔라·23년 원펀맨·24년 2ACE·25~26년 WPL). '
           '<strong>"NHN의 지배력은 강화되는 동시에, 5위권은 신규 진입이 활발"</strong>.</div>')
if not OLD_INS_PAT.search(html):
    raise RuntimeError("Step 6 .ins 앵커 매칭 실패")
html = OLD_INS_PAT.sub(NEW_INS, html, count=1)

# ============================================================
# 4) 저장 + div 밸런스 검증
# ============================================================
with open(HTML, 'w', encoding='utf-8') as f: f.write(html)

new_open = html.count('<div'); new_close = html.count('</div>')
print(f"\n[AFTER] <div>={new_open}, </div>={new_close}  delta={new_open-new_close}")
if new_open == new_close:
    print("  ✅ div 밸런스 OK")
else:
    print("  ❌ div 불균형!")

print("[DONE] 저장:", HTML)
print("[BACKUP]", BACKUP)
