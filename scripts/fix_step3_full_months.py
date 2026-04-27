# -*- coding: utf-8 -*-
"""Step 3 장르별 공식을 '전체 월수 분모'로 통일 → Step 1과 합계 일치"""
import os, re, psycopg2

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

def query_country_genre(country, split_rpg=False):
    genre_expr = """
        CASE
          WHEN genre='Role Playing' AND sub_genre='MMORPG' THEN 'MMORPG'
          WHEN genre='Role Playing' THEN '비MMORPG RPG'
          ELSE genre
        END
    """ if split_rpg else "genre"
    # 핵심 변경: 등장월 AVG → 전체월수로 나누기
    sql = f"""
    WITH base AS (
      SELECT
        CASE WHEN date>='2026-01-01' THEN '26.1Q' ELSE TO_CHAR(date,'YYYY') END AS yr,
        date, {genre_expr} AS g, revenue_krw_100
      FROM dw_app_monthly
      WHERE country=%s AND in_revenue_top100_unified_os=TRUE
        AND date BETWEEN '2022-01-01' AND '2026-03-01'
    ),
    monthly AS (
      SELECT yr, g, date, SUM(revenue_krw_100) AS m FROM base GROUP BY yr, g, date
    ),
    agg AS (
      SELECT yr, g, SUM(m) AS total FROM monthly GROUP BY yr, g
    )
    SELECT yr, g,
      (total / (CASE WHEN yr='26.1Q' THEN 3 ELSE 12 END) / 1e8)::numeric AS avg_eok
    FROM agg ORDER BY yr, avg_eok DESC NULLS LAST;
    """
    cur.execute(sql, (country,))
    data = {}
    for yr, g, eok in cur.fetchall():
        data.setdefault(yr, {})[g if g else '(null)'] = float(eok) if eok else 0
    return data

GENRES_KR = ['Strategy','Puzzle','비MMORPG RPG','Casual','Casino','Adventure',
             'Sports','Card','Racing','Arcade','Simulation','Action','MMORPG']
GENRES_JP = ['Arcade','Strategy','Simulation','Card','Puzzle','Action','Sports',
             'Role Playing','Adventure','Music']

