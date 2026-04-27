# -*- coding: utf-8 -*-
"""
전체 탭 수정:
1. '매출 집중도 분석 (80/20)' 섹션 제거
2. '3국 중화권 퍼블리셔 매출 비중 추이' 섹션을 상세 버전으로 교체
   - 절대값 (중화권 매출/전체 매출) + 비중 % + 연도별 변화 테이블
   - 비중 추이 라인 차트
   - 절대 매출 바 차트
   - 25년 전후 비교 요약
"""
import re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
with open(r"C:\Users\NHN\Documents\sensortower_api\scripts\china_share_data.json", 'r', encoding='utf-8') as f:
    D = json.load(f)

YEARS = ['2022','2023','2024','2025','26.1Q']
YR_M = {'2022':12,'2023':12,'2024':12,'2025':12,'26.1Q':3}
COUNTRIES = [('KR','🇰🇷','한국','#3b82f6'),
             ('JP','🇯🇵','일본','#ef4444'),
             ('US','🇺🇸','미국','#a855f7')]

# 전/후 평균 계산 (월수 가중)
def period_avg(country, group):
    b_sum = sum(D[country][y].get(group, 0) * YR_M[y] for y in ['2022','2023','2024'])
    a_sum = sum(D[country][y].get(group, 0) * YR_M[y] for y in ['2025','26.1Q'])
    return b_sum/36, a_sum/15

# ============================================================
# 1) 상세 테이블 (국가별 행, 연도별 열)
#    각 셀에 중화권 매출 / 전체 매출 / 비중 3줄 표시
# ============================================================
def build_table():
    rows = []
    for cc, flag, name, color in COUNTRIES:
        # 각 셀: 중화권/전체/비중 (3줄)
        tds = []
        prev_share = None
        for yr in YEARS:
            d = D[cc][yr]
            ch = d.get('중화권', 0); ot = d.get('기타', 0); tot = ch + ot
            share = ch/tot*100 if tot else 0
            is_26 = yr == '26.1Q'
            td_base = 'num col26' if is_26 else 'num'
            # 비중 변화 색상
            cls = ''
            if prev_share is not None:
                if share > prev_share + 0.5: cls = ' up'
                elif share < prev_share - 0.5: cls = ' dn'
            prev_share = share
            tds.append(
                f'<td class="{td_base}{cls}" style="padding:6px 8px;vertical-align:middle;">'
                f'<div style="font-size:0.82rem;color:{color};font-weight:800;line-height:1.2;">{share:.1f}%</div>'
                f'<div style="font-size:0.68rem;color:#64748b;font-weight:600;line-height:1.2;margin-top:2px;">{ch:,.0f}억</div>'
                f'<div style="font-size:0.62rem;color:#cbd5e1;line-height:1.1;">/ {tot:,.0f}억</div>'
                f'</td>'
            )
        # 전/후 변화
        b_ch, a_ch = period_avg(cc, '중화권')
        b_tot_ch, a_tot_ch = period_avg(cc, '중화권')
        # 전체 전/후
        b_all = sum((D[cc][y].get('중화권',0)+D[cc][y].get('기타',0)) * YR_M[y] for y in ['2022','2023','2024'])/36
        a_all = sum((D[cc][y].get('중화권',0)+D[cc][y].get('기타',0)) * YR_M[y] for y in ['2025','26.1Q'])/15
        b_share = b_ch/b_all*100 if b_all else 0
        a_share = a_ch/a_all*100 if a_all else 0
        d_share = a_share - b_share
        d_ch_pct = (a_ch-b_ch)/b_ch*100 if b_ch else 0
        change_color = '#059669' if d_share > 0 else '#dc2626'
        change_td = (
            f'<td class="num" style="padding:6px 8px;vertical-align:middle;'
            f'border-left:2px solid #e2e8f0;background:#f8fafc;">'
            f'<div style="font-size:0.82rem;color:{change_color};font-weight:800;line-height:1.2;">'
            f'▲ +{d_share:.1f}%p</div>'
            f'<div style="font-size:0.68rem;color:#059669;font-weight:600;line-height:1.2;margin-top:2px;">'
            f'중화권 +{a_ch-b_ch:,.0f}억 (+{d_ch_pct:.0f}%)</div>'
            f'<div style="font-size:0.62rem;color:#94a3b8;line-height:1.1;">'
            f'전{b_share:.1f}% → 후{a_share:.1f}%</div>'
            f'</td>'
        )
        row_style = f'border-left:3px solid {color};'
        rows.append(
            f'<tr style="{row_style}">'
            f'<td style="padding:6px 10px;font-weight:700;color:{color};">'
            f'<span style="font-size:0.9rem;margin-right:4px;">{flag}</span>{cc} {name}</td>'
            + ''.join(tds) + change_td + '</tr>'
        )
    return '\n            '.join(rows)

