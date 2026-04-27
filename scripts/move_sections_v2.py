#!/usr/bin/env python3
"""섹션 이동 - 정확한 위치 계산"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'

def find_step_by_title(html, title, start_from=0):
    """제목으로 step div 찾기. (div_start, div_end) 반환"""
    title_pos = html.find(title, start_from)
    if title_pos < 0:
        return None, None

    # title 앞에서 <div class="step"> 찾기 (가장 가까운)
    div_start = html.rfind('<div class="step">', 0, title_pos)

    # div depth 추적
    depth = 0
    end = div_start
    for m in re.finditer(r'<div[\s>]|</div>', html[div_start:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                end = div_start + m.end()
                break
        else:
            depth += 1

    return div_start, end


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # ====== 1. 각 섹션 추출 (개별적으로 정확한 위치) ======

    # 섹션 1: 순위별 규모 (KR 패널에 있음)
    sec1_start, sec1_end = find_step_by_title(html, '국가별 매출 순위별 월평균 규모')
    sec1_html = html[sec1_start:sec1_end]
    print(f'[sec1] 순위별 규모: {sec1_start}~{sec1_end}, {len(sec1_html)} chars')

    # 섹션 2: 80/20 집중도 (KR 패널에 있음)
    sec2_start, sec2_end = find_step_by_title(html, '매출 집중도 분석')
    sec2_html = html[sec2_start:sec2_end]
    print(f'[sec2] 집중도: {sec2_start}~{sec2_end}, {len(sec2_html)} chars')

    # 섹션 3: 중화권 비중 (ALL 패널에 있음)
    sec3_start, sec3_end = find_step_by_title(html, '3국 중화권 퍼블리셔 매출 비중 추이')
    sec3_html = html[sec3_start:sec3_end]
    print(f'[sec3] 중화권 비중: {sec3_start}~{sec3_end}, {len(sec3_html)} chars')

    # ====== 2. 위치 역순 정렬하여 제거 ======
    sections = sorted([
        (sec1_start, sec1_end, 'sec1'),
        (sec2_start, sec2_end, 'sec2'),
        (sec3_start, sec3_end, 'sec3'),
    ], key=lambda x: -x[0])

    for start, end, name in sections:
        # 앞뒤 공백 포함 제거
        # 바로 앞의 \n이나 공백 제거
        actual_start = start
        while actual_start > 0 and html[actual_start-1] in ' \n\t':
            actual_start -= 1
        html = html[:actual_start] + html[end:]
        print(f'  제거: {name} at {actual_start}~{end}')

    # ====== 3. ALL 탭 하단에 순서대로 삽입 ======
    # 삽입 순서 (위에서 아래):
    # 1) 중화권 비중 추이 (이미 ALL 탭 소속이었으므로 자연스러움)
    # 2) 국가별 순위별 규모
    # 3) 80/20 집중도

    # ALL 탭의 마지막 step 뒤 + ctab-panel 닫는 </div> 앞에 삽입
    all_panel_start = html.find('<div class="ctab-panel active" id="all">')
    if all_panel_start < 0:
        all_panel_start = html.find('id="all"')
        all_panel_start = html.rfind('<div', 0, all_panel_start)

    # ALL 패널의 끝 찾기 (depth 추적)
    depth = 0
    panel_end = all_panel_start
    for m in re.finditer(r'<div[\s>]|</div>', html[all_panel_start:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                panel_end = all_panel_start + m.end()
                break
        else:
            depth += 1

    # panel_end는 </div> 포함 끝 위치
    # 닫는 </div> 직전에 삽입
    insert_pos = panel_end - 6  # "</div>" 앞

    print(f'\nALL 패널: {all_panel_start} ~ {panel_end}')
    print(f'삽입 위치: {insert_pos}')

    insert_html = '\n' + sec3_html + '\n' + sec1_html + '\n' + sec2_html + '\n'
    html = html[:insert_pos] + insert_html + html[insert_pos:]
    print(f'삽입 완료: {len(insert_html)} chars')

    # ====== 검증 ======
    d = html.count('<div')
    c = html.count('</div>')
    print(f'\ndiv: {d}/{c} diff={d-c}')

    if d == c:
        with open(HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        print('Saved!')
    else:
        print('ERROR: div imbalance - NOT saving')


if __name__ == '__main__':
    main()
