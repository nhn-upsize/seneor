# -*- coding: utf-8 -*-
"""Step 5 NHN vs 네오위즈 맞짱 1:1 비교 값 전체 최신화 (26.1Q DB 실측)"""
import os, re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

# DB 실측 26.1Q 값
STATS = {
    '한게임 포커':   {'rev':44, 'paid':32.1, 'age':37.0, 'm':78, 'f':22},
    'Pmang Poker':   {'rev':19, 'paid':20.6, 'age':38.0, 'm':77, 'f':23},
    '한게임 신맞고': {'rev':10, 'paid':45.1, 'age':44.0, 'm':52, 'f':48},
    '피망 뉴맞고':   {'rev':11, 'paid': 9.3, 'age':43.0, 'm':49, 'f':51},
}

# 포커 맞대결 — 한게임 포커 카드 (기존 44억/24.7%/37.6세/M80F20)
def build_poker_nhn():
    s = STATS['한게임 포커']
    return f'''<div class="compare-title nhn">🔵 한게임 포커 (NHN)</div>
        <div class="compare-stat"><span>26.1Q 월평균 매출</span><strong style="color:#059669;">{s["rev"]}억원</strong></div>
        <div class="compare-stat"><span>광고유입률</span><strong>{s["paid"]:.1f}%</strong></div>
        <div class="compare-stat"><span>평균 연령</span><strong>{s["age"]:.1f}세</strong></div>
        <div class="compare-stat"><span>남/녀 비중</span><strong>M {s["m"]} / F {s["f"]}</strong></div>
        <div class="compare-stat" style="border:0;"><span>TOP100 체류</span><strong style="color:#0085ca;">51개월 (전기간)</strong></div>'''

def build_poker_neo():
    s = STATS['Pmang Poker']
    return f'''<div class="compare-title neowiz">🟠 Pmang Poker (네오위즈)</div>
        <div class="compare-stat"><span>26.1Q 월평균 매출</span><strong style="color:#dc2626;">{s["rev"]}억원</strong></div>
        <div class="compare-stat"><span>광고유입률</span><strong>{s["paid"]:.1f}%</strong></div>
        <div class="compare-stat"><span>평균 연령</span><strong>{s["age"]:.1f}세</strong></div>
        <div class="compare-stat"><span>남/녀 비중</span><strong>M {s["m"]} / F {s["f"]}</strong></div>
        <div class="compare-stat" style="border:0;"><span>TOP100 체류</span><strong>51개월 (전기간)</strong></div>'''

def build_gostop_nhn():
    s = STATS['한게임 신맞고']
    return f'''<div class="compare-title nhn">🔵 한게임 신맞고 (NHN)</div>
        <div class="compare-stat"><span>26.1Q 월평균 매출</span><strong style="color:#059669;">{s["rev"]}억원</strong></div>
        <div class="compare-stat"><span>광고유입률</span><strong>{s["paid"]:.1f}%</strong></div>
        <div class="compare-stat"><span>평균 연령</span><strong>{s["age"]:.1f}세</strong></div>
        <div class="compare-stat"><span>남/녀 비중</span><strong>M {s["m"]} / F {s["f"]}</strong></div>
        <div class="compare-stat" style="border:0;"><span>성장률 (25년 전후)</span><strong>+3%</strong></div>'''

def build_gostop_neo():
    s = STATS['피망 뉴맞고']
    return f'''<div class="compare-title neowiz">🟠 피망 뉴맞고 (네오위즈)</div>
        <div class="compare-stat"><span>26.1Q 월평균 매출</span><strong style="color:#dc2626;">{s["rev"]}억원</strong></div>
        <div class="compare-stat"><span>광고유입률</span><strong>{s["paid"]:.1f}%</strong></div>
        <div class="compare-stat"><span>평균 연령</span><strong>{s["age"]:.1f}세</strong></div>
        <div class="compare-stat"><span>남/녀 비중</span><strong>M {s["m"]} / F {s["f"]}</strong></div>
        <div class="compare-stat" style="border:0;"><span>성장률 (25년 전후)</span><strong style="color:#dc2626;">-5%</strong></div>'''

poker_nhn = build_poker_nhn()
poker_neo = build_poker_neo()
gostop_nhn = build_gostop_nhn()
gostop_neo = build_gostop_neo()

