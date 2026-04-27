# -*- coding: utf-8 -*-
"""
신규 진입 탭(tab-newgame) Section 1~6 재구성
- OS 통합 (AOS/iOS 분리 제거)
- 25년 전(22~24) vs 후(25~26.1Q) 비교 축으로 교체
- Section 7(장르 비중)은 유지 (이미 전후 + OS 중립)
"""
import os, re, json

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
DATA_JSON = r"C:\Users\NHN\Documents\sensortower_api\scripts\newgame_data_v2.json"

with open(DATA_JSON, 'r', encoding='utf-8') as f: D = json.load(f)

# ============================================================
# 데이터 인덱싱
# ============================================================
# Section 1: (country, period) -> {total, surv, rate}
s1 = {(r['country'], r['period']): r for r in D['section1']}
# Section 2: (country, period, survived) -> {pct, n}
s2 = {(r['country'], r['period'], r['survived']): r for r in D['section2']}
# Section 3: (pub_grp, period) -> {total, surv, rate}
s3 = {(r['pub_grp'], r['period']): r for r in D['section3']}
# Section 4: (pub_grp, period, survived) -> {pct, n}
s4 = {(r['pub_grp'], r['period'], r['survived']): r for r in D['section4']}
s5 = D['section5']  # {country: {before:[], after:[]}}
s6 = D['section6']

COUNTRIES = [('KR','🇰🇷','한국','#3b82f6'), ('JP','🇯🇵','일본','#ef4444'), ('US','🇺🇸','미국','#a855f7')]
PUB_GRPS = [('KR','🇰🇷','KR','#3b82f6'),
            ('JP','🇯🇵','JP','#ef4444'),
            ('중화권','🇨🇳','중화권','#f59e0b'),
            ('북미','🇺🇸','북미','#8b5cf6'),
            ('기타','🌍','기타','#64748b')]

# ============================================================
# 헬퍼
# ============================================================
def color_diff(delta):
    if delta > 0: return '#059669'
    if delta < 0: return '#dc2626'
    return '#64748b'

def arrow(delta):
    if delta > 0.1: return '▲'
    if delta < -0.1: return '▼'
    return '—'

def card_header(color, flag, name_txt, rate_txt, rate_color):
    return (f'  <div class="ng-card-header">\n'
            f'    <span class="ng-flag">{flag}</span>\n'
            f'    <span class="ng-name">{name_txt}</span>\n'
            f'    <span class="ng-rate" style="color:{rate_color};">{rate_txt}</span>\n'
            f'  </div>\n')

# ============================================================
# Section 1: 국가별 3개월 생존율 (전/후)
# ============================================================
def build_s1():
    cards = []
    for cc, flag, name, color in COUNTRIES:
        before = s1.get((cc,'before'), {'total':0,'surv':0,'rate':0})
        after = s1.get((cc,'after'),  {'total':0,'surv':0,'rate':0})
        delta = after['rate'] - before['rate']
        card = (
            f'<div class="ng-card" style="border-top-color:{color};">\n'
            + card_header(color, flag, f'{cc} {name}', f'{after["rate"]:.1f}%', color)
            + f'  <div class="ng-card-stat">\n'
            f'    <div class="ng-stat-detail">전: 진입 <strong>{before["total"]}</strong>개 중 <strong>{before["surv"]}</strong>개 생존 · 후: <strong>{after["total"]}</strong>개 중 <strong>{after["surv"]}</strong>개 생존</div>\n'
            f'    <div class="ng-bar-row"><div class="ng-bar-label">전(22~24)</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{before["rate"]}%;background:#94a3b8;"></div></div><div class="ng-bar-val" style="color:#64748b;">{before["rate"]:.1f}%</div></div>\n'
            f'    <div class="ng-bar-row"><div class="ng-bar-label">후(25~26.1Q)</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{after["rate"]}%;background:{color};"></div></div><div class="ng-bar-val" style="color:{color};">{after["rate"]:.1f}%</div></div>\n'
            f'    <div class="ng-os-diff">전→후 변화: <strong style="color:{color_diff(delta)};">{arrow(delta)} {delta:+.1f}%p</strong></div>\n'
            f'  </div>\n'
            f'</div>'
        )
        cards.append(card)

    # 해석
    kr_d = s1[('KR','after')]['rate'] - s1[('KR','before')]['rate']
    jp_d = s1[('JP','after')]['rate'] - s1[('JP','before')]['rate']
    us_d = s1[('US','after')]['rate'] - s1[('US','before')]['rate']
    ins = (f'<div class="ng-ins"><strong>핵심:</strong> 25년 전후로 생존율 변화가 국가별 상이 — '
           f'<strong>KR {kr_d:+.1f}%p</strong> (유일하게 하락), <strong>JP {jp_d:+.1f}%p</strong>, '
           f'<strong>US {us_d:+.1f}%p</strong>. KR은 신작 공급 증가와 경쟁 심화로 생존 장벽 높아짐, '
           f'JP/US는 선별된 신규 진입의 품질 향상으로 생존율 개선.</div>')

    return (
        '<div class="ng-section">\n'
        '  <div class="ng-section-head">\n'
        '    <div class="ng-section-num" style="background:#0f172a;">1</div>\n'
        '    <div>\n'
        '      <h2>🌏 국가별 신규 진입 게임 3개월 생존율</h2>\n'
        '      <div class="ng-desc">진입월 + 3개월 후에도 TOP 100에 존재하는 비율 · 전(22~24 진입) vs 후(25~26.1Q 진입) · OS 통합</div>\n'
        '  </div>\n'
        '  </div>\n'
        '  <div class="ng-card-grid cols-3">' + ''.join(cards) + '</div>\n'
        '  ' + ins + '\n'
        '</div>'
    )

