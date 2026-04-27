# -*- coding: utf-8 -*-
"""백업에서 tab-newgame 섹션만 추출해서 별도 HTML 파일로 저장"""
import re

with open('reports/NHN_market_analysis_bak.html','r',encoding='utf-8') as f:
    content = f.read()

# tab-newgame div 블록 찾기 (depth counting)
lines = content.split('\n')
start_idx = None
for i, ln in enumerate(lines):
    if '<div id="tab-newgame" class="tab-content">' in ln:
        start_idx = i
        break

depth = 0
end_idx = None
for i in range(start_idx, len(lines)):
    ln = lines[i]
    depth += ln.count('<div')
    depth -= ln.count('</div>')
    if depth == 0 and i > start_idx:
        end_idx = i
        break

newgame_html = '\n'.join(lines[start_idx:end_idx+1])
print(f'추출된 라인: {start_idx+1}~{end_idx+1} ({end_idx-start_idx+1}줄)')

# 메인의 <style> 블록도 함께 추출 (클래스 스타일 필요)
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
style_content = style_match.group(1) if style_match else ''

# 독립 HTML 구성
output = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>신규 진입 게임 분석 (KR·JP·US)</title>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable.css" rel="stylesheet">
<style>
body {{ margin:0; padding:0; font-family:'Pretendard Variable', Pretendard, -apple-system, sans-serif; background:#f5f7fa; color:#0f172a; }}
.tab-content {{ display:block !important; }}
{style_content}
</style>
</head>
<body>
{newgame_html}
</body>
</html>
'''

with open('reports/newgame_tab_standalone.html','w',encoding='utf-8') as f:
    f.write(output)

print(f'저장: reports/newgame_tab_standalone.html ({len(output):,} bytes)')
