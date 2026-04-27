# -*- coding: utf-8 -*-
"""Step 4 하단에 7게임 × 연도별 연령/성별/MAU/DL 비교 블록 추가"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
GAMES_ORDER = ['한게임 포커','한게임 섯다&맞고','한게임포커 클래식','한게임 신맞고',
               'Pmang Poker','피망 뉴맞고','WPL (윈조이 포커 리그)']

def is_nhn(name):
    return name.startswith('한게임')

def fmt_val(v, unit='', dec=1):
    if v is None: return '<span style="color:#cbd5e1;">-</span>'
    if dec == 0: return f"{v:.0f}{unit}"
    return f"{v:.1f}{unit}"

def build_metric_table(title, key, unit='', dec=1, color='#0085ca', extra_fmt=None):
    """metric별 (연령/성별/MAU/DL) 테이블 생성"""
    rows = []
    for game in GAMES_ORDER:
        data = D[game]
        row_cls = 'background:#eff6ff;' if is_nhn(game) else ''
        name_color = '#0085ca' if is_nhn(game) else '#1e293b'
        name_weight = '700' if is_nhn(game) else '500'
        tds = [
            f'<td style="padding:5px 8px;font-size:0.72rem;color:{name_color};font-weight:{name_weight};{row_cls}">{game}</td>'
        ]
        for yr in YEARS:
            d = data.get(yr, {})
            v = d.get(key)
            is_26 = (yr == '26.1Q')
            bg = 'background:#fef3c7;' if is_26 else row_cls
            if extra_fmt:
                txt = extra_fmt(d, yr) if v is not None else '<span style="color:#cbd5e1;">-</span>'
            else:
                txt = fmt_val(v, unit, dec)
            tds.append(f'<td class="num" style="padding:5px 8px;font-size:0.72rem;{bg}">{txt}</td>')
        rows.append('            <tr>' + ''.join(tds) + '</tr>')

    thead = ('<thead><tr>'
             '<th style="text-align:left;padding:6px 8px;background:#f8fafc;font-size:0.7rem;">게임</th>'
             + ''.join(f'<th class="num" style="padding:6px 8px;background:#f8fafc;font-size:0.7rem;">\'{y[-2:] if y!="26.1Q" else y}</th>' if y != '26.1Q'
                       else f'<th class="num" style="padding:6px 8px;background:#fbbf24;color:#78350f;font-size:0.7rem;">{y}</th>' for y in YEARS)
             + '</tr></thead>')

    return (f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;background:#fff;">\n'
            f'  <div style="font-size:0.82rem;font-weight:700;color:{color};margin-bottom:8px;">{title}</div>\n'
            f'  <table style="width:100%;border-collapse:collapse;">\n'
            f'    {thead}\n'
            f'    <tbody>\n'
            + '\n'.join(rows) + '\n'
            f'    </tbody>\n'
            f'  </table>\n'
            f'</div>')

# 성별 전용 포맷터
def gender_fmt(d, yr):
    m, f = d.get('m_pct'), d.get('f_pct')
    if m is None or f is None: return '<span style="color:#cbd5e1;">-</span>'
    return f'M{m:.0f}/F{f:.0f}'

# 4개 테이블
t_age = build_metric_table('👥 평균 연령 (세)', 'age', unit='세', dec=1, color='#0ea5e9')
t_gender = build_metric_table('⚧ 남/녀 비중 (%)', 'm_pct', color='#ec4899', extra_fmt=gender_fmt)
t_mau = build_metric_table('📊 월평균 MAU (만명)', 'mau_man', unit='만', dec=1, color='#f59e0b')
t_dl = build_metric_table('📥 월평균 다운로드 (만건)', 'dl_man', unit='만', dec=1, color='#059669')

# 블록 생성
demographics_block = f'''
    <div style="margin-top:20px;">
      <h4 style="font-size:0.95rem;font-weight:700;color:#0f172a;margin-bottom:8px;padding:8px 12px;background:linear-gradient(90deg,#f1f5f9,transparent);border-left:3px solid #0085ca;border-radius:3px;">📊 7게임 × 연도별 유저/다운로드 비교</h4>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        {t_age}
        {t_gender}
        {t_mau}
        {t_dl}
      </div>
      <div class="ins" style="margin-top:10px;"><strong>핵심:</strong>
        <strong class="nhn">한게임 섯다&맞고 33세</strong>로 7게임 중 가장 젊음, <strong>한게임 신맞고/피망 뉴맞고 44세</strong>로 가장 고령 — 고스톱 장르가 중장년층 타겟.
        성별: 포커류는 <strong>M75~80%</strong> 남성 편중, 고스톱은 <strong>M50~55%</strong>로 성별 균형.
        MAU 규모: <strong>피망 뉴맞고가 26.9만→10.7만(-60%)</strong>로 가장 큰 유저 이탈, 한게임 신맞고도 16.5만→11.6만 감소.
        다운로드: 전반적으로 신규 유입 감소세, 26.1Q에 <strong>한게임 신맞고 3.8만</strong>으로 신규 유입 최대.
      </div>
      <div class="formula-box" style="margin-top:10px;font-size:0.68rem;">
        <strong>📐 정의/공식</strong><br>
        • 연령/성별: <code>dw_app_monthly</code>의 <code>avg_age_total / female_pct / male_pct</code> (Sensor Tower demographics, 분기→월 forward-fill)<br>
        • MAU/DL: <code>mau / units</code> 월평균 (만 단위)<br>
        • WPL는 Sensor Tower demographics 미제공 (신규 앱) — 연령/성별/MAU NULL
      </div>
    </div>'''

# ============================================================
# HTML 삽입
# ============================================================
def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 중복 삽입 방지
    if '7게임 × 연도별 유저/다운로드 비교' in wb:
        print("  (이미 삽입됨, 스킵)")
        return html if is_main else wb

    # Step 4 테이블 끝을 찾기
    # 앵커: Step 4의 </table> 직후 (step-body는 열린 채)
    s4_q = wb.find('<div class="step-q">웹보드 대표 게임별 매출 추이')
    if s4_q == -1:
        raise RuntimeError("Step 4 못찾음")
    # Step 4 step-body 찾기
    step4_body_start = wb.find('<div class="step-body">', s4_q)
    # 해당 step-body 내 첫 </table>의 위치 찾기
    table_end = wb.find('</table>', step4_body_start)
    if table_end == -1:
        raise RuntimeError("Step 4 table 끝 못찾음")
    insert_pos = table_end + len('</table>')
    wb = wb[:insert_pos] + demographics_block + wb[insert_pos:]

    if is_main:
        return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    o = h.count('<div'); oc = h.count('</div>')
    print(f"\n[{os.path.basename(path)}]")
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"  <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
