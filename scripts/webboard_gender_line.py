# -*- coding: utf-8 -*-
"""남/녀 비중 차트를 라인 차트(M%)로 변경 — 연령 차트와 동일 스타일"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\webboard_7games.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
GAMES = ['한게임 포커','한게임 섯다&맞고','한게임포커 클래식','한게임 신맞고',
         'Pmang Poker','피망 뉴맞고','WPL (윈조이 포커 리그)']
COLORS = {'한게임 포커':'#0085ca','한게임 섯다&맞고':'#10b981','한게임포커 클래식':'#8b5cf6',
          '한게임 신맞고':'#f59e0b','Pmang Poker':'#dc2626','피망 뉴맞고':'#ec4899',
          'WPL (윈조이 포커 리그)':'#64748b'}

def is_nhn(n): return n.startswith('한게임')

def build_male_line():
    W, H = 720, 280
    left, right, top, bot = 60, 620, 40, 230
    def yc(v): return top + (bot-top) * (1 - (v-40)/50)  # 40~90% 범위
    xs = [left + i*((right-left)/4) for i in range(5)]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:900px;height:auto;display:block;margin:8px 0;">']
    # grid
    for gv in [40,50,60,70,80,90]:
        y = yc(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">M {gv}%</text>')
    # 50% 기준선 (남녀 동일)
    svg.append(f'<line x1="{left}" y1="{yc(50):.1f}" x2="{right}" y2="{yc(50):.1f}" stroke="#fca5a5" stroke-dasharray="4,3" stroke-width="1"/>')
    svg.append(f'<text x="{right-5}" y="{yc(50)-3:.1f}" text-anchor="end" font-size="9" fill="#dc2626">성별 균형선 (M=F)</text>')
    # X labels
    for i, yr in enumerate(YEARS):
        c = '#f59e0b' if yr=='26.1Q' else '#64748b'
        w = '800' if yr=='26.1Q' else '600'
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+20}" text-anchor="middle" font-size="11" fill="{c}" font-weight="{w}">{yr}</text>')
    # Lines per game (M% only)
    for game in GAMES:
        color = COLORS[game]
        vals = [D[game].get(yr, {}).get('m_pct') for yr in YEARS]
        pts_non_null = [(xs[i], yc(vals[i])) for i in range(5) if vals[i] is not None]
        if len(pts_non_null) >= 2:
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts_non_null)
            svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="{"2.5" if is_nhn(game) else "2"}" points="{pts_str}" opacity="{"1" if is_nhn(game) else "0.7"}"/>')
        for i, v in enumerate(vals):
            if v is not None:
                svg.append(f'<circle cx="{xs[i]:.1f}" cy="{yc(v):.1f}" r="3.5" fill="{color}"/>')

    # Legend
    legend_x = right + 10
    for i, game in enumerate(GAMES):
        y = top + i * 22
        color = COLORS[game]
        fw = '700' if is_nhn(game) else '400'
        svg.append(f'<rect x="{legend_x}" y="{y}" width="12" height="3" fill="{color}"/>')
        svg.append(f'<text x="{legend_x+17}" y="{y+5}" font-size="9" fill="{color}" font-weight="{fw}">{game}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

gender_line = build_male_line()

def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # 기존 남녀 비중 블록 찾기 (이전 두 형태 모두 대응)
    anchors = ['⚧ 남/녀 비중 (연도별)', '⚧ 남/녀 비중 (26.1Q)']
    wrap_start = None
    for a in anchors:
        anchor = wb.find(a)
        if anchor != -1:
            wrap_start = wb.rfind('<div style="border:1px solid #e2e8f0;border-radius:8px;', 0, anchor)
            break
    if wrap_start is None:
        print("  [anchor 못찾음]")
        return html if is_main else wb

    # depth counting으로 wrap 끝 찾기
    depth = 0
    div_re = re.compile(r'<div\b|</div>')
    wrap_end = None
    for m in div_re.finditer(wb, wrap_start):
        if m.group() == '</div>':
            depth -= 1
            if depth == 0:
                wrap_end = m.end()
                break
        else:
            depth += 1
    if not wrap_end:
        return html if is_main else wb

    new_wrap = (f'<div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;background:#fff;margin-bottom:12px;">\n'
                f'        <div style="font-size:0.82rem;font-weight:700;color:#ec4899;margin-bottom:6px;">⚧ 남성 비중 추이 (%, M 비율)</div>\n'
                f'        {gender_line}\n'
                f'        <div style="font-size:0.68rem;color:#94a3b8;margin-top:4px;">※ M% = 남성 비중, 50% 기준선 아래는 여성이 더 많음. F% = 100 - M%</div>\n'
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
