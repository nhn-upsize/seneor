# -*- coding: utf-8 -*-
"""남/녀 비중을 26.1Q 기준 단일 바 차트로 복구"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

GAMES = ['한게임 포커','한게임 섯다&맞고','한게임포커 클래식','한게임 신맞고',
         'Pmang Poker','피망 뉴맞고','WPL (윈조이 포커 리그)']

def is_nhn(n): return n.startswith('한게임')

def build_gender_26q():
    W, H = 720, 280
    bar_h = 20
    row_gap = 12
    left, right, top = 160, 600, 40
    total_w = right - left

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:900px;height:auto;display:block;margin:8px 0;">']
    svg.append(f'<text x="{(left+right)/2}" y="20" text-anchor="middle" font-size="11" fill="#475569" font-weight="600">26.1Q 기준 · M(파랑) / F(분홍)</text>')
    for i, game in enumerate(GAMES):
        y = top + i * (bar_h + row_gap)
        d = D[game].get('26.1Q', {})
        m = d.get('m_pct'); f = d.get('f_pct')
        name_color = '#0085ca' if is_nhn(game) else '#475569'
        fw = '700' if is_nhn(game) else '500'
        svg.append(f'<text x="{left-8}" y="{y+bar_h/2+4}" text-anchor="end" font-size="11" fill="{name_color}" font-weight="{fw}">{game}</text>')
        if m is None or f is None:
            svg.append(f'<rect x="{left}" y="{y}" width="{total_w}" height="{bar_h}" fill="#f1f5f9" rx="3"/>')
            svg.append(f'<text x="{left+total_w/2}" y="{y+bar_h/2+4}" text-anchor="middle" font-size="10" fill="#cbd5e1">데이터 없음</text>')
            continue
        m_w = total_w * m / 100
        f_w = total_w * f / 100
        svg.append(f'<rect x="{left}" y="{y}" width="{m_w:.1f}" height="{bar_h}" fill="#3b82f6" rx="3"/>')
        svg.append(f'<rect x="{left+m_w:.1f}" y="{y}" width="{f_w:.1f}" height="{bar_h}" fill="#ec4899" rx="3"/>')
        svg.append(f'<text x="{left+m_w/2:.1f}" y="{y+bar_h/2+4}" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">M {m:.0f}%</text>')
        svg.append(f'<text x="{left+m_w+f_w/2:.1f}" y="{y+bar_h/2+4}" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">F {f:.0f}%</text>')
    svg.append('</svg>')
    return '\n'.join(svg)

gender_svg = build_gender_26q()

def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    anchors = ['⚧ 남/녀 비중 (연도별)', '⚧ 남/녀 비중 (26.1Q)', '⚧ 남성 비중 추이', '⚧ 남/녀 비중']
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
                f'        <div style="font-size:0.82rem;font-weight:700;color:#ec4899;margin-bottom:6px;">⚧ 남/녀 비중 (26.1Q 대표값)</div>\n'
                f'        {gender_svg}\n'
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
