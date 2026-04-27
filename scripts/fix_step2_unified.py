# -*- coding: utf-8 -*-
"""
국가별 심층분석 탭의 Step 2 (퍼블리셔 국적별 매출 변화)를
in_revenue_top100_unified_os=TRUE 기준으로 재계산.

대상:
- all (3국 합산)
- KR / JP / US 각 sub-tab

퍼블리셔 국적 분류: KR(한국+NEXON강제), JP, 중화권(CN/HK/TW/MO+FUNFLY강제), 북미(US/Canada), 기타
KR 서브분류: KR TOP 5 합산(엔씨·넥슨·넷마블·카카오·NHN) / 한국 기타
"""
import os, re, psycopg2

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
BAK = MAIN + '.bak.before_step2_unified'

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

CASE_GROUP = """
    CASE
      WHEN publisher_name ILIKE '%%NEXON%%' THEN 'KR'
      WHEN publisher_name ILIKE '%%FUNFLY%%' THEN '중화권'
      WHEN publisher_country IN ('South Korea') THEN 'KR'
      WHEN publisher_country IN ('Japan') THEN 'JP'
      WHEN publisher_country IN ('China','Hong Kong','Taiwan','Macao') THEN '중화권'
      WHEN publisher_country IN ('US','USA','United States','Canada') THEN '북미'
      ELSE '기타'
    END
"""

# 국가별·연도별·그룹별 매출/게임수 집계 (unified 기준)
# 게임수 = 월평균 고유 앱수 (TOP100 per-month 평균)
def query_country(country):
    sql = f"""
    WITH base AS (
      SELECT
        CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, unified_app_id,
        {CASE_GROUP} AS grp,
        revenue_krw_100
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
    ),
    monthly AS (
      SELECT yr, grp, date, SUM(revenue_krw_100) AS m,
             COUNT(DISTINCT unified_app_id) AS n_m
      FROM base GROUP BY yr, grp, date
    )
    SELECT yr, grp, ROUND((AVG(m)/1e8)::numeric, 0) AS avg_eok,
           ROUND(AVG(n_m)::numeric, 0) AS avg_n
    FROM monthly GROUP BY yr, grp ORDER BY yr, grp;
    """
    cur.execute(sql, (country,))
    data = {}  # {yr: {grp: (eok, n)}}
    for yr, grp, eok, n in cur.fetchall():
        data.setdefault(yr, {})[grp] = (float(eok), int(n) if n else 0)
    return data

# KR TOP5 합산 (월평균 고유 앱수)
def query_kr_top5(country):
    like_conditions = ' OR '.join(['publisher_name ILIKE %s'] * 6)
    sql = f"""
    WITH base AS (
      SELECT
        CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, unified_app_id, revenue_krw_100
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
        AND ({like_conditions})
    ),
    monthly AS (
      SELECT yr, date, SUM(revenue_krw_100) AS m,
             COUNT(DISTINCT unified_app_id) AS n_m
      FROM base GROUP BY yr, date
    )
    SELECT yr, ROUND((AVG(m)/1e8)::numeric, 0), ROUND(AVG(n_m)::numeric, 0)
    FROM monthly GROUP BY yr ORDER BY yr;
    """
    cur.execute(sql, (country, '%NCSOFT%','%NEXON%','%Netmarble%','%Kakao Games%','%KAKAO GAMES%','%NHN%'))
    out = {}
    for yr, eok, n in cur.fetchall():
        out[yr] = (float(eok), int(n) if n else 0)
    return out

# 3국 합산 (월평균 고유 앱수 = 각 월 3국 전체 distinct (country,unified_app_id) 평균)
def query_all():
    sql = f"""
    WITH base AS (
      SELECT
        country,
        CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, unified_app_id,
        {CASE_GROUP} AS grp,
        revenue_krw_100
      FROM dw_app_monthly
      WHERE country IN ('KR','JP','US') AND in_revenue_top100_unified_os=TRUE
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
    ),
    monthly_per_country AS (
      SELECT yr, grp, date, country,
             SUM(revenue_krw_100) AS m,
             COUNT(DISTINCT unified_app_id) AS n_m
      FROM base GROUP BY yr, grp, date, country
    ),
    monthly_3c AS (
      SELECT yr, grp, date, SUM(m) AS m3, SUM(n_m) AS n_m
      FROM monthly_per_country GROUP BY yr, grp, date
    )
    SELECT yr, grp, ROUND((AVG(m3)/1e8)::numeric, 0), ROUND(AVG(n_m)::numeric, 0)
    FROM monthly_3c GROUP BY yr, grp ORDER BY yr, grp;
    """
    cur.execute(sql)
    data = {}
    for yr, grp, eok, n in cur.fetchall():
        data.setdefault(yr, {})[grp] = (float(eok), int(n) if n else 0)
    return data

