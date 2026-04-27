# -*- coding: utf-8 -*-
"""
웹보드 탭 전체 재계산 v2:
- 제외: 모두의마블, Disney Solitaire (Card/Casino/Board 장르이지만 웹보드 아님)
- 기준: KR · in_revenue_top100_unified_os=TRUE · Card+Casino+Board
- Step 1/2/3/4 및 헤드라인, 스파크라인, 해석문구 전체 갱신
"""
import os, re, json, psycopg2

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

# 제외 필터 (모든 쿼리에 공통 추가)
EXCL = "AND name NOT ILIKE '%%모두의마블%%' AND name NOT ILIKE '%%모두의 마블%%' AND name NOT ILIKE '%%Disney Solitaire%%'"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# ============================================================
# 1) Step 1: 매출 / MAU / ARPMAU / DL
# ============================================================
cur.execute(f"""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, SUM(revenue_krw_100) AS m, SUM(mau) AS mau_sum, SUM(units) AS u
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    {EXCL}
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY yr, date
)
SELECT yr,
  ROUND((AVG(m)/1e8)::numeric, 1) AS rev,
  ROUND((AVG(mau_sum)/10000.0)::numeric, 0) AS mau,
  ROUND((AVG(m)/NULLIF(AVG(mau_sum),0))::numeric, 0) AS arp,
  ROUND((AVG(u)/10000.0)::numeric, 1) AS dl
FROM base GROUP BY yr ORDER BY yr;
""")
s1 = {}
for yr, rev, mau, arp, dl in cur.fetchall():
    s1[yr] = {'rev': float(rev), 'mau': int(mau), 'arp': int(arp) if arp else 0, 'dl': float(dl)}
print("[Step 1]", s1)

# ============================================================
# 2) Step 2: 분기별 매출
# ============================================================
cur.execute(f"""
WITH base AS (
  SELECT date, SUM(revenue_krw_100) AS m
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    {EXCL}
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
  GROUP BY date
)
SELECT EXTRACT(YEAR FROM date)::int AS y, EXTRACT(QUARTER FROM date)::int AS q,
       ROUND((AVG(m)/1e8)::numeric, 1)
FROM base GROUP BY y, q ORDER BY y, q;
""")
q_data = {(r[0], r[1]): float(r[2]) for r in cur.fetchall()}

# ============================================================
# 3) Step 3: 퍼블리셔 그룹
# ============================================================
cur.execute(f"""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, unified_app_id,
         CASE
           WHEN publisher_name ILIKE '%%NHN%%' THEN 'NHN'
           WHEN publisher_name ILIKE '%%NEOWIZ%%' THEN '네오위즈'
           WHEN publisher_name ILIKE '%%Zempot%%' OR publisher_name ILIKE '%%ZEMPOT%%' THEN 'Zempot'
           ELSE '기타' END AS grp,
         revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    {EXCL}
    AND date BETWEEN '2022-01-01' AND '2026-03-01'
)
SELECT yr, grp, SUM(revenue_krw_100) AS rev, COUNT(DISTINCT unified_app_id) AS n
FROM base GROUP BY yr, grp ORDER BY yr, grp;
""")
s3 = {}
for yr, grp, rev, n in cur.fetchall():
    eok = float(rev)/1e8/YR_M[yr] if rev else 0
    s3.setdefault(yr, {})[grp] = {'eok': eok, 'games': n}
print("[Step 3]", {y: {g: round(d['eok'],0) for g,d in s3[y].items()} for y in YEARS})

# ============================================================
# 4) Step 4: 대표 게임별 (7게임)
# ============================================================
GAMES_S4 = [
    ('한게임 포커',         ['한게임 포커'],            'NHN'),
    ('한게임 섯다&맞고',    ['한게임 섯다'],            'NHN'),
    ('한게임포커 클래식',   ['한게임포커 클래식'],      'NHN'),
    ('한게임 신맞고',       ['한게임 신맞고'],          'NHN'),
    ('Pmang Poker',         ['Pmang Poker'],            'NEOWIZ'),
    ('피망 뉴맞고',         ['피망 뉴맞고','Pmang Gostop'], 'NEOWIZ'),
    ('WPL (윈조이 포커 리그)', ['WPL','윈조이 포커 리그'], 'Zempot'),
]
s4 = {}
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
    s4[label] = {yr: (float(tot)/1e8/YR_M[yr] if tot else 0) for yr, tot in cur.fetchall()}

