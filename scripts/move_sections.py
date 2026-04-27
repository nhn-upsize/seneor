#!/usr/bin/env python3
"""섹션 이동 작업"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML_PATH = r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'

def find_section_by_title(html, title, from_pos=0):
    """특정 제목을 가진 step/section div를 찾아 (start, end) 반환"""
    title_pos = html.find(title, from_pos)
    if title_pos < 0:
        return None, None
    # step div 시작 찾기 (가장 가까운 <div class="step"> 또는 <!-- 주석)
    div_starts = []
    for pattern in ['<!-- 매출 순위별', '<!-- 매출 집중도', '<!-- 중화권', '<div class="step">']:
        pos = html.rfind(pattern, 0, title_pos)
        if pos > 0:
            div_starts.append(pos)

    start = max(div_starts) if div_starts else html.rfind('<div class="step">', 0, title_pos)

    # 해당 div 끝 찾기 (depth 추적)
    # 주석이면 그 뒤 <div class="step">부터 시작
    if html[start:start+10].startswith('<!--'):
        div_start = html.find('<div class="step">', start)
    else:
        div_start = start

    # div depth 추적해서 끝 찾기
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

    return start, end

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # ======== 단계 1: 추출 (원본 섹션 내용 저장) ========

    # 섹션 1: 순위별 규모
    s1_start, s1_end = find_section_by_title(html, '국가별 매출 순위별 월평균 규모')
    sec1_html = html[s1_start:s1_end]
    print(f'순위별 규모 섹션: {s1_start} ~ {s1_end} ({len(sec1_html)} chars)')

    # 섹션 2: 80/20 집중도
    s2_start, s2_end = find_section_by_title(html, '매출 집중도 분석')
    sec2_html = html[s2_start:s2_end]
    print(f'집중도 섹션: {s2_start} ~ {s2_end} ({len(sec2_html)} chars)')

    # 섹션 3: 중화권 비중 (ALL 탭)
    s3_start, s3_end = find_section_by_title(html, '3국 중화권 퍼블리셔 매출 비중 추이')
    sec3_html = html[s3_start:s3_end]
    print(f'중화권 비중 섹션: {s3_start} ~ {s3_end} ({len(sec3_html)} chars)')

    # ======== 단계 2: 원본 위치에서 제거 (역순으로) ========
    # 위치가 높은 것부터 제거해야 앞 위치가 안 바뀜
    positions = sorted([
        (s1_start, s1_end, 'sec1'),
        (s2_start, s2_end, 'sec2'),
        (s3_start, s3_end, 'sec3'),
    ], key=lambda x: -x[0])  # 뒤에서부터

    for start, end, name in positions:
        html = html[:start] + html[end:]
        print(f'{name} 제거: {start} ~ {end}')

    # ======== 단계 3: 새 위치에 삽입 ========

    # 3-1. 중화권 비중 (sec3) → ALL 패널 하단 (마지막 step 뒤, 결론 앞)
    # ALL 패널 찾기
    all_start = html.find('<div class="ctab-panel active" id="all">')
    if all_start < 0:
        all_start = html.find('id="all"')
    # ALL 패널 끝 = KR 패널 시작
    kr_start = html.find('id="kr"', all_start + 10)

    # ALL 패널 안에서 마지막 </div> 위치 찾기 (다음 패널 직전)
    # ALL 패널 닫는 </div> 바로 앞에 삽입
    # 다음 <div id="kr" 앞 위치
    all_panel_close = html.rfind('</div>', all_start, kr_start)
    print(f'ALL 패널 끝 (닫는 </div>): {all_panel_close}')

    # 중화권 비중을 ALL 패널 끝 </div> 앞에 삽입
    html = html[:all_panel_close] + '\n' + sec3_html + '\n' + html[all_panel_close:]
    print(f'중화권 비중 → ALL 탭 하단')

    # 3-2. 순위별 규모 + 집중도 → ALL 탭 하단 (중화권 비중 뒤)
    # 이번엔 중화권 비중이 이미 들어갔으므로 위치 재계산
    # ALL 탭 하단을 다시 찾기
    all_start = html.find('id="all"')
    kr_start = html.find('id="kr"', all_start + 10)
    all_panel_close = html.rfind('</div>', all_start, kr_start)

    html = html[:all_panel_close] + '\n' + sec1_html + '\n' + sec2_html + '\n' + html[all_panel_close:]
    print(f'순위별규모 + 집중도 → ALL 탭 하단')

    # ======== 검증 ========
    d = html.count('<div')
    c = html.count('</div>')
    print(f'\ndiv: {d}/{c} diff={d-c}')

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Done!')

if __name__ == '__main__':
    main()
