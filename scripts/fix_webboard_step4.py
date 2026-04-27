# -*- coding: utf-8 -*-
"""
Step 4 수정:
- 헤더 "월평균 매출 (억원)" 명시
- 모든 수치를 Step 3과 동일 방식(전 기간 월수 기준)으로 재계산 → 일관성 확보
- 맨 아래 합계 행 추가 (8게임 월평균 합)
- webboard 단독 + 메인 HTML 동시 반영
"""
import os, re, psycopg2

WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"
MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

# 대표 게임 8개 식별 (brand name 기준 — unified_app_id 바뀔 수 있음에 대비)
GAMES = [
    ('한게임 포커',          'NHN',    'nhn'),
    ('한게임 섯다&맞고',      'NHN',    'nhn'),
    ('한게임포커 클래식',     'NHN',    'nhn'),
    ('한게임 신맞고',         'NHN',    'nhn'),
    ('Pmang Poker',          '네오위즈', 'neowiz'),
    ('피망 뉴맞고',           '네오위즈', 'neowiz'),
    ('WPL (윈조이 포커)',     'Zempot',  'zempot'),
    ('Yu-Gi-Oh! Master Duel','KONAMI',  'etc'),
]

# 게임명별 매칭 패턴 (DB상 이름 변동 대응)
NAME_PAT = {
    '한게임 포커':          ['한게임 포커'],
    '한게임 섯다&맞고':      ['한게임 섯다', '한게임섯다'],
    '한게임포커 클래식':     ['한게임포커 클래식', '한게임 포커 클래식'],
    '한게임 신맞고':         ['한게임 신맞고'],
    'Pmang Poker':          ['Pmang Poker'],  # for kakao & Casino Royal 둘 다
    '피망 뉴맞고':           ['피망 뉴맞고', 'Pmang Gostop'],
    'WPL (윈조이 포커)':     ['WPL', '윈조이 포커 리그'],
    'Yu-Gi-Oh! Master Duel':['Yu-Gi-Oh'],
}
PUB_PAT = {'NHN':'NHN', '네오위즈':'NEOWIZ', 'Zempot':'Zempot', 'KONAMI':'KONAMI'}

yr_months = {'2022':12, '2023':12, '2024':12, '2025':12, '26.1Q':3}
YEARS = ['2022','2023','2024','2025','26.1Q']

def query_game(name_patterns, pub_key):
    # 해당 브랜드의 모든 unified_app_id 매출 합
    like_clauses = " OR ".join(["name ILIKE %s"] * len(name_patterns))
    pat_args = [f"%{p}%" for p in name_patterns]
    sql = f"""
    WITH base AS (
        SELECT
            CASE WHEN date >= '2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
            date, revenue_krw_100
        FROM dw_app_monthly
        WHERE country='KR' AND in_revenue_top100_unified_os=TRUE
          AND genre IN ('Card','Casino','Board')
          AND publisher_name ILIKE %s
          AND ({like_clauses})
          AND date BETWEEN '2022-01-01' AND '2026-03-01'
    ),
    monthly_sum AS (
        SELECT yr, date, SUM(revenue_krw_100) AS m FROM base GROUP BY yr, date
    )
    SELECT yr, SUM(m) AS tot FROM monthly_sum GROUP BY yr ORDER BY yr;
    """
    cur.execute(sql, tuple([f"%{PUB_PAT[pub_key]}%"] + pat_args))
    result = {yr: 0 for yr in YEARS}
    for yr, tot in cur.fetchall():
        if tot:
            result[yr] = float(tot) / 1e8 / yr_months[yr]
    return result

data = {}
for name, pub, row_cls in GAMES:
    vals = query_game(NAME_PAT[name], pub)
    data[name] = {'vals': vals, 'pub': pub, 'row_cls': row_cls}

print("[Step 4 재계산 (억원, 월평균)]")
print(f"{'게임':<24}{'22':>8}{'23':>8}{'24':>8}{'25':>8}{'26.1Q':>8}")
for name, _, _ in GAMES:
    v = data[name]['vals']
    print(f"{name[:24]:<24}" + "".join(f"{v[y]:>8.1f}" for y in YEARS))

# 합계 (연도별)
sums = {yr: sum(data[n]['vals'][yr] for n,_,_ in GAMES) for yr in YEARS}
print("\n[연도별 합계]", sums)

cur.close(); conn.close()

# ============================================================
# Step 4 tbody + header 재생성
# ============================================================
def fmt(v):
    if v is None or v < 0.05:
        return '-'
    return f"{round(v)}"

def cls(prev, cur):
    if prev is None or cur is None: return ""
    if cur > prev + 0.5: return " up"
    if cur < prev - 0.5: return " dn"
    return ""