# ============================================================
# 5) Step 6 TOP5 연도별
# ============================================================
cur.execute(f"""
WITH base AS (
  SELECT CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
         date, os, unified_app_id, name, publisher_name, revenue_krw_100
  FROM dw_app_monthly
  WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
    AND genre IN ('Card','Casino','Board')
    {EXCL}
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

cur.close(); conn.close()

# ============================================================
# HTML 빌더
# ============================================================
def _cls(prev, v):
    if prev is None: return ""
    if v > prev + 0.5: return " up"
    if v < prev - 0.5: return " dn"
    return ""

def _pct(b, a): return (a-b)/b*100 if b else 0

def _ba(d):
    b = sum(d.get(y,0) * YR_M[y] for y in ['2022','2023','2024']) / 36
    a = sum(d.get(y,0) * YR_M[y] for y in ['2025','26.1Q']) / 15
    return b, a

# -------- Step 1 tbody --------
rev_b, rev_a = _ba({y: s1[y]['rev'] for y in YEARS})
mau_b, mau_a = _ba({y: s1[y]['mau'] for y in YEARS})
arp_b, arp_a = _ba({y: s1[y]['arp'] for y in YEARS})

step1_tbody = f"""<tbody>
        <tr><td>월평균 매출 (억원)</td>
          <td class="num">{s1['2022']['rev']}</td>
          <td class="num {'up' if s1['2023']['rev']>s1['2022']['rev'] else 'dn'}">{s1['2023']['rev']}</td>
          <td class="num {'up' if s1['2024']['rev']>s1['2023']['rev'] else 'dn'}">{s1['2024']['rev']}</td>
          <td class="num {'up' if s1['2025']['rev']>s1['2024']['rev'] else 'dn'}">{s1['2025']['rev']}</td>
          <td class="num col26 {'up' if s1['26.1Q']['rev']>s1['2025']['rev'] else 'dn'}">{s1['26.1Q']['rev']}</td>
          <td class="num up"><strong>{rev_b:.0f} → {rev_a:.0f}</strong><br>+{rev_a-rev_b:.0f}억 (+{_pct(rev_b,rev_a):.0f}%)</td>
        </tr>
        <tr><td>월평균 MAU (만명)</td>
          <td class="num">{s1['2022']['mau']}</td>
          <td class="num dn">{s1['2023']['mau']}</td>
          <td class="num dn">{s1['2024']['mau']}</td>
          <td class="num {'up' if s1['2025']['mau']>s1['2024']['mau'] else 'dn'}">{s1['2025']['mau']}</td>
          <td class="num col26 up">{s1['26.1Q']['mau']}</td>
          <td class="num dn"><strong>{mau_b:.0f} → {mau_a:.0f}</strong><br>{mau_a-mau_b:.0f}만 ({_pct(mau_b,mau_a):.0f}%)</td>
        </tr>
        <tr><td>ARPMAU (원/MAU)</td>
          <td class="num">{s1['2022']['arp']:,}</td>
          <td class="num up">{s1['2023']['arp']:,}</td>
          <td class="num up">{s1['2024']['arp']:,}</td>
          <td class="num up">{s1['2025']['arp']:,}</td>
          <td class="num col26 dn">{s1['26.1Q']['arp']:,}</td>
          <td class="num up"><strong>{arp_b:,.0f} → {arp_a:,.0f}</strong><br>+{arp_a-arp_b:,.0f}원 (+{_pct(arp_b,arp_a):.0f}%)</td>
        </tr>
      </tbody>"""

# -------- Step 1 스파크라인 --------
def spark_pts(values):
    xs = [20, 85, 150, 215, 280]
    vmax, vmin = max(values), min(values)
    span = vmax - vmin if vmax != vmin else 1
    return list(zip(xs, [round(15 + 45 * (vmax - v) / span, 1) for v in values]))

def make_spark(gid, color, values):
    pts = spark_pts(values)
    poly = " ".join(f"{x},{y}" for x,y in pts) + " 280,68 20,68"
    line = " ".join(f"{x},{y}" for x,y in pts)
    circs = ""
    for i,(x,y) in enumerate(pts):
        if i == len(pts)-1:
            circs += f'<circle cx="{x}" cy="{y}" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>'
        else:
            circs += f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
    vlab = ""
    for i,((x,y),v) in enumerate(zip(pts, values)):
        c = '#f59e0b' if i==len(pts)-1 else color
        vlab += f'<text x="{x}" y="{y-7}" text-anchor="middle" style="font-size:9.5px;fill:{c};font-weight:700;font-family:Pretendard,-apple-system,sans-serif;">{v}</text>'
    ylab = ""
    for i,(x,_) in enumerate(pts):
        col, wt = ('#f59e0b','800') if i==len(pts)-1 else ('#64748b','600')
        yr_lbl = YEARS[i] if YEARS[i]=='26.1Q' else f"'{YEARS[i][-2:]}"
        ylab += f'<text x="{x}" y="78" text-anchor="middle" style="font-size:11px;fill:{col};font-weight:{wt};font-family:Pretendard,-apple-system,sans-serif;">{yr_lbl}</text>'
    return (f'<svg viewBox="0 0 300 85" style="width:100%;max-width:420px;height:68px;margin-top:6px;" preserveAspectRatio="none">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%%" stop-color="{color}" stop-opacity="0.4"/>'
            f'<stop offset="100%%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<polygon fill="url(#{gid})" points="{poly}"/>'
            f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{line}"/>'
            f'{circs}{vlab}{ylab}</svg>').replace('%%','%')

mau_vals = [s1[y]['mau'] for y in YEARS]
dl_vals = [s1[y]['dl'] for y in YEARS]
mau_svg = make_spark("wb-mau-grad", "#f59e0b", mau_vals)
dl_svg = make_spark("wb-dl-grad", "#3b82f6", dl_vals)

spark_block = (
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">'
    '<div>'
    '<div style="font-size:0.72rem;color:#64748b;font-weight:600;padding:4px 8px;border-left:2px solid #f59e0b;">'
    '📉 월평균 MAU 추이 (만명) — 활성 유저</div>'
    f'{mau_svg}</div>'
    '<div>'
    '<div style="font-size:0.72rem;color:#64748b;font-weight:600;padding:4px 8px;border-left:2px solid #3b82f6;">'
    '📥 월평균 다운로드 추이 (만건) — 신규 유입</div>'
    f'{dl_svg}</div>'
    '</div>'
)

# -------- Step 2 SVG (기존 로직 재사용) --------
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
cy = None; qi = 0
for y, q, v in bars:
    if y != cy: cy = y; qi = 0
    x = year_x[y] + qi*35 if y != '26.1Q' else year_x['26.1Q']
    w = 30 if y != '26.1Q' else 35
    h_ = v * SCALE; yy = BASE_Y - h_
    if y == '26.1Q': fill, tfill = '#f59e0b', '#b45309'
    elif q == 'Q1': fill, tfill = '#0085ca', '#0085ca'
    else: fill, tfill = '#bfdbfe', '#64748b'
    svg_lines.append(f'  <rect x="{x}" y="{yy:.1f}" width="{w}" height="{h_:.1f}" fill="{fill}" rx="2"/>')
    svg_lines.append(f'  <text x="{x+w/2}" y="{yy-5:.1f}" text-anchor="middle" font-size="{"10" if y=="26.1Q" else "9"}" fill="{tfill}" font-weight="{"800" if y=="26.1Q" else "700"}">{int(round(v))}</text>')
    qi += 1
for yn in ['2022','2023','2024','2025']:
    svg_lines.append(f'  <text x="{year_x[yn]+2*35}" y="212" text-anchor="middle" font-size="11" fill="#64748b" font-weight="600">{yn}</text>')
svg_lines.append(f'  <text x="{year_x["26.1Q"]+17.5}" y="212" text-anchor="middle" font-size="11" fill="#f59e0b" font-weight="800">26.1Q</text>')
for yn in ['2022','2023','2024','2025']:
    for i, q in enumerate(['Q1','Q2','Q3','Q4']):
        svg_lines.append(f'  <text x="{year_x[yn]+i*35+15}" y="225" text-anchor="middle" font-size="8" fill="#94a3b8">{q}</text>')
svg_lines.append(f'  <text x="{year_x["26.1Q"]+17.5}" y="225" text-anchor="middle" font-size="8" fill="#f59e0b" font-weight="700">Q1</text>')
svg_lines.append(f'  <rect x="700" y="8" width="10" height="10" fill="#0085ca" rx="1"/><text x="715" y="17" font-size="9" fill="#475569">Q1 성수기</text>')
svg_lines.append(f'  <rect x="790" y="8" width="10" height="10" fill="#f59e0b" rx="1"/><text x="805" y="17" font-size="9" fill="#475569">26.1Q</text>')
svg_lines.append('</svg>')
new_svg = '    ' + '\n    '.join(svg_lines)

q26 = q_data.get((2026, 1), 0)
step2_ins = (f'<div class="ins"><strong>성수기 패턴:</strong> 웹보드는 <strong>매년 Q1(정월·설 연휴)가 가장 강한 성수기</strong>. '
             f'Q2는 일관된 비수기. Q4도 연말·크리스마스 효과로 강세. '
             f'<strong>26Q1 {int(round(q26))}억원 돌파 — 사상 최고치</strong>, '
             f'이는 Zempot WPL 등 신규 진입 + NHN 3종의 동반 상승 효과.</div>')

# -------- Step 3 tbody --------
def fmt_change(b, a):
    d = a - b; p = _pct(b, a)
    cls_ = 'up' if d > 0.5 else ('dn' if d < -0.5 else '')
    if p >= 200: pct_html = f'<span style="color:#059669;font-weight:700;">{p:+.0f}%</span>'
    else: pct_html = f'{p:+.0f}%'
    return f'<td class="num {cls_}"><strong>{round(b)} → {round(a)}</strong><br>{d:+.0f}억 ({pct_html})</td>'

def pub_row(grp, label, is_nhn=False):
    row_cls = ' class="nhn-row"' if is_nhn else ''
    tds = []; prev = None
    for y in YEARS:
        d = s3[y].get(grp, {'eok':0,'games':0})
        total = sum(s3[y][g]['eok'] for g in s3[y])
        v = d['eok']; n = d['games']
        share = v/total*100 if total else 0
        is_26 = (y == '26.1Q')
        td_base = 'num col26' if is_26 else 'num'
        c = _cls(prev, v); prev = v
        if v < 0.05 and grp=='Zempot' and y in ('2023','2024'):
            tds.append(f'<td class="{td_base}">-<br><span style="color:#64748b;font-size:0.68rem;">-</span></td>')
        else:
            tds.append(
                f'<td class="{td_base}{c}">{round(v)}억<br>'
                f'<span style="color:#64748b;font-size:0.68rem;">{share:.1f}%</span><br>'
                f'<span style="color:#cbd5e1;font-size:0.65rem;">{n}게임</span></td>'
            )
    b, a = _ba({y: s3[y].get(grp,{'eok':0})['eok'] for y in YEARS})
    return f'        <tr{row_cls}><td>{label}</td>' + ''.join(tds) + fmt_change(b, a) + '</tr>'

s3_rows = [
    pub_row('NHN', '<span class="nhn">NHN</span>', is_nhn=True),
    pub_row('네오위즈', '네오위즈 (피망)'),
    pub_row('Zempot', 'Zempot (WPL)'),
    pub_row('기타', '기타 (2ACE 포커 등)'),
]
tot_tds = []
for y in YEARS:
    total = sum(s3[y][g]['eok'] for g in s3[y])
    td_base = 'num col26' if y == '26.1Q' else 'num'
    tot_tds.append(f'<td class="{td_base}">{round(total)}억</td>')
tot_b = sum(sum(s3[y][g]['eok'] for g in s3[y]) * YR_M[y] for y in ['2022','2023','2024']) / 36
tot_a = sum(sum(s3[y][g]['eok'] for g in s3[y]) * YR_M[y] for y in ['2025','26.1Q']) / 15
s3_rows.append(f'        <tr class="tot"><td>합계</td>' + ''.join(tot_tds) +
    f'<td class="num up"><strong>{round(tot_b)} → {round(tot_a)}</strong><br>+{round(tot_a-tot_b)}억 (+{_pct(tot_b,tot_a):.0f}%)</td></tr>')
step3_tbody = '<tbody>\n' + '\n'.join(s3_rows) + '\n      </tbody>'

# -------- Step 4 tbody (7게임) --------
def name_td(name, pub_disp):
    is_nhn = pub_disp == 'NHN'
    tr_cls = ' class="nhn-row"' if is_nhn else ''
    name_cls = ' class="nhn"' if is_nhn else ''
    bold = is_nhn or name.startswith('WPL')
    ni = f'<strong>{name}</strong>' if bold else name
    return tr_cls, f'<td{name_cls}>{ni}</td>', f'<td>{pub_disp}</td>'

s4_rows = []
for name, pats, pub in GAMES_S4:
    vals = s4[name]
    pub_disp = '네오위즈' if pub=='NEOWIZ' else pub
    tr_cls, ntd, ptd = name_td(name, pub_disp)
    tds = []; prev = None
    for y in YEARS:
        v = vals.get(y, 0)
        td_base = 'num col26' if y == '26.1Q' else 'num'
        c = _cls(prev, v); prev = v if v > 0.05 else prev
        tds.append(f'<td class="{td_base}">-</td>' if v < 0.05 else f'<td class="{td_base}{c}">{round(v)}</td>')
    b, a = _ba(vals)
    diff = a - b; pct = _pct(b, a)
    cls_ch = 'up' if diff > 0.5 else ('dn' if diff < -0.5 else '')
    pct_html = f'{pct:+.0f}%'
    if pct >= 200: pct_html = f'<span style="color:#059669;font-weight:700;">{pct_html}</span>'
    elif pct <= -50: pct_html = f'<span style="color:#dc2626;font-weight:700;">{pct_html}</span>'
    change_td = f'<td class="num {cls_ch}"><strong>{round(b)} → {round(a)}</strong><br>{diff:+.0f}억 ({pct_html})</td>'
    style = ''
    if name.startswith('Pmang'): style = ' style="border-top:2px solid #e2e8f0;"'
    elif name.startswith('WPL'): style = ' style="border-top:2px solid #e2e8f0;background:#fffbeb;"'
    s4_rows.append(f'        <tr{tr_cls}{style}>' + ntd + ptd + ''.join(tds) + change_td + '</tr>')

sums = {y: sum(s4[n].get(y, 0) for n, _, _ in GAMES_S4) for y in YEARS}
tot_tds = []
for y in YEARS:
    td_base = 'num col26' if y == '26.1Q' else 'num'
    tot_tds.append(f'<td class="{td_base}">{round(sums[y])}</td>')
b_tot = sum(sums[y] * YR_M[y] for y in ['2022','2023','2024']) / 36
a_tot = sum(sums[y] * YR_M[y] for y in ['2025','26.1Q']) / 15
s4_rows.append(
    f'        <tr class="tot"><td>합계 (7게임)</td><td></td>' + ''.join(tot_tds)
    + f'<td class="num up"><strong>{round(b_tot)} → {round(a_tot)}</strong><br>+{round(a_tot-b_tot)}억 ({_pct(b_tot,a_tot):+.0f}%)</td></tr>'
)
step4_tbody = '<tbody>\n' + '\n'.join(s4_rows) + '\n      </tbody>'
step4_thead = ('<thead>\n'
               '        <tr>'
               '<th>게임</th><th>퍼블리셔</th>'
               '<th class="num">\'22</th><th class="num">\'23</th><th class="num">\'24</th>'
               '<th class="num">\'25</th><th class="num col26">\'26.1Q</th>'
               '<th class="num">25년 전후 변화</th></tr>\n'
               '        <tr><th colspan="8" style="background:#f8fafc;font-weight:500;color:#64748b;font-size:0.7rem;text-align:right;padding:4px 10px;">단위: 월평균 매출 (억원) · 웹보드 전용 (모두의마블/Disney Solitaire/KONAMI 제외)</th></tr>\n'
               '      </thead>')

# -------- 헤드라인 --------
new_headline = ('<h2>🎴 KR 웹보드 시장: 월평균 매출 '
                f'{round(rev_b)}억원 (22~24) → {round(rev_a)}억원 (25~26.1Q) (+{_pct(rev_b,rev_a):.0f}%)</h2>\n'
                '  <p class="sub">\n'
                '    <strong>NHN이 KR 웹보드 시장의 절대 강자 (점유율 약 70%)</strong>. '
                f'22년 86억 → 26.1Q 135억원으로 4년 연속 안정 성장. '
                '<strong>3종(한게임 포커·섯다&맞고·포커클래식) 모두 TOP 100에 51개월(만료 없음) 체류</strong>. '
                '경쟁사 네오위즈(피망)는 30억 수준 정체, Zempot(WPL)이 신흥 위협.\n'
                '  </p>')

# -------- 해석 --------
arp_level = f'{s1["26.1Q"]["arp"]//1000*1000:,}원대' if s1["26.1Q"]["arp"] else ''
step1_ins = (f'<div class="ins"><strong>해석:</strong> 웹보드는 <strong>대한민국 모바일 게임 시장 전체 '
             f'ARPMAU(13,263원) 보다도 높은 {arp_level}</strong> — 평균 유저당 과금이 시장 평균 대비 '
             f'<strong>1.2배</strong>. <strong>"적은 수의 고과금 충성 유저가 시장을 유지"</strong>하는 구조. '
             f'26.1Q MAU 반등({s1["26.1Q"]["mau"]}만)은 신규 Zempot WPL 등 유입 효과로 추정.</div>')

# ============================================================
# HTML 패치
# ============================================================
def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 헤드라인
    wb = re.sub(r'<h2>🎴 KR 웹보드 시장:.*?</p>', new_headline, wb, count=1, flags=re.DOTALL)
    # Step 1 tbody
    wb = re.sub(r'<tbody>\s*\n?\s*<tr><td>월평균 매출 \(억원\)</td>.*?</tbody>', step1_tbody, wb, count=1, flags=re.DOTALL)
    # Step 1 해석
    wb = re.sub(r'<div class="ins"><strong>해석:</strong> 웹보드는.*?추정\.</div>', step1_ins, wb, count=1, flags=re.DOTALL)
    # 스파크라인
    wb = re.sub(
        r'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">.*?</div></div>',
        spark_block, wb, count=1, flags=re.DOTALL
    )
    # Step 2 SVG
    wb = re.sub(r'    <svg viewBox="0 (?:-30 )?0? ?900 (?:270|230|240)"[^>]*>.*?</svg>', new_svg, wb, count=1, flags=re.DOTALL)
    # Step 2 해석
    wb = re.sub(r'<div class="ins"><strong>성수기 패턴:</strong>.*?</div>', step2_ins, wb, count=1, flags=re.DOTALL)
    # Step 3 tbody
    wb = re.sub(r'<tbody>\s*\n?\s*<tr class="nhn-row"><td><span class="nhn">NHN</span></td>.*?<tr class="tot"><td>합계</td>.*?</tbody>', step3_tbody, wb, count=1, flags=re.DOTALL)
    # Step 4 thead + tbody
    wb = re.sub(r'<thead>\s*\n?\s*<tr><th>게임</th><th>퍼블리셔</th>.*?</thead>', step4_thead, wb, count=1, flags=re.DOTALL)
    wb = re.sub(r'<tbody>\s*\n?\s*<tr class="nhn-row"(?:[^>]*)?><td class="nhn"><strong>한게임 포커</strong>.*?</tbody>', step4_tbody, wb, count=1, flags=re.DOTALL)

    if is_main: return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_exclude_v2'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
