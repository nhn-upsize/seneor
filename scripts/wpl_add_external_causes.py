# -*- coding: utf-8 -*-
"""WPL 섹션에 25.9월 급증 외부 원인 분석 박스 추가 (5번 제외, 구체수치 출처 표기)"""
import os, re

MAIN = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"
WB = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_webboard_analysis.html"

external_block = '''
    <!-- 25.9월 급증 원인 분석 (외부 확인) -->
    <div style="margin-top:14px;border:2px solid #8b5cf6;border-radius:8px;padding:14px 18px;background:linear-gradient(135deg,#faf5ff,#fdf4ff);">
      <div style="font-size:0.92rem;font-weight:800;color:#6b21a8;margin-bottom:10px;">🎯 25.9월 매출 급증 원인 (외부 확인 + DB 정합 검증)</div>
      <div style="font-size:0.75rem;color:#475569;margin-bottom:10px;line-height:1.6;">DB 단서(Android 버전 TOP 100 신규 진입 + iOS 동시 성장) 외에, Zempot의 <strong>비즈니스·마케팅 전략 전환</strong>이 실질 동인으로 확인됨.</div>
      <ul style="margin:0;padding-left:20px;font-size:0.78rem;color:#1e293b;line-height:1.85;">
        <li>
          <strong style="color:#8b5cf6;">① 대형 오프라인 대회(WPH) 정례화</strong> — 상금 규모 <strong>10억 원대로 대폭 확대<sup style="color:#94a3b8;font-size:0.6rem;">[외부]</sup></strong>, 오프라인 본선 + 온라인 예선 연계 시스템 안착 → 유저 참여 극대화
          <span style="color:#059669;font-size:0.72rem;margin-left:6px;">✓ DB 정합: 25.9월 DL +141% (1,876 → 4,529)</span>
        </li>
        <li>
          <strong style="color:#8b5cf6;">② 고단가 BM 안착</strong> — 오프라인 대회 티켓 + 고액 코인 결합한 <strong>50만원 이상 고단가 패키지<sup style="color:#94a3b8;font-size:0.6rem;">[외부]</sup></strong>가 핵심 매출원으로 정착 → ARPPU 대폭 견인
          <span style="color:#059669;font-size:0.72rem;margin-left:6px;">✓ DB 정합: ARPDL 18만원 → 23만원 (+28%)</span>
        </li>
        <li>
          <strong style="color:#8b5cf6;">③ 스포츠 브랜딩 + 팬덤 마케팅</strong> — <strong>임요환 등 프로 선수 활용 라이브 콘텐츠<sup style="color:#94a3b8;font-size:0.6rem;">[외부]</sup></strong>로 "실력 기반 스포츠" 이미지 강화 → 고과금 유저(Whale) 충성도 확보
          <span style="color:#059669;font-size:0.72rem;margin-left:6px;">✓ DB 정합: 외부 노출 증가 → DL 폭증과 일치</span>
        </li>
        <li>
          <strong style="color:#8b5cf6;">④ 리그 생태계 상설화</strong> — 대형 대회 공백기에 온라인 전용 시리즈 촘촘히 배치 → 유저 이탈 방지 + 매출 하한선(Floor) 상향 평준화
          <span style="color:#059669;font-size:0.72rem;margin-left:6px;">✓ DB 정합: 8월까지 간헐적 → 9월부터 TOP 100 연속 유지</span>
        </li>
      </ul>
      <div style="font-size:0.68rem;color:#94a3b8;margin-top:12px;padding-top:8px;border-top:1px dashed #d8b4fe;line-height:1.5;">
        <strong style="color:#6b21a8;"><sup>[외부]</sup> 출처</strong>: 외부 뉴스·공지·Zempot 공식 채널 검색 기반 요약. Sensor Tower DB에는 마케팅·이벤트 데이터 미포함.<br>
        "실력 기반 스포츠" 포지셔닝 = 국내 웹보드 규제(1회 결제 5만원 한도 등)를 회피하고 프리미엄 타겟 확보 전략으로 해석 가능.
      </div>
    </div>
'''

def patch(h):
    if '25.9월 매출 급증 원인' in h: return h, True
    anchor = '<div class="ins" style="margin-top:12px;">\n      <strong>핵심:</strong> WPL은'
    if anchor not in h: return h, False
    h = h.replace(anchor, external_block.strip() + '\n\n    ' + anchor, 1)
    return h, True

for path in [MAIN, WB]:
    with open(path, 'r', encoding='utf-8') as f: h = f.read()
    o = h.count('<div'); oc = h.count('</div>')
    h2, ok = patch(h)
    if not ok:
        print(f"[{os.path.basename(path)}] 앵커 못찾음 또는 이미 존재")
        continue
    n = h2.count('<div'); nc = h2.count('</div>')
    with open(path, 'w', encoding='utf-8') as f: f.write(h2)
    print(f"[{os.path.basename(path)}] <div> {o}→{n}, </div> {oc}→{nc}  {'✅' if n==nc else '❌'}")
