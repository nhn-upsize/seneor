# -*- coding: utf-8 -*-
"""
웹보드 심층분석 모든 섹션을 현재 DB 기준으로 재적용.
- Card+Casino+Board 장르 필터로 원펀맨/솔라/월드크러쉬/하이큐 자동 제외
- webboard 단독 + 메인(tab-webboard) 둘 다 반영
"""
import os, re, json

WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_refresh.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_MONTHS = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# ============================================================
# 전/후 월평균 계산용 헬퍼
# ============================================================
def before_after_avg(values_by_year):
    """values_by_year: {'2022':x, '2023':y, ...}  →  (before_avg, after_avg)"""
    before_sum = sum(values_by_year[y] * YR_MONTHS[y] for y in ['2022','2023','2024'])
    after_sum = sum(values_by_year[y] * YR_MONTHS[y] for y in ['2025','26.1Q'])
    return before_sum/36, after_sum/15

# ============================================================
# Step 1: 시장 매출/MAU/ARPMAU 표
# ============================================================
s1 = D['step1']  # {'2022': [rev, mau, arpmau], ...}
rev_by = {y: s1[y][0] for y in YEARS}
mau_by = {y: s1[y][1] for y in YEARS}
arp_by = {y: s1[y][2] for y in YEARS}

rev_b, rev_a = before_after_avg(rev_by)
mau_b, mau_a = before_after_avg(mau_by)
arp_b, arp_a = before_after_avg(arp_by)

def diff_pct(b, a): return (a-b)/b*100 if b else 0

def upordn(b, a, invert=False):
    d = a - b
    if invert: d = -d
    return 'up' if d > 0 else ('dn' if d < 0 else '')

# 새 Step 1 tbody
step1_tbody = f"""<tbody>
        <tr><td>월평균 매출 (억원)</td>
          <td class="num">{rev_by['2022']:.1f}</td>
          <td class="num {'up' if rev_by['2023']>rev_by['2022'] else 'dn'}">{rev_by['2023']:.1f}</td>
          <td class="num {'up' if rev_by['2024']>rev_by['2023'] else 'dn'}">{rev_by['2024']:.1f}</td>
          <td class="num {'up' if rev_by['2025']>rev_by['2024'] else 'dn'}">{rev_by['2025']:.1f}</td>
          <td class="num col26 {'up' if rev_by['26.1Q']>rev_by['2025'] else 'dn'}">{rev_by['26.1Q']:.1f}</td>
          <td class="num up"><strong>{rev_b:.0f} → {rev_a:.0f}</strong><br>+{rev_a-rev_b:.0f}억 (+{diff_pct(rev_b,rev_a):.0f}%)</td>
        </tr>
        <tr><td>월평균 MAU (만명)</td>
          <td class="num">{mau_by['2022']}</td>
          <td class="num dn">{mau_by['2023']}</td>
          <td class="num dn">{mau_by['2024']}</td>
          <td class="num dn">{mau_by['2025']}</td>
          <td class="num col26 up">{mau_by['26.1Q']}</td>
          <td class="num dn"><strong>{mau_b:.0f} → {mau_a:.0f}</strong><br>{mau_a-mau_b:.0f}만 ({diff_pct(mau_b,mau_a):.0f}%)</td>
        </tr>
        <tr><td>ARPMAU (원/MAU)</td>
          <td class="num">{arp_by['2022']:,}</td>
          <td class="num up">{arp_by['2023']:,}</td>
          <td class="num up">{arp_by['2024']:,}</td>
          <td class="num up">{arp_by['2025']:,}</td>
          <td class="num col26 dn">{arp_by['26.1Q']:,}</td>
          <td class="num up"><strong>{arp_b:,.0f} → {arp_a:,.0f}</strong><br>+{arp_a-arp_b:,.0f}원 (+{diff_pct(arp_b,arp_a):.0f}%)</td>
        </tr>
      </tbody>"""