print("[쿼리 시작]")
data_all = query_all()
data_kr = query_country('KR')
data_jp = query_country('JP')
data_us = query_country('US')
kr_top5 = query_kr_top5('KR')

# KR 기타 = KR 전체 - KR TOP5
kr_etc = {}
for yr in YEARS:
    kr_total = data_kr[yr].get('KR', (0,0))
    t5 = kr_top5.get(yr, (0,0))
    kr_etc[yr] = (kr_total[0] - t5[0], kr_total[1] - t5[1])

print("\n[all 합산] 2022:", data_all['2022'])
print("[KR] 2022:", data_kr['2022'], "| TOP5:", kr_top5['2022'], "| 기타:", kr_etc['2022'])
print("[JP] 2022:", data_jp['2022'])
print("[US] 2022:", data_us['2022'])

cur.close(); conn.close()

# ============================================================
# tbody 생성
# ============================================================
def fmt(v): return f"{int(round(v)):,}억" if v else "-"
def fmt_share(v, tot): return f"{v/tot*100:.1f}%" if tot else "0.0%"
def cls_updn(prev, now):
    if prev is None or now is None: return ""
    if now > prev + 0.5: return " up"
    if now < prev - 0.5: return " dn"
    return ""

def before_after(data_group):
    """data_group: {yr: (eok, n)} → (b_eok, a_eok)"""
    b = sum(data_group.get(y,(0,0))[0] * YR_M[y] for y in ['2022','2023','2024']) / 36
    a = sum(data_group.get(y,(0,0))[0] * YR_M[y] for y in ['2025','26.1Q']) / 15
    return b, a

def pct_change(b, a):
    if b == 0: return 0
    return (a-b)/b*100

def build_cell(eok, share, n, is_26=False, cls=''):
    td_base = 'num col26' if is_26 else 'num'
    return (f'<td class="{td_base}{cls}">{int(round(eok)):,}억'
            f'<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">{share:.1f}%</span>'
            f'<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">{n}게임</span></td>')

def build_sub_cell(eok, share, n, is_26=False):
    """서브 행 (더 작은 폰트)"""
    td_base = 'num col26' if is_26 else 'num'
    return (f'<td class="{td_base}" style="font-size:0.7rem;color:#475569;">{int(round(eok)):,}억'
            f'<br><span style="color:#94a3b8;font-weight:400;font-size:0.65rem;">{share:.1f}%</span>'
            f'<br><span style="color:#cbd5e1;font-weight:400;font-size:0.6rem;">{n}게임</span></td>')

def build_change_td(b, a, cls='', strong=True):
    diff = a-b
    pct = pct_change(b, a)
    cls_final = 'up' if diff>0.5 else ('dn' if diff<-0.5 else '')
    bold_open = '<strong>' if strong else ''
    bold_close = '</strong>' if strong else ''
    return (f'<td class="num {cls_final}">{bold_open}{int(round(b)):,}억 → {int(round(a)):,}억{bold_close}'
            f'<br>{"+" if diff>=0 else ""}{int(round(diff))}억 ({pct:+.0f}%)</td>')

def build_change_td_small(b, a):
    diff = a-b
    pct = pct_change(b, a)
    cls_final = 'up' if diff>0.5 else ('dn' if diff<-0.5 else '')
    return (f'<td class="num {cls_final}" style="font-size:0.7rem;"><strong>{int(round(b)):,} → {int(round(a)):,}</strong>'
            f'<br>{"+" if diff>=0 else ""}{int(round(diff))}억 ({pct:+.0f}%)</td>')