# ============================================================
# Section 2: 국가별 광고집행률 (전/후) — table by period
# ============================================================
def build_s2():
    cards = []
    for cc, flag, name, color in COUNTRIES:
        rows = []
        sums = []
        for period, label in [('before','전 (22~24)'), ('after','후 (25~26.1Q)')]:
            y = s2.get((cc, period, True),  {'pct':0,'n':0})
            n = s2.get((cc, period, False), {'pct':0,'n':0})
            diff = y['pct'] - n['pct']
            highlight = ' style="background:#fef3c7;"' if period == 'after' else ''
            rows.append(
                f'<tr{highlight}><td><strong>{label}</strong></td>'
                f'<td class="r" style="color:#059669;">{y["pct"]:.1f}% <small style="color:#cbd5e1;">(n={y["n"]})</small></td>'
                f'<td class="r" style="color:#dc2626;">{n["pct"]:.1f}% <small style="color:#cbd5e1;">(n={n["n"]})</small></td>'
                f'<td class="r" style="color:{color_diff(diff)};font-weight:700;">{diff:+.1f}%p</td></tr>'
            )
            sums.append(diff)
        hero_delta = sums[1]  # 후 기간 Δ
        card = (
            f'<div class="ng-card" style="border-top-color:{color};">\n'
            + card_header(color, flag, f'{cc} {name}', f'후 {hero_delta:+.1f}%p', color_diff(hero_delta))
            + f'  <div class="ng-card-stat">\n'
            f'    <table class="ng-paid-table">\n'
            f'      <thead><tr><th>기간</th><th class="r">생존 광고%</th><th class="r">미생존 광고%</th><th class="r">Δ</th></tr></thead>\n'
            f'      <tbody>{"".join(rows)}</tbody>\n'
            f'    </table>\n'
            f'  </div>\n'
            f'</div>'
        )
        cards.append(card)

    ins = ('<div class="ng-ins"><strong>핵심:</strong> 3국 모두 <strong>생존 게임이 미생존보다 광고 집행률 높음</strong> — '
           '광고 투자가 생존에 기여. 25년 후(25~26.1Q 진입) 기간에 그 격차가 더 벌어짐 '
           '(특히 US: 생존 66.7% vs 미생존 18.8%로 Δ +47.9%p). '
           '광고 Driven 진입이 실제 생존으로 이어지는 경향 강화.</div>')

    return (
        '<div class="ng-section">\n'
        '  <div class="ng-section-head">\n'
        '    <div class="ng-section-num" style="background:#0f172a;">2</div>\n'
        '    <div>\n'
        '      <h2>📣 국가별 생존 vs 미생존 게임의 광고집행률</h2>\n'
        '      <div class="ng-desc">진입 후 3개월간 평균 광고유입률 = paid_abs/(paid+organic+browser) · 전/후 비교 · OS 통합</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="ng-card-grid cols-3">' + ''.join(cards) + '</div>\n'
        '  ' + ins + '\n'
        '</div>'
    )