def make_row(name, pub, row_cls, vals):
    is_nhn = (pub == 'NHN')
    tr_cls = ' class="nhn-row"' if is_nhn else ''
    name_td_cls = ' class="nhn"' if is_nhn else ''
    # 이름 볼드(NHN + WPL 기존 강조 유지)
    name_inner = f'<strong>{name}</strong>' if (is_nhn or name.startswith('WPL')) else name
    # 앞/뒤 변화
    before = sum(vals[y] * yr_months[y] for y in ['2022','2023','2024']) / 36
    after = sum(vals[y] * yr_months[y] for y in ['2025','26.1Q']) / 15
    diff = after - before
    pct = (diff/before*100) if before > 0.05 else None
    change_cls = 'up' if diff > 0.5 else ('dn' if diff < -0.5 else '')
    pct_str = f"{pct:+.0f}%" if pct is not None else "-"
    # Zempot/Konami 같이 매우 큰 변화율은 색 강조
    pct_html = pct_str
    if pct is not None and pct >= 200:
        pct_html = f'<span style="color:#059669;font-weight:700;">{pct_str}</span>'
    elif pct is not None and pct <= -50:
        pct_html = f'<span style="color:#dc2626;font-weight:700;">{pct_str}</span>'

    # 데이터 셀
    tds = []
    prev = None
    for i, yr in enumerate(YEARS):
        v = vals[yr]
        is_26 = (yr == '26.1Q')
        td_base = 'num col26' if is_26 else 'num'
        c = cls(prev, v)
        prev = v if v > 0.05 else prev
        tds.append(f'<td class="{td_base}{c}">{fmt(v)}</td>')

    # 변화 셀
    b_disp = round(before)
    a_disp = round(after)
    change_td = (f'<td class="num {change_cls}"><strong>{b_disp} → {a_disp}</strong><br>'
                 f'{diff:+.0f}억 ({pct_html})</td>')

    style = ''
    if name.startswith('Pmang'): style = ' style="border-top:2px solid #e2e8f0;"'
    elif name.startswith('WPL'): style = ' style="border-top:2px solid #e2e8f0;background:#fffbeb;"'
    elif 'Yu-Gi-Oh' in name: style = ' style="border-top:2px solid #e2e8f0;"'

    return (f'        <tr{tr_cls}{style}>'
            f'<td{name_td_cls}>{name_inner}</td>'
            f'<td>{pub}</td>'
            + ''.join(tds) + change_td + '</tr>')

rows_html = [make_row(n, p, c, data[n]['vals']) for n,p,c in GAMES]

# 합계 행
before_tot = sum(data[n]['vals'][y] * yr_months[y] for n,_,_ in GAMES for y in ['2022','2023','2024']) / 36
after_tot = sum(data[n]['vals'][y] * yr_months[y] for n,_,_ in GAMES for y in ['2025','26.1Q']) / 15
diff_tot = after_tot - before_tot
pct_tot = diff_tot/before_tot*100

tot_tds = []
for yr in YEARS:
    is_26 = (yr == '26.1Q')
    td_base = 'num col26' if is_26 else 'num'
    tot_tds.append(f'<td class="{td_base}">{round(sums[yr])}</td>')

tot_change = (f'<td class="num up"><strong>{round(before_tot)} → {round(after_tot)}</strong><br>'
              f'{diff_tot:+.0f}억 ({pct_tot:+.0f}%)</td>')

rows_html.append(
    f'        <tr class="tot">'
    f'<td>합계 (8게임)</td><td></td>' + ''.join(tot_tds) + tot_change + '</tr>'
)

new_tbody = '<tbody>\n' + '\n'.join(rows_html) + '\n      </tbody>'

# 새 thead (단위 명시)
new_thead = (
    '<thead>\n'
    '        <tr>'
    '<th>게임</th><th>퍼블리셔</th>'
    '<th class="num">\'22</th><th class="num">\'23</th><th class="num">\'24</th>'
    '<th class="num">\'25</th><th class="num col26">\'26.1Q</th>'
    '<th class="num">25년 전후 변화</th>'
    '</tr>\n'
    '        <tr><th colspan="8" style="background:#f8fafc;font-weight:500;color:#64748b;font-size:0.7rem;text-align:right;padding:4px 10px;">단위: 월평균 매출 (억원) · 전 기간 월수 기준</th></tr>\n'
    '      </thead>'
)

# ============================================================
# Step 4 패치 — tbody + thead 교체
# 앵커: Step 4 step-body 내부 table
# ============================================================
# Step 4 고유 패턴: '대표 게임별 매출 추이' 바로 아래 table
STEP4_TABLE_RE = re.compile(
    r'(<div class="step-q">웹보드 대표 게임별 매출 추이[^<]*</div>[\s\S]*?<table>\s*\n)'
    r'\s*(<thead>[\s\S]*?</thead>)\s*\n'
    r'\s*(<tbody>[\s\S]*?</tbody>)\s*',
    re.MULTILINE
)

def patch(html):
    m = STEP4_TABLE_RE.search(html)
    if not m:
        raise RuntimeError("Step 4 테이블 매칭 실패")
    replacement = m.group(1) + '      ' + new_thead + '\n      ' + new_tbody + '\n'
    html = html[:m.start()] + replacement + html[m.end():]
    return html

for path in [WB, MAIN]:
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_step4fix'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    h = patch(h)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    ok = '✅' if n == nc else '❌'
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {ok}")

print("\n[DONE]")
