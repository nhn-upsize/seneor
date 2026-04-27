#!/usr/bin/env python3
"""Count div opens/closes in HTML."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import re
path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html'
html = open(path, encoding='utf-8').read()
print(f'size={len(html):,}')
o, c = html.count('<div'), html.count('</div>')
print(f'open={o} close={c} diff={o-c}')
# list tabs
tabs = re.findall(r'<div id="(tab-[^"]+)"', html)
print(f'tab divs: {tabs}')
btns = re.findall(r'data-tab="(tab-[^"]+)"', html)
print(f'tab buttons: {btns}')
