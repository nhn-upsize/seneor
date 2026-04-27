# -*- coding: utf-8 -*-
"""NHN_market_analysis.html 전체 탭의 '국가별 매출 순위별 월평균 규모' 테이블 하단에
연도별 라인 차트 3개 (KR/JP/US) 추가"""
import os, re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

YEARS = ['2022','2023','2024','2025','26.1Q']
# 실측값 (이미 HTML 내 표시된 값들)
DATA = {
    'KR': {
        '1위':    [406, 476, 510, 455, 487],
        '10위':   [67, 94, 85, 132, 88],
        '20위':   [42, 45, 48, 62, 46],
        '50위':   [23, 20, 21, 22, 23],
        '100위':  [20, 26, 9, 8, 15],
    },
    'JP': {
        '1위':    [748, 640, 559, 470, 433],
        '10위':   [213, 190, 235, 219, 223],
        '20위':   [105, 111, 139, 127, 131],
        '50위':   [62, 47, 58, 52, 54],
        '100위':  [40, 26, 29, 59, 35],
    },
    'US': {
        '1위':    [896, 1680, 2267, 1793, 1483],
        '10위':   [278, 319, 329, 408, 406],
        '20위':   [206, 189, 212, 267, 222],
        '50위':   [113, 107, 105, 110, 110],
        '100위':  [43, 57, 62, 86, 73],
    },
}
COUNTRIES = [
    ('KR', '🇰🇷 KR 한국', '#3b82f6', '#dbeafe', '#93c5fd'),
    ('JP', '🇯🇵 JP 일본', '#ef4444', '#fee2e2', '#fca5a5'),
    ('US', '🇺🇸 US 미국', '#a855f7', '#f3e8ff', '#d8b4fe'),
]
# 순위별 색상 (진한 색 → 연한 색)
RANK_COLORS = {
    '1위':   {'KR':'#1e40af','JP':'#991b1b','US':'#581c87'},
    '10위':  {'KR':'#2563eb','JP':'#dc2626','US':'#7c3aed'},
    '20위':  {'KR':'#3b82f6','JP':'#ef4444','US':'#a855f7'},
    '50위':  {'KR':'#60a5fa','JP':'#f87171','US':'#c084fc'},
    '100위': {'KR':'#93c5fd','JP':'#fca5a5','US':'#d8b4fe'},
}

def build_country_chart(country, name, color, bg, light):
    """로그 스케일 라인 차트 (5 순위 × 5 연도)"""
    W = 440; H = 290
    left, right, top, bot = 50, 400, 40, 230
    # 로그 스케일 (1위 값이 100위 대비 30배 이상)
    import math
    all_vals = [v for r in DATA[country].values() for v in r]
    log_min = math.log10(max(min(all_vals), 1))
    log_max = math.log10(max(all_vals))
    # 적당히 반올림
    log_min = math.floor(log_min)  # 1 (log10)
    log_max = math.ceil(log_max)    # 4 (log10)
    def yc(v):
        if v <= 0: return bot
        lv = math.log10(v)
        return top + (bot-top) * (1 - (lv - log_min) / (log_max - log_min))
    xs = [left + i*((right-left)/(len(YEARS)-1)) for i in range(len(YEARS))]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:500px;height:auto;display:block;">']
    # 제목
    svg.append(f'<text x="{(left+right)/2}" y="18" text-anchor="middle" font-size="12" fill="{color}" font-weight="700">{name}</text>')

    # Y grid (log scale — 10/100/1000 등)
    for exp in range(int(log_min), int(log_max)+1):
        v = 10**exp
        y = yc(v)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        label = f'{v:,}억' if v < 10000 else f'{v//10000:,}만억'
        svg.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{label}</text>')
    # X labels
    for i, lbl in enumerate(YEARS):
        c = '#f59e0b' if lbl=='26.1Q' else '#64748b'
        w = '800' if lbl=='26.1Q' else '600'
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+16}" text-anchor="middle" font-size="10" fill="{c}" font-weight="{w}">{lbl}</text>')

    # 5개 라인 (순위별)
    for rank in ['1위','10위','20위','50위','100위']:
        rc = RANK_COLORS[rank][country]
        vals = DATA[country][rank]
        pts = [(xs[i], yc(vals[i])) for i in range(len(vals))]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
        svg.append(f'<polyline fill="none" stroke="{rc}" stroke-width="2" points="{pts_str}"/>')
        for i, (x, y) in enumerate(pts):
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{rc}"/>')
        # 끝 값 라벨
        svg.append(f'<text x="{pts[-1][0]+6:.1f}" y="{pts[-1][1]+4:.1f}" font-size="10" fill="{rc}" font-weight="700">{rank}</text>')

    svg.append('</svg>')
    return ''.join(svg)

# 3국 차트 블록
charts_html = '\n      <!-- 순위별 라인 차트 (로그 스케일) -->\n      <div style="margin-top:18px;padding:14px;background:#f8fafc;border-radius:8px;">\n'
charts_html += '        <div style="font-size:0.82rem;font-weight:700;color:#475569;margin-bottom:10px;">📈 국가별 순위 매출 추이 (로그 스케일) — 1위 ~ 100위</div>\n'
charts_html += '        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">\n'
for cc, name, color, bg, light in COUNTRIES:
    chart = build_country_chart(cc, name, color, bg, light)
    charts_html += f'          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:8px;">{chart}</div>\n'
charts_html += '        </div>\n'
charts_html += '        <div style="font-size:0.68rem;color:#94a3b8;margin-top:8px;">※ 로그 스케일 — 1위(100억+)와 100위(10억+) 한 화면에 모두 표시. 선 5개 = 순위 1/10/20/50/100</div>\n'
charts_html += '      </div>'

# HTML 삽입 — '국가별 매출 순위별 월평균 규모' 표 그리드 닫는 곳 직후
with open(MAIN, 'r', encoding='utf-8') as f: h = f.read()
o_open = h.count('<div'); o_close = h.count('</div>')

if '📈 국가별 순위 매출 추이 (로그 스케일)' in h:
    print("이미 추가됨")
else:
    # 앵커: <div class="step-q">국가별 매출 순위별 월평균 규모
    anchor = '국가별 매출 순위별 월평균 규모'
    idx = h.find(anchor)
    if idx == -1:
        raise RuntimeError('앵커 못찾음')
    # 해당 step-body 안의 첫 .ins 직전에 삽입 (3국 테이블 다음)
    ins_pos = h.find('<div class="ins"', idx)
    if ins_pos == -1:
        raise RuntimeError('.ins 못찾음')
    h = h[:ins_pos] + charts_html.strip() + '\n      ' + h[ins_pos:]
    n_open = h.count('<div'); n_close = h.count('</div>')
    with open(MAIN, 'w', encoding='utf-8') as f: f.write(h)
    print(f"<div> {o_open}→{n_open}, </div> {o_close}→{n_close}  {'✅' if n_open==n_close else '❌'}")