def build_tbody(data, genres=None, top_n=10):
    all_g = set()
    for d in data.values(): all_g.update(d.keys())
    if genres is None:
        scored = {g: sum(data[y].get(g,0)*YR_M[y] for y in YEARS) for g in all_g if g != '(null)'}
        genres = [g for g,_ in sorted(scored.items(), key=lambda x:-x[1])[:top_n]]

    rows = []
    shown = {y:0 for y in YEARS}
    for g in genres:
        tds = []; prev = None
        for y in YEARS:
            v = data[y].get(g, 0)
            cls = ''
            if prev is not None:
                if v > prev + 0.5: cls = ' up'
                elif v < prev - 0.5: cls = ' dn'
            prev = v
            td_base = 'num col26' if y == '26.1Q' else 'num'
            tds.append(f'<td class="{td_base}{cls}">{int(round(v)):,}</td>')
            shown[y] += v
        b = sum(data[y].get(g,0)*YR_M[y] for y in ['2022','2023','2024'])/36
        a = sum(data[y].get(g,0)*YR_M[y] for y in ['2025','26.1Q'])/15
        diff = a-b; pct = (diff/b*100) if b else 0
        cls_ch = 'up' if diff>0.5 else ('dn' if diff<-0.5 else '')
        color = '#059669' if diff > 0 else '#dc2626'
        rows.append(f'          <tr><td><strong>{g}</strong></td>' + ''.join(tds)
                    + f'<td class="num {cls_ch}"><strong>{int(round(b)):,} → {int(round(a)):,}</strong>'
                    f'<br>{"+" if diff>=0 else ""}{int(round(diff))}억 '
                    f'(<span style="color:{color};font-weight:700;">{pct:+.0f}%</span>)</td></tr>')

    # 기타 장르
    other_g = [g for g in all_g if g not in genres and g != '(null)']
    if other_g:
        etc = {y: sum(data[y].get(g,0) for g in other_g) for y in YEARS}
        tds = []; prev = None
        for y in YEARS:
            v = etc[y]
            cls = ' up' if (prev is not None and v > prev+0.5) else (' dn' if (prev is not None and v < prev-0.5) else '')
            prev = v
            td_base = 'num col26' if y == '26.1Q' else 'num'
            tds.append(f'<td class="{td_base}{cls}">{int(round(v)):,}</td>')
            shown[y] += v
        b = sum(etc[y]*YR_M[y] for y in ['2022','2023','2024'])/36
        a = sum(etc[y]*YR_M[y] for y in ['2025','26.1Q'])/15
        diff = a-b; pct = (diff/b*100) if b else 0
        cls_ch = 'up' if diff>0.5 else ('dn' if diff<-0.5 else '')
        color = '#059669' if diff > 0 else '#dc2626'
        rows.append(f'          <tr style="color:#94a3b8;"><td>기타 장르 <small style="color:#cbd5e1;">({len(other_g)}개)</small></td>'
                    + ''.join(tds)
                    + f'<td class="num {cls_ch}"><strong>{int(round(b)):,} → {int(round(a)):,}</strong>'
                    f'<br>{"+" if diff>=0 else ""}{int(round(diff))}억 ({pct:+.0f}%)</td></tr>')

    tot_tds = []
    for y in YEARS:
        td_base = 'num col26' if y=='26.1Q' else 'num'
        tot_tds.append(f'<td class="{td_base}">{int(round(shown[y])):,}</td>')
    tb = sum(shown[y]*YR_M[y] for y in ['2022','2023','2024'])/36
    ta = sum(shown[y]*YR_M[y] for y in ['2025','26.1Q'])/15
    rows.append(f'          <tr class="tot"><td>합계</td>' + ''.join(tot_tds)
                + f'<td class="num">+{int(round(ta-tb))}억</td></tr>')

    return '<tbody>\n' + '\n'.join(rows) + '\n        </tbody>'

data_kr = query_country_genre('KR', split_rpg=True)
data_jp = query_country_genre('JP', split_rpg=False)
data_us = query_country_genre('US', split_rpg=False)

kr_tbody = build_tbody(data_kr, GENRES_KR)
jp_tbody = build_tbody(data_jp, GENRES_JP)
us_tbody = build_tbody(data_us, None, top_n=10)

# 검증
print(f"[KR 2022 합계] {sum(data_kr['2022'].values()):.1f} (Step 1 = 3,835)")
print(f"[JP 2022 합계] {sum(data_jp['2022'].values()):.1f} (Step 1 = 9,700)")
print(f"[US 2022 합계] {sum(data_us['2022'].values()):.1f} (Step 1 = 14,687)")

cur.close(); conn.close()

# HTML 교체
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
o = html.count('<div'); oc = html.count('</div>')

def find_panel(html, pid):
    start = html.find(f'<div class="ctab-panel{" active" if pid=="all" else ""}" id="{pid}">')
    if start == -1: start = html.find(f'<div class="ctab-panel" id="{pid}">')
    cands = [html.find('<div class="ctab-panel', start+10),
             html.find('<!-- ===== JavaScript', start)]
    cands = [c for c in cands if c > start]
    return start, (min(cands) if cands else len(html))

def replace_step3(html, pid, new_tbody):
    ps, pe = find_panel(html, pid); sec = html[ps:pe]
    s3 = sec.find('장르별 월평균 매출 변화')
    if s3 == -1: return html
    tb_m = re.search(r'<tbody>.*?</tbody>', sec[s3:], re.DOTALL)
    if not tb_m: return html
    return html[:ps] + sec[:s3+tb_m.start()] + new_tbody + sec[s3+tb_m.end():] + html[pe:]

html = replace_step3(html, 'kr', kr_tbody)
html = replace_step3(html, 'jp', jp_tbody)
html = replace_step3(html, 'us', us_tbody)

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
n = html.count('<div'); nc = html.count('</div>')
print(f"\n<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