# ============================================================
# KR 탭용 tbody (한국 + TOP5 합산/기타 + 중화권 + 기타 + 북미 + 일본 + 합계)
# ============================================================
def build_kr_tbody():
    # 연도별 총합
    totals = {y: sum(data_kr[y].get(g,(0,0))[0] for g in ['KR','JP','중화권','북미','기타']) for y in YEARS}
    # 연도별 게임수 총합 (중복 카운트될 수 있어 부정확하지만 UI 목적)
    game_totals = {y: sum(data_kr[y].get(g,(0,0))[1] for g in ['KR','JP','중화권','북미','기타']) for y in YEARS}

    rows = []
    # 한국 (KR) 대분류
    prev = None
    tds = []
    for yr in YEARS:
        eok, n = data_kr[yr].get('KR', (0,0))
        cls = cls_updn(prev, eok); prev = eok
        tds.append(build_cell(eok, eok/totals[yr]*100 if totals[yr] else 0, n, is_26=(yr=='26.1Q'), cls=cls))
    b, a = before_after({y: data_kr[y].get('KR',(0,0)) for y in YEARS})
    rows.append(f'          <tr><td class="nhn">한국 (KR)</td>' + ''.join(tds) + build_change_td(b,a) + '</tr>')

    # └ TOP5 합산 (서브 행, 파란 배경)
    prev = None
    tds = []
    for yr in YEARS:
        eok, n = kr_top5.get(yr, (0,0))
        cls = cls_updn(prev, eok); prev = eok
        tds.append(build_sub_cell(eok, eok/totals[yr]*100 if totals[yr] else 0, n, is_26=(yr=='26.1Q')))
    b, a = before_after(kr_top5)
    rows.append(f'          <tr style="background:#dbeafe;"><td style="padding-left:28px;font-size:0.72rem;background:#dbeafe;font-weight:700;color:#1e40af;">└ 한국 TOP 5 합산 (엔씨·넥슨·넷마블·카카오·NHN)</td>'
                + ''.join(tds) + build_change_td_small(b,a) + '</tr>')

    # └ KR 기타
    prev = None
    tds = []
    for yr in YEARS:
        eok, n = kr_etc.get(yr, (0,0))
        cls = cls_updn(prev, eok); prev = eok
        tds.append(build_sub_cell(eok, eok/totals[yr]*100 if totals[yr] else 0, n, is_26=(yr=='26.1Q')))
    b, a = before_after(kr_etc)
    rows.append(f'          <tr style="background:#f8fafc;"><td style="padding-left:28px;font-size:0.72rem;color:#64748b;background:#f8fafc;">└ 한국 기타 (TOP 5 외)</td>'
                + ''.join(tds) + build_change_td_small(b,a) + '</tr>')

    # 중화권/기타/북미/일본
    for grp_key, label in [('중화권','중화권 <span style="font-size:0.65rem;color:var(--amber);">(FUNFLY 포함)</span>'),
                           ('기타','기타 (글로벌)'),
                           ('북미','북미'),
                           ('JP','일본')]:
        prev = None
        tds = []
        for yr in YEARS:
            eok, n = data_kr[yr].get(grp_key, (0,0))
            cls = cls_updn(prev, eok); prev = eok
            tds.append(build_cell(eok, eok/totals[yr]*100 if totals[yr] else 0, n, is_26=(yr=='26.1Q'), cls=cls))
        b, a = before_after({y: data_kr[y].get(grp_key,(0,0)) for y in YEARS})
        rows.append(f'          <tr><td>{label}</td>' + ''.join(tds) + build_change_td(b,a) + '</tr>')

    # 합계
    tot_tds = []
    for yr in YEARS:
        td_base = 'num col26' if yr=='26.1Q' else 'num'
        tot_tds.append(f'<td class="{td_base}">{int(round(totals[yr])):,}억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">{game_totals[yr]}게임</span></td>')
    b_tot = sum(totals[y] * YR_M[y] for y in ['2022','2023','2024']) / 36
    a_tot = sum(totals[y] * YR_M[y] for y in ['2025','26.1Q']) / 15
    rows.append(f'          <tr class="tot"><td>합계</td>' + ''.join(tot_tds)
                + build_change_td(b_tot, a_tot) + '</tr>')

    return '<tbody>\n' + '\n'.join(rows) + '\n        </tbody>'