# ============================================================
# Section 3: 퍼블리셔 국적별 3개월 생존율 (전/후)
# ============================================================
def build_s3():
    cards = []
    for grp, flag, name, color in PUB_GRPS:
        before = s3.get((grp,'before'), {'total':0,'surv':0,'rate':0})
        after = s3.get((grp,'after'),  {'total':0,'surv':0,'rate':0})
        delta = after['rate'] - before['rate']
        card = (
            f'<div class="ng-card" style="border-top-color:{color};">\n'
            + card_header(color, flag, name, f'{after["rate"]:.1f}%', color)
            + f'  <div class="ng-card-stat">\n'
            f'    <div class="ng-stat-detail">전: <strong>{before["surv"]}/{before["total"]}</strong> · 후: <strong>{after["surv"]}/{after["total"]}</strong></div>\n'
            f'    <div class="ng-bar-row"><div class="ng-bar-label">전</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{before["rate"]}%;background:#94a3b8;"></div></div><div class="ng-bar-val" style="color:#64748b;">{before["rate"]:.1f}%</div></div>\n'
            f'    <div class="ng-bar-row"><div class="ng-bar-label">후</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{after["rate"]}%;background:{color};"></div></div><div class="ng-bar-val" style="color:{color};">{after["rate"]:.1f}%</div></div>\n'
            f'    <div class="ng-os-diff">Δ: <strong style="color:{color_diff(delta)};">{arrow(delta)} {delta:+.1f}%p</strong></div>\n'
            f'  </div>\n'
            f'</div>'
        )
        cards.append(card)

    ins = ('<div class="ng-ins"><strong>핵심:</strong> '
           '<strong style="color:#dc2626;">중화권 54.1% → 38.7% (-15.4%p) 급락</strong> — 25년 이후 진입한 중화권 신작의 경쟁력 약화. '
           '<strong style="color:#059669;">JP 32.7% → 57.1% (+24.4%p)</strong> — 엄선된 일본 신작이 강세. '
           'KR은 44% 수준 유지, 북미는 표본 작음(6건).</div>')

    return (
        '<div class="ng-section">\n'
        '  <div class="ng-section-head">\n'
        '    <div class="ng-section-num" style="background:#0f172a;">3</div>\n'
        '    <div>\n'
        '      <h2>🏢 퍼블리셔 국적별 신규 진입 게임 3개월 생존율</h2>\n'
        '      <div class="ng-desc">퍼블리셔 국적 5개 그룹 · 전/후 비교 · OS 통합 (NEXON→KR, FUNFLY→중화권 강제 분류)</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="ng-card-grid cols-3">' + ''.join(cards) + '</div>\n'
        '  ' + ins + '\n'
        '</div>'
    )

# ============================================================
# Section 4: 퍼블리셔별 광고집행률 (전/후)
# ============================================================
def build_s4():
    cards = []
    for grp, flag, name, color in PUB_GRPS:
        rows = []
        sums = []
        for period, label in [('before','전 (22~24)'), ('after','후 (25~26.1Q)')]:
            y = s4.get((grp, period, True),  {'pct':0,'n':0})
            n = s4.get((grp, period, False), {'pct':0,'n':0})
            diff = y['pct'] - n['pct']
            highlight = ' style="background:#fef3c7;"' if period == 'after' else ''
            rows.append(
                f'<tr{highlight}><td><strong>{label}</strong></td>'
                f'<td class="r" style="color:#059669;">{y["pct"]:.1f}% <small style="color:#cbd5e1;">(n={y["n"]})</small></td>'
                f'<td class="r" style="color:#dc2626;">{n["pct"]:.1f}% <small style="color:#cbd5e1;">(n={n["n"]})</small></td>'
                f'<td class="r" style="color:{color_diff(diff)};font-weight:700;">{diff:+.1f}%p</td></tr>'
            )
            sums.append(diff)
        hero_delta = sums[1]
        card = (
            f'<div class="ng-card" style="border-top-color:{color};">\n'
            + card_header(color, flag, name, f'후 {hero_delta:+.1f}%p', color_diff(hero_delta))
            + f'  <div class="ng-card-stat">\n'
            f'    <table class="ng-paid-table">\n'
            f'      <thead><tr><th>기간</th><th class="r">생존</th><th class="r">미생존</th><th class="r">Δ</th></tr></thead>\n'
            f'      <tbody>{"".join(rows)}</tbody>\n'
            f'    </table>\n'
            f'  </div>\n'
            f'</div>'
        )
        cards.append(card)

    ins = ('<div class="ng-ins"><strong>핵심:</strong> '
           '<strong>중화권·기타 그룹은 광고 Driven 생존이 뚜렷</strong> — '
           '중화권 후 생존 62.5% vs 미생존 43.8% (Δ +18.7%p), 기타 후 71.2% vs 48.3% (Δ +22.9%p). '
           'KR은 생존/미생존 간 광고집행률 차이 적음 (자연 유입 비중 높음). '
           '북미는 표본 적어 해석 주의.</div>')

    return (
        '<div class="ng-section">\n'
        '  <div class="ng-section-head">\n'
        '    <div class="ng-section-num" style="background:#0f172a;">4</div>\n'
        '    <div>\n'
        '      <h2>📢 퍼블리셔별 생존 vs 미생존 게임의 광고집행률</h2>\n'
        '      <div class="ng-desc">전/후 비교 · OS 통합</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="ng-card-grid cols-3">' + ''.join(cards) + '</div>\n'
        '  ' + ins + '\n'
        '</div>'
    )

