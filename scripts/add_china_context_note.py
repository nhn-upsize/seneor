# -*- coding: utf-8 -*-
"""중화권 섹션 상단에 '분석 배경' 주석 박스 추가"""
import os

path = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
with open(path, 'r', encoding='utf-8') as f: h = f.read()
o = h.count('<div'); oc = h.count('</div>')

if '📌 분석 배경' in h:
    print("이미 추가됨, 스킵")
else:
    anchor = '3국 중화권 퍼블리셔 매출 흐름'
    idx = h.find(anchor)
    if idx == -1:
        raise RuntimeError('앵커 못찾음')
    # step-body 시작 직후에 삽입
    step_body_start = h.find('<div class="step-body">', idx)
    insert_pos = step_body_start + len('<div class="step-body">')

    note_box = '''
      <!-- 분석 배경 주석 -->
      <div style="margin:8px 0 14px;padding:12px 16px;background:#fef3c7;border-left:4px solid #d97706;border-radius:4px;">
        <div style="font-size:0.82rem;font-weight:700;color:#78350f;margin-bottom:6px;">📌 분석 배경</div>
        <div style="font-size:0.76rem;color:#475569;line-height:1.7;">
          3국(KR·JP·US) 각각의 시장을 개별로 살펴봤을 때 <strong>중화권 퍼블리셔의 영향력이 공통적으로 크게 나타나는 패턴</strong>을 확인.
          이 섹션에서는 <strong>3국 전반에서 중화권이 얼마나(매출 절대값), 어떤 비중으로(점유율)</strong>
          성장하고 있는지 통합 비교하여 <strong>중화권 영향력의 규모와 확산 속도</strong>를 조망함.
        </div>
      </div>'''
    h = h[:insert_pos] + note_box + h[insert_pos:]
    n = h.count('<div'); nc = h.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h)
    print(f"<div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
