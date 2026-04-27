# -*- coding: utf-8 -*-
"""남/녀 비중 차트를 연도별(5년) 모두 보여주도록 변경"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
GAMES = ['한게임 포커','한게임 섯다&맞고','한게임포커 클래식','한게임 신맞고',
         'Pmang Poker','피망 뉴맞고','WPL (윈조이 포커 리그)']

def is_nhn(n): return n.startswith('한게임')

# ============================================================
# 연도별 남녀 비중 수평 누적 막대 (게임별 그룹, 게임 내 5연도 세로 나열)
# ============================================================
def build_gender_yearly():
    W = 780
    row_h = 16  # 각 연도 바 높이
    row_gap = 3  # 연도 간 간격
    game_gap = 14  # 게임 그룹 간 간격
    left = 180
    right = 660
    total_w = right - left
    top = 50

    # 총 높이 계산
    per_game_h = 5 * (row_h + row_gap) + game_gap
    H = top + per_game_h * len(GAMES) + 20

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:960px;height:auto;display:block;margin:8px 0;">']
    svg.append(f'<text x="{(left+right)/2}" y="20" text-anchor="middle" font-size="11" fill="#475569" font-weight="600">연도별 남/녀 비중 · M(파랑) / F(분홍)</text>')

    # 연도 컬러 코드 라벨 (상단)
    svg.append(f'<text x="{left-8}" y="38" text-anchor="end" font-size="9" fill="#94a3b8">연도</text>')

    cur_y = top
    for g_idx, game in enumerate(GAMES):
        # 게임명 (그룹 중앙)
        game_y_mid = cur_y + per_game_h/2 - game_gap/2
        name_color = '#0085ca' if is_nhn(game) else '#475569'
        fw = '700' if is_nhn(game) else '500'
        svg.append(f'<text x="{left-8}" y="{game_y_mid+4}" text-anchor="end" font-size="11" fill="{name_color}" font-weight="{fw}">{game}</text>')
        # 구분선 (게임 간)
        if g_idx > 0:
            svg.append(f'<line x1="0" y1="{cur_y-game_gap/2}" x2="{W}" y2="{cur_y-game_gap/2}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')

        for yi, yr in enumerate(YEARS):
            y = cur_y + yi * (row_h + row_gap)
            d = D[game].get(yr, {})
            m = d.get('m_pct'); f = d.get('f_pct')
            # 연도 라벨 (바 왼쪽)
            yr_c = '#f59e0b' if yr == '26.1Q' else '#94a3b8'
            yr_w = '700' if yr == '26.1Q' else '500'
            yr_lbl = yr if yr == '26.1Q' else f"'{yr[-2:]}"
            svg.append(f'<text x="{left-4}" y="{y+row_h/2+3.5}" text-anchor="end" font-size="9" fill="{yr_c}" font-weight="{yr_w}">{yr_lbl}</text>')

            if m is None or f is None:
                svg.append(f'<rect x="{left}" y="{y}" width="{total_w}" height="{row_h}" fill="#f8fafc" rx="2"/>')
                svg.append(f'<text x="{left+total_w/2}" y="{y+row_h/2+3.5}" text-anchor="middle" font-size="9" fill="#cbd5e1">-</text>')
                continue
            m_w = total_w * m / 100
            f_w = total_w * f / 100
            svg.append(f'<rect x="{left}" y="{y}" width="{m_w:.1f}" height="{row_h}" fill="#3b82f6" rx="2"/>')
            svg.append(f'<rect x="{left+m_w:.1f}" y="{y}" width="{f_w:.1f}" height="{row_h}" fill="#ec4899" rx="2"/>')
            # 값 라벨 (바 안쪽)
            if m_w > 40:
                svg.append(f'<text x="{left+m_w/2:.1f}" y="{y+row_h/2+3.5}" text-anchor="middle" font-size="9" fill="#fff" font-weight="700">M{m:.0f}%</text>')
            if f_w > 40:
                svg.append(f'<text x="{left+m_w+f_w/2:.1f}" y="{y+row_h/2+3.5}" text-anchor="middle" font-size="9" fill="#fff" font-weight="700">F{f:.0f}%</text>')

        cur_y += per_game_h

    svg.append('</svg>')
    return '\n'.join(svg)

gender_yearly = build_gender_yearly()

# 기존 gender 차트 블록 찾아서 교체
# 헤더 문구 "⚧ 남/녀 비중 (26.1Q)" → "⚧ 남/녀 비중 (연도별)"
def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 기존 블록 찾기: ⚧ 남/녀 비중 으로 시작하는 wrapping div
    anchor = wb.find('<div style="font-size:0.82rem;font-weight:700;color:#ec4899;margin-bottom:6px;">⚧ 남/녀 비중')
    if anchor == -1:
        print("  [anchor 못찾음]")
        return html if is_main else wb
    # wrapping div 시작점 (한 단계 위)
    wrap_start = wb.rfind('<div style="border:1px solid #e2e8f0;border-radius:8px;', 0, anchor)
    # wrap 끝 (깊이 카운팅)
    depth = 0; i = wrap_start
    div_re = re.compile(r'<div\b|</div>')
    wrap_end = None
    for m in div_re.finditer(wb, i):
        if m.group() == '</div>':
            depth -= 1
            if depth == 0:
                wrap_end = m.end()
                break
        else:
            depth += 1
    if not wrap_end:
        print("  [wrap 끝 못찾음]")
        return html if is_main else wb

    new_wrap = (f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;background:#fff;margin-bottom:12px;">\n'
                f'        <div style="font-size:0.82rem;font-weight:700;color:#ec4899;margin-bottom:6px;">⚧ 남/녀 비중 (연도별)</div>\n'
                f'        {gender_yearly}\n'
                f'      </div>')
    wb = wb[:wrap_start] + new_wrap + wb[wrap_end:]

    if is_main: return html[:ws] + wb + html[we:]
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
