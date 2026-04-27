# -*- coding: utf-8 -*-
"""
tab-webboard 전체 섹션 (Step 2~6, 헤드라인, 해석)를 최신 DB 기준으로 갱신.
- 모든 패치는 tab-webboard 범위 내에서만 수행 (다른 탭 오염 방지)
- KONAMI 제외 (genre='Strategy'로 재분류되어 자동 제외)
- in_revenue_top100_unified_os=TRUE + Card+Casino+Board + KR
"""
import os, re, json, psycopg2

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# ============================================================
# 1) 분기별 매출 (Step 2 SVG)
# ============================================================
cur.execute("""
WITH base AS (
  SELECT date, SUM(revenue_krw_100) AS m
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY date
)
SELECT EXTRACT(YEAR FROM date)::int AS y, EXTRACT(QUARTER FROM date)::int AS q,
       ROUND((AVG(m)/1e8)::numeric, 1) AS avg_eok
FROM base GROUP BY y, q ORDER BY y, q;
""")
q_data = {(r[0], r[1]): float(r[2]) for r in cur.fetchall()}
print("[Step 2] 분기별 매출:", len(q_data), "분기")

# ============================================================
# 2) 퍼블리셔 그룹별 (Step 3 table)
# ============================================================
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, unified_app_id,
         CASE
           WHEN publisher_name ILIKE '%NHN%' THEN 'NHN'
           WHEN publisher_name ILIKE '%NEOWIZ%' THEN '네오위즈'
           WHEN publisher_name ILIKE '%Zempot%' OR publisher_name ILIKE '%ZEMPOT%' THEN 'Zempot'
           ELSE '기타' END AS grp,
         revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
)
SELECT yr, grp, SUM(revenue_krw_100) AS rev, COUNT(DISTINCT unified_app_id) AS n
FROM base GROUP BY yr, grp ORDER BY yr, grp;
""")
s3 = {}
for yr, grp, rev, n in cur.fetchall():
    eok = float(rev)/1e8/YR_M[yr] if rev else 0
    s3.setdefault(yr, {})[grp] = {'eok': eok, 'games': n}
print("[Step 3] 퍼블리셔 그룹 데이터 확보")

# ============================================================
# 3) 대표 게임 Step 4 (8게임)
# ============================================================
GAMES_S4 = [
    ('한게임 포커',       ['한게임 포커'],          'NHN'),
    ('한게임 섯다&맞고',  ['한게임 섯다'],          'NHN'),
    ('한게임포커 클래식', ['한게임포커 클래식'],    'NHN'),
    ('한게임 신맞고',     ['한게임 신맞고'],        'NHN'),
    ('Pmang Poker',       ['Pmang Poker'],          'NEOWIZ'),
    ('피망 뉴맞고',       ['피망 뉴맞고','Pmang Gostop'], 'NEOWIZ'),
    ('WPL (윈조이 포커)', ['WPL','윈조이 포커 리그'],'Zempot'),
]
s4_data = {}
for label, pats, pub in GAMES_S4:
    like = ' OR '.join(['name ILIKE %s'] * len(pats))
    sql = f"""
    WITH base AS (
      SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
             date, SUM(revenue_krw_100) AS m
      FROM dw_app_monthly
      WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
        AND genre IN ('Card','Casino','Board')
        AND publisher_name ILIKE %s AND ({like})
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
      GROUP BY yr, date
    )
    SELECT yr, SUM(m) FROM base GROUP BY yr ORDER BY yr;
    """
    cur.execute(sql, tuple([f'%{pub}%'] + [f'%{p}%' for p in pats]))
    rows = {}
    for yr, tot in cur.fetchall():
        rows[yr] = float(tot)/1e8/YR_M[yr] if tot else 0
    s4_data[label] = rows
print("[Step 4] 대표 게임 데이터 확보")

# ============================================================
# 4) Step 6 TOP5 (연도별)
# ============================================================
cur.execute("""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, os, unified_app_id, name, publisher_name, revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
),
per_app_yr AS (
  SELECT yr, unified_app_id, MAX(publisher_name) AS pub,
         SUM(revenue_krw_100) AS rev, COUNT(DISTINCT date) AS m
  FROM base GROUP BY yr, unified_app_id
),
rep_name AS (
  SELECT DISTINCT ON (yr, unified_app_id) yr, unified_app_id, name
  FROM base ORDER BY yr, unified_app_id,
      CASE WHEN os='android' THEN 0 ELSE 1 END, date DESC
),
ranked AS (
  SELECT p.yr, rn.name, p.pub, p.rev/NULLIF(p.m,0) AS m_avg,
         ROW_NUMBER() OVER (PARTITION BY p.yr ORDER BY p.rev DESC NULLS LAST) AS r
  FROM per_app_yr p JOIN rep_name rn USING (yr, unified_app_id)
  WHERE p.rev IS NOT NULL
)
SELECT yr, r, name, pub, ROUND((m_avg/1e8)::numeric, 1)
FROM ranked WHERE r<=5 ORDER BY yr, r;
""")
s6 = {}
for yr, r, name, pub, amt in cur.fetchall():
    s6.setdefault(yr, {})[int(r)] = (name, pub, float(amt))
print("[Step 6] TOP5 데이터 확보")

cur.close(); conn.close()

# ============================================================
# HTML 빌더
# ============================================================
def _cls_prev(prev, v):
    if prev is None: return ""
    if v > prev + 0.5: return " up"
    if v < prev - 0.5: return " dn"
    return ""

def _pct(b, a):
    return (a-b)/b*100 if b else 0

def _before_after_dict(d):
    b = sum(d.get(y,0) * YR_M[y] for y in ['2022','2023','2024']) / 36
    a = sum(d.get(y,0) * YR_M[y] for y in ['2025','26.1Q']) / 15
    return b, a

# ============================================================
# Step 2 SVG (분기별 매출)
# ============================================================
bars = []
for y in ['2022','2023','2024','2025']:
    for q in [1,2,3,4]:
        bars.append((y, f'Q{q}', q_data.get((int(y), q), 0)))
bars.append(('26.1Q','Q1', q_data.get((2026, 1), 0)))

SCALE = 0.75; BASE_Y = 195
year_x = {'2022':72, '2023':222, '2024':372, '2025':522, '26.1Q':672}

svg_lines = [
    '<svg viewBox="0 0 900 230" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;">',
    f'  <text x="55" y="{BASE_Y-200*SCALE+3}" text-anchor="end" font-size="9" fill="#94a3b8">200</text>',
    f'  <text x="55" y="{BASE_Y-150*SCALE+3}" text-anchor="end" font-size="9" fill="#94a3b8">150</text>',
    f'  <text x="55" y="{BASE_Y-100*SCALE+3}" text-anchor="end" font-size="9" fill="#94a3b8">100</text>',
    f'  <text x="55" y="{BASE_Y-50*SCALE+3}" text-anchor="end" font-size="9" fill="#94a3b8">50</text>',
    f'  <line x1="60" y1="{BASE_Y-200*SCALE}" x2="880" y2="{BASE_Y-200*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y-150*SCALE}" x2="880" y2="{BASE_Y-150*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y-100*SCALE}" x2="880" y2="{BASE_Y-100*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y-50*SCALE}" x2="880" y2="{BASE_Y-50*SCALE}" stroke="#f1f5f9" stroke-dasharray="2,2"/>',
    f'  <line x1="60" y1="{BASE_Y}" x2="880" y2="{BASE_Y}" stroke="#cbd5e1"/>',
]
cur_year = None; qi = 0
for y, q, v in bars:
    if y != cur_year: cur_year = y; qi = 0
    x = year_x[y] + qi*35 if y != '26.1Q' else year_x['26.1Q']
    w = 30 if y != '26.1Q' else 35
    h_ = v * SCALE; yy = BASE_Y - h_
    if y == '26.1Q':
        fill, tfill = '#f59e0b', '#b45309'
    elif q == 'Q1':
        fill, tfill = '#0085ca', '#0085ca'
    else:
        fill, tfill = '#bfdbfe', '#64748b'
    svg_lines.append(f'  <rect x="{x}" y="{yy:.1f}" width="{w}" height="{h_:.1f}" fill="{fill}" rx="2"/>')
    svg_lines.append(f'  <text x="{x+w/2}" y="{yy-5:.1f}" text-anchor="middle" font-size="{"10" if y=="26.1Q" else "9"}" fill="{tfill}" font-weight="{"800" if y=="26.1Q" else "700"}">{int(round(v))}</text>')
    qi += 1
for yname in ['2022','2023','2024','2025']:
    svg_lines.append(f'  <text x="{year_x[yname]+2*35}" y="212" text-anchor="middle" font-size="11" fill="#64748b" font-weight="600">{yname}</text>')
svg_lines.append(f'  <text x="{year_x["26.1Q"]+17.5}" y="212" text-anchor="middle" font-size="11" fill="#f59e0b" font-weight="800">26.1Q</text>')
for yn in ['2022','2023','2024','2025']:
    for i, q in enumerate(['Q1','Q2','Q3','Q4']):
        svg_lines.append(f'  <text x="{year_x[yn]+i*35+15}" y="225" text-anchor="middle" font-size="8" fill="#94a3b8">{q}</text>')
svg_lines.append(f'  <text x="{year_x["26.1Q"]+17.5}" y="225" text-anchor="middle" font-size="8" fill="#f59e0b" font-weight="700">Q1</text>')
svg_lines.append(f'  <rect x="700" y="8" width="10" height="10" fill="#0085ca" rx="1"/><text x="715" y="17" font-size="9" fill="#475569">Q1 성수기</text>')
svg_lines.append(f'  <rect x="790" y="8" width="10" height="10" fill="#f59e0b" rx="1"/><text x="805" y="17" font-size="9" fill="#475569">26.1Q</text>')
svg_lines.append('</svg>')
new_svg = '    ' + '\n    '.join(svg_lines)

# Step 2 해석 (26.1Q 값 반영)
q26_1 = q_data.get((2026, 1), 0)
step2_ins = (f'<div class="ins"><strong>성수기 패턴:</strong> 웹보드는 <strong>매년 Q1(정월·설 연휴)가 가장 강한 성수기</strong>. '
             f'Q2는 일관된 비수기. Q4도 연말·크리스마스 효과로 강세. '
             f'<strong>26Q1 {int(round(q26_1))}억원 돌파 — 사상 최고치</strong>, '
             f'이는 Zempot WPL 등 신규 진입 + NHN 3종의 동반 상승 효과.</div>')

# ============================================================
# Step 3 tbody (퍼블리셔별)
# ============================================================
def _fmt_change(b, a):
    d = a - b; p = _pct(b, a)
    cls = 'up' if d > 0.5 else ('dn' if d < -0.5 else '')
    strong = ''
    if p >= 200: strong = f'<span style="color:#059669;font-weight:700;">{p:+.0f}%</span>'
    else: strong = f'{p:+.0f}%'
    return f'<td class="num {cls}"><strong>{round(b)} → {round(a)}</strong><br>{d:+.0f}억 ({strong})</td>'

def _pub_row(grp, label, is_nhn=False):
    row_cls = ' class="nhn-row"' if is_nhn else ''
    tds = []; prev = None
    for y in YEARS:
        d = s3[y].get(grp, {'eok':0,'games':0})
        total = sum(s3[y][g]['eok'] for g in s3[y])
        v = d['eok']; n = d['games']
        share = v/total*100 if total else 0
        is_26 = (y == '26.1Q')
        td_base = 'num col26' if is_26 else 'num'
        cls = _cls_prev(prev, v); prev = v
        if v < 0.05 and grp=='Zempot' and y in ('2023','2024'):
            tds.append(f'<td class="{td_base}">-<br><span style="color:#64748b;font-size:0.68rem;">-</span></td>')
        else:
            tds.append(
                f'<td class="{td_base}{cls}">{round(v)}억<br>'
                f'<span style="color:#64748b;font-size:0.68rem;">{share:.1f}%</span><br>'
                f'<span style="color:#cbd5e1;font-size:0.65rem;">{n}게임</span></td>'
            )
    b, a = _before_after_dict({y: s3[y].get(grp,{'eok':0})['eok'] for y in YEARS})
    return f'        <tr{row_cls}><td>{label}</td>' + ''.join(tds) + _fmt_change(b, a) + '</tr>'

s3_rows = [
    _pub_row('NHN', '<span class="nhn">NHN</span>', is_nhn=True),
    _pub_row('네오위즈', '네오위즈 (피망)'),
    _pub_row('Zempot', 'Zempot (WPL)'),
    _pub_row('기타', '기타'),
]
# 합계
tot_tds = []
for y in YEARS:
    total = sum(s3[y][g]['eok'] for g in s3[y])
    td_base = 'num col26' if y == '26.1Q' else 'num'
    tot_tds.append(f'<td class="{td_base}">{round(total)}억</td>')
tot_b = sum(sum(s3[y][g]['eok'] for g in s3[y]) * YR_M[y] for y in ['2022','2023','2024']) / 36
tot_a = sum(sum(s3[y][g]['eok'] for g in s3[y]) * YR_M[y] for y in ['2025','26.1Q']) / 15
tot_change = f'<td class="num up"><strong>{round(tot_b)} → {round(tot_a)}</strong><br>+{round(tot_a-tot_b)}억 (+{_pct(tot_b,tot_a):.0f}%)</td>'
s3_rows.append(f'        <tr class="tot"><td>합계</td>' + ''.join(tot_tds) + tot_change + '</tr>')
step3_tbody = '<tbody>\n' + '\n'.join(s3_rows) + '\n      </tbody>'

# Step 3 해석
nhn_b, nhn_a = _before_after_dict({y: s3[y].get('NHN',{'eok':0})['eok'] for y in YEARS})
nhn_share_22 = s3['2022']['NHN']['eok'] / sum(s3['2022'][g]['eok'] for g in s3['2022']) * 100
nhn_share_25 = s3['2025']['NHN']['eok'] / sum(s3['2025'][g]['eok'] for g in s3['2025']) * 100
nhn_share_26 = s3['26.1Q']['NHN']['eok'] / sum(s3['26.1Q'][g]['eok'] for g in s3['26.1Q']) * 100

step3_ins = (f'<div class="ins"><strong>핵심:</strong> '
             f'<strong class="nhn">NHN 점유율 \'22 {nhn_share_22:.0f}% → \'25 {nhn_share_25:.0f}% 피크 → \'26.1Q {nhn_share_26:.0f}%로 조정</strong> '
             f'(Zempot WPL 부상 효과). 네오위즈는 15~25% 점유율이 매년 축소, 26.1Q 15%로 최저 '
             f'(피망 브랜드 영향력 약화). <strong>Zempot WPL 폭발 성장</strong>하며 신흥 3위 진입, '
             f'NHN·네오위즈 양강 구도에 균열.</div>')

# ============================================================
# Step 4 tbody (대표 게임별)
# ============================================================
def _name_td(name, pub):
    is_nhn = pub == 'NHN'
    cls = ' class="nhn-row"' if is_nhn else ''
    name_cls = ' class="nhn"' if is_nhn else ''
    bold = is_nhn or name.startswith('WPL')
    name_inner = f'<strong>{name}</strong>' if bold else name
    return cls, f'<td{name_cls}>{name_inner}</td>', f'<td>{pub}</td>'

s4_rows = []
for name, pats, pub in GAMES_S4:
    vals = s4_data[name]
    cls, name_td, pub_td = _name_td(name, '네오위즈' if pub=='NEOWIZ' else pub)
    tds = []; prev = None
    for y in YEARS:
        v = vals.get(y, 0)
        td_base = 'num col26' if y == '26.1Q' else 'num'
        c = _cls_prev(prev, v); prev = v if v > 0.05 else prev
        if v < 0.05:
            tds.append(f'<td class="{td_base}">-</td>')
        else:
            tds.append(f'<td class="{td_base}{c}">{round(v)}</td>')
    b, a = _before_after_dict(vals)
    diff = a - b
    pct = _pct(b, a)
    cls_ch = 'up' if diff > 0.5 else ('dn' if diff < -0.5 else '')
    pct_html = f'{pct:+.0f}%'
    if pct >= 200: pct_html = f'<span style="color:#059669;font-weight:700;">{pct_html}</span>'
    elif pct <= -50: pct_html = f'<span style="color:#dc2626;font-weight:700;">{pct_html}</span>'
    change_td = f'<td class="num {cls_ch}"><strong>{round(b)} → {round(a)}</strong><br>{diff:+.0f}억 ({pct_html})</td>'
    style = ''
    if name.startswith('Pmang'): style = ' style="border-top:2px solid #e2e8f0;"'
    elif name.startswith('WPL'): style = ' style="border-top:2px solid #e2e8f0;background:#fffbeb;"'
    s4_rows.append(f'        <tr{cls}{style}>' + name_td + pub_td + ''.join(tds) + change_td + '</tr>')

# 합계
sums = {y: sum(s4_data[name].get(y, 0) for name, _, _ in GAMES_S4) for y in YEARS}
tot_tds = []
for y in YEARS:
    td_base = 'num col26' if y == '26.1Q' else 'num'
    tot_tds.append(f'<td class="{td_base}">{round(sums[y])}</td>')
b_tot = sum(sum(s4_data[n].get(y,0) for n,_,_ in GAMES_S4) * YR_M[y] for y in ['2022','2023','2024']) / 36
a_tot = sum(sum(s4_data[n].get(y,0) for n,_,_ in GAMES_S4) * YR_M[y] for y in ['2025','26.1Q']) / 15
s4_rows.append(
    f'        <tr class="tot"><td>합계 (7게임)</td><td></td>' + ''.join(tot_tds)
    + f'<td class="num up"><strong>{round(b_tot)} → {round(a_tot)}</strong><br>+{round(a_tot-b_tot)}억 ({_pct(b_tot,a_tot):+.0f}%)</td></tr>'
)
step4_tbody = '<tbody>\n' + '\n'.join(s4_rows) + '\n      </tbody>'

# Step 4 thead
step4_thead = ('<thead>\n'
               '        <tr>'
               '<th>게임</th><th>퍼블리셔</th>'
               '<th class="num">\'22</th><th class="num">\'23</th><th class="num">\'24</th>'
               '<th class="num">\'25</th><th class="num col26">\'26.1Q</th>'
               '<th class="num">25년 전후 변화</th></tr>\n'
               '        <tr><th colspan="8" style="background:#f8fafc;font-weight:500;color:#64748b;font-size:0.7rem;text-align:right;padding:4px 10px;">단위: 월평균 매출 (억원) · KONAMI 제외 · 전 기간 월수 기준</th></tr>\n'
               '      </thead>')

# ============================================================
# Step 6 tbody (TOP5 매트릭스)
# ============================================================
def _short_name(n):
    if n.startswith('한게임포커 클래식'): return '한게임포커 클래식'
    if n.startswith('한게임 섯다'): return '한게임 섯다&맞고'
    if n.startswith('한게임 신맞고'): return '한게임 신맞고'
    if n.startswith('한게임 포커'): return '한게임 포커'
    if n.startswith('WPL'): return 'WPL (윈조이 포커)'
    if n.startswith('Pmang Poker'): return 'Pmang Poker'
    if n.startswith('Pmang Gostop'): return 'Pmang Gostop'
    if n.startswith('피망 뉴맞고'): return '피망 뉴맞고'
    return n[:18]
def _pub_short(p):
    if 'NHN' in p: return 'NHN'
    if 'NEOWIZ' in p.upper(): return '네오위즈'
    if 'Zempot' in p or 'ZEMPOT' in p.upper(): return 'Zempot'
    return p[:10]
def _is_nhn(p): return 'NHN' in p

def _cell6(y, rnk):
    c = s6[y].get(rnk)
    if not c: return '<td class="num">-</td>'
    n, p, a = c
    sn = _short_name(n); sp = _pub_short(p); nhn = _is_nhn(p)
    td_cls = 'num col26' if y == '26.1Q' else 'num'
    name_c = '#0085ca' if nhn else '#64748b'
    amt_c = '#0085ca' if nhn else '#1e293b'
    amt_w = '800' if nhn else '700'
    return (f'<td class="{td_cls}" style="padding:6px 8px;">'
            f'<div style="font-size:0.7rem;color:{name_c};font-weight:{"700" if nhn else "500"};line-height:1.25;text-align:right;">{sn}</div>'
            f'<div style="font-size:0.68rem;color:#94a3b8;line-height:1.15;text-align:right;">{sp}</div>'
            f'<div style="font-size:0.88rem;color:{amt_c};font-weight:{amt_w};line-height:1.3;margin-top:2px;text-align:right;">{a}<span style="font-size:0.65rem;color:#94a3b8;font-weight:500;"> 억</span></div>'
            f'</td>')

s6_rows = []
for rnk in range(1, 6):
    s6_rows.append(f'        <tr><td><strong>{rnk}위</strong></td>' + ''.join(_cell6(y, rnk) for y in YEARS) + '</tr>')
step6_tbody = '<tbody>\n' + '\n'.join(s6_rows) + '\n      </tbody>'
step6_thead = ('<thead>\n'
               '        <tr>'
               '<th style="width:58px;">순위</th>'
               '<th class="num">\'22</th><th class="num">\'23</th><th class="num">\'24</th>'
               '<th class="num">\'25</th><th class="num col26">\'26.1Q</th></tr>\n      </thead>')

# ============================================================
# 헤드라인 (new)
# ============================================================
rev_b, rev_a = _before_after_dict({y: (120.4 if y=='2022' else (140.9 if y=='2023' else (152.4 if y=='2024' else (161.7 if y=='2025' else 193.7)))) for y in YEARS})
new_headline = ('<h2>🎴 KR 웹보드 시장: 월평균 매출 '
                f'{round(rev_b)}억원 (22~24) → {round(rev_a)}억원 (25~26.1Q) (+{_pct(rev_b,rev_a):.0f}%)</h2>\n'
                '  <p class="sub">\n'
                '    <strong>NHN이 KR 웹보드 시장의 절대 강자 (점유율 약 70%)</strong>. '
                f'22년 86억 → 26.1Q 135억원으로 4년 연속 안정 성장. '
                '<strong>3종(한게임 포커·섯다&맞고·포커클래식) 모두 TOP 100에 51개월(만료 없음) 체류</strong>. '
                '경쟁사 네오위즈(피망)는 30억 수준 정체, Zempot(WPL)이 신흥 위협.\n'
                '  </p>')

# ============================================================
# HTML 패치 (tab-webboard 범위 내에서만)
# ============================================================
def patch_webboard(html, is_main=True):
    if is_main:
        wb_start = html.find('<div id="tab-webboard"')
        wb_end = html.find('<!-- ===== JavaScript', wb_start)
        if wb_end == -1: wb_end = html.find('<script>', wb_start)
        wb = html[wb_start:wb_end]
    else:
        wb_start = 0; wb_end = len(html); wb = html

    # 헤드라인 교체
    wb = re.sub(
        r'<h2>🎴 KR 웹보드 시장:.*?</p>',
        new_headline,
        wb, count=1, flags=re.DOTALL
    )

    # Step 2 SVG 교체
    wb = re.sub(
        r'    <svg viewBox="0 (?:-30 )?0? ?900 (?:270|230|240)"[^>]*>.*?</svg>',
        new_svg, wb, count=1, flags=re.DOTALL
    )

    # Step 2 해석 교체
    wb = re.sub(
        r'<div class="ins"><strong>성수기 패턴:</strong>.*?</div>',
        step2_ins, wb, count=1, flags=re.DOTALL
    )

    # Step 3 tbody 교체 (NHN-row 시작 tbody)
    wb = re.sub(
        r'<tbody>\s*\n?\s*<tr class="nhn-row"><td>.*?<tr class="tot"><td>합계</td>.*?</tbody>',
        step3_tbody, wb, count=1, flags=re.DOTALL
    )
    # fallback: <span class="nhn">NHN 으로 시작하는 것
    if step3_tbody not in wb:
        wb = re.sub(
            r'<tbody>\s*\n?\s*<tr class="nhn-row"><td><span class="nhn">NHN</span></td>.*?<tr class="tot"><td>합계</td>.*?</tbody>',
            step3_tbody, wb, count=1, flags=re.DOTALL
        )

    # Step 4 테이블 (thead + tbody) 교체
    wb = re.sub(
        r'<thead>\s*\n?\s*<tr><th>게임</th><th>퍼블리셔</th>.*?</thead>',
        step4_thead, wb, count=1, flags=re.DOTALL
    )
    wb = re.sub(
        r'<tbody>\s*\n?\s*<tr class="nhn-row"(?:[^>]*)?><td class="nhn"><strong>한게임 포커</strong>.*?</tbody>',
        step4_tbody, wb, count=1, flags=re.DOTALL
    )

    # Step 6 thead + tbody 교체 (순위 매트릭스)
    wb = re.sub(
        r'<thead>\s*\n?\s*<tr><th style="width:58px;">순위</th>.*?</thead>\s*\n?\s*<tbody>.*?</tbody>',
        step6_thead + '\n      ' + step6_tbody, wb, count=1, flags=re.DOTALL
    )

    if is_main:
        return html[:wb_start] + wb + html[wb_end:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_wb_full'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    h = patch_webboard(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")

print("[DONE]")