# ============================================================
# Section 5 / 6: M+1 ~ M+12 차트 (전/후, OS 통합, 단일 SVG)
# ============================================================
def build_retention_svg(before_vals, after_vals, color_after):
    W, H = 620, 240
    left, right, top, bot = 50, 600, 30, 200
    def yc(v):
        # 0~80% 스케일 (원본 차트와 동일)
        return top + (bot - top) * (1 - v/80)
    # grid
    grids = ""
    for g in [0, 20, 40, 60, 80]:
        y = yc(g)
        grids += (f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#f1f5f9" stroke-dasharray="2,2"/>'
                  f'<text x="{left-5}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#94a3b8">{g}%</text>')
    # 전 (점선 회색)
    xs = [left + i*((right-left)/11) for i in range(12)]
    before_pts = " ".join(f"{xs[i]:.1f},{yc(before_vals[i]):.1f}" for i in range(12))
    after_pts = " ".join(f"{xs[i]:.1f},{yc(after_vals[i]):.1f}" for i in range(12))
    before_circles = "".join(
        f'<circle cx="{xs[i]:.1f}" cy="{yc(before_vals[i]):.1f}" r="3.5" fill="white" stroke="#94a3b8" stroke-width="1.5"/>'
        for i in range(12)
    )
    after_circles = "".join(
        f'<circle cx="{xs[i]:.1f}" cy="{yc(after_vals[i]):.1f}" r="3.5" fill="{color_after}"/>'
        for i in range(12)
    )
    x_labels = "".join(
        f'<text x="{xs[i]:.1f}" y="216" text-anchor="middle" font-size="10" fill="#64748b">M+{i+1}</text>'
        for i in range(12)
    )
    # M+12 Δ
    delta_12 = after_vals[11] - before_vals[11]
    delta_color = color_diff(delta_12)
    delta_txt = f'<text x="{right}" y="14" text-anchor="end" font-size="10" fill="{delta_color}" font-weight="700">M+12 Δ {delta_12:+.1f}%p</text>'
    legend = (
        f'<rect x="50" y="8" width="14" height="3" fill="#94a3b8"/>'
        f'<text x="68" y="14" font-size="10" fill="#475569" font-weight="600">전 (22~24)</text>'
        f'<rect x="140" y="8" width="14" height="3" fill="{color_after}"/>'
        f'<text x="158" y="14" font-size="10" fill="{color_after}" font-weight="700">후 (25~26.1Q)</text>'
    )
    return (
        f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;">'
        f'{grids}'
        f'<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5,3" points="{before_pts}"/>'
        f'{before_circles}'
        f'<polyline fill="none" stroke="{color_after}" stroke-width="2.5" points="{after_pts}"/>'
        f'{after_circles}'
        f'{x_labels}{legend}{delta_txt}'
        f'</svg>'
    )

def build_s5():
    cards = []
    for cc, flag, name, color in COUNTRIES:
        before = s5[cc]['before']
        after = s5[cc]['after']
        svg = build_retention_svg(before, after, color)
        card = (
            f'<div class="ng-card" style="border-top-color:{color};">\n'
            f'  <div class="ng-card-header">\n'
            f'    <span class="ng-flag">{flag}</span>\n'
            f'    <span class="ng-name">{cc} {name}</span>\n'
            f'  </div>\n'
            f'  <div class="ng-card-stat" style="padding:8px 10px;">{svg}</div>\n'
            f'</div>'
        )
        cards.append(card)
    return (
        '<div class="ng-section">\n'
        '  <div class="ng-section-head">\n'
        '    <div class="ng-section-num" style="background:#0f172a;">5</div>\n'
        '    <div>\n'
        '      <h2>📉 국가별 차트 잔존율 25년 전후 비교 (M+1 ~ M+12)</h2>\n'
        '      <div class="ng-desc">점선(회색) = 전(22~24 진입) · 실선(컬러) = 후(25~26.1Q 진입) · OS 통합</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="ng-card-grid cols-3">' + ''.join(cards) + '</div>\n'
        '</div>'
    )

