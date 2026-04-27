#!/usr/bin/env python3
"""신규 진입 게임 분석 탭 재설계"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'

# ===== 데이터 =====

# 1. 국가별 생존율 (전체/AOS/iOS)
COUNTRY_SURVIVAL = {
    'KR': {'all': (843, 342, 40.6), 'android': (435, 177, 40.7), 'ios': (408, 165, 40.4)},
    'JP': {'all': (559, 201, 36.0), 'android': (283, 100, 35.3), 'ios': (276, 101, 36.6)},
    'US': {'all': (276, 162, 58.7), 'android': (134, 78, 58.2), 'ios': (142, 84, 59.2)},
}

# 2. 국가별 광고집행률 (생존 vs 미생존, 전체/AOS/iOS)
COUNTRY_PAID = {
    'KR': {
        'all': {'survived': (288, 43.6), 'died': (394, 36.1)},
        'android': {'survived': (145, 39.7), 'died': (204, 34.5)},
        'ios': {'survived': (143, 47.5), 'died': (190, 37.8)},
    },
    'JP': {
        'all': {'survived': (193, 34.9), 'died': (337, 22.5)},
        'android': {'survived': (96, 32.4), 'died': (172, 21.5)},
        'ios': {'survived': (97, 37.3), 'died': (165, 23.6)},
    },
    'US': {
        'all': {'survived': (160, 49.2), 'died': (114, 36.5)},
        'android': {'survived': (77, 46.4), 'died': (56, 35.6)},
        'ios': {'survived': (83, 51.7), 'died': (58, 37.5)},
    },
}

# 3. 퍼블리셔별 생존율
PUB_SURVIVAL = {
    'KR':     {'all': (389, 163, 41.9), 'android': (199, 82, 41.2), 'ios': (190, 81, 42.6)},
    'JP':     {'all': (328, 102, 31.1), 'android': (165, 51, 30.9), 'ios': (163, 51, 31.3)},
    '중화권': {'all': (628, 278, 44.3), 'android': (330, 144, 43.6), 'ios': (298, 134, 45.0)},
    '북미':   {'all': (109, 54, 49.5), 'android': (54, 26, 48.1), 'ios': (55, 28, 50.9)},
    '기타':   {'all': (224, 108, 48.2), 'android': (104, 52, 50.0), 'ios': (120, 56, 46.7)},
}

# 4. 퍼블리셔별 광고율
PUB_PAID = {
    'KR':     {'all': {'survived': (140, 32.3), 'died': (195, 29.9)}, 'android': {'survived': (70, 29.8), 'died': (100, 29.7)}, 'ios': {'survived': (70, 34.7), 'died': (95, 30.2)}},
    'JP':     {'all': {'survived': (94, 21.2), 'died': (214, 18.1)}, 'android': {'survived': (47, 19.2), 'died': (108, 16.9)}, 'ios': {'survived': (47, 23.1), 'died': (106, 19.2)}},
    '중화권': {'all': {'survived': (246, 52.7), 'died': (281, 37.3)}, 'android': {'survived': (124, 47.3), 'died': (151, 34.9)}, 'ios': {'survived': (122, 58.1), 'died': (130, 40.1)}},
    '북미':   {'all': {'survived': (53, 26.7), 'died': (55, 26.8)}, 'android': {'survived': (25, 24.1), 'died': (28, 25.5)}, 'ios': {'survived': (28, 29.1), 'died': (27, 28.1)}},
    '기타':   {'all': {'survived': (108, 58.0), 'died': (100, 43.3)}, 'android': {'survived': (52, 57.3), 'died': (45, 43.6)}, 'ios': {'survived': (56, 58.6), 'died': (55, 43.1)}},
}

# 5. 국가별 차트 잔존율 M+1~M+12 (Android, iOS)
COUNTRY_RETENTION = {
    'KR': {
        'android': [63.7, 48.0, 40.7, 33.8, 26.9, 25.7, 20.5, 18.6, 16.3, 14.5, 14.7, 16.1],
        'ios':     [64.2, 48.8, 40.4, 32.8, 26.2, 25.2, 20.8, 19.4, 17.2, 15.4, 15.4, 17.4],
    },
    'JP': {
        'android': [54.1, 39.9, 35.3, 32.9, 30.7, 29.0, 22.6, 21.9, 21.6, 20.8, 19.8, 24.4],
        'ios':     [54.0, 40.2, 36.6, 33.7, 32.6, 30.8, 23.6, 22.8, 23.2, 21.7, 20.7, 25.7],
    },
    'US': {
        'android': [68.7, 57.5, 58.2, 53.7, 51.5, 44.0, 40.3, 39.6, 38.1, 35.8, 31.3, 32.8],
        'ios':     [72.5, 59.9, 59.2, 56.3, 51.4, 44.4, 40.1, 38.7, 36.6, 35.2, 28.9, 30.3],
    },
}

# 6. 퍼블리셔별 차트 잔존율 (Android, iOS)
PUB_RETENTION = {
    'KR':     {'android': [60.3, 50.3, 41.2, 34.7, 24.6, 25.1, 21.6, 20.1, 17.1, 15.6, 15.1, 18.6], 'ios': [61.6, 51.1, 42.6, 34.2, 25.3, 25.3, 21.6, 22.1, 18.4, 17.4, 16.8, 20.5]},
    'JP':     {'android': [43.6, 32.7, 30.9, 27.9, 29.1, 27.9, 20.6, 17.6, 17.6, 18.8, 18.2, 27.3], 'ios': [42.3, 31.9, 31.3, 27.0, 30.7, 30.1, 20.9, 17.8, 19.0, 19.0, 18.4, 28.2]},
    '중화권': {'android': [67.6, 48.2, 43.6, 35.5, 31.2, 28.8, 21.8, 21.5, 19.7, 18.2, 17.9, 16.1], 'ios': [69.5, 50.3, 45.0, 37.2, 32.2, 29.9, 23.8, 22.8, 21.1, 19.8, 19.1, 17.8]},
    '북미':   {'android': [68.5, 51.9, 48.1, 51.9, 51.9, 42.6, 35.2, 35.2, 38.9, 35.2, 27.8, 38.9], 'ios': [70.9, 56.4, 50.9, 54.5, 52.7, 43.6, 36.4, 34.5, 38.2, 34.5, 27.3, 38.2]},
    '기타':   {'android': [67.3, 55.8, 50.0, 50.0, 43.3, 37.5, 37.5, 35.6, 32.7, 27.9, 26.9, 26.0], 'ios': [68.3, 54.2, 46.7, 47.5, 39.2, 34.2, 34.2, 32.5, 30.0, 25.8, 22.5, 21.7]},
}

# 색상
COUNTRY_COLOR = {'KR': '#3b82f6', 'JP': '#ef4444', 'US': '#a855f7'}
COUNTRY_FLAG = {'KR': '🇰🇷', 'JP': '🇯🇵', 'US': '🇺🇸'}
COUNTRY_NAME = {'KR': 'KR 한국', 'JP': 'JP 일본', 'US': 'US 미국'}

PUB_COLOR = {'KR': '#3b82f6', 'JP': '#ef4444', '중화권': '#f59e0b', '북미': '#8b5cf6', '기타': '#64748b'}
PUB_FLAG = {'KR': '🇰🇷', 'JP': '🇯🇵', '중화권': '🇨🇳', '북미': '🇺🇸', '기타': '🌐'}
PUB_NAME = {'KR': 'KR 한국', 'JP': 'JP 일본', '중화권': '중화권', '북미': '북미', '기타': '기타 (글로벌)'}

# ===== 카드 생성 함수 =====

def gen_survival_card(group, color, flag, name, data):
    """생존율 카드: 전체값 크게 + AOS/iOS 막대 비교"""
    all_t, all_s, all_p = data['all']
    aos_t, aos_s, aos_p = data['android']
    ios_t, ios_s, ios_p = data['ios']
    diff = round(ios_p - aos_p, 1)
    diff_str = f'+{diff}%p' if diff > 0 else f'{diff}%p' if diff < 0 else '동일'
    diff_color = '#dc2626' if diff > 0 else '#059669' if diff < 0 else '#94a3b8'

    return f'''<div class="ng-card" style="border-color:{color};background:#fff;">
  <div class="ng-card-header" style="border-bottom:2px solid {color};">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
    <span class="ng-rate" style="color:{color};">{all_p}%</span>
  </div>
  <div class="ng-card-stat">
    <div class="ng-stat-detail">전체 <strong>{all_s}/{all_t}</strong> 생존</div>
    <div class="ng-bar-row">
      <div class="ng-bar-label">전체</div>
      <div class="ng-bar-track"><div class="ng-bar-fill" style="width:{all_p}%;background:{color};"></div></div>
      <div class="ng-bar-val" style="color:{color};">{all_p}%</div>
    </div>
    <div class="ng-bar-row">
      <div class="ng-bar-label">AOS</div>
      <div class="ng-bar-track"><div class="ng-bar-fill" style="width:{aos_p}%;background:{color};opacity:0.6;"></div></div>
      <div class="ng-bar-val" style="color:{color};opacity:0.8;">{aos_p}%</div>
    </div>
    <div class="ng-bar-row">
      <div class="ng-bar-label">iOS</div>
      <div class="ng-bar-track"><div class="ng-bar-fill" style="width:{ios_p}%;background:{color};opacity:0.4;"></div></div>
      <div class="ng-bar-val" style="color:{color};opacity:0.6;">{ios_p}%</div>
    </div>
    <div class="ng-os-diff">iOS - AOS: <strong style="color:{diff_color};">{diff_str}</strong></div>
  </div>
</div>'''

def gen_paid_card(group, color, flag, name, data):
    """광고율 카드: 생존 vs 미생존"""
    all_s = data['all']['survived']
    all_d = data['all']['died']
    aos_s = data['android']['survived']
    aos_d = data['android']['died']
    ios_s = data['ios']['survived']
    ios_d = data['ios']['died']

    diff_all = round(all_s[1] - all_d[1], 1)
    diff_color = '#059669' if diff_all > 0 else '#dc2626' if diff_all < 0 else '#94a3b8'

    def bar(pct, c):
        w = min(pct, 100)
        return f'<div class="ng-bar-track-mini"><div class="ng-bar-fill" style="width:{w}%;background:{c};"></div></div>'

    return f'''<div class="ng-card" style="border-color:{color};background:#fff;">
  <div class="ng-card-header" style="border-bottom:2px solid {color};">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
    <span class="ng-rate" style="color:{diff_color};">+{diff_all:.1f}%p</span>
  </div>
  <div class="ng-card-stat">
    <table class="ng-paid-table">
      <thead><tr><th>OS</th><th class="r" style="color:#059669;">생존</th><th class="r" style="color:#dc2626;">미생존</th><th class="r">차이</th></tr></thead>
      <tbody>
        <tr><td><strong>전체</strong></td><td class="r"><strong style="color:#059669;">{all_s[1]}%</strong> <span class="ng-cnt">({all_s[0]})</span></td><td class="r" style="color:#dc2626;">{all_d[1]}% <span class="ng-cnt">({all_d[0]})</span></td><td class="r" style="color:{diff_color};font-weight:700;">+{round(all_s[1]-all_d[1],1)}%p</td></tr>
        <tr><td>AOS</td><td class="r" style="color:#059669;">{aos_s[1]}%</td><td class="r" style="color:#dc2626;">{aos_d[1]}%</td><td class="r" style="color:{diff_color};">+{round(aos_s[1]-aos_d[1],1)}%p</td></tr>
        <tr><td>iOS</td><td class="r" style="color:#059669;">{ios_s[1]}%</td><td class="r" style="color:#dc2626;">{ios_d[1]}%</td><td class="r" style="color:{diff_color};">+{round(ios_s[1]-ios_d[1],1)}%p</td></tr>
      </tbody>
    </table>
  </div>
</div>'''

def gen_retention_chart(group, color, flag, name, data):
    """차트 잔존율 - AOS/iOS 라인 한 차트에"""
    aos = data['android']
    ios = data['ios']

    # SVG
    chart_w = 600
    chart_h = 220
    pad_l = 50
    pad_r = 20
    pad_t = 25
    pad_b = 35
    plot_w = chart_w - pad_l - pad_r  # 530
    plot_h = chart_h - pad_t - pad_b  # 160

    n = 12
    x_step = plot_w / (n - 1)

    # Y축 (0~80%)
    y_max = 80

    # Y축 그리드 + 라벨
    y_grid = ''
    for v in [0, 20, 40, 60, 80]:
        y = pad_t + plot_h - (v / y_max) * plot_h
        y_grid += f'<line x1="{pad_l}" y1="{y}" x2="{chart_w-pad_r}" y2="{y}" stroke="#f1f5f9" stroke-dasharray="2,2"/>'
        y_grid += f'<text x="{pad_l-5}" y="{y+3}" text-anchor="end" font-size="9" fill="#94a3b8">{v}%</text>'

    # X축 라벨
    x_labels = ''
    for i in range(n):
        x = pad_l + i * x_step
        x_labels += f'<text x="{x}" y="{chart_h-pad_b+15}" text-anchor="middle" font-size="9" fill="#64748b">M+{i+1}</text>'

    # AOS 라인 (실선)
    aos_pts = ' '.join(f'{pad_l+i*x_step:.1f},{pad_t+plot_h-(v/y_max)*plot_h:.1f}' for i, v in enumerate(aos))
    aos_circles = ''.join(f'<circle cx="{pad_l+i*x_step:.1f}" cy="{pad_t+plot_h-(v/y_max)*plot_h:.1f}" r="3" fill="{color}"/>' for i, v in enumerate(aos))

    # iOS 라인 (점선)
    ios_pts = ' '.join(f'{pad_l+i*x_step:.1f},{pad_t+plot_h-(v/y_max)*plot_h:.1f}' for i, v in enumerate(ios))
    ios_circles = ''.join(f'<circle cx="{pad_l+i*x_step:.1f}" cy="{pad_t+plot_h-(v/y_max)*plot_h:.1f}" r="3" fill="white" stroke="{color}" stroke-width="2"/>' for i, v in enumerate(ios))

    return f'''<div class="ng-card" style="border-color:{color};background:#fff;">
  <div class="ng-card-header" style="border-bottom:2px solid {color};">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
    <span style="font-size:0.7rem;color:#94a3b8;margin-left:auto;">M+1: {(aos[0]+ios[0])/2:.0f}% → M+12: {(aos[11]+ios[11])/2:.0f}%</span>
  </div>
  <div class="ng-card-stat">
    <svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;max-width:600px;">
      {y_grid}
      <polyline fill="none" stroke="{color}" stroke-width="2" points="{aos_pts}"/>
      {aos_circles}
      <polyline fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="4,3" points="{ios_pts}"/>
      {ios_circles}
      {x_labels}
      <!-- Legend -->
      <rect x="{chart_w-100}" y="{pad_t-15}" width="14" height="2" fill="{color}"/>
      <text x="{chart_w-83}" y="{pad_t-12}" font-size="9" fill="#475569">AOS</text>
      <rect x="{chart_w-50}" y="{pad_t-15}" width="14" height="2" fill="{color}" stroke-dasharray="2,2"/>
      <text x="{chart_w-33}" y="{pad_t-12}" font-size="9" fill="#475569">iOS</text>
    </svg>
  </div>
</div>'''

# ===== 새 탭 콘텐츠 생성 =====

def build_new_content():
    out = []

    # CSS 추가 (기존 ng- prefix 위에 추가)
    extra_css = '''
  /* ===== Newgame v2 통일 카드 디자인 ===== */
  .tab-newgame .ng-container { max-width: 1200px !important; margin: 0 auto; padding: 0 16px; }
  .tab-newgame .ng-card-grid { display: grid; gap: 16px; }
  .tab-newgame .ng-card-grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
  .tab-newgame .ng-card-grid.cols-5 { grid-template-columns: repeat(5, 1fr); }
  .tab-newgame .ng-card { border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; border-top-width: 4px; }
  .tab-newgame .ng-card-header { padding: 10px 14px; display: flex; align-items: center; gap: 8px; background: #fafbfc; }
  .tab-newgame .ng-flag { font-size: 1rem; }
  .tab-newgame .ng-name { font-size: 0.78rem; font-weight: 700; color: #1e293b; }
  .tab-newgame .ng-rate { margin-left: auto; font-size: 1.1rem; font-weight: 800; }
  .tab-newgame .ng-card-stat { padding: 12px 14px; }
  .tab-newgame .ng-stat-detail { font-size: 0.7rem; color: #64748b; margin-bottom: 10px; }
  .tab-newgame .ng-stat-detail strong { color: #1e293b; }
  .tab-newgame .ng-bar-row { display: grid; grid-template-columns: 30px 1fr 40px; align-items: center; gap: 6px; margin-bottom: 4px; font-size: 0.68rem; }
  .tab-newgame .ng-bar-label { color: #94a3b8; font-weight: 600; }
  .tab-newgame .ng-bar-track { height: 14px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
  .tab-newgame .ng-bar-track-mini { height: 8px; background: #f1f5f9; border-radius: 2px; overflow: hidden; }
  .tab-newgame .ng-bar-fill { height: 100%; }
  .tab-newgame .ng-bar-val { font-weight: 700; text-align: right; font-variant-numeric: tabular-nums; }
  .tab-newgame .ng-os-diff { margin-top: 8px; padding-top: 6px; border-top: 1px dashed #e2e8f0; font-size: 0.65rem; color: #64748b; text-align: center; }
  .tab-newgame .ng-paid-table { width: 100%; border-collapse: collapse; font-size: 0.7rem; }
  .tab-newgame .ng-paid-table th { background: #f8fafc; padding: 4px 6px; text-align: left; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #64748b; font-size: 0.62rem; }
  .tab-newgame .ng-paid-table th.r { text-align: right; }
  .tab-newgame .ng-paid-table td { padding: 4px 6px; border-bottom: 1px solid #f1f5f9; }
  .tab-newgame .ng-paid-table td.r { text-align: right; font-variant-numeric: tabular-nums; }
  .tab-newgame .ng-cnt { color: #cbd5e1; font-weight: 400; font-size: 0.6rem; }
  @media (max-width: 1100px) { .tab-newgame .ng-card-grid.cols-5 { grid-template-columns: repeat(3, 1fr); } }
  @media (max-width: 768px) { .tab-newgame .ng-card-grid.cols-3, .tab-newgame .ng-card-grid.cols-5 { grid-template-columns: 1fr; } }
'''
    return extra_css


def build_section(num, icon, title, desc, body_html, ins_text):
    return f'''
<div class="ng-section">
  <div class="ng-section-head">
    <div class="ng-section-num">{num}</div>
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

    # 1. CSS 추가
    extra_css = build_new_content()
    if '/* ===== Newgame v2' not in html:
        html = html.replace('</style>', extra_css + '\n</style>', 1)
        print('CSS added')

    # === 섹션 1: 국가별 생존율 ===
    cards = ''.join([gen_survival_card(c, COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_SURVIVAL[c]) for c in ['KR','JP','US']])
    sec1 = build_section(
        '1', '🌏', '국가별 신규 진입 게임 3개월 생존율',
        '진입월 + 3개월 후에도 TOP 100에 존재하는 비율 (전체 + AOS/iOS 비교)',
        f'<div class="ng-card-grid cols-3">{cards}</div>',
        '<strong>핵심:</strong> 🇺🇸 US 58.7%로 3국 중 가장 높은 생존율 — 시장 크기로 안정성 확보. KR(40.6%) · JP(36.0%) 대비 1.5배. <strong>OS 차이는 미미</strong> (대부분 ±1%p 이내).'
    )

    # === 섹션 2: 국가별 광고집행률 ===
    cards2 = ''.join([gen_paid_card(c, COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_PAID[c]) for c in ['KR','JP','US']])
    sec2 = build_section(
        '2', '📣', '국가별 생존 vs 미생존 게임의 광고집행률',
        '진입 후 3개월간 평균 광고유입률 = paid_abs / (paid + organic + browser)',
        f'<div class="ng-card-grid cols-3">{cards2}</div>',
        '<strong>핵심:</strong> 3국 모두 <strong>생존 게임이 미생존보다 광고 집행률이 높음</strong> (평균 +11.6%p). <strong>광고 투자가 생존으로 이어진다</strong>는 강한 상관관계. iOS가 AOS보다 광고 집행률 높은 경향 (특히 JP iOS +13.7%p).'
    )

    # === 섹션 3: 퍼블리셔별 생존율 ===
    cards3 = ''.join([gen_survival_card(p, PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_SURVIVAL[p]) for p in ['KR','JP','중화권','북미','기타']])
    sec3 = build_section(
        '3', '🏢', '퍼블리셔 국적별 신규 진입 게임 3개월 생존율',
        'NEXON→KR, FUNFLY→중화권 강제 분류 · 5개 퍼블 그룹별 비교',
        f'<div class="ng-card-grid cols-5">{cards3}</div>',
        '<strong>핵심:</strong> <strong>북미/기타(글로벌) 퍼블리셔가 생존율 최고</strong> (48~50%). <strong>JP 퍼블리셔가 생존율 최저</strong> (31.1%) — 전통 IP 의존도 높고 신규 IP 안착률 낮음. <strong>중화권(44.3%)은 공격적 진입 628개 중 278개 생존</strong>.'
    )

    # === 섹션 4: 퍼블리셔별 광고집행률 ===
    cards4 = ''.join([gen_paid_card(p, PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_PAID[p]) for p in ['KR','JP','중화권','북미','기타']])
    sec4 = build_section(
        '4', '📢', '퍼블리셔별 생존 vs 미생존 게임의 광고집행률',
        '광고 투자와 생존의 상관관계 분석',
        f'<div class="ng-card-grid cols-5">{cards4}</div>',
        '<strong>핵심:</strong> <strong>중화권 + 글로벌(기타) 퍼블은 광고-생존 강한 상관</strong> (+15%p 차이). 반면 <strong>KR/JP/북미 퍼블은 광고-생존 상관성 낮음</strong> — IP 기반 오가닉 성장. <strong>NHN 같은 웹보드 KR 퍼블은 오가닉 전략이 유효</strong>.'
    )

    # === 섹션 5: 국가별 차트 잔존율 ===
    cards5 = ''.join([gen_retention_chart(c, COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_RETENTION[c]) for c in ['KR','JP','US']])
    sec5 = build_section(
        '5', '📉', '국가별 신규 진입 게임 차트 잔존율 (M+1 ~ M+12)',
        '진입월로부터 1~12개월 후 TOP 100 잔존율 추이 · AOS(실선) vs iOS(점선)',
        f'<div class="ng-card-grid cols-3">{cards5}</div>',
        '<strong>핵심:</strong> <strong>KR은 가장 빠른 하락 곡선</strong> — M+1 64% → M+12 17%. 신작 수명 짧음. <strong>US는 완만한 하락</strong> (M+12 30%) — 오래 가는 시장. <strong>JP는 M+12에서 반등</strong> (25%) — 이벤트/업데이트로 복귀 게임 많음. AOS/iOS 추이는 거의 일치.'
    )

    # === 섹션 6: 퍼블리셔별 차트 잔존율 ===
    cards6 = ''.join([gen_retention_chart(p, PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_RETENTION[p]) for p in ['KR','JP','중화권','북미','기타']])
    sec6 = build_section(
        '6', '📉', '퍼블리셔별 신규 진입 게임 차트 잔존율 (M+1 ~ M+12)',
        '5개 퍼블 그룹별 잔존율 추이 · AOS(실선) vs iOS(점선)',
        f'<div class="ng-card-grid cols-5">{cards6}</div>',
        '<strong>핵심:</strong> <strong>북미 퍼블리셔가 가장 긴 수명</strong> — M+12에 38% 잔존 (다른 그룹 대비 2배). <strong>중화권은 초기 생존율 높지만(68%) 급락</strong>. <strong>JP는 M+1부터 낮지만 M+12 반등</strong> — IP 기반 리바이벌 패턴.'
    )

    # === 섹션 7: 장르 비중 25년 전후 ===
    sec7 = build_section(
        '7', '🎮', '신규 진입 게임 25년 전후 장르 비중',
        '전(22~24) vs 후(25~26.1Q) 신규 진입 게임의 장르 분포 변화',
        '''<table style="width:100%;border-collapse:collapse;font-size:0.78rem;">
  <thead>
    <tr style="background:#f1f5f9;">
      <th style="padding:8px 12px;text-align:left;color:#475569;">장르</th>
      <th class="r" style="padding:8px 12px;text-align:right;color:#475569;">전 (22~24) 게임수</th>
      <th class="r" style="padding:8px 12px;text-align:right;color:#475569;">전 비중</th>
      <th class="r" style="padding:8px 12px;text-align:right;color:#475569;">후 (25~26.1Q) 게임수</th>
      <th class="r" style="padding:8px 12px;text-align:right;color:#475569;">후 비중</th>
      <th class="r" style="padding:8px 12px;text-align:right;color:#475569;">변화</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:6px 12px;font-weight:700;">Role Playing</td><td class="r" style="padding:6px 12px;text-align:right;">520</td><td class="r" style="padding:6px 12px;text-align:right;">53.6%</td><td class="r" style="padding:6px 12px;text-align:right;">188</td><td class="r ng-dn" style="padding:6px 12px;text-align:right;">46.8%</td><td class="r ng-dn" style="padding:6px 12px;text-align:right;">-6.8%p</td></tr>
    <tr><td style="padding:6px 12px;">Strategy</td><td class="r" style="padding:6px 12px;text-align:right;">111</td><td class="r" style="padding:6px 12px;text-align:right;">11.4%</td><td class="r" style="padding:6px 12px;text-align:right;">49</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">12.2%</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">+0.8%p</td></tr>
    <tr style="background:#fef3c7;"><td style="padding:6px 12px;font-weight:700;">Adventure</td><td class="r" style="padding:6px 12px;text-align:right;">31</td><td class="r" style="padding:6px 12px;text-align:right;">3.2%</td><td class="r" style="padding:6px 12px;text-align:right;">35</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">8.7%</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">+5.5%p</td></tr>
    <tr><td style="padding:6px 12px;">Simulation</td><td class="r" style="padding:6px 12px;text-align:right;">63</td><td class="r" style="padding:6px 12px;text-align:right;">6.5%</td><td class="r" style="padding:6px 12px;text-align:right;">29</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">7.2%</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">+0.7%p</td></tr>
    <tr><td style="padding:6px 12px;">Action</td><td class="r" style="padding:6px 12px;text-align:right;">53</td><td class="r" style="padding:6px 12px;text-align:right;">5.5%</td><td class="r" style="padding:6px 12px;text-align:right;">26</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">6.5%</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">+1.0%p</td></tr>
    <tr><td style="padding:6px 12px;">Puzzle</td><td class="r" style="padding:6px 12px;text-align:right;">51</td><td class="r" style="padding:6px 12px;text-align:right;">5.3%</td><td class="r" style="padding:6px 12px;text-align:right;">24</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">6.0%</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">+0.7%p</td></tr>
    <tr style="background:#fef3c7;"><td style="padding:6px 12px;font-weight:700;">Casual</td><td class="r" style="padding:6px 12px;text-align:right;">34</td><td class="r" style="padding:6px 12px;text-align:right;">3.5%</td><td class="r" style="padding:6px 12px;text-align:right;">20</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">5.0%</td><td class="r ng-up" style="padding:6px 12px;text-align:right;">+1.5%p</td></tr>
    <tr><td style="padding:6px 12px;">Card</td><td class="r" style="padding:6px 12px;text-align:right;">25</td><td class="r" style="padding:6px 12px;text-align:right;">2.6%</td><td class="r" style="padding:6px 12px;text-align:right;">10</td><td class="r" style="padding:6px 12px;text-align:right;">2.5%</td><td class="r ng-dn" style="padding:6px 12px;text-align:right;">-0.1%p</td></tr>
    <tr><td style="padding:6px 12px;">Sports</td><td class="r" style="padding:6px 12px;text-align:right;">31</td><td class="r" style="padding:6px 12px;text-align:right;">3.2%</td><td class="r" style="padding:6px 12px;text-align:right;">9</td><td class="r ng-dn" style="padding:6px 12px;text-align:right;">2.2%</td><td class="r ng-dn" style="padding:6px 12px;text-align:right;">-1.0%p</td></tr>
    <tr style="background:#f8fafc;font-weight:700;"><td style="padding:6px 12px;">합계</td><td class="r" style="padding:6px 12px;text-align:right;">970</td><td class="r" style="padding:6px 12px;text-align:right;">100%</td><td class="r" style="padding:6px 12px;text-align:right;">402</td><td class="r" style="padding:6px 12px;text-align:right;">100%</td><td class="r" style="padding:6px 12px;text-align:right;"></td></tr>
  </tbody>
</table>''',
        '<strong>핵심:</strong> <strong>Role Playing 비중 53.6% → 46.8%로 6.8%p 감소</strong> — 전통 RPG 신작 공급 줄어듦. 반면 <strong>Adventure 3.2% → 8.7% (+5.5%p 최대 성장)</strong>, <strong>Casual +1.5%p</strong> — 캐주얼/어드벤처 신작 증가. <strong>"신규 진입 트렌드가 RPG 중심에서 Adventure·Casual로 분산 중"</strong>.'
    )

    new_content = sec1 + sec2 + sec3 + sec4 + sec5 + sec6 + sec7

    # 기존 신규 진입 탭의 ng-section들을 모두 새 콘텐츠로 교체
    # tab-newgame 내부의 ng-container 안 내용을 교체
    tab_start = html.find('<div id="tab-newgame"')
    if tab_start < 0:
        print('tab-newgame not found!')
        return

    # 기존 ng-section들을 찾아 교체
    # ng-container 안에서 헤더(definition까지)는 유지하고 그 뒤 첫 번째 ng-section부터 footer까지 교체
    container_start = html.find('<div class="ng-container">', tab_start)

    # definition 끝 위치 찾기
    def_end = html.find('</div>\n', html.find('class="ng-definition"', container_start)) + 6

    # ng-footer 시작 위치
    footer_start = html.find('<div class="ng-footer">', container_start)

    # 그 사이를 새 콘텐츠로 교체
    if def_end > 0 and footer_start > 0:
        html = html[:def_end] + '\n' + new_content + '\n  ' + html[footer_start:]
        print(f'Replaced sections: {def_end} to {footer_start}')

    # Verify
    d = html.count('<div')
    c = html.count('</div>')
    print(f'\ndiv: {d}/{c} diff={d-c}')

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Done!')

if __name__ == '__main__':
    main()