# ============================================================
# 2) 비중 추이 라인 차트 (3개국, 5개 연도)
# ============================================================
def build_line_chart():
    W, H = 760, 260
    left, right, top, bot = 60, 720, 40, 220
    # Y 0~50% range
    def yc(v): return top + (bot-top) * (1 - v/50)
    xs_labels = YEARS
    xs = [left + i*((right-left)/4) for i in range(5)]

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;">']
    # Y grid
    for gv in [0, 10, 20, 30, 40, 50]:
        y = yc(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">{gv}%</text>')
    # Baseline
    svg.append(f'<line x1="{left}" y1="{yc(0)}" x2="{right}" y2="{yc(0)}" stroke="#cbd5e1"/>')
    # X labels
    for i, y in enumerate(xs_labels):
        svg.append(f'<text x="{xs[i]:.1f}" y="{bot+20}" text-anchor="middle" font-size="11" '
                   f'fill="{"#f59e0b" if y=="26.1Q" else "#64748b"}" '
                   f'font-weight="{"800" if y=="26.1Q" else "600"}">{y}</text>')

    # Lines for each country
    for cc, flag, name, color in COUNTRIES:
        vals = []
        for yr in YEARS:
            d = D[cc][yr]
            ch = d.get('중화권',0); tot = ch + d.get('기타',0)
            vals.append(ch/tot*100 if tot else 0)
        pts = ' '.join(f'{xs[i]:.1f},{yc(vals[i]):.1f}' for i in range(5))
        svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{pts}"/>')
        for i, v in enumerate(vals):
            svg.append(f'<circle cx="{xs[i]:.1f}" cy="{yc(v):.1f}" r="4" fill="{color}"/>')
            # 값 라벨
            svg.append(f'<text x="{xs[i]:.1f}" y="{yc(v)-8:.1f}" text-anchor="middle" font-size="10" fill="{color}" font-weight="700">{v:.1f}%</text>')

    # Legend
    legend_x = left
    for i, (cc, flag, name, color) in enumerate(COUNTRIES):
        svg.append(f'<rect x="{legend_x + i*150}" y="15" width="14" height="3" fill="{color}"/>')
        svg.append(f'<text x="{legend_x + i*150 + 20}" y="21" font-size="11" fill="{color}" font-weight="700">{cc} {name}</text>')

    svg.append('</svg>')
    return ''.join(svg)

# ============================================================
# 3) 절대값 바 차트 (중화권 매출 성장)
# ============================================================
def build_bar_chart():
    W, H = 760, 240
    left, right, top, bot = 60, 720, 40, 200
    # Find max across all countries/years
    max_v = max(D[cc][yr].get('중화권',0) for cc in ['KR','JP','US'] for yr in YEARS)
    # Round up for scale
    y_max = int((max_v // 1000 + 1) * 1000)
    def yc(v): return top + (bot-top) * (1 - v/y_max)

    svg = [f'<svg viewBox="0 0 {W} {H}" style="width:100%;max-width:1000px;height:auto;display:block;margin:8px 0;">']
    # Y grid
    for gv in [0, y_max//4, y_max//2, y_max*3//4, y_max]:
        y = yc(gv)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>')
        svg.append(f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">{gv:,}</text>')
    svg.append(f'<line x1="{left}" y1="{yc(0)}" x2="{right}" y2="{yc(0)}" stroke="#cbd5e1"/>')

    # Bars: 5 years × 3 countries grouped
    year_group_w = (right-left)/5
    bar_w = 22
    for i, yr in enumerate(YEARS):
        cx = left + i*year_group_w + year_group_w/2
        for j, (cc, flag, name, color) in enumerate(COUNTRIES):
            v = D[cc][yr].get('중화권', 0)
            x = cx - (len(COUNTRIES)*bar_w + 2*(len(COUNTRIES)-1))/2 + j*(bar_w+4)
            y = yc(v)
            h = yc(0) - y
            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="{color}" rx="2"/>')
            svg.append(f'<text x="{x+bar_w/2:.1f}" y="{y-4:.1f}" text-anchor="middle" font-size="8.5" fill="{color}" font-weight="700">{v:,.0f}</text>')
        # Year label
        svg.append(f'<text x="{cx:.1f}" y="{bot+22}" text-anchor="middle" font-size="11" '
                   f'fill="{"#f59e0b" if yr=="26.1Q" else "#64748b"}" '
                   f'font-weight="{"800" if yr=="26.1Q" else "600"}">{yr}</text>')

    # Legend
    legend_x = left
    for i, (cc, flag, name, color) in enumerate(COUNTRIES):
        svg.append(f'<rect x="{legend_x + i*150}" y="15" width="14" height="10" fill="{color}" rx="1"/>')
        svg.append(f'<text x="{legend_x + i*150 + 20}" y="24" font-size="11" fill="{color}" font-weight="700">{cc} {name}</text>')

    svg.append('</svg>')
    return ''.join(svg)

# ============================================================
# 신규 섹션 HTML
# ============================================================
def build_section():
    # 25년 전후 요약
    kr_b, kr_a = period_avg('KR', '중화권')
    jp_b, jp_a = period_avg('JP', '중화권')
    us_b, us_a = period_avg('US', '중화권')
    kr_all_b = sum((D['KR'][y].get('중화권',0)+D['KR'][y].get('기타',0)) * YR_M[y] for y in ['2022','2023','2024'])/36
    kr_all_a = sum((D['KR'][y].get('중화권',0)+D['KR'][y].get('기타',0)) * YR_M[y] for y in ['2025','26.1Q'])/15
    jp_all_b = sum((D['JP'][y].get('중화권',0)+D['JP'][y].get('기타',0)) * YR_M[y] for y in ['2022','2023','2024'])/36
    jp_all_a = sum((D['JP'][y].get('중화권',0)+D['JP'][y].get('기타',0)) * YR_M[y] for y in ['2025','26.1Q'])/15
    us_all_b = sum((D['US'][y].get('중화권',0)+D['US'][y].get('기타',0)) * YR_M[y] for y in ['2022','2023','2024'])/36
    us_all_a = sum((D['US'][y].get('중화권',0)+D['US'][y].get('기타',0)) * YR_M[y] for y in ['2025','26.1Q'])/15
    kr_sh_d = (kr_a/kr_all_a - kr_b/kr_all_b)*100
    jp_sh_d = (jp_a/jp_all_a - jp_b/jp_all_b)*100
    us_sh_d = (us_a/us_all_a - us_b/us_all_b)*100

    return f'''<div class="step">
    <div class="step-head">
      <div class="step-num" style="background:#d97706;">🇨🇳</div>
      <div class="step-info">
        <div class="step-q">3국 중화권 퍼블리셔 매출 흐름 — 절대값 × 비중 추이</div>
        <div class="step-a">KR <span style="color:#3b82f6;font-weight:700;">{kr_b/kr_all_b*100:.1f}% → {kr_a/kr_all_a*100:.1f}% ({kr_sh_d:+.1f}%p)</span> · JP <span style="color:#ef4444;font-weight:700;">{jp_b/jp_all_b*100:.1f}% → {jp_a/jp_all_a*100:.1f}% ({jp_sh_d:+.1f}%p)</span> · US <span style="color:#a855f7;font-weight:700;">{us_b/us_all_b*100:.1f}% → {us_a/us_all_a*100:.1f}% ({us_sh_d:+.1f}%p)</span> — 3국 모두 중화권 침투 가속</div>
      </div>
    </div>
    <div class="step-body">

      <!-- 1) 상세 테이블 -->
      <h4 style="font-size:0.85rem;font-weight:700;color:#0f172a;margin:8px 0 6px;padding:6px 10px;background:#fef3c7;border-left:3px solid #d97706;border-radius:3px;">📊 국가×연도별 중화권 퍼블리셔 매출 (각 셀: 비중% / 중화권 매출 / 전체 매출)</h4>
      <table style="width:100%;border-collapse:collapse;font-size:0.72rem;margin-top:6px;">
        <thead>
          <tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0;">
            <th style="padding:6px 10px;text-align:left;font-weight:700;color:#475569;">국가</th>
            <th class="num" style="padding:6px 8px;font-weight:700;color:#475569;">&apos;22</th>
            <th class="num" style="padding:6px 8px;font-weight:700;color:#475569;">&apos;23</th>
            <th class="num" style="padding:6px 8px;font-weight:700;color:#475569;">&apos;24</th>
            <th class="num" style="padding:6px 8px;font-weight:700;color:#475569;">&apos;25</th>
            <th class="num col26" style="padding:6px 8px;font-weight:700;background:#fbbf24;color:#78350f;">&apos;26.1Q</th>
            <th class="num" style="padding:6px 8px;font-weight:700;background:#f0f9ff;color:#0284c7;border-left:2px solid #e2e8f0;">25년 전후 변화</th>
          </tr>
        </thead>
        <tbody>
            {build_table()}
        </tbody>
      </table>

      <!-- 2) 비중 추이 라인 차트 -->
      <h4 style="font-size:0.85rem;font-weight:700;color:#0f172a;margin:18px 0 6px;padding:6px 10px;background:#f1f5f9;border-left:3px solid #64748b;border-radius:3px;">📈 중화권 매출 비중 추이 (%)</h4>
      {build_line_chart()}

      <!-- 3) 절대값 바 차트 -->
      <h4 style="font-size:0.85rem;font-weight:700;color:#0f172a;margin:18px 0 6px;padding:6px 10px;background:#f1f5f9;border-left:3px solid #64748b;border-radius:3px;">📊 중화권 매출 절대값 추이 (억원, 월평균)</h4>
      {build_bar_chart()}

      <!-- 4) 인사이트 -->
      <div class="ins" style="margin-top:14px;"><strong>핵심:</strong> 3국 모두 중화권 비중 상승 추세. <strong style="color:#3b82f6;">KR은 가장 빠른 상승</strong> (전 27.4% → 후 37.2%, +9.8%p) — Survival 메가히트(Last War/Whiteout/Kingshot) 견인. <strong style="color:#a855f7;">US는 후기 가속</strong> — 22~24년 평균 15%대 유지하다 25년 22.3% → 26.1Q 26.8%로 급등, +{us_sh_d:.1f}%p 최대 상승. <strong style="color:#ef4444;">JP는 가장 안정적</strong> 점진 상승. <strong>중화권 단독 3국 합산 순증가 약 +3,003억/월 (+46%)</strong>로 전체 시장 +10% 성장의 단독 드라이버.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        &bull; 중화권 퍼블리셔: <code>publisher_country IN (China, Hong Kong, Taiwan, Macao)</code> + FUNFLY(싱가포르 등록이지만 강제 중화권 분류)<br>
        &bull; 매출 = <code>revenue_krw_100</code> (ST 100% 보정 + 연도별 환율)<br>
        &bull; 월평균 매출 = SUM(해당월 매출) / 해당 기간 월수 (전: 36개월, 후: 15개월)<br>
        &bull; 비중 = 중화권 매출 / 전체 TOP100 매출 × 100
      </div>
    </div>
  </div>'''

# ============================================================
# HTML 패치
# ============================================================
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
bk = MAIN + '.bak.before_china_section'
import os
if not os.path.exists(bk):
    with open(bk, 'w', encoding='utf-8') as f: f.write(html)
o = html.count('<div'); oc = html.count('</div>')

# 1) 기존 '3국 중화권 퍼블리셔 매출 비중 추이' 섹션 제거
OLD_CHINA_RE = re.compile(
    r'<div class="step">\s*\n?\s*<div class="step-head">\s*\n?\s*'
    r'<div class="step-num"[^>]*>[^<]*</div>\s*\n?\s*'
    r'<div class="step-info">\s*\n?\s*'
    r'<div class="step-q">3국 중화권 퍼블리셔 매출 비중 추이[^<]*</div>.*?'
    r'(?=<div class="step">)',
    re.DOTALL
)
m = OLD_CHINA_RE.search(html)
if not m: raise RuntimeError("중화권 기존 섹션 매칭 실패")
# 새 섹션으로 교체
new_section = build_section() + '\n'
html = html[:m.start()] + new_section + html[m.end():]

# 2) '매출 집중도 분석' 섹션 제거 — 깊이 카운팅으로 정확한 블록 경계 찾기
def find_step_block(text, start_idx):
    """start_idx: <div class="step"> 시작 인덱스. 반환: (start, end) - 매칭되는 </div>의 end+1"""
    i = start_idx
    depth = 0
    div_open_re = re.compile(r'<div\b')
    div_close_re = re.compile(r'</div>')
    while i < len(text):
        m_open = div_open_re.search(text, i)
        m_close = div_close_re.search(text, i)
        if not m_close: break
        if m_open and m_open.start() < m_close.start():
            depth += 1
            i = m_open.end()
        else:
            depth -= 1
            i = m_close.end()
            if depth == 0:
                return (start_idx, i)
    raise RuntimeError("step block end 못찾음")

# 집중도 분석 step-q 위치 찾아서 역방향으로 <div class="step"> 시작점 탐색
concen_qi = html.find('<div class="step-q">매출 집중도 분석')
if concen_qi == -1: raise RuntimeError("집중도 step-q 못찾음")
# 앞에서 가장 가까운 <div class="step"> 찾기
step_start = html.rfind('<div class="step">', 0, concen_qi)
if step_start == -1: raise RuntimeError("집중도 step 시작 못찾음")
s, e = find_step_block(html, step_start)
removed_block = html[s:e]
print(f"[집중도 섹션 제거] {e-s}자 · <div>={removed_block.count('<div')} </div>={removed_block.count('</div>')}")
# 뒤따르는 공백/개행도 함께 제거
while e < len(html) and html[e] in ' \n\t':
    e += 1
html = html[:s] + html[e:]

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)
n = html.count('<div'); nc = html.count('</div>')
print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
print("[DONE]")
