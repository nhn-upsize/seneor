#!/usr/bin/env python3
"""섹션 이동 - v3: 정확한 개별 위치"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'

def find_step_containing(html, title):
    """title을 포함하는 <div class="step">의 정확한 시작과 끝 반환"""
    title_pos = html.find(title)
    if title_pos < 0:
        return None, None

    # title 바로 앞에서 <div class="step"> 찾기
    # 단, title보다 더 가까운 <div class="step">을 찾기 위해 역방향
    div_start = html.rfind('<div class="step">', 0, title_pos)

    # 해당 step의 </div>를 depth tracking으로 찾기
    depth = 1  # <div class="step">이 이미 열린 상태
    pos = div_start + len('<div class="step">')
    for m in re.finditer(r'<div[\s>]|</div>', html[pos:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                return div_start, pos + m.end()
        else:
            depth += 1

    return None, None


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 섹션 3개 각각 찾기
    # 중요: 각각 찾되, find/rfind가 안 겹치도록 주의

    # 순위별 규모 섹션
    s1_title_pos = html.find('국가별 매출 순위별 월평균 규모')
    s1_start = html.rfind('<div class="step">', 0, s1_title_pos)
    # s1 끝 찾기
    depth = 1
    pos = s1_start + len('<div class="step">')
    s1_end = None
    for m in re.finditer(r'<div[\s>]|</div>', html[pos:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                s1_end = pos + m.end()
                break
        else:
            depth += 1

    # 집중도 섹션
    s2_title_pos = html.find('매출 집중도 분석')
    s2_start = html.rfind('<div class="step">', 0, s2_title_pos)
    depth = 1
    pos = s2_start + len('<div class="step">')
    s2_end = None
    for m in re.finditer(r'<div[\s>]|</div>', html[pos:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                s2_end = pos + m.end()
                break
        else:
            depth += 1

    # 중화권 비중
    s3_title_pos = html.find('3국 중화권 퍼블리셔 매출 비중 추이')
    s3_start = html.rfind('<div class="step">', 0, s3_title_pos)
    depth = 1
    pos = s3_start + len('<div class="step">')
    s3_end = None
    for m in re.finditer(r'<div[\s>]|</div>', html[pos:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                s3_end = pos + m.end()
                break
        else:
            depth += 1

    print(f's1(순위별 규모): {s1_start} ~ {s1_end}')
    print(f's2(집중도):      {s2_start} ~ {s2_end}')
    print(f's3(중화권 비중): {s3_start} ~ {s3_end}')

    # 위치 확인: s1과 s2가 다른 위치인지
    if s1_start == s2_start:
        print('ERROR: s1 and s2 overlap!')
        return

    sec1_html = html[s1_start:s1_end]
    sec2_html = html[s2_start:s2_end]
    sec3_html = html[s3_start:s3_end]

    print(f'Sizes: s1={len(sec1_html)}, s2={len(sec2_html)}, s3={len(sec3_html)}')

    # 뒤에서부터 제거 (위치 보존)
    positions = sorted([
        (s1_start, s1_end, 'sec1', sec1_html),
        (s2_start, s2_end, 'sec2', sec2_html),
        (s3_start, s3_end, 'sec3', sec3_html),
    ], key=lambda x: -x[0])

    for start, end, name, content in positions:
        html = html[:start] + html[end:]
        print(f'Removed {name}: {start}~{end}')

    d1 = html.count('<div')
    c1 = html.count('</div>')
    print(f'After removal: div {d1}/{c1} diff={d1-c1}')

    # 이제 ALL 패널 끝에 삽입
    all_start = html.find('<div class="ctab-panel active" id="all">')
    if all_start < 0:
        all_start = html.find('id="all"')
        all_start = html.rfind('<div', 0, all_start)

    # ALL 패널 끝 찾기
    depth = 1
    pos = all_start + 1
    # <div id=... 태그 닫기
    tag_end = html.find('>', pos) + 1
    pos = tag_end
    panel_end = None
    for m in re.finditer(r'<div[\s>]|</div>', html[pos:]):
        if m.group().startswith('</'):
            depth -= 1
            if depth == 0:
                panel_end = pos + m.end()
                break
        else:
            depth += 1

    # 닫는 </div> 직전 위치
    insert_pos = panel_end - len('</div>')

    print(f'\nALL panel: {all_start} ~ {panel_end}')
    print(f'Insert at: {insert_pos}')

    # 순서: 중화권 비중 → 순위별 규모 → 집중도 (위→아래)
    insert_content = '\n' + sec3_html + '\n' + sec1_html + '\n' + sec2_html + '\n'
    html = html[:insert_pos] + insert_content + html[insert_pos:]

    d = html.count('<div')
    c = html.count('</div>')
    print(f'\nFinal: div {d}/{c} diff={d-c}')

    if d == c:
        with open(HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        print('Saved!')
    else:
        print('ERROR: div imbalance - NOT saving')


if __name__ == '__main__':
    main()
