# -*- coding: utf-8 -*-
"""newgame_tab_standalone.html의 KR 패널을 tab-country-deep 스타일로 재스타일"""
import re

with open('reports/newgame_tab_standalone.html','r',encoding='utf-8') as f:
    c = f.read()

# ========== 1. <h1>KR 시장</h1> 와 그 위 주석을 headline 박스로 교체 ==========
old_head = '''<div class="ng-panel active" id="ng-kr">

<h1>KR 시장</h1>
<p class="subtitle">
기준: <code>dw_app_monthly.in_revenue_top100_unified_os = true</code>, <code>country = 'KR'</code>, iOS+Android 합산<br>
신규 진입 정의: 전체 기간(2022.01~2026.03) 중 최초 TOP100 진입월 (1월 제외, 재진입 미카운트)<br>
3개월 생존: 진입월 + 3개월 시점에 TOP100 잔류 여부<br>
매출: 연도별 환율(22:1,292 / 23:1,307 / 24:1,364 / 25:1,422 / 26:1,409) + 센서타워 100% 보정(÷0.7) 적용
</p>'''

new_head = '''<div class="ng-panel active" id="ng-kr">
<div class="ct" style="max-width:1280px;margin:0 auto;padding:0 10px;">

<!-- 헤드라인 (tab-country-deep.headline.kr 스타일) -->
<div style="background:linear-gradient(135deg, #1e40af, #3b82f6);color:#fff;border-radius:14px;padding:24px 28px;margin-bottom:18px;box-shadow:0 4px 16px rgba(0,0,0,0.1);">
  <h2 style="font-size:1.15rem;font-weight:800;margin-bottom:8px;letter-spacing:-0.3px;line-height:1.4;color:#fff;">🇰🇷 KR 시장 — 신규 진입 &amp; 3개월 생존 분석</h2>
  <p style="font-size:0.82rem;color:rgba(255,255,255,0.95);line-height:1.7;margin:0;">
    매출 TOP100 신규 진입 <strong>월평균 8.5개(&apos;22) → 6.9개(&apos;25) -18% 감소</strong> · RPG 비중 60~64% 유지 · 생존율 22~24년 <strong>45~49% 안정</strong> → 25년 <strong>36.8% 급락</strong> (중화권 RPG 57→30% 하락이 주 원인)
  </p>
</div>

<!-- 분석 기준 박스 -->
<div style="padding:14px 20px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;font-size:0.75rem;color:#475569;line-height:1.7;margin-bottom:24px;">
  <div><strong style="color:#0f172a;">📊 분석 기준</strong> · KR 시장 매출 TOP100 (in_revenue_top100_unified_os=TRUE, iOS+Android 합산) · 2022.1 ~ 2026.3</div>
  <div><strong style="color:#0f172a;">📌 신규 진입 정의</strong> · 전체 기간 중 최초 TOP100 진입월 (1월 제외, 재진입 미카운트)</div>
  <div><strong style="color:#0f172a;">🎯 3개월 생존</strong> · 진입월 + 3개월 시점에 TOP100 잔류 여부 · 25년까지 집계</div>
  <div><strong style="color:#0f172a;">💱 환율</strong> · 22=1,292 / 23=1,307 / 24=1,364 / 25=1,422 / 26=1,409 원/USD · 센서타워 100% 보정(÷0.7)</div>
</div>'''

c = c.replace(old_head, new_head)

# ========== 2. section 3개를 step 스타일로 래핑 변환 ==========
# <div class="section"> ... <h2>1. ... </h2> → <div class="step"><div class="step-head"><div class="step-num">1</div>...
# 각 section을 step으로 변환

# Part 1: 신규 진입 물량
c = c.replace(
    '<div class="section">\n<h2>1. 신규 진입 물량</h2>\n<p class="desc">연도별 순수 신규 진입 수 (재진입 제외)</p>',
    '''<div class="step">
<div class="step-head">
<div class="step-num">1</div>
<div class="step-info">
<div class="step-q">신규 진입 물량</div>
<div class="step-a">연도별 순수 신규 진입 수 (재진입 제외) · 월평균 <span class="dn">8.5 → 6.9개 (-18%)</span> 매년 감소 · RPG 비중 60~64% 유지</div>
</div>
</div>
<div class="step-body">'''
)

# Part 2: 3개월 생존율
c = c.replace(
    '<div class="section">\n<h2>2. 신규진입 3개월 생존율</h2>\n<p class="desc">신규 진입 후 3개월 시점에 TOP100 잔류 비율</p>',
    '''<div class="step">
<div class="step-head">
<div class="step-num">2</div>
<div class="step-info">
<div class="step-q">신규진입 3개월 생존율</div>
<div class="step-a">신규 진입 후 3개월 시점에 TOP100 잔류 비율 · 22~24년 <span class="up">45~49% 안정</span> → 25년 <span class="dn">36.8% 급락 (△-11.4%p)</span></div>
</div>
</div>
<div class="step-body">'''
)

# Part 3: 25년 전후 요약
c = c.replace(
    '<div class="section">\n<h2>3. 25년 전후 요약 — 물량 vs 성적</h2>',
    '''<div class="step">
<div class="step-head">
<div class="step-num">3</div>
<div class="step-info">
<div class="step-q">25년 전후 종합 요약 — 물량 vs 성적</div>
<div class="step-a">KR <strong>물량 감소, 성적 유지</strong> · 중화권 <strong>물량 감소 + 성적 하락</strong> (RPG 원인) · 기타 <strong>물량 증가, 성적 최하</strong></div>
</div>
</div>
<div class="step-body">'''
)

