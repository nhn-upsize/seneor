# -*- coding: utf-8 -*-
"""남/녀 비중 — 게임별 미니 차트 (5연도 세로 막대 흐름) · small multiples 레이아웃"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
GAMES = ['한게임 포커','한게임 섯다&맞고','한게임포커 클래식','한게임 신맞고',
         'Pmang Poker','피망 뉴맞고','WPL (윈조이 포커 리그)']
def is_nhn(n): return n.startswith('한게임')

def build_mini_chart(game):
    """게임 하나의 미니 차트 — 5연도 세로 누적 막대"""
    W = 320; H = 180
    pad_l = 20; pad_r = 10; pad_t = 30; pad_b = 32
    bar_w = (W - pad_l - pad_r) / 5 * 0.7
    gap = (W - pad_l - pad_r) / 5 * 0.3
    max_h = H - pad_t - pad_b

    name_color = '#0085ca' if is_nhn(game) else '#475569'
    fw = '700' if is_nhn(game) else '600'

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block;">']
    svg.append(f'<text x="{W/2}" y="18" text-anchor="middle" font-size="11" fill="{name_color}" font-weight="{fw}">{game}</text>')
    # Y guidelines (0, 50, 100)
    for v in [0, 50, 100]:
        y = pad_t + max_h * (1 - v/100)
        svg.append(f'<line x1="{pad_l}" y1="{y}" x2="{W-pad_r}" y2="{y}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')

    for i, yr in enumerate(YEARS):
        x = pad_l + i * ((W - pad_l - pad_r) / 5) + gap/2
        d = D[game].get(yr, {})
        m = d.get('m_pct'); f = d.get('f_pct')
        yr_c = '#f59e0b' if yr=='26.1Q' else '#94a3b8'
        yr_w = '700' if yr=='26.1Q' else '500'
        yr_lbl = yr if yr=='26.1Q' else f"'{yr[-2:]}"
        svg.append(f'<text x="{x+bar_w/2}" y="{H-pad_b+14}" text-anchor="middle" font-size="9" fill="{yr_c}" font-weight="{yr_w}">{yr_lbl}</text>')

        if m is None or f is None:
            svg.append(f'<rect x="{x}" y="{pad_t}" width="{bar_w}" height="{max_h}" fill="#f8fafc" stroke="#e2e8f0" stroke-dasharray="2,2" rx="2"/>')
            svg.append(f'<text x="{x+bar_w/2}" y="{pad_t+max_h/2+4}" text-anchor="middle" font-size="8" fill="#cbd5e1">-</text>')
            continue
        m_h = max_h * m / 100
        f_h = max_h * f / 100
        # M (아래)
        svg.append(f'<rect x="{x}" y="{pad_t+f_h}" width="{bar_w}" height="{m_h:.1f}" fill="#3b82f6" rx="2"/>')
        # F (위)
        svg.append(f'<rect x="{x}" y="{pad_t}" width="{bar_w}" height="{f_h:.1f}" fill="#ec4899" rx="2"/>')
        # M% 값 (바 내부 아래)
        if m_h > 18:
            svg.append(f'<text x="{x+bar_w/2}" y="{pad_t+f_h+m_h/2+3}" text-anchor="middle" font-size="9" fill="#fff" font-weight="700">{m:.0f}</text>')
        # F% 값 (바 내부 위)
        if f_h > 18:
            svg.append(f'<text x="{x+bar_w/2}" y="{pad_t+f_h/2+3}" text-anchor="middle" font-size="9" fill="#fff" font-weight="700">{f:.0f}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# 게임별 미니 차트 카드
mini_cards = []
for game in GAMES:
    chart = build_mini_chart(game)
    mini_cards.append(f'<div style="border:1px solid #e2e8f0;border-radius:6px;padding:8px;background:#fff;">{chart}</div>')

# 전체 블록 (3열 × 3행 그리드, 마지막 1칸은 범례)
legend_box = ('<div style="border:1px solid #e2e8f0;border-radius:6px;padding:10px 14px;background:#fafbfc;display:flex;flex-direction:column;justify-content:center;gap:8px;">'
              '<div style="font-size:0.78rem;font-weight:700;color:#475569;">범례</div>'
              '<div style="display:flex;align-items:center;gap:6px;font-size:0.72rem;"><span style="display:inline-block;width:12px;height:12px;background:#3b82f6;border-radius:2px;"></span>남성 (M%)</div>'
              '<div style="display:flex;align-items:center;gap:6px;font-size:0.72rem;"><span style="display:inline-block;width:12px;height:12px;background:#ec4899;border-radius:2px;"></span>여성 (F%)</div>'
              '<div style="font-size:0.65rem;color:#94a3b8;margin-top:4px;">각 바: 100% 누적 · 숫자는 % · 26.1Q는 주황 라벨 · WPL은 demographics 미제공</div>'
              '</div>')

gender_block = (f'<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px;">'
                + ''.join(mini_cards)
                + legend_box
                + '</div>')

def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    anchors = ['⚧ 남/녀 비중 (26.1Q 대표값)','⚧ 남/녀 비중 (연도별)', '⚧ 남/녀 비중 (26.1Q)', '⚧ 남성 비중 추이', '⚧ 남/녀 비중']
    wrap_start = None
    for a in anchors:
        anchor = wb.find(a)
        if anchor != -1:
            wrap_start = wb.rfind('<div style="border:1px solid #e2e8f0;border-radius:8px;', 0, anchor)
            if wrap_start != -1: break
    if wrap_start is None or wrap_start == -1:
        return html if is_main else wb

    depth = 0
    div_re = re.compile(r'<div\b|</div>')
    wrap_end = None
    for m in div_re.finditer(wb, wrap_start):
        if m.group() == '</div>':
            depth -= 1
            if depth == 0: wrap_end = m.end(); break
        else: depth += 1
    if not wrap_end:
        return html if is_main else wb

    new_wrap = (f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;background:#fff;margin-bottom:12px;">\n'
                f'        <div style="font-size:0.82rem;font-weight:700;color:#ec4899;margin-bottom:8px;">⚧ 게임별 남/녀 비중 연도별 흐름</div>\n'
                f'        {gender_block}\n'
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
