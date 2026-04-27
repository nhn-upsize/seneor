#!/usr/bin/env python3
"""신규 진입 탭 콘텐츠 교체"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'

# 데이터
COUNTRY_SURVIVAL = {
    'KR': {'all': (843, 342, 40.6), 'android': (435, 177, 40.7), 'ios': (408, 165, 40.4)},
    'JP': {'all': (559, 201, 36.0), 'android': (283, 100, 35.3), 'ios': (276, 101, 36.6)},
    'US': {'all': (276, 162, 58.7), 'android': (134, 78, 58.2), 'ios': (142, 84, 59.2)},
}
COUNTRY_PAID = {
    'KR': {'all': {'survived': (288, 43.6), 'died': (394, 36.1)}, 'android': {'survived': (145, 39.7), 'died': (204, 34.5)}, 'ios': {'survived': (143, 47.5), 'died': (190, 37.8)}},
    'JP': {'all': {'survived': (193, 34.9), 'died': (337, 22.5)}, 'android': {'survived': (96, 32.4), 'died': (172, 21.5)}, 'ios': {'survived': (97, 37.3), 'died': (165, 23.6)}},
    'US': {'all': {'survived': (160, 49.2), 'died': (114, 36.5)}, 'android': {'survived': (77, 46.4), 'died': (56, 35.6)}, 'ios': {'survived': (83, 51.7), 'died': (58, 37.5)}},
}
PUB_SURVIVAL = {
    'KR':     {'all': (389, 163, 41.9), 'android': (199, 82, 41.2), 'ios': (190, 81, 42.6)},
    'JP':     {'all': (328, 102, 31.1), 'android': (165, 51, 30.9), 'ios': (163, 51, 31.3)},
    '중화권': {'all': (628, 278, 44.3), 'android': (330, 144, 43.6), 'ios': (298, 134, 45.0)},
    '북미':   {'all': (109, 54, 49.5), 'android': (54, 26, 48.1), 'ios': (55, 28, 50.9)},
    '기타':   {'all': (224, 108, 48.2), 'android': (104, 52, 50.0), 'ios': (120, 56, 46.7)},
}
PUB_PAID = {
    'KR':     {'all': {'survived': (140, 32.3), 'died': (195, 29.9)}, 'android': {'survived': (70, 29.8), 'died': (100, 29.7)}, 'ios': {'survived': (70, 34.7), 'died': (95, 30.2)}},
    'JP':     {'all': {'survived': (94, 21.2), 'died': (214, 18.1)}, 'android': {'survived': (47, 19.2), 'died': (108, 16.9)}, 'ios': {'survived': (47, 23.1), 'died': (106, 19.2)}},
    '중화권': {'all': {'survived': (246, 52.7), 'died': (281, 37.3)}, 'android': {'survived': (124, 47.3), 'died': (151, 34.9)}, 'ios': {'survived': (122, 58.1), 'died': (130, 40.1)}},
    '북미':   {'all': {'survived': (53, 26.7), 'died': (55, 26.8)}, 'android': {'survived': (25, 24.1), 'died': (28, 25.5)}, 'ios': {'survived': (28, 29.1), 'died': (27, 28.1)}},
    '기타':   {'all': {'survived': (108, 58.0), 'died': (100, 43.3)}, 'android': {'survived': (52, 57.3), 'died': (45, 43.6)}, 'ios': {'survived': (56, 58.6), 'died': (55, 43.1)}},
}
COUNTRY_RETENTION = {
    'KR': {'android': [63.7,48.0,40.7,33.8,26.9,25.7,20.5,18.6,16.3,14.5,14.7,16.1], 'ios': [64.2,48.8,40.4,32.8,26.2,25.2,20.8,19.4,17.2,15.4,15.4,17.4]},
    'JP': {'android': [54.1,39.9,35.3,32.9,30.7,29.0,22.6,21.9,21.6,20.8,19.8,24.4], 'ios': [54.0,40.2,36.6,33.7,32.6,30.8,23.6,22.8,23.2,21.7,20.7,25.7]},
    'US': {'android': [68.7,57.5,58.2,53.7,51.5,44.0,40.3,39.6,38.1,35.8,31.3,32.8], 'ios': [72.5,59.9,59.2,56.3,51.4,44.4,40.1,38.7,36.6,35.2,28.9,30.3]},
}
PUB_RETENTION = {
    'KR':     {'android':[60.3,50.3,41.2,34.7,24.6,25.1,21.6,20.1,17.1,15.6,15.1,18.6], 'ios':[61.6,51.1,42.6,34.2,25.3,25.3,21.6,22.1,18.4,17.4,16.8,20.5]},
    'JP':     {'android':[43.6,32.7,30.9,27.9,29.1,27.9,20.6,17.6,17.6,18.8,18.2,27.3], 'ios':[42.3,31.9,31.3,27.0,30.7,30.1,20.9,17.8,19.0,19.0,18.4,28.2]},
    '중화권': {'android':[67.6,48.2,43.6,35.5,31.2,28.8,21.8,21.5,19.7,18.2,17.9,16.1], 'ios':[69.5,50.3,45.0,37.2,32.2,29.9,23.8,22.8,21.1,19.8,19.1,17.8]},
    '북미':   {'android':[68.5,51.9,48.1,51.9,51.9,42.6,35.2,35.2,38.9,35.2,27.8,38.9], 'ios':[70.9,56.4,50.9,54.5,52.7,43.6,36.4,34.5,38.2,34.5,27.3,38.2]},
    '기타':   {'android':[67.3,55.8,50.0,50.0,43.3,37.5,37.5,35.6,32.7,27.9,26.9,26.0], 'ios':[68.3,54.2,46.7,47.5,39.2,34.2,34.2,32.5,30.0,25.8,22.5,21.7]},
}

COUNTRY_COLOR = {'KR': '#3b82f6', 'JP': '#ef4444', 'US': '#a855f7'}
COUNTRY_FLAG = {'KR': '🇰🇷', 'JP': '🇯🇵', 'US': '🇺🇸'}
COUNTRY_NAME = {'KR': 'KR 한국', 'JP': 'JP 일본', 'US': 'US 미국'}
PUB_COLOR = {'KR': '#3b82f6', 'JP': '#ef4444', '중화권': '#f59e0b', '북미': '#8b5cf6', '기타': '#64748b'}
PUB_FLAG = {'KR': '🇰🇷', 'JP': '🇯🇵', '중화권': '🇨🇳', '북미': '🇺🇸', '기타': '🌐'}
PUB_NAME = {'KR': 'KR 한국', 'JP': 'JP 일본', '중화권': '중화권', '북미': '북미', '기타': '기타 (글로벌)'}


def gen_survival_card(color, flag, name, data):
    all_t, all_s, all_p = data['all']
    aos_p = data['android'][2]
    ios_p = data['ios'][2]
    diff = round(ios_p - aos_p, 1)
    diff_str = f'+{diff}%p' if diff > 0 else (f'{diff}%p' if diff < 0 else '동일')
    diff_color = '#dc2626' if diff > 0 else ('#059669' if diff < 0 else '#94a3b8')

    return f'''<div class="ng-card" style="border-top-color:{color};">
  <div class="ng-card-header">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
    <span class="ng-rate" style="color:{color};">{all_p}%</span>
  </div>
  <div class="ng-card-stat">
    <div class="ng-stat-detail">전체 <strong>{all_s}/{all_t}</strong> 생존</div>
    <div class="ng-bar-row"><div class="ng-bar-label">전체</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{all_p}%;background:{color};"></div></div><div class="ng-bar-val" style="color:{color};">{all_p}%</div></div>
    <div class="ng-bar-row"><div class="ng-bar-label">AOS</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{aos_p}%;background:{color};opacity:0.6;"></div></div><div class="ng-bar-val" style="color:{color};opacity:0.8;">{aos_p}%</div></div>
    <div class="ng-bar-row"><div class="ng-bar-label">iOS</div><div class="ng-bar-track"><div class="ng-bar-fill" style="width:{ios_p}%;background:{color};opacity:0.4;"></div></div><div class="ng-bar-val" style="color:{color};opacity:0.6;">{ios_p}%</div></div>
    <div class="ng-os-diff">iOS - AOS: <strong style="color:{diff_color};">{diff_str}</strong></div>
  </div>
</div>'''


def gen_paid_card(color, flag, name, data):
    all_s = data['all']['survived']
    all_d = data['all']['died']
    aos_s = data['android']['survived']
    aos_d = data['android']['died']
    ios_s = data['ios']['survived']
    ios_d = data['ios']['died']

    diff_all = round(all_s[1] - all_d[1], 1)
    diff_color = '#059669' if diff_all > 0 else '#dc2626' if diff_all < 0 else '#94a3b8'
    diff_all_str = f'+{diff_all}%p' if diff_all >= 0 else f'{diff_all}%p'

    return f'''<div class="ng-card" style="border-top-color:{color};">
  <div class="ng-card-header">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
    <span class="ng-rate" style="color:{diff_color};">{diff_all_str}</span>
  </div>
  <div class="ng-card-stat">
    <table class="ng-paid-table">
      <thead><tr><th>OS</th><th class="r">생존</th><th class="r">미생존</th><th class="r">차이</th></tr></thead>
      <tbody>
        <tr style="background:#fef3c7;"><td><strong>전체</strong></td><td class="r" style="color:#059669;"><strong>{all_s[1]}%</strong></td><td class="r" style="color:#dc2626;">{all_d[1]}%</td><td class="r" style="color:{diff_color};font-weight:700;">+{round(all_s[1]-all_d[1],1)}%p</td></tr>
        <tr><td>AOS</td><td class="r" style="color:#059669;">{aos_s[1]}%</td><td class="r" style="color:#dc2626;">{aos_d[1]}%</td><td class="r" style="color:{diff_color};">+{round(aos_s[1]-aos_d[1],1)}%p</td></tr>
        <tr><td>iOS</td><td class="r" style="color:#059669;">{ios_s[1]}%</td><td class="r" style="color:#dc2626;">{ios_d[1]}%</td><td class="r" style="color:{diff_color};">+{round(ios_s[1]-ios_d[1],1)}%p</td></tr>
      </tbody>
    </table>
  </div>
</div>'''


def gen_retention_chart(color, flag, name, data):
    aos = data['android']
    ios = data['ios']
    chart_w, chart_h = 600, 220
    pad_l, pad_r, pad_t, pad_b = 50, 20, 25, 35
    plot_w = chart_w - pad_l - pad_r
    plot_h = chart_h - pad_t - pad_b
    n = 12
    x_step = plot_w / (n - 1)
    y_max = 80

    y_grid = ''.join(f'<line x1="{pad_l}" y1="{pad_t+plot_h-(v/y_max)*plot_h}" x2="{chart_w-pad_r}" y2="{pad_t+plot_h-(v/y_max)*plot_h}" stroke="#f1f5f9" stroke-dasharray="2,2"/><text x="{pad_l-5}" y="{pad_t+plot_h-(v/y_max)*plot_h+3}" text-anchor="end" font-size="9" fill="#94a3b8">{v}%</text>' for v in [0,20,40,60,80])
    x_labels = ''.join(f'<text x="{pad_l+i*x_step}" y="{chart_h-pad_b+15}" text-anchor="middle" font-size="9" fill="#64748b">M+{i+1}</text>' for i in range(n))
    aos_pts = ' '.join(f'{pad_l+i*x_step:.1f},{pad_t+plot_h-(v/y_max)*plot_h:.1f}' for i, v in enumerate(aos))
    aos_circles = ''.join(f'<circle cx="{pad_l+i*x_step:.1f}" cy="{pad_t+plot_h-(v/y_max)*plot_h:.1f}" r="3" fill="{color}"/>' for i, v in enumerate(aos))
    ios_pts = ' '.join(f'{pad_l+i*x_step:.1f},{pad_t+plot_h-(v/y_max)*plot_h:.1f}' for i, v in enumerate(ios))
    ios_circles = ''.join(f'<circle cx="{pad_l+i*x_step:.1f}" cy="{pad_t+plot_h-(v/y_max)*plot_h:.1f}" r="3" fill="white" stroke="{color}" stroke-width="2"/>' for i, v in enumerate(ios))

    return f'''<div class="ng-card" style="border-top-color:{color};">
  <div class="ng-card-header">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
    <span style="font-size:0.68rem;color:#94a3b8;margin-left:auto;">M+1 → M+12</span>
  </div>
  <div class="ng-card-stat">
    <svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;height:auto;">
      {y_grid}
      <polyline fill="none" stroke="{color}" stroke-width="2" points="{aos_pts}"/>
      {aos_circles}
      <polyline fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="4,3" points="{ios_pts}"/>
      {ios_circles}
      {x_labels}
      <rect x="{chart_w-110}" y="{pad_t-18}" width="12" height="2" fill="{color}"/><text x="{chart_w-94}" y="{pad_t-14}" font-size="9" fill="#475569">AOS</text>
      <line x1="{chart_w-60}" y1="{pad_t-17}" x2="{chart_w-48}" y2="{pad_t-17}" stroke="{color}" stroke-width="2" stroke-dasharray="3,2"/><text x="{chart_w-44}" y="{pad_t-14}" font-size="9" fill="#475569">iOS</text>
    </svg>
  </div>
</div>'''


def build_section(num, icon, title, desc, body_html, ins_text):
    return f'''
<div class="ng-section">
  <div class="ng-section-head">
    <div class="ng-section-num" style="background:#0f172a;">{num}</div>
    <div>
      <h2>{icon} {title}</h2>
      <div class="ng-desc">{desc}</div>
    </div>
  </div>
  {body_html}
  <div class="ng-ins">{ins_text}</div>
</div>'''


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Generate all sections
    # 1. 국가별 생존율
    cards1 = ''.join([gen_survival_card(COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_SURVIVAL[c]) for c in ['KR','JP','US']])
    sec1 = build_section('1', '🌏', '국가별 신규 진입 게임 3개월 생존율', '진입월 + 3개월 후에도 TOP 100에 존재하는 비율 (전체 + AOS/iOS 비교)',
        f'<div class="ng-card-grid cols-3">{cards1}</div>',
        '<strong>핵심:</strong> 🇺🇸 US 58.7%로 3국 중 가장 높은 생존율 — 시장 크기로 안정성 확보. KR(40.6%) · JP(36.0%) 대비 1.5배. <strong>OS 차이는 미미</strong> (대부분 ±1%p 이내).')

    # 2. 국가별 광고율
    cards2 = ''.join([gen_paid_card(COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_PAID[c]) for c in ['KR','JP','US']])
    sec2 = build_section('2', '📣', '국가별 생존 vs 미생존 게임의 광고집행률', '진입 후 3개월간 평균 광고유입률 = paid_abs / (paid + organic + browser)',
        f'<div class="ng-card-grid cols-3">{cards2}</div>',
        '<strong>핵심:</strong> 3국 모두 <strong>생존 게임이 미생존보다 광고 집행률이 높음</strong> (평균 +11.6%p). <strong>광고 투자가 생존으로 이어진다</strong>는 강한 상관관계. iOS가 AOS보다 광고 집행률 높은 경향 (특히 JP iOS +13.7%p).')

    # 3. 퍼블리셔별 생존율
    cards3 = ''.join([gen_survival_card(PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_SURVIVAL[p]) for p in ['KR','JP','중화권','북미','기타']])
    sec3 = build_section('3', '🏢', '퍼블리셔 국적별 신규 진입 게임 3개월 생존율', 'NEXON→KR, FUNFLY→중화권 강제 분류 · 5개 퍼블 그룹별 비교',
        f'<div class="ng-card-grid cols-5">{cards3}</div>',
        '<strong>핵심:</strong> <strong>북미/기타(글로벌) 퍼블리셔가 생존율 최고</strong> (48~50%). <strong>JP 퍼블리셔가 생존율 최저</strong> (31.1%) — 전통 IP 의존도 높고 신규 IP 안착률 낮음. <strong>중화권(44.3%)은 공격적 진입 628개 중 278개 생존</strong>.')

    # 4. 퍼블리셔별 광고율
    cards4 = ''.join([gen_paid_card(PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_PAID[p]) for p in ['KR','JP','중화권','북미','기타']])
    sec4 = build_section('4', '📢', '퍼블리셔별 생존 vs 미생존 게임의 광고집행률', '광고 투자와 생존의 상관관계 분석',
        f'<div class="ng-card-grid cols-5">{cards4}</div>',
        '<strong>핵심:</strong> <strong>중화권 + 글로벌(기타) 퍼블은 광고-생존 강한 상관</strong> (+15%p 차이). 반면 <strong>KR/JP/북미 퍼블은 광고-생존 상관성 낮음</strong> — IP 기반 오가닉 성장. <strong>NHN 같은 웹보드 KR 퍼블은 오가닉 전략이 유효</strong>.')

    # 5. 국가별 차트 잔존율
    cards5 = ''.join([gen_retention_chart(COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_RETENTION[c]) for c in ['KR','JP','US']])
    sec5 = build_section('5', '📉', '국가별 차트 잔존율 (M+1 ~ M+12)', '진입월로부터 1~12개월 후 TOP 100 잔존율 추이 · AOS(실선) vs iOS(점선)',
        f'<div class="ng-card-grid cols-3">{cards5}</div>',
        '<strong>핵심:</strong> <strong>KR은 가장 빠른 하락 곡선</strong> — M+1 64% → M+12 17%. 신작 수명 짧음. <strong>US는 완만한 하락</strong> (M+12 30%) — 오래 가는 시장. <strong>JP는 M+12에서 반등</strong> (25%) — 이벤트/업데이트로 복귀 게임 많음. AOS/iOS 추이는 거의 일치.')

    # 6. 퍼블리셔별 차트 잔존율
    cards6 = ''.join([gen_retention_chart(PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_RETENTION[p]) for p in ['KR','JP','중화권','북미','기타']])
    sec6 = build_section('6', '📉', '퍼블리셔별 차트 잔존율 (M+1 ~ M+12)', '5개 퍼블 그룹별 잔존율 추이 · AOS(실선) vs iOS(점선)',
        f'<div class="ng-card-grid cols-5">{cards6}</div>',
        '<strong>핵심:</strong> <strong>북미 퍼블리셔가 가장 긴 수명</strong> — M+12에 38% 잔존 (다른 그룹 대비 2배). <strong>중화권은 초기 생존율 높지만(68%) 급락</strong>. <strong>JP는 M+1부터 낮지만 M+12 반등</strong> — IP 기반 리바이벌 패턴.')

    # 7. 장르 비중
    sec7_body = '''<table style="width:100%;border-collapse:collapse;font-size:0.78rem;">
  <thead><tr style="background:#f1f5f9;">
    <th style="padding:8px 12px;text-align:left;color:#475569;">장르</th>
    <th style="padding:8px 12px;text-align:right;color:#475569;">전(22~24) 게임수</th>
    <th style="padding:8px 12px;text-align:right;color:#475569;">전 비중</th>
    <th style="padding:8px 12px;text-align:right;color:#475569;">후(25~26.1Q) 게임수</th>
    <th style="padding:8px 12px;text-align:right;color:#475569;">후 비중</th>
    <th style="padding:8px 12px;text-align:right;color:#475569;">변화</th>
  </tr></thead>
  <tbody>
    <tr><td style="padding:6px 12px;font-weight:700;">Role Playing</td><td style="padding:6px 12px;text-align:right;">520</td><td style="padding:6px 12px;text-align:right;">53.6%</td><td style="padding:6px 12px;text-align:right;">188</td><td style="padding:6px 12px;text-align:right;color:#dc2626;font-weight:700;">46.8%</td><td style="padding:6px 12px;text-align:right;color:#dc2626;font-weight:700;">-6.8%p</td></tr>
    <tr><td style="padding:6px 12px;">Strategy</td><td style="padding:6px 12px;text-align:right;">111</td><td style="padding:6px 12px;text-align:right;">11.4%</td><td style="padding:6px 12px;text-align:right;">49</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">12.2%</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">+0.8%p</td></tr>
    <tr style="background:#fef3c7;"><td style="padding:6px 12px;font-weight:700;">Adventure</td><td style="padding:6px 12px;text-align:right;">31</td><td style="padding:6px 12px;text-align:right;">3.2%</td><td style="padding:6px 12px;text-align:right;">35</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">8.7%</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">+5.5%p</td></tr>
    <tr><td style="padding:6px 12px;">Simulation</td><td style="padding:6px 12px;text-align:right;">63</td><td style="padding:6px 12px;text-align:right;">6.5%</td><td style="padding:6px 12px;text-align:right;">29</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">7.2%</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">+0.7%p</td></tr>
    <tr><td style="padding:6px 12px;">Action</td><td style="padding:6px 12px;text-align:right;">53</td><td style="padding:6px 12px;text-align:right;">5.5%</td><td style="padding:6px 12px;text-align:right;">26</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">6.5%</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">+1.0%p</td></tr>
    <tr><td style="padding:6px 12px;">Puzzle</td><td style="padding:6px 12px;text-align:right;">51</td><td style="padding:6px 12px;text-align:right;">5.3%</td><td style="padding:6px 12px;text-align:right;">24</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">6.0%</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">+0.7%p</td></tr>
    <tr style="background:#fef3c7;"><td style="padding:6px 12px;font-weight:700;">Casual</td><td style="padding:6px 12px;text-align:right;">34</td><td style="padding:6px 12px;text-align:right;">3.5%</td><td style="padding:6px 12px;text-align:right;">20</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">5.0%</td><td style="padding:6px 12px;text-align:right;color:#059669;font-weight:700;">+1.5%p</td></tr>
    <tr><td style="padding:6px 12px;">Card</td><td style="padding:6px 12px;text-align:right;">25</td><td style="padding:6px 12px;text-align:right;">2.6%</td><td style="padding:6px 12px;text-align:right;">10</td><td style="padding:6px 12px;text-align:right;">2.5%</td><td style="padding:6px 12px;text-align:right;color:#dc2626;font-weight:700;">-0.1%p</td></tr>
    <tr><td style="padding:6px 12px;">Sports</td><td style="padding:6px 12px;text-align:right;">31</td><td style="padding:6px 12px;text-align:right;">3.2%</td><td style="padding:6px 12px;text-align:right;">9</td><td style="padding:6px 12px;text-align:right;color:#dc2626;font-weight:700;">2.2%</td><td style="padding:6px 12px;text-align:right;color:#dc2626;font-weight:700;">-1.0%p</td></tr>
    <tr style="background:#f8fafc;font-weight:700;"><td style="padding:6px 12px;">합계</td><td style="padding:6px 12px;text-align:right;">970</td><td style="padding:6px 12px;text-align:right;">100%</td><td style="padding:6px 12px;text-align:right;">402</td><td style="padding:6px 12px;text-align:right;">100%</td><td style="padding:6px 12px;text-align:right;"></td></tr>
  </tbody>
</table>'''
    sec7 = build_section('7', '🎮', '신규 진입 게임 25년 전후 장르 비중', '전(22~24) vs 후(25~26.1Q) 신규 진입 게임의 장르 분포 변화', sec7_body,
        '<strong>핵심:</strong> <strong>Role Playing 비중 53.6% → 46.8%로 6.8%p 감소</strong> — 전통 RPG 신작 공급 줄어듦. 반면 <strong>Adventure 3.2% → 8.7% (+5.5%p 최대 성장)</strong>, <strong>Casual +1.5%p</strong> — 캐주얼/어드벤처 신작 증가.')

    new_content = sec1 + sec2 + sec3 + sec4 + sec5 + sec6 + sec7

    # 기존 ng-section들 모두 삭제, 새 콘텐츠로 교체
    # ng-definition 닫는 </div> 뒤부터 ng-footer 전까지
    start = html.find('<div class="ng-definition">')
    definition_end = html.find('</div>', start) + 6
    footer_start = html.find('<div class="ng-footer">', definition_end)

    print(f'Definition end: {definition_end}')
    print(f'Footer start: {footer_start}')

    if definition_end > 0 and footer_start > 0:
        html = html[:definition_end] + '\n' + new_content + '\n\n' + html[footer_start:]
        print('Replaced content!')

    # Verify
    d = html.count('<div')
    c = html.count('</div>')
    print(f'\ndiv: {d}/{c} diff={d-c}')

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Saved!')

if __name__ == '__main__':
    main()
