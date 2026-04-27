# -*- coding: utf-8 -*-
"""
Step 3 (장르별 매출 변화) 를 unified 기준으로 재계산.
- 각 sub-tab(KR/JP/US)에 대해 현재 장르 리스트 유지하면서 unified 값으로 교체
- 누락된 소규모 장르는 "기타 장르" 행으로 합산 → 합계가 Step 1과 일치
- KR만 Role Playing을 MMORPG / 비MMORPG RPG 로 분리 (sub_genre 기반)
"""
import os, re, psycopg2
conn = psycopg2.connect("postgresql://postgres:upsize@10.77.13.162:5432/AI_mobilegame")
cur = conn.cursor()

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
BAK = MAIN + '.bak.before_step3_unified'

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}

# ============================================================
# 국가별·연도별·장르별 unified 매출 (월평균)
# KR만 Role Playing을 MMORPG/비MMORPG로 쪼갬
# ============================================================
def query_country_genre(country, split_rpg=False):
    genre_expr = """
        CASE
          WHEN genre='Role Playing' AND sub_genre='MMORPG' THEN 'MMORPG'
          WHEN genre='Role Playing' THEN '비MMORPG RPG'
          ELSE genre
        END
    """ if split_rpg else "genre"
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
    )
    SELECT yr, g, (AVG(m)/1e8)::numeric AS avg_eok
    FROM monthly GROUP BY yr, g ORDER BY yr, avg_eok DESC NULLS LAST;
    """
    cur.execute(sql, (country,))
    data = {}  # {yr: {genre: eok}}
    for yr, g, eok in cur.fetchall():
        data.setdefault(yr, {})[g if g else '(null)'] = float(eok) if eok else 0
    return data

# ============================================================
# 현재 HTML의 Step 3 장르 행 리스트 (sub-tab별)
# ============================================================
GENRES_KR = ['Strategy','Puzzle','비MMORPG RPG','Casual','Casino','Adventure',
             'Sports','Card','Racing','Arcade','Simulation','Action','MMORPG']
GENRES_JP = ['Arcade','Strategy','Simulation','Card','Puzzle','Action','Sports',
             'Role Playing','Adventure','Music']
GENRES_US = None  # US Step 3 구조 확인 필요 — 일단 매출 상위 ~10개 장르 자동 추출

def build_step3_tbody(data, genres=None, top_n=10):
    """
    data: {yr: {genre: eok}}
    genres: 표시할 장르 리스트. None이면 25년 전후 평균 기준 상위 top_n + 기타
    """
    # 모든 장르
    all_g = set()
    for yr_data in data.values():
        all_g.update(yr_data.keys())

    if genres is None:
        # 25년 전후 월평균 기준 매출 상위 top_n
        scored = {}
        for g in all_g:
            total = sum(data[y].get(g, 0) * YR_M[y] for y in YEARS)
            scored[g] = total
        sorted_g = sorted(scored.items(), key=lambda x: -x[1])
        genres = [g for g, _ in sorted_g[:top_n] if g != '(null)']

    rows = []
    # 표시 장르 합
    shown_totals = {y: 0 for y in YEARS}
    for g in genres:
        tds = []
        prev = None
        for y in YEARS:
            v = data[y].get(g, 0)
            cls = ''
            if prev is not None:
                if v > prev + 0.5: cls = ' up'
                elif v < prev - 0.5: cls = ' dn'
            prev = v
            td_base = 'num col26' if y == '26.1Q' else 'num'
            tds.append(f'<td class="{td_base}{cls}">{int(round(v)):,}</td>')
            shown_totals[y] += v
        # 전/후 변화
        b = sum(data[y].get(g, 0) * YR_M[y] for y in ['2022','2023','2024']) / 36
        a = sum(data[y].get(g, 0) * YR_M[y] for y in ['2025','26.1Q']) / 15
        diff = a - b
        pct = (diff/b*100) if b else 0
        cls_final = 'up' if diff > 0.5 else ('dn' if diff < -0.5 else '')
        color = '#059669' if diff > 0 else '#dc2626'
        rows.append(
            f'          <tr><td><strong>{g}</strong></td>' + ''.join(tds)
            + f'<td class="num {cls_final}"><strong>{int(round(b)):,} → {int(round(a)):,}</strong>'
            f'<br>{"+" if diff>=0 else ""}{int(round(diff))}억 '
            f'(<span style="color:{color};font-weight:700;">{pct:+.0f}%</span>)</td></tr>'
        )

    # 기타 장르 (잔여 장르 합)
    other_g = [g for g in all_g if g not in genres and g != '(null)']
    if other_g:
        etc_data = {y: sum(data[y].get(g, 0) for g in other_g) for y in YEARS}
        tds = []
        prev = None
        for y in YEARS:
            v = etc_data[y]
            cls = ''
            if prev is not None:
                if v > prev + 0.5: cls = ' up'
                elif v < prev - 0.5: cls = ' dn'
            prev = v
            td_base = 'num col26' if y == '26.1Q' else 'num'
            tds.append(f'<td class="{td_base}{cls}">{int(round(v)):,}</td>')
            shown_totals[y] += v
        b = sum(etc_data[y] * YR_M[y] for y in ['2022','2023','2024']) / 36
        a = sum(etc_data[y] * YR_M[y] for y in ['2025','26.1Q']) / 15
        diff = a - b
        pct = (diff/b*100) if b else 0
        cls_final = 'up' if diff > 0.5 else ('dn' if diff < -0.5 else '')
        color = '#059669' if diff > 0 else '#dc2626'
        rows.append(
            f'          <tr style="color:#94a3b8;"><td>기타 장르 <small style="color:#cbd5e1;">({len(other_g)}개)</small></td>'
            + ''.join(tds)
            + f'<td class="num {cls_final}"><strong>{int(round(b)):,} → {int(round(a)):,}</strong>'
            f'<br>{"+" if diff>=0 else ""}{int(round(diff))}억 ({pct:+.0f}%)</td></tr>'
        )

    # 합계 (Step 1과 일치해야 함)
    tot_tds = []
    for y in YEARS:
        td_base = 'num col26' if y == '26.1Q' else 'num'
        tot_tds.append(f'<td class="{td_base}">{int(round(shown_totals[y])):,}</td>')
    tot_b = sum(shown_totals[y] * YR_M[y] for y in ['2022','2023','2024']) / 36
    tot_a = sum(shown_totals[y] * YR_M[y] for y in ['2025','26.1Q']) / 15
    tot_diff = tot_a - tot_b
    rows.append(
        f'          <tr class="tot"><td>합계</td>' + ''.join(tot_tds)
        + f'<td class="num">+{int(round(tot_diff))}억</td></tr>'
    )

    return '<tbody>\n' + '\n'.join(rows) + '\n        </tbody>'

# ============================================================
# 쿼리 + 빌드
# ============================================================
data_kr = query_country_genre('KR', split_rpg=True)
data_jp = query_country_genre('JP', split_rpg=False)
data_us = query_country_genre('US', split_rpg=False)

# KR은 지정 장르 리스트 사용
kr_tbody = build_step3_tbody(data_kr, GENRES_KR)
# JP도 지정 장르 리스트
jp_tbody = build_step3_tbody(data_jp, GENRES_JP)
# US는 자동 상위 10개
us_tbody = build_step3_tbody(data_us, None, top_n=10)

# 검증: 합계 출력
def total_2022(data):
    return sum(data['2022'].values())
print(f"[검증] KR 2022 장르 합계: {total_2022(data_kr):.0f}억 (Step 1 = 3,835)")
print(f"[검증] JP 2022 장르 합계: {total_2022(data_jp):.0f}억 (Step 1 = 9,700)")
print(f"[검증] US 2022 장르 합계: {total_2022(data_us):.0f}억 (Step 1 = 14,687)")

# ============================================================
# HTML 교체
# ============================================================
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
if not os.path.exists(BAK):
    with open(BAK, 'w', encoding='utf-8') as f: f.write(html)
o_open = html.count('<div'); o_close = html.count('</div>')

def find_panel(html, pid):
    start = html.find(f'<div class="ctab-panel{" active" if pid=="all" else ""}" id="{pid}">')
    if start == -1:
        start = html.find(f'<div class="ctab-panel" id="{pid}">')
    candidates = [html.find('<div class="ctab-panel', start + 10),
                  html.find('<!-- ===== JavaScript', start)]
    candidates = [c for c in candidates if c > start]
    end = min(candidates) if candidates else len(html)
    return start, end

def replace_step3(html, pid, new_tbody):
    p_start, p_end = find_panel(html, pid)
    section = html[p_start:p_end]
    s3_pos = section.find('장르별 월평균 매출 변화')
    if s3_pos == -1: raise RuntimeError(f'{pid}: Step 3 앵커 못찾음')
    tbody_m = re.search(r'<tbody>.*?</tbody>', section[s3_pos:], re.DOTALL)
    if not tbody_m: raise RuntimeError(f'{pid}: tbody 못찾음')
    new_section = (section[:s3_pos + tbody_m.start()]
                   + new_tbody
                   + section[s3_pos + tbody_m.end():])
    return html[:p_start] + new_section + html[p_end:]

html = replace_step3(html, 'kr', kr_tbody)
html = replace_step3(html, 'jp', jp_tbody)
html = replace_step3(html, 'us', us_tbody)

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
n_open = html.count('<div'); n_close = html.count('</div>')
print(f"\n<div> {o_open}→{n_open}, </div> {o_close}→{n_close}  {'✅' if n_open==n_close else '❌'}")
print("[DONE]")

cur.close(); conn.close()