# ============================================================
# Step 2 SVG
# ============================================================
# step2 json: list of (year, q, value)
q_map = {(r[0], r[1]): r[2] for r in D['step2']}
bars = []
for y in ['2022','2023','2024','2025']:
    for q in ['Q1','Q2','Q3','Q4']:
        bars.append((y, q, q_map[(y,q)]))
bars.append(('26.1Q','Q1', q_map[('2026','Q1')]))

# SCALE: 매출 * 0.75, baseline 195
SCALE = 0.75
BASE_Y = 195
year_x = {'2022':72, '2023':222, '2024':372, '2025':522, '26.1Q':672}

svg_parts = [
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
    if y != cur_year: cur_year=y; qi=0
    x = year_x[y] + qi*35 if y != '26.1Q' else year_x['26.1Q']
    w = 30 if y != '26.1Q' else 35
    h = v * SCALE
    yy = BASE_Y - h
    if y == '26.1Q':
        fill, tfill = '#f59e0b', '#b45309'
    elif q == 'Q1':
        fill, tfill = '#0085ca', '#0085ca'
    else:
        fill, tfill = '#bfdbfe', '#64748b'
    svg_parts.append(f'  <rect x="{x}" y="{yy:.1f}" width="{w}" height="{h:.1f}" fill="{fill}" rx="2"/>')
    svg_parts.append(f'  <text x="{x+w/2}" y="{yy-5:.1f}" text-anchor="middle" font-size="{"10" if y=="26.1Q" else "9"}" fill="{tfill}" font-weight="{"800" if y=="26.1Q" else "700"}">{int(round(v))}</text>')
    qi += 1

# 연도/분기 라벨
for yname in ['2022','2023','2024','2025']:
    xc = year_x[yname] + 2*35
    svg_parts.append(f'  <text x="{xc}" y="212" text-anchor="middle" font-size="11" fill="#64748b" font-weight="600">{yname}</text>')
svg_parts.append(f'  <text x="{year_x["26.1Q"]+17.5}" y="212" text-anchor="middle" font-size="11" fill="#f59e0b" font-weight="800">26.1Q</text>')

for yn in ['2022','2023','2024','2025']:
    for i,q in enumerate(['Q1','Q2','Q3','Q4']):
        xc = year_x[yn] + i*35 + 15
        svg_parts.append(f'  <text x="{xc}" y="225" text-anchor="middle" font-size="8" fill="#94a3b8">{q}</text>')
svg_parts.append(f'  <text x="{year_x["26.1Q"]+17.5}" y="225" text-anchor="middle" font-size="8" fill="#f59e0b" font-weight="700">Q1</text>')

svg_parts.append(f'  <rect x="700" y="8" width="10" height="10" fill="#0085ca" rx="1"/><text x="715" y="17" font-size="9" fill="#475569">Q1 성수기</text>')
svg_parts.append(f'  <rect x="790" y="8" width="10" height="10" fill="#f59e0b" rx="1"/><text x="805" y="17" font-size="9" fill="#475569">26.1Q</text>')
svg_parts.append('</svg>')
new_svg = '    ' + '\n    '.join(svg_parts)

# ============================================================
# Step 3 tbody
# ============================================================
s3 = D['step3']
def step3_cls(prev, now):
    if prev is None or now is None: return ""
    if now > prev + 0.5: return " up"
    if now < prev - 0.5: return " dn"
    return ""

def pub_row(grp, label, is_nhn=False):
    row_cls = ' class="nhn-row"' if is_nhn else ''
    tds = []
    prev = None
    for y in YEARS:
        d = s3[y].get(grp, {'eok':0,'games':0})
        total = sum(s3[y][g]['eok'] for g in s3[y])
        v = d['eok']; n = d['games']
        share = v/total*100 if total else 0
        is_26 = y == '26.1Q'
        td = 'num col26' if is_26 else 'num'
        cls = step3_cls(prev, v); prev = v
        if v < 0.05 and grp=='Zempot' and y in ('2023','2024'):
            tds.append(f'<td class="{td}">-<br><span style="color:#64748b;font-size:0.68rem;">-</span></td>')
        else:
            tds.append(f'<td class="{td}{cls}">{round(v)}억<br><span style="color:#64748b;font-size:0.68rem;">{share:.1f}%</span><br><span style="color:#cbd5e1;font-size:0.65rem;">{n}게임</span></td>')
    rev_y = {y: s3[y].get(grp,{'eok':0})['eok'] for y in YEARS}
    b, a = before_after_avg(rev_y)
    diff = a-b
    pct = diff/b*100 if b else 0
    change_cls = 'up' if diff>0.5 else ('dn' if diff<-0.5 else '')
    pct_html = f'{pct:+.0f}%'
    if pct >= 200:
        pct_html = f'<span style="color:#059669;font-weight:700;">{pct_html}</span>'
    change_td = f'<td class="num {change_cls}"><strong>{round(b)} → {round(a)}</strong><br>{diff:+.0f}억 ({pct_html})</td>'
    return f'        <tr{row_cls}><td>{label}</td>' + ''.join(tds) + change_td + '</tr>'

s3_rows = [
    pub_row('NHN', '<span class="nhn">NHN</span>', is_nhn=True),
    pub_row('네오위즈', '네오위즈 (피망)'),
    pub_row('Zempot', 'Zempot (WPL)'),
    pub_row('기타', '기타 (Konami 등)'),
]
# 합계
tot_tds = []
for y in YEARS:
    total = sum(s3[y][g]['eok'] for g in s3[y])
    td = 'num col26' if y=='26.1Q' else 'num'
    tot_tds.append(f'<td class="{td}">{round(total)}억</td>')
tot_b = sum(sum(s3[y][g]['eok'] for g in s3[y])*YR_MONTHS[y] for y in ['2022','2023','2024'])/36
tot_a = sum(sum(s3[y][g]['eok'] for g in s3[y])*YR_MONTHS[y] for y in ['2025','26.1Q'])/15
tot_diff = tot_a-tot_b; tot_pct = tot_diff/tot_b*100
s3_rows.append(f'        <tr class="tot"><td>합계</td>' + ''.join(tot_tds) + f'<td class="num up"><strong>{round(tot_b)} → {round(tot_a)}</strong><br>+{tot_diff:.0f}억 (+{tot_pct:.0f}%)</td></tr>')
step3_tbody = '<tbody>\n' + '\n'.join(s3_rows) + '\n      </tbody>'

# ============================================================
# Step 6 TOP5 매트릭스
# ============================================================
def short_name(n):
    if n.startswith('한게임포커 클래식'): return '한게임포커 클래식'
    if n.startswith('한게임 섯다'): return '한게임 섯다&맞고'
    if n.startswith('한게임 신맞고'): return '한게임 신맞고'
    if n.startswith('한게임 포커'): return '한게임 포커'
    if n.startswith('WPL'): return 'WPL (윈조이 포커)'
    if n.startswith('Pmang Poker'): return 'Pmang Poker'
    if n.startswith('Pmang Gostop'): return 'Pmang Gostop'
    if 'Yu-Gi-Oh' in n: return '유희왕 마스터 듀얼'
    return n[:18]

def pub_short(p):
    if 'NHN' in p: return 'NHN'
    if 'NEOWIZ' in p.upper(): return '네오위즈'
    if 'Zempot' in p or 'ZEMPOT' in p.upper(): return 'Zempot'
    if 'KONAMI' in p.upper(): return 'Konami'
    if '2ACE' in p.upper(): return '2ACE'
    return p[:10]

def is_nhn_pub(p): return 'NHN' in p

s6_data = D['step6']  # {'2022': {'1':(n,p,a), ...}}
thead6 = ('<thead>\n'
          '        <tr><th style="width:58px;">순위</th>'
          + ''.join(f'<th class="num{" col26" if y=="26.1Q" else ""}">\'{y[-2:]}</th>' if y!='26.1Q' else '<th class="num col26">\'26.1Q</th>' for y in YEARS)
          + '</tr>\n      </thead>')

def cell6(y, rnk):
    cell_d = s6_data[y].get(str(rnk))
    if not cell_d: return '<td class="num">-</td>'
    n,p,a = cell_d
    sn, sp = short_name(n), pub_short(p)
    nhn = is_nhn_pub(p)
    is_26 = y=='26.1Q'
    td_cls = 'num col26' if is_26 else 'num'
    name_c = '#0085ca' if nhn else '#64748b'
    amt_c = '#0085ca' if nhn else '#1e293b'
    amt_w = '800' if nhn else '700'
    return (f'<td class="{td_cls}" style="padding:6px 8px;">'
            f'<div style="font-size:0.7rem;color:{name_c};font-weight:{"700" if nhn else "500"};line-height:1.25;text-align:right;">{sn}</div>'
            f'<div style="font-size:0.68rem;color:#94a3b8;line-height:1.15;text-align:right;">{sp}</div>'
            f'<div style="font-size:0.88rem;color:{amt_c};font-weight:{amt_w};line-height:1.3;margin-top:2px;text-align:right;">{a}<span style="font-size:0.65rem;color:#94a3b8;font-weight:500;"> 억</span></div>'
            f'</td>')

tbody6_rows = []
for rnk in range(1,6):
    tbody6_rows.append(f'        <tr><td><strong>{rnk}위</strong></td>' + ''.join(cell6(y,rnk) for y in YEARS) + '</tr>')
step6_tbody = '<tbody>\n' + '\n'.join(tbody6_rows) + '\n      </tbody>'

# ============================================================
# HTML 패치 적용 (양쪽 파일)
# ============================================================
def patch_html(html):
    # Step 1 tbody (월평균 매출/MAU/ARPMAU 표)
    STEP1_RE = re.compile(
        r'<tbody>\s*\n\s*<tr><td>월평균 매출 \(억원\)</td>.*?</tbody>',
        re.DOTALL
    )
    m = STEP1_RE.search(html)
    if m:
        html = html[:m.start()] + step1_tbody + html[m.end():]

    # Step 1 해석 문구
    OLD_STEP1_INS_RE = re.compile(r'<div class="ins"><strong>해석:</strong> 웹보드는 <strong>대한민국[^<]*</strong>.*?</div>', re.DOTALL)
    # 그대로 유지 (MAU 반등 등 해석 문구는 손대지 않음)

    # Step 2 SVG (viewBox 0 0 900 230 로 새로 생성됨, 기존은 0 0 900 230 또는 0 -30 900 270)
    STEP2_SVG_RE = re.compile(
        r'    <svg viewBox="0 (-30|0) 900 (270|230|240)"[^>]*>.*?</svg>',
        re.DOTALL
    )
    m2 = STEP2_SVG_RE.search(html)
    if m2:
        html = html[:m2.start()] + new_svg + html[m2.end():]

    # Step 3 tbody (퍼블리셔별)
    STEP3_RE = re.compile(
        r'<tbody>\s*\n\s*<tr class="nhn-row"><td class="nhn">NHN</td>.*?<tr class="tot"><td>합계</td>.*?</tbody>',
        re.DOTALL
    )
    m3 = STEP3_RE.search(html)
    if m3:
        html = html[:m3.start()] + step3_tbody + html[m3.end():]

    # Step 6 — 순위별 표 (thead + tbody, 5x5 매트릭스)
    # 현재 구조: <table>\n      <thead>\n ...'순위'... '게임명 (26.1Q 기준)' ...  OR 새 구조 (연도×순위 매트릭스)
    STEP6_RE = re.compile(
        r'<thead>\s*\n\s*<tr><th style="width:58px;">순위</th>.*?</thead>\s*\n\s*<tbody>.*?</tbody>',
        re.DOTALL
    )
    m6 = STEP6_RE.search(html)
    if m6:
        html = html[:m6.start()] + thead6 + '\n      ' + step6_tbody + html[m6.end():]

    return html

for path in [WB, MAIN]:
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_refresh'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    h = patch_html(h)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    ok = '✅' if n==nc else '❌'
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {ok}")

print("\n[DONE]")