# Step 5 .ins 업데이트
new_ins = ('<div class="ins"><strong>핵심:</strong> '
           f'포커는 <strong class="nhn">NHN {STATS["한게임 포커"]["rev"]}억 vs 네오위즈 {STATS["Pmang Poker"]["rev"]}억</strong>으로 NHN이 <strong>{STATS["한게임 포커"]["rev"]/STATS["Pmang Poker"]["rev"]:.1f}배</strong>. '
           f'고스톱(대장 대 대장)은 <strong class="nhn">한게임 신맞고 {STATS["한게임 신맞고"]["rev"]}억 vs 피망 뉴맞고 {STATS["피망 뉴맞고"]["rev"]}억</strong>으로 대등한 경쟁 구도. '
           f'<strong>광고 유입률: NHN 포커 {STATS["한게임 포커"]["paid"]:.0f}% · 신맞고 {STATS["한게임 신맞고"]["paid"]:.0f}%</strong>로 NHN이 공격적 마케팅, 피망은 '
           f'오가닉 의존({STATS["Pmang Poker"]["paid"]:.0f}% / {STATS["피망 뉴맞고"]["paid"]:.0f}%)으로 안정 유지. '
           f'연령대: 포커는 NHN 37세 vs 피망 38세 (유사), 고스톱은 NHN 44세 vs 피망 43세 (유사).</div>')

# step-a 업데이트
new_step_a = '<div class="step-a">포커: NHN 44억 vs 네오위즈 19억 (2.3배) · 고스톱: 신맞고 10억 vs 뉴맞고 11억 (대등) · NHN 광고 적극 활용</div>'

def patch(html, is_main=True):
    if is_main:
        ws = html.find('<div id="tab-webboard"')
        we = html.find('<!-- ===== JavaScript', ws)
        if we == -1: we = html.find('<script>', ws)
        wb = html[ws:we]
    else:
        wb = html

    # compare-box 내부 컨텐츠를 깊이 카운팅으로 치환
    def replace_box_content(text, anchor_title, new_content):
        idx = text.find(anchor_title)
        if idx == -1: return text
        # anchor_title은 <div class="compare-title ...">🔵 ... (NHN)</div> 로 시작
        # 그 이전의 <div class="compare-box xxx"> 를 찾음
        box_start = text.rfind('<div class="compare-box ', 0, idx)
        # depth 카운팅으로 compare-box 끝 찾기
        depth = 0; i = box_start
        div_re = re.compile(r'<div\b|</div>')
        box_end = None
        for mm in div_re.finditer(text, i):
            if mm.group() == '</div>':
                depth -= 1
                if depth == 0: box_end = mm.end(); break
            else: depth += 1
        if not box_end: return text
        # compare-box 열기 태그는 유지, 내부만 교체
        open_end = text.find('>', box_start) + 1
        # box_end 직전의 </div>를 유지
        new_box = text[box_start:open_end] + '\n        ' + new_content + '\n      </div>'
        return text[:box_start] + new_box + text[box_end:]

    wb = replace_box_content(wb, '🔵 한게임 포커 (NHN)</div>', poker_nhn)
    wb = replace_box_content(wb, '🟠 Pmang Poker (네오위즈)</div>', poker_neo)
    wb = replace_box_content(wb, '🔵 한게임 신맞고 (NHN)</div>', gostop_nhn)
    wb = replace_box_content(wb, '🟠 피망 뉴맞고 (네오위즈)</div>', gostop_neo)

    # Step 5 .ins 교체 (핵심: 포커로 시작)
    wb = re.sub(
        r'<div class="ins"><strong>핵심:</strong> 포커는 <strong class="nhn">NHN.*?</div>',
        new_ins, wb, count=1, flags=re.DOTALL
    )
    # Step 5 step-a
    wb = re.sub(
        r'(<div class="step-q">NHN vs 네오위즈 맞짱 1:1 비교</div>\s*\n?\s*)<div class="step-a">.*?</div>',
        r'\1' + new_step_a, wb, count=1, flags=re.DOTALL
    )

    if is_main: return html[:ws] + wb + html[we:]
    return wb

for path in [MAIN, WB]:
    is_main = (path == MAIN)
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    bk = path + '.bak.before_step5_refresh'
    if not os.path.exists(bk):
        with open(bk, 'w', encoding='utf-8') as f: f.write(h)
    o = h.count('<div'); oc = h.count('</div>')
    h = patch(h, is_main)
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
