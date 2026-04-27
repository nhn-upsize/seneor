# -*- coding: utf-8 -*-
"""
웹보드 수정 리스트:
1. Step 7 (웹보드 게임 수명 분석) 제거
2. Step 6 (순위별 월평균 매출 규모) 제거
3. Step 5 고스톱 맞대결: 한게임 섯다&맞고 → 한게임 신맞고
"""
import os, re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

# 한게임 신맞고 최신 데이터 (DB 조회 결과)
SINMATGO_26Q = 11  # 10.5 → 11로 반올림
SINMATGO_PAID = 45.0
SINMATGO_AGE = 44.0
SINMATGO_F = 48
SINMATGO_M = 52
SINMATGO_GROWTH = 3

# 피망 뉴맞고 수치 (기존 유지, 재검증 필요하면 별도)
PIMANG_26Q = 11  # 최신 쿼리에서 11.3억

def find_div_end(text, start):
    """<div class="step">...</div> 매칭 종료 찾기 (깊이 카운팅)"""
    depth = 0
    div_re = re.compile(r'<div\b|</div>')
    for m in div_re.finditer(text, start):
        if m.group() == '</div>':
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    raise RuntimeError("matching </div> not found")

def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # ========================================================
    # 1) Step 7 제거 (웹보드 게임 수명 분석)
    # ========================================================
    s7_q = wb.find('<div class="step-q">웹보드 게임 수명 분석')
    if s7_q != -1:
        s7_start = wb.rfind('<div class="step">', 0, s7_q)
        # 주석도 같이 잡기
        comment_anchor = wb.rfind('<!-- Step 7', 0, s7_start)
        if comment_anchor == -1:
            comment_anchor = wb.rfind('<!--', 0, s7_start)
            # 주석이 step 바로 앞이 아니면 사용 안 함
            if wb[comment_anchor:s7_start].count('\n') > 3:
                comment_anchor = s7_start
        s7_end = find_div_end(wb, s7_start)
        # 뒤 공백도
        while s7_end < len(wb) and wb[s7_end] in ' \n\t':
            s7_end += 1
        start_cut = comment_anchor if comment_anchor < s7_start else s7_start
        removed = wb[start_cut:s7_end]
        print(f"  [Step 7 제거] {s7_end-start_cut}자 · <div>={removed.count('<div')}/{removed.count('</div>')}")
        wb = wb[:start_cut] + wb[s7_end:]

    # ========================================================
    # 2) Step 6 제거 (순위별 월평균 매출 규모)
    # ========================================================
    s6_q = wb.find('<div class="step-q">웹보드 순위별 월평균 매출 규모')
    if s6_q != -1:
        s6_start = wb.rfind('<div class="step">', 0, s6_q)
        comment_anchor = wb.rfind('<!-- Step 6', 0, s6_start)
        if comment_anchor == -1 or wb[comment_anchor:s6_start].count('\n') > 3:
            comment_anchor = s6_start
        s6_end = find_div_end(wb, s6_start)
        while s6_end < len(wb) and wb[s6_end] in ' \n\t':
            s6_end += 1
        start_cut = comment_anchor
        removed = wb[start_cut:s6_end]
        print(f"  [Step 6 제거] {s6_end-start_cut}자 · <div>={removed.count('<div')}/{removed.count('</div>')}")
        wb = wb[:start_cut] + wb[s6_end:]

    # ========================================================
    # 3) Step 5 고스톱 맞대결: 한게임 섯다&맞고 → 한게임 신맞고
    # ========================================================
    # NHN 카드 (compare-box nhn)
    old_nhn = (r'<div class="compare-title nhn">🔵 한게임 섯다&맞고 \(NHN\)</div>.*?'
               r'<div class="compare-stat" style="border:0;"><span>성장률 \(25년 전후\)</span>'
               r'<strong style="color:#059669;">\+44%</strong></div>')
    new_nhn = (f'<div class="compare-title nhn">🔵 한게임 신맞고 (NHN)</div>\n'
               f'        <div class="compare-stat"><span>26.1Q 월평균 매출</span>'
               f'<strong style="color:#059669;">{SINMATGO_26Q}억원</strong></div>\n'
               f'        <div class="compare-stat"><span>광고유입률</span>'
               f'<strong>{SINMATGO_PAID:.1f}%</strong></div>\n'
               f'        <div class="compare-stat"><span>평균 연령</span>'
               f'<strong>{SINMATGO_AGE:.1f}세</strong></div>\n'
               f'        <div class="compare-stat"><span>남/녀 비중</span>'
               f'<strong>M {SINMATGO_M} / F {SINMATGO_F}</strong></div>\n'
               f'        <div class="compare-stat" style="border:0;"><span>성장률 (25년 전후)</span>'
               f'<strong>+{SINMATGO_GROWTH}%</strong></div>')
    wb = re.sub(old_nhn, new_nhn, wb, count=1, flags=re.DOTALL)

    # Step 5 .ins (고스톱 관련 문구 업데이트)
    old_ins = (r'<div class="ins"><strong>핵심:</strong> 포커는 <strong class="nhn">NHN 44억 vs 네오위즈 19억</strong>으로 NHN이 <strong>2\.3배</strong>\. '
               r'고스톱은 <strong class="nhn">NHN 37억 vs 네오위즈 9억</strong>으로 <strong>4\.1배</strong> 격차\. '
               r'NHN은 광고 적극 활용\(24~38%\)으로 공격적 마케팅, 네오위즈는 오가닉 의존\(8~11%\) 안정 유지\. '
               r'<strong>한게임 섯다&맞고 34세 vs 피망 뉴맞고 42세 — 유저 연령 8세 차이</strong>로 NHN이 상대적으로 젊은 유저 확보\.</div>')
    new_ins = ('<div class="ins"><strong>핵심:</strong> 포커는 <strong class="nhn">NHN 44억 vs 네오위즈 19억</strong>으로 NHN이 <strong>2.3배</strong>. '
               f'고스톱(대장 대 대장) 비교에서는 <strong class="nhn">한게임 신맞고 {SINMATGO_26Q}억 vs 피망 뉴맞고 {PIMANG_26Q}억</strong>으로 대등한 경쟁 구도. '
               f'한게임 신맞고는 광고 유입률 <strong>{SINMATGO_PAID:.0f}%</strong>로 적극 마케팅(피망 8%의 5배), 평균연령 {SINMATGO_AGE:.0f}세로 피망 뉴맞고(42세)와 비슷한 중장년층 타겟. '
               '성별 비중도 M52/F48로 피망과 유사(M50/F50).</div>')
    wb = re.sub(old_ins, new_ins, wb, count=1, flags=re.DOTALL)

    # ========================================================
    # 4) WPL(윈조이 포커) → WPL(윈조이 포커 리그)
    # ========================================================
    wb = wb.replace('WPL (윈조이 포커)', 'WPL (윈조이 포커 리그)')
    wb = wb.replace('WPL(윈조이 포커)', 'WPL (윈조이 포커 리그)')

    if is_main:
        return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_list1'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    print(f"\n[{os.path.basename(path)}]")
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"  <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