# ========== 3. </div> 닫는 부분 정리 ==========
# 마지막 </div> 추가 (ct container close)
# <div class="ng-panel"...id="ng-jp"> 직전에 </div> 추가 필요
c = c.replace(
    '<p class="note" style="text-align:center; margin-top:24px;">분석 기준일: 2026-04-20 | 데이터: Sensor Tower via AI_mobilegame DB (dw_app_monthly)</p>',
    '''<p class="note" style="text-align:center; margin-top:24px;color:#94a3b8;font-size:0.7rem;">분석 기준일: 2026-04-20 | 데이터: Sensor Tower via AI_mobilegame DB (dw_app_monthly)</p>

</div><!-- /.ct -->'''
)

# ========== 4. summary-box를 ins 스타일로 변환 ==========
c = re.sub(
    r'<div class="summary-box"([^>]*)>',
    r'<div class="ins"\1 style="background:#eff6ff;border-left:3px solid #3b82f6;padding:12px 14px;border-radius:0 6px 6px 0;margin:16px 0;font-size:0.85rem;line-height:1.7;">',
    c
)

# ========== 5. .note 를 formula-box 스타일로 ==========
# 각 section 마지막 .note를 포함하기 어려우니, 원본 .note 유지하되 폰트 크기만 조정
c = c.replace(
    '<p class="note">',
    '<p class="note" style="font-size:0.72rem;color:#64748b;margin-top:10px;padding:8px 12px;background:#f8fafc;border-left:3px solid #cbd5e1;border-radius:4px;">'
)

# ========== 6. h3를 탭 스타일로 (sub-heading) ==========
c = re.sub(
    r'<h3>(.*?)</h3>',
    r'<h4 style="font-size:0.9rem;font-weight:700;color:#0f172a;margin:20px 0 10px;padding:6px 10px;background:#f1f5f9;border-left:3px solid #0085ca;border-radius:3px;">\1</h4>',
    c
)

# ========== 7. CSS: ct 클래스 스타일 보강 ==========
# tab-country-deep 의 .step 스타일이 이미 ng 쪽에 적용되는지 확인 후 필요시 추가
# 현재 <style>에 .tab-country-deep .step 만 있으니 글로벌에 복제 추가
extra_css = '''

/* ===== Restyle patch: newgame KR 패널을 country-deep 스타일로 ===== */
.ng-panel .ct { padding: 0 10px; }
.ng-panel .step { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:22px 26px; margin-bottom:20px; box-shadow:0 2px 8px rgba(0,0,0,0.03); }
.ng-panel .step-head { display:flex; align-items:flex-start; gap:12px; margin-bottom:16px; }
.ng-panel .step-num { width:32px; height:32px; border-radius:8px; color:#fff; font-size:0.9rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; background:#3b82f6; }
.ng-panel .step-info { flex:1; }
.ng-panel .step-q { font-size:0.95rem; font-weight:700; color:#0f172a; }
.ng-panel .step-a { font-size:0.78rem; color:#475569; margin-top:4px; line-height:1.6; }
.ng-panel .step-a strong { color:#0f172a; }
.ng-panel .step-a .up { color:#059669; font-weight:700; }
.ng-panel .step-a .dn { color:#dc2626; font-weight:700; }
.ng-panel .step-body { }
.ng-panel .step-body table { width:100%; border-collapse:collapse; font-size:0.8rem; margin:10px 0; }
.ng-panel .step-body th { background:#f1f5f9; font-weight:700; color:#475569; padding:8px 10px; text-align:left; border-bottom:2px solid #e2e8f0; font-size:0.74rem; }
.ng-panel .step-body td { padding:7px 10px; border-bottom:1px solid #f1f5f9; color:#1e293b; vertical-align:top; }
.ng-panel .step-body th.num, .ng-panel .step-body td.num { text-align:right; font-variant-numeric:tabular-nums; }
.ng-panel .step-body tr.tot td { background:#f8fafc; font-weight:700; border-top:2px solid #cbd5e1; }
.ng-panel .ins { background:#f0f9ff; border-left:3px solid #0085ca; padding:12px 14px; border-radius:0 6px 6px 0; margin:14px 0 0; font-size:0.82rem; line-height:1.7; color:#1e293b; }
.ng-panel .ins strong { color:#0f172a; }
.ng-panel details { margin:10px 0; }
.ng-panel details summary { cursor:pointer; padding:8px 10px; background:#f8fafc; border-radius:4px; font-size:0.82rem; font-weight:600; color:#475569; }
.ng-panel details summary:hover { background:#f1f5f9; color:#0f172a; }
.ng-panel .highlight { background:#fef3c7 !important; }
.ng-panel .col26 { background:#fef3c7 !important; color:#78350f !important; }
.ng-panel .down { color:#dc2626; font-weight:600; }
.ng-panel .up { color:#059669; font-weight:600; }
.ng-panel .neutral { color:#64748b; }
.ng-panel .cell-split { line-height:1.2; }
.ng-panel .cell-split .pct { font-size:0.9rem; font-weight:600; }
.ng-panel .cell-split .sub { font-size:0.7rem; color:#94a3b8; }
.ng-panel .game-list { font-size:0.78rem; margin:4px 0 12px 16px; line-height:1.8; }
.ng-panel hr.divider { display:none; }
'''

# <style> 태그 맨 끝에 추가
c = c.replace('</style>', extra_css + '</style>', 1)

with open('reports/newgame_tab_standalone.html','w',encoding='utf-8') as f:
    f.write(c)

print(f'재스타일 완료: {len(c):,} bytes')
