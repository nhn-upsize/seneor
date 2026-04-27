#!/usr/bin/env python3
"""차트 잔존율 섹션을 25년 전후 비교로 재구성"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'

# ===== 국가별 25년 전후 차트 잔존율 (android, ios) =====
COUNTRY_RETENTION = {
    'KR': {
        'android': {'pre': [67.0,52.6,44.6,36.5,29.2,28.5,22.4,20.5,18.3,16.7,17.3,19.9], 'post': [55.3,36.6,30.9,26.8,21.1,18.7,15.4,13.8,11.4,8.9,8.1,6.5]},
        'ios':     {'pre': [68.7,53.6,44.7,35.7,28.2,28.2,22.3,21.0,18.9,17.5,18.2,21.6], 'post': [53.0,36.8,29.9,25.6,21.4,17.9,17.1,15.4,12.8,10.3,8.5,6.8]},
    },
    'JP': {
        'android': {'pre': [53.3,40.0,36.7,35.2,32.9,32.9,24.3,25.7,24.3,24.8,23.8,31.0], 'post': [56.2,39.7,31.5,26.0,24.7,17.8,17.8,11.0,13.7,9.6,8.2,5.5]},
        'ios':     {'pre': [52.2,40.4,38.4,36.5,35.5,35.5,25.6,27.1,26.6,26.1,25.1,33.0], 'post': [58.9,39.7,31.5,26.0,24.7,17.8,17.8,11.0,13.7,9.6,8.2,5.5]},
    },
    'US': {
        'android': {'pre': [71.0,61.3,62.4,55.9,54.8,46.2,47.3,45.2,46.2,41.9,38.7,44.1], 'post': [63.4,48.8,48.8,48.8,43.9,39.0,24.4,26.8,19.5,22.0,14.6,7.3]},
        'ios':     {'pre': [72.9,62.5,60.4,56.3,52.1,44.8,45.8,42.7,42.7,39.6,36.5,40.6], 'post': [71.7,54.3,56.5,56.5,50.0,43.5,28.3,30.4,23.9,26.1,13.0,8.7]},
    },
}

PUB_RETENTION = {
    'KR': {
        'android': {'pre': [61.1,51.7,40.3,36.2,24.8,26.8,22.1,21.5,18.8,16.8,16.8,21.5], 'post': [58.0,46.0,44.0,30.0,24.0,20.0,20.0,16.0,12.0,12.0,10.0,10.0]},
        'ios':     {'pre': [64.5,53.2,41.8,36.2,25.5,27.0,22.0,24.1,20.6,19.1,19.1,24.1], 'post': [53.1,44.9,44.9,28.6,24.5,20.4,20.4,16.3,12.2,12.2,10.2,10.2]},
    },
    'JP': {
        'android': {'pre': [40.5,30.2,31.7,27.0,27.8,28.6,22.2,19.0,18.3,21.4,20.6,33.3], 'post': [53.8,41.0,28.2,30.8,33.3,25.6,15.4,12.8,15.4,10.3,10.3,7.7]},
        'ios':     {'pre': [38.7,29.0,32.3,25.8,29.8,31.5,22.6,19.4,20.2,21.8,21.0,34.7], 'post': [53.8,41.0,28.2,30.8,33.3,25.6,15.4,12.8,15.4,10.3,10.3,7.7]},
    },
    '중화권': {
        'android': {'pre': [72.5,53.8,49.2,40.0,36.3,33.3,25.8,25.8,24.2,22.5,22.1,21.3], 'post': [54.4,33.3,28.9,23.3,17.8,16.7,11.1,10.0,7.8,6.7,6.7,2.2]},
        'ios':     {'pre': [74.5,56.5,50.5,42.1,37.0,34.7,27.3,26.4,25.0,23.6,23.6,23.6], 'post': [56.1,34.1,30.5,24.4,19.5,17.1,14.6,13.4,11.0,9.8,7.3,2.4]},
    },
    '북미': {
        'android': {'pre': [70.7,58.5,56.1,58.5,58.5,48.8,41.5,39.0,43.9,39.0,34.1,48.8], 'post': [61.5,30.8,23.1,30.8,30.8,23.1,15.4,23.1,23.1,23.1,7.7,7.7]},
        'ios':     {'pre': [73.2,63.4,58.5,61.0,58.5,48.8,43.9,39.0,43.9,39.0,34.1,48.8], 'post': [64.3,35.7,28.6,35.7,35.7,28.6,14.3,21.4,21.4,21.4,7.1,7.1]},
    },
    '기타': {
        'android': {'pre': [71.2,62.7,55.9,54.2,47.5,42.4,42.4,44.1,40.7,35.6,37.3,39.0], 'post': [62.2,46.7,42.2,44.4,37.8,31.1,31.1,24.4,22.2,17.8,13.3,8.9]},
        'ios':     {'pre': [67.6,57.4,50.0,48.5,39.7,36.8,36.8,38.2,35.3,30.9,30.9,30.9], 'post': [69.2,50.0,42.3,46.2,38.5,30.8,30.8,25.0,23.1,19.2,11.5,9.6]},
    },
}

COUNTRY_COLOR = {'KR': '#3b82f6', 'JP': '#ef4444', 'US': '#a855f7'}
COUNTRY_FLAG = {'KR': '🇰🇷', 'JP': '🇯🇵', 'US': '🇺🇸'}
COUNTRY_NAME = {'KR': 'KR 한국', 'JP': 'JP 일본', 'US': 'US 미국'}
PUB_COLOR = {'KR': '#3b82f6', 'JP': '#ef4444', '중화권': '#f59e0b', '북미': '#8b5cf6', '기타': '#64748b'}
PUB_FLAG = {'KR': '🇰🇷', 'JP': '🇯🇵', '중화권': '🇨🇳', '북미': '🇺🇸', '기타': '🌐'}
PUB_NAME = {'KR': 'KR 한국', 'JP': 'JP 일본', '중화권': '중화권', '북미': '북미', '기타': '기타 (글로벌)'}


def gen_retention_chart(group_id, color, flag, name, data):
    """
    하나의 카드 안에 AOS/iOS 내부 탭으로 구분
    각 탭 안에는 pre(전, 회색) vs post(후, 컬러) 2개 라인
    """
    chart_w, chart_h = 620, 240
    pad_l, pad_r, pad_t, pad_b = 50, 20, 30, 40
    plot_w = chart_w - pad_l - pad_r
    plot_h = chart_h - pad_t - pad_b
    n = 12
    x_step = plot_w / (n - 1)
    y_max = 80

    def gen_svg(pre, post, os_label):
        y_grid = ''.join(f'<line x1="{pad_l}" y1="{pad_t+plot_h-(v/y_max)*plot_h}" x2="{chart_w-pad_r}" y2="{pad_t+plot_h-(v/y_max)*plot_h}" stroke="#f1f5f9" stroke-dasharray="2,2"/><text x="{pad_l-5}" y="{pad_t+plot_h-(v/y_max)*plot_h+3}" text-anchor="end" font-size="10" fill="#94a3b8">{v}%</text>' for v in [0,20,40,60,80])
        x_labels = ''.join(f'<text x="{pad_l+i*x_step}" y="{chart_h-pad_b+16}" text-anchor="middle" font-size="10" fill="#64748b">M+{i+1}</text>' for i in range(n))

        # 전 (회색, 점선)
        pre_pts = ' '.join(f'{pad_l+i*x_step:.1f},{pad_t+plot_h-(v/y_max)*plot_h:.1f}' for i, v in enumerate(pre))
        pre_circles = ''.join(f'<circle cx="{pad_l+i*x_step:.1f}" cy="{pad_t+plot_h-(v/y_max)*plot_h:.1f}" r="3.5" fill="white" stroke="#94a3b8" stroke-width="1.5"/>' for i, v in enumerate(pre))

        # 후 (컬러, 실선)
        post_pts = ' '.join(f'{pad_l+i*x_step:.1f},{pad_t+plot_h-(v/y_max)*plot_h:.1f}' for i, v in enumerate(post))
        post_circles = ''.join(f'<circle cx="{pad_l+i*x_step:.1f}" cy="{pad_t+plot_h-(v/y_max)*plot_h:.1f}" r="3.5" fill="{color}"/>' for i, v in enumerate(post))

        # 값 차이 분석 (M+3, M+6, M+12에서)
        diff_3 = round(post[2] - pre[2], 1)
        diff_6 = round(post[5] - pre[5], 1)
        diff_12 = round(post[11] - pre[11], 1)
        diff_color = '#dc2626' if diff_12 < -5 else ('#059669' if diff_12 > 5 else '#64748b')

        return f'''<svg viewBox="0 0 {chart_w} {chart_h}" style="width:100%;height:auto;">
  {y_grid}
  <polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5,3" points="{pre_pts}"/>
  {pre_circles}
  <polyline fill="none" stroke="{color}" stroke-width="2.5" points="{post_pts}"/>
  {post_circles}
  {x_labels}
  <!-- Legend -->
  <rect x="{pad_l}" y="8" width="14" height="3" fill="#94a3b8"/>
  <text x="{pad_l+18}" y="14" font-size="10" fill="#475569" font-weight="600">전 (22~24)</text>
  <rect x="{pad_l+90}" y="8" width="14" height="3" fill="{color}"/>
  <text x="{pad_l+108}" y="14" font-size="10" fill="{color}" font-weight="700">후 (25~26.1Q)</text>
  <text x="{chart_w-pad_r}" y="14" text-anchor="end" font-size="10" fill="{diff_color}" font-weight="700">M+12 Δ {diff_12:+}%p</text>
</svg>'''

    svg_aos = gen_svg(data['android']['pre'], data['android']['post'], 'AOS')
    svg_ios = gen_svg(data['ios']['pre'], data['ios']['post'], 'iOS')

    return f'''<div class="ng-card" style="border-top-color:{color};">
  <div class="ng-card-header">
    <span class="ng-flag">{flag}</span>
    <span class="ng-name">{name}</span>
  </div>
  <div class="ng-card-stat" style="padding:8px 10px;">
    <div class="ng-os-inner-tabs">
      <button class="ng-os-inner-tab active" onclick="switchNgInnerOS(this, '{group_id}', 'aos')">AOS</button>
      <button class="ng-os-inner-tab" onclick="switchNgInnerOS(this, '{group_id}', 'ios')">iOS</button>
    </div>
    <div id="ng-chart-{group_id}-aos" class="ng-chart-inner active">{svg_aos}</div>
    <div id="ng-chart-{group_id}-ios" class="ng-chart-inner">{svg_ios}</div>
  </div>
</div>'''


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # CSS 추가
    extra_css = '''
  /* 신규진입 탭 내부 OS 탭 (AOS/IOS) */
  .tab-newgame .ng-os-inner-tabs { display: flex; gap: 2px; border-bottom: 1px solid #e2e8f0; margin-bottom: 8px; }
  .tab-newgame .ng-os-inner-tab { padding: 5px 12px; border: none; background: none; cursor: pointer; font-size: 0.72rem; font-weight: 600; color: #94a3b8; border-bottom: 2px solid transparent; margin-bottom: -1px; font-family: inherit; }
  .tab-newgame .ng-os-inner-tab.active { color: #1e293b; border-bottom-color: #0f172a; }
  .tab-newgame .ng-chart-inner { display: none; }
  .tab-newgame .ng-chart-inner.active { display: block; }
'''
    if '.ng-os-inner-tabs' not in html:
        html = html.replace('</style>', extra_css + '\n</style>', 1)
        print('Inner OS tabs CSS added')

    # JS 함수 추가
    js_func = '''
function switchNgInnerOS(btn, groupId, os) {
  var tabs = btn.parentElement.querySelectorAll('.ng-os-inner-tab');
  tabs.forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  var charts = btn.parentElement.parentElement.querySelectorAll('.ng-chart-inner');
  charts.forEach(c => c.classList.remove('active'));
  var target = document.getElementById('ng-chart-' + groupId + '-' + os);
  if (target) target.classList.add('active');
}
'''
    if 'switchNgInnerOS' not in html:
        html = html.replace('</script>', js_func + '\n</script>', 1)
        print('switchNgInnerOS function added')

    # ===== 섹션 5 교체: 국가별 차트 잔존율 =====
    cards5 = ''.join([gen_retention_chart(f'c-{c}', COUNTRY_COLOR[c], COUNTRY_FLAG[c], COUNTRY_NAME[c], COUNTRY_RETENTION[c]) for c in ['KR','JP','US']])

    # 섹션 5 찾기: "국가별 차트 잔존율" 헤더 포함한 ng-section
    sec5_start = html.find('국가별 차트 잔존율 (M+1 ~ M+12)')
    if sec5_start > 0:
        # 해당 ng-section div 시작점 찾기
        sec_div_start = html.rfind('<div class="ng-section">', 0, sec5_start)
        # ng-section 닫는 </div> 찾기 (다음 ng-section 또는 ng-footer 전)
        sec_div_end_candidates = [html.find('<div class="ng-section">', sec_div_start + 30), html.find('<div class="ng-footer">', sec_div_start)]
        sec_div_end = min([p for p in sec_div_end_candidates if p > 0])

        # 새 섹션 생성
        new_sec5 = f'''<div class="ng-section">
  <div class="ng-section-head">
    <div class="ng-section-num" style="background:#0f172a;">5</div>
    <div>
      <h2>📉 국가별 차트 잔존율 25년 전후 비교 (M+1 ~ M+12)</h2>
      <div class="ng-desc">점선(회색) = 전(22~24 진입) · 실선(컬러) = 후(25~26.1Q 진입) · 내부 탭으로 AOS/iOS 전환</div>
    </div>
  </div>
  <div class="ng-card-grid cols-3">{cards5}</div>
  <div class="ng-ins"><strong>핵심:</strong> <strong>3국 모두 25년 이후 진입 게임 잔존율 급락</strong>. 🇰🇷 KR은 M+12 20%→7% (-13%p), 🇺🇸 US는 44%→7% (-37%p) 특히 큰 폭 하락. 🇯🇵 JP는 초기 M+1~2는 유지되나 M+12에서 31%→5% 붕괴. <strong>"최근 시장은 신작 수명이 크게 짧아지는 중"</strong>.</div>
</div>

'''
        html = html[:sec_div_start] + new_sec5 + html[sec_div_end:]
        print('Section 5 replaced')

    # ===== 섹션 6 교체: 퍼블리셔별 차트 잔존율 =====
    cards6 = ''.join([gen_retention_chart(f'p-{i}', PUB_COLOR[p], PUB_FLAG[p], PUB_NAME[p], PUB_RETENTION[p]) for i, p in enumerate(['KR','JP','중화권','북미','기타'])])

    sec6_start = html.find('퍼블리셔별 차트 잔존율')
    if sec6_start > 0:
        sec_div_start = html.rfind('<div class="ng-section">', 0, sec6_start)
        sec_div_end_candidates = [html.find('<div class="ng-section">', sec_div_start + 30), html.find('<div class="ng-footer">', sec_div_start)]
        sec_div_end = min([p for p in sec_div_end_candidates if p > 0])

        new_sec6 = f'''<div class="ng-section">
  <div class="ng-section-head">
    <div class="ng-section-num" style="background:#0f172a;">6</div>
    <div>
      <h2>📉 퍼블리셔별 차트 잔존율 25년 전후 비교 (M+1 ~ M+12)</h2>
      <div class="ng-desc">점선(회색) = 전(22~24 진입) · 실선(컬러) = 후(25~26.1Q 진입) · 내부 탭으로 AOS/iOS 전환</div>
    </div>
  </div>
  <div class="ng-card-grid cols-5">{cards6}</div>
  <div class="ng-ins"><strong>핵심:</strong> <strong>모든 퍼블 그룹이 25년 이후 잔존율 하락</strong>. 🇨🇳 중화권은 M+12 21%→2%로 가장 큰 폭 하락 (-19%p). 🇺🇸 북미는 49%→8% (-41%p)로 가장 극적인 변화. 🇯🇵 JP 퍼블만 M+12에서 33%→8% 하락폭이 상대적으로 작지만 전반적 수명 단축.</div>
</div>

'''
        html = html[:sec_div_start] + new_sec6 + html[sec_div_end:]
        print('Section 6 replaced')

    # Verify
    d = html.count('<div')
    c = html.count('</div>')
    print(f'\ndiv: {d}/{c} diff={d-c}')

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Done!')

if __name__ == '__main__':
    main()