# ============================================================
# JP/US 탭용 tbody (5행 + 합계)
# ============================================================
def build_simple_tbody(data_country, row_order, label_map):
    """
    data_country: {yr: {grp: (eok,n)}}
    row_order: ['JP','중화권','기타','북미','KR'] 순서
    label_map: {grp: display_label}
    """
    totals = {y: sum(data_country[y].get(g,(0,0))[0] for g in ['KR','JP','중화권','북미','기타']) for y in YEARS}
    game_totals = {y: sum(data_country[y].get(g,(0,0))[1] for g in ['KR','JP','중화권','북미','기타']) for y in YEARS}

    rows = []
    for grp in row_order:
        label = label_map[grp]
        prev = None
        tds = []
        for yr in YEARS:
            eok, n = data_country[yr].get(grp, (0,0))
            cls = cls_updn(prev, eok); prev = eok
            tds.append(build_cell(eok, eok/totals[yr]*100 if totals[yr] else 0, n, is_26=(yr=='26.1Q'), cls=cls))
        b, a = before_after({y: data_country[y].get(grp,(0,0)) for y in YEARS})
        row_cls = 'nhn' if grp=='KR' else ''
        td_cls = ' class="nhn"' if grp=='KR' else ''
        rows.append(f'          <tr class="{row_cls}"><td{td_cls}>{label}</td>' + ''.join(tds) + build_change_td(b,a) + '</tr>')

    # 합계
    tot_tds = []
    for yr in YEARS:
        td_base = 'num col26' if yr=='26.1Q' else 'num'
        tot_tds.append(f'<td class="{td_base}">{int(round(totals[yr])):,}억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">{game_totals[yr]}게임</span></td>')
    b_tot = sum(totals[y] * YR_M[y] for y in ['2022','2023','2024']) / 36
    a_tot = sum(totals[y] * YR_M[y] for y in ['2025','26.1Q']) / 15
    rows.append(f'          <tr class="tot"><td>합계</td>' + ''.join(tot_tds) + build_change_td(b_tot, a_tot) + '</tr>')

    return '<tbody>\n' + '\n'.join(rows) + '\n        </tbody>'

jp_tbody = build_simple_tbody(
    data_jp, ['JP','중화권','기타','북미','KR'],
    {'JP':'일본 (JP)',
     '중화권':'중화권 <span style="font-size:0.65rem;color:var(--amber);">(FUNFLY 포함)</span>',
     '기타':'기타 (글로벌)', '북미':'북미', 'KR':'한국 (KR)'}
)
us_tbody = build_simple_tbody(
    data_us, ['기타','북미','중화권','JP','KR'],
    {'JP':'일본',
     '중화권':'중화권 <span style="font-size:0.65rem;color:var(--amber);">(FUNFLY 포함)</span>',
     '기타':'기타 (글로벌)', '북미':'북미', 'KR':'한국 (KR)'}
)
all_tbody = build_simple_tbody(
    data_all, ['중화권','기타','JP','북미','KR'],
    {'JP':'일본 (JP)',
     '중화권':'<strong>중화권</strong>',
     '기타':'기타 (글로벌)', '북미':'북미', 'KR':'한국 (KR)'}
)
kr_tbody = build_kr_tbody()

# ============================================================
# HTML 패치 (ctab-panel 범위 내에서 Step 2 tbody 교체)
# ============================================================
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
if not os.path.exists(BAK):
    with open(BAK, 'w', encoding='utf-8') as f: f.write(html)
o_open = html.count('<div'); o_close = html.count('</div>')

def find_panel(html, pid):
    start = html.find(f'<div class="ctab-panel{" active" if pid=="all" else ""}" id="{pid}">')
    if start == -1:
        start = html.find(f'<div class="ctab-panel" id="{pid}">')
    # 끝: 다음 ctab-panel 또는 script
    candidates = [html.find('<div class="ctab-panel', start + 10),
                  html.find('<!-- ===== JavaScript', start),
                  html.find('</script>', start)]
    candidates = [c for c in candidates if c > start]
    end = min(candidates) if candidates else len(html)
    return start, end

# 각 sub-tab의 Step 2 table tbody 교체
# 앵커: "퍼블리셔 국적별 월평균 매출 변화" 이후 첫 <tbody>...</tbody>
def replace_step2(html, pid, new_tbody):
    p_start, p_end = find_panel(html, pid)
    section = html[p_start:p_end]
    # Step 2 step-q 찾기
    s2_pos = section.find('퍼블리셔 국적별 월평균 매출 변화')
    if s2_pos == -1: raise RuntimeError(f'{pid}: Step 2 앵커 못찾음')
    # 그 이후 첫 <tbody>...</tbody> 교체
    tbody_m = re.search(r'<tbody>.*?</tbody>', section[s2_pos:], re.DOTALL)
    if not tbody_m: raise RuntimeError(f'{pid}: tbody 못찾음')
    new_section = (section[:s2_pos + tbody_m.start()]
                   + new_tbody
                   + section[s2_pos + tbody_m.end():])
    return html[:p_start] + new_section + html[p_end:]

html = replace_step2(html, 'all', all_tbody)
html = replace_step2(html, 'kr', kr_tbody)
html = replace_step2(html, 'jp', jp_tbody)
html = replace_step2(html, 'us', us_tbody)

# 저장 + 검증
with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
n_open = html.count('<div'); n_close = html.count('</div>')
print(f"\n<div> {o_open}→{n_open}, </div> {o_close}→{n_close}  {'✅' if n_open==n_close else '❌'}")
print("[DONE]")