def build_s6():
    cards = []
    for grp, flag, name, color in PUB_GRPS:
        if grp not in s6: continue
        before = s6[grp]['before']
        after = s6[grp]['after']
        svg = build_retention_svg(before, after, color)
        card = (
            f'<div class="ng-card" style="border-top-color:{color};">\n'
            f'  <div class="ng-card-header">\n'
            f'    <span class="ng-flag">{flag}</span>\n'
            f'    <span class="ng-name">{name}</span>\n'
            f'  </div>\n'
            f'  <div class="ng-card-stat" style="padding:8px 10px;">{svg}</div>\n'
            f'</div>'
        )
        cards.append(card)
    return (
        '<div class="ng-section">\n'
        '  <div class="ng-section-head">\n'
        '    <div class="ng-section-num" style="background:#0f172a;">6</div>\n'
        '    <div>\n'
        '      <h2>📉 퍼블리셔 국적별 차트 잔존율 25년 전후 비교 (M+1 ~ M+12)</h2>\n'
        '      <div class="ng-desc">점선(회색) = 전(22~24 진입) · 실선(컬러) = 후(25~26.1Q 진입) · OS 통합</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="ng-card-grid cols-4">' + ''.join(cards) + '</div>\n'
        '</div>'
    )

# ============================================================
# HTML 패치 — 기존 Section 1~6 전체 제거 후 신규 삽입
# ============================================================
with open(MAIN, 'r', encoding='utf-8') as f: html = f.read()
bk = MAIN + '.bak.before_newgame_v2'
if not os.path.exists(bk):
    with open(bk, 'w', encoding='utf-8') as f: f.write(html)
o_open = html.count('<div'); o_close = html.count('</div>')
print(f"[BEFORE] <div>={o_open}, </div>={o_close}")

# Section 1~6 경계 찾기
# Start: 첫 번째 <div class="ng-section"> (ng-definition 바로 다음)
# End: Section 7(장르 비중) 직전 또는 현 Section 6 끝
# 장르 비중 section은 "🎨 장르" 같은 별도 마커 필요. Section 7 헤더부터 시작하는 <div class="ng-section">을 찾자.

# Section 7 앵커 — "장르 비중 변화" 또는 "장르 비중"
s7_anchor_re = re.compile(r'<div class="ng-section">\s*\n?\s*<div class="ng-section-head">\s*\n?\s*<div class="ng-section-num"[^>]*>7</div>', re.DOTALL)
s7_m = s7_anchor_re.search(html)
if not s7_m:
    # Section 7이 없을 수도 — 그 경우 footer 앞까지
    end_anchor = re.search(r'<div class="ng-footer">', html)
    end_pos = end_anchor.start() if end_anchor else None
else:
    end_pos = s7_m.start()

# Section 1 시작 — ng-definition 뒤 첫 ng-section
s1_start_re = re.compile(r'<div class="ng-definition">.*?</div>\s*\n\s*(<div class="ng-section">)', re.DOTALL)
s1_m = s1_start_re.search(html)
if not s1_m:
    raise RuntimeError("Section 1 시작 앵커 못찾음")
start_pos = s1_m.start(1)

if end_pos is None:
    raise RuntimeError("Section 1~6 끝 위치 못찾음")

print(f"  Section 1~6 범위: {start_pos} ~ {end_pos}")

# 신규 섹션 HTML
new_sections = (
    build_s1() + '\n'
    + build_s2() + '\n'
    + build_s3() + '\n'
    + build_s4() + '\n'
    + build_s5() + '\n'
    + build_s6() + '\n'
)

html = html[:start_pos] + new_sections + html[end_pos:]

# ng-definition 문구 업데이트
OLD_DEF = '<strong>📌 신규 진입 정의:</strong> 각 연도별 TOP 100에 2~12월 중 처음 진입한 게임 (1월은 전년도 잔류 포함되어 제외) · <strong>국가·OS별로 별도 집계</strong>'
NEW_DEF = '<strong>📌 신규 진입 정의:</strong> TOP 100에 2~12월 중 처음 진입한 게임 (1월 제외·전년 잔류 배제) · <strong>OS 통합</strong> · 전(22~24 진입) vs 후(25~26.1Q 진입) 비교'
if OLD_DEF in html:
    html = html.replace(OLD_DEF, NEW_DEF, 1)

# 하단 주석(ng-footer의 "앱 존재월") 업데이트 — 이 탭은 tab-growth에 있었음, 그대로 둠.

with open(MAIN, 'w', encoding='utf-8') as f: f.write(html)

n_open = html.count('<div'); n_close = html.count('</div>')
print(f"[AFTER]  <div>={n_open}, </div>={n_close}")
ok = '✅' if n_open == n_close else '❌'
print(f"  {ok}  delta={n_open-n_close}")
print("[DONE]", MAIN)
