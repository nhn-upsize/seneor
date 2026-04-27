# -*- coding: utf-8 -*-
"""중화권 매출/비중 차트를 임원 보고용 통합 combo 차트로 재구성"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\china_share_data.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}
COUNTRIES = [('KR','🇰🇷','한국','#3b82f6','#60a5fa'),
             ('JP','🇯🇵','일본','#ef4444','#f87171'),
             ('US','🇺🇸','미국','#a855f7','#c084fc')]

def ba_pair(country):
    ch_b = sum(D[country][y].get('중화권',0)*YR_M[y] for y in ['2022','2023','2024'])/36
    ch_a = sum(D[country][y].get('중화권',0)*YR_M[y] for y in ['2025','26.1Q'])/15
    all_b = sum((D[country][y].get('중화권',0)+D[country][y].get('기타',0))*YR_M[y] for y in ['2022','2023','2024'])/36
    all_a = sum((D[country][y].get('중화권',0)+D[country][y].get('기타',0))*YR_M[y] for y in ['2025','26.1Q'])/15
    sh_b = ch_b/all_b*100
    sh_a = ch_a/all_a*100
    return ch_b, ch_a, sh_b, sh_a

def build_combo_panel(country, flag, name, color_dark, color_light):
    # 데이터 준비
    rev_vals = [D[country][y].get('중화권', 0) for y in YEARS]
    share_vals = []
    for y in YEARS:
        ch = D[country][y].get('중화권', 0)
        tot = ch + D[country][y].get('기타', 0)
        share_vals.append(ch/tot*100 if tot else 0)

    # SVG 크기
    W = 480; H = 260
    left, right, top, bot = 50, 430, 56, 200
    # 좌측 Y: 매출 (0~국가별 max)
    rev_max = max(rev_vals)
    rev_max_round = int((rev_max // 1000 + 1) * 1000) if rev_max > 1000 else int((rev_max // 500 + 1) * 500)
    # 우측 Y: 비중 (0~50%)
    share_max = 50

    xs = [left + i*((right-left)/4) for i in range(5)]
    bar_w = 28

    def y_rev(v): return bot - (bot-top) * v / rev_max_round
    def y_share(v): return bot - (bot-top) * v / share_max

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block;">']
    # 제목
    svg.append(f'<text x="{W/2}" y="22" text-anchor="middle" font-size="13" fill="{color_dark}" font-weight="800">{flag} {country} {name}</text>')

    # Y 그리드 (좌측 매출)
    for i in range(5):
        gv = rev_max_round * i / 4
        y = y_rev(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-4}" y="{y+3:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{int(gv):,}</text>')
    # 우측 Y (비중)
    for gv in [0, 25, 50]:
        y = y_share(gv)
        svg.append(f'<text x="{right+4}" y="{y+3:.1f}" font-size="9" fill="{color_dark}">{gv}%</text>')

    # 막대 (매출)
    for i, v in enumerate(rev_vals):
        x = xs[i] - bar_w/2
        h = bot - y_rev(v)
        y = y_rev(v)
        is_26 = YEARS[i] == '26.1Q'
        fill = '#f59e0b' if is_26 else color_light
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{fill}" rx="2"/>')
        # 값
        svg.append(f'<text x="{xs[i]:.1f}" y="{y-4:.1f}" text-anchor="middle" font-size="9" fill="{"#b45309" if is_26 else color_dark}" font-weight="700">{int(round(v)):,}</text>')

    # 라인 (비중)
    pts = [(xs[i], y_share(share_vals[i])) for i in range(5)]
    pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
    svg.append(f'<polyline fill="none" stroke="{color_dark}" stroke-width="2.5" points="{pts_str}"/>')
    for i, (x, y) in enumerate(pts):
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color_dark}" stroke="white" stroke-width="1.5"/>')
        # 비중 값
        svg.append(f'<text x="{x:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="9" fill="{color_dark}" font-weight="700">{share_vals[i]:.1f}%</text>')

    # X 라벨
    for i, yr in enumerate(YEARS):
        c = '#f59e0b' if yr == '26.1Q' else '#64748b'
        w = '800' if yr == '26.1Q' else '500'
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+16}" text-anchor="middle" font-size="10" fill="{c}" font-weight="{w}">{yr}</text>')

    # 축 라벨
    svg.append(f'<text x="{left-28}" y="{top-10}" font-size="9" fill="#475569" font-weight="600">매출(억)</text>')
    svg.append(f'<text x="{right+5}" y="{top-10}" font-size="9" fill="{color_dark}" font-weight="600">비중%</text>')

    # 범례 (하단 좌측)
    svg.append(f'<rect x="{left}" y="{H-32}" width="10" height="10" fill="{color_light}" rx="1"/>')
    svg.append(f'<text x="{left+14}" y="{H-23}" font-size="10" fill="#475569">매출(바)</text>')
    svg.append(f'<rect x="{left+70}" y="{H-28}" width="14" height="3" fill="{color_dark}"/>')
    svg.append(f'<text x="{left+87}" y="{H-23}" font-size="10" fill="#475569">비중(라인)</text>')
    # 26.1Q 표시
    svg.append(f'<rect x="{left+160}" y="{H-32}" width="10" height="10" fill="#f59e0b" rx="1"/>')
    svg.append(f'<text x="{left+174}" y="{H-23}" font-size="10" fill="#475569">26.1Q</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

# 각 국가 combo 패널 + 전후 요약 카드
def build_country_card(country, flag, name, color_dark, color_light):
    chart = build_combo_panel(country, flag, name, color_dark, color_light)
    ch_b, ch_a, sh_b, sh_a = ba_pair(country)
    rev_pct = (ch_a-ch_b)/ch_b*100 if ch_b else 0
    sh_d = sh_a - sh_b

    return f'''<div style="border:1px solid #e2e8f0;border-radius:10px;padding:14px;background:#fff;border-top:4px solid {color_dark};">
        {chart}
        <div style="margin-top:10px;padding-top:10px;border-top:1px dashed #e2e8f0;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          <div style="text-align:center;padding:6px;background:#f8fafc;border-radius:6px;">
            <div style="font-size:0.65rem;color:#64748b;">매출 25년 전후</div>
            <div style="font-size:0.88rem;color:{color_dark};font-weight:800;margin-top:2px;">{int(round(ch_b)):,} → {int(round(ch_a)):,}</div>
            <div style="font-size:0.7rem;color:#059669;font-weight:700;">+{int(round(ch_a-ch_b)):,}억 ({rev_pct:+.0f}%)</div>
          </div>
          <div style="text-align:center;padding:6px;background:#f8fafc;border-radius:6px;">
            <div style="font-size:0.65rem;color:#64748b;">비중 25년 전후</div>
            <div style="font-size:0.88rem;color:{color_dark};font-weight:800;margin-top:2px;">{sh_b:.1f}% → {sh_a:.1f}%</div>
            <div style="font-size:0.7rem;color:#059669;font-weight:700;">{sh_d:+.1f}%p</div>
          </div>
        </div>
      </div>'''

cards = ''.join(build_country_card(cc, flag, name, cd, cl) for cc, flag, name, cd, cl in COUNTRIES)

# 전체 블록 (기존 2개 차트 대체)
new_block = f'''
      <!-- 임원 보고용 통합 combo 차트 -->
      <h4 style="font-size:0.88rem;font-weight:700;color:#0f172a;margin:18px 0 10px;padding:8px 12px;background:linear-gradient(90deg,#fef3c7,transparent);border-left:3px solid #d97706;border-radius:3px;">📊 3국별 중화권 매출 × 비중 추이 (25년 전후 요약)</h4>
      <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;">
        {cards}
      </div>'''

# HTML 교체: 기존 중화권 매출 비중 추이 & 절대값 2개 블록을 neue combo block으로 교체
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
o = html.count('<div'); oc = html.count('</div>')

# 기존 블록 찾기: "📈 중화권 매출 비중 추이" 시작, "📊 중화권 매출 절대값 추이" 다음 svg 끝까지
def find_block(html):
    h_start = html.find('📈 중화권 매출 비중 추이')
    if h_start == -1: return None, None
    # 감싸는 <h4> 앞 위치
    wrap_start = html.rfind('<h4', 0, h_start)
    # 끝: "📊 중화권 매출 절대값 추이" 포함 마지막 SVG의 닫는 </svg>
    bar_h = html.find('📊 중화권 매출 절대값 추이', h_start)
    if bar_h == -1: return None, None
    svg_end = html.find('</svg>', bar_h)
    # svg 다음의 줄 끝까지 포함
    end = svg_end + len('</svg>')
    return wrap_start, end

s, e = find_block(html)
if s is None:
    raise RuntimeError("기존 중화권 차트 블록 못찾음")

block_removed = html[s:e]
print(f"[제거] {e-s}자 · <div>={block_removed.count('<div')} </div>={block_removed.count('</div>')}")
html = html[:s] + new_block.strip() + html[e:]

n = html.count('<div'); nc = html.count('</div>')
with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
