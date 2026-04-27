# -*- coding: utf-8 -*-
"""KR 신규진입 섹션을 tab-country-deep 스타일로 재구성"""
import re

with open('reports/NHN_market_analysis.html','r',encoding='utf-8') as f:
    main = f.read()

# KR 패널 내용 찾기: <div class="ng-panel active" id="ng-kr"> ~ 다음 </div>
start_marker = '<div class="ng-panel active" id="ng-kr">'
end_marker = '<!-- JP 패널 -->'
start = main.find(start_marker)
end = main.find(end_marker)

# 새 KR 패널 내용
new_kr = '''<div class="ng-panel active" id="ng-kr">
<div class="ct" style="max-width:1280px;margin:0 auto;padding:0 10px;">

  <!-- 헤드라인 (tab-country-deep.headline.kr 스타일 차용) -->
  <div style="background:linear-gradient(135deg, #1e40af, #3b82f6);color:#fff;border-radius:14px;padding:24px 28px;margin-bottom:18px;box-shadow:0 4px 16px rgba(0,0,0,0.1);">
    <h2 style="font-size:1.15rem;font-weight:800;margin-bottom:8px;letter-spacing:-0.3px;line-height:1.4;">🇰🇷 KR 시장 신규 진입 & 3개월 생존 분석</h2>
    <p style="font-size:0.82rem;color:rgba(255,255,255,0.95);line-height:1.7;margin:0;">
      매출 TOP100 신규 진입 <strong>월평균 8.5개('22) → 6.9개('25) -18% 감소</strong> · RPG 비중 60~64% 유지 · 생존율 22~24년 <strong>45~49% 안정</strong> → 25년 <strong>36.8% 급락</strong> (중화권 RPG 57→30% 하락이 주 원인)
    </p>
  </div>

  <!-- 분석 기준 박스 -->
  <div style="padding:14px 20px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;font-size:0.75rem;color:#475569;line-height:1.7;margin-bottom:24px;">
    <div><strong style="color:#0f172a;">📊 분석 기준</strong> · KR 시장 매출 TOP100 (in_revenue_top100_unified_os=TRUE, iOS+Android 합산) · 2022.1 ~ 2026.3</div>
    <div><strong style="color:#0f172a;">📌 신규 진입 정의</strong> · 전체 기간 중 최초 TOP100 진입월 (1월 제외, 재진입 미카운트) — 22~24년은 연 11개월 · 26년 1Q는 2~3월 2개월</div>
    <div><strong style="color:#0f172a;">🎯 3개월 생존</strong> · 진입월 + 3개월 시점에 TOP100 잔류 여부 · 25년 기준까지 집계 (26년 1Q는 측정 불가)</div>
    <div><strong style="color:#0f172a;">💱 매출 환율</strong> · 22=1,292 / 23=1,307 / 24=1,364 / 25=1,422 / 26=1,409 원/USD · 센서타워 100% 보정(÷0.7) 적용</div>
  </div>

  <!-- Step 1: 신규 진입 물량 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">1</div>
      <div class="step-info">
        <div class="step-q">신규 진입 물량 — 전체 추이</div>
        <div class="step-a">월평균 신규 진입 <span class="dn">8.5 → 6.9개 (-18%)</span> 매년 감소 · RPG 비중 <strong>60~64% 유지</strong> — 특정 장르 문제 아닌 전체 신규 공급 축소</div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>연도</th><th class="num">월평균 진입</th><th class="num">연간 총합</th><th class="num">RPG 비중</th></tr></thead>
        <tbody>
          <tr><td>2022</td><td class="num">8.5</td><td class="num">94</td><td class="num">63.8%</td></tr>
          <tr><td>2023</td><td class="num dn">8.2</td><td class="num">90</td><td class="num">61.1%</td></tr>
          <tr><td>2024</td><td class="num dn">7.5</td><td class="num">83</td><td class="num">63.9%</td></tr>
          <tr><td>2025</td><td class="num dn">6.9</td><td class="num">76</td><td class="num">60.5%</td></tr>
          <tr><td class="col26">26.1Q</td><td class="num col26">6.5</td><td class="num col26">13 (2개월)</td><td class="num col26">61.5%</td></tr>
        </tbody>
      </table>
      <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;">
        <canvas id="chartEntry" width="380" height="220"></canvas>
        <canvas id="chartGenreAbs" width="380" height="220"></canvas>
      </div>
      <div class="ins"><strong>핵심:</strong> 매년 월평균 신규 진입 수 감소 (22년 8.5개 → 25년 6.9개, -18%). RPG 비중은 60~64%로 일정하게 유지되므로 <strong>"RPG가 줄어서 감소한 게 아니라 전체 신작 공급 자체가 축소"</strong>되는 구조적 변화. 시장 포화 + 대작 중심 집중 투자 기조의 결과.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 월평균 진입 = 연간 신규 진입 게임 수 / 11개월 (1월 제외) · 26.1Q = 2개월(2~3월) 집계<br>
        • RPG = Role Playing + 방치형/서브컬처 RPG 통합 · 비RPG = Strategy, Simulation, Casual, Puzzle, Arcade, Adventure 등
      </div>
    </div>
  </div>

  <!-- Step 2: 퍼블국적별 신규 진입 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">2</div>
      <div class="step-info">
        <div class="step-q">퍼블리셔 국적별 신규 진입</div>
        <div class="step-a">KR <span class="dn">3.8→2.0개 (-47%)</span> 지속 감소 · 중화권 <span class="dn">4.1→3.5개</span> 25년부터 하락 · 기타(글로벌) <span class="up">0.5→1.0개 (+100%)</span> 유일 증가</div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>퍼블리셔</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">26.1Q</th><th>추이</th></tr></thead>
        <tbody>
          <tr><td>KR</td><td class="num">3.8<br><span style="color:#94a3b8;font-size:0.65rem;">44.7%</span></td><td class="num dn">3.3<br><span style="color:#94a3b8;font-size:0.65rem;">40.0%</span></td><td class="num dn">2.4<br><span style="color:#94a3b8;font-size:0.65rem;">31.3%</span></td><td class="num up">2.5<br><span style="color:#94a3b8;font-size:0.65rem;">35.5%</span></td><td class="num col26 dn">2.0<br><span style="color:#94a3b8;font-size:0.65rem;">30.8%</span></td><td class="dn">지속 감소 -47%</td></tr>
          <tr><td>중화권</td><td class="num">3.5<br><span style="color:#94a3b8;font-size:0.65rem;">40.4%</span></td><td class="num up">4.2<br><span style="color:#94a3b8;font-size:0.65rem;">51.1%</span></td><td class="num dn">4.1<br><span style="color:#94a3b8;font-size:0.65rem;">54.2%</span></td><td class="num dn">3.0<br><span style="color:#94a3b8;font-size:0.65rem;">43.4%</span></td><td class="num col26 up">3.5<br><span style="color:#94a3b8;font-size:0.65rem;">53.8%</span></td><td>23~24 피크, 25년 하락</td></tr>
          <tr><td>기타 (글로벌)</td><td class="num">0.5<br><span style="color:#94a3b8;font-size:0.65rem;">6.4%</span></td><td class="num">0.5<br><span style="color:#94a3b8;font-size:0.65rem;">5.6%</span></td><td class="num up">0.7<br><span style="color:#94a3b8;font-size:0.65rem;">9.6%</span></td><td class="num up">1.2<br><span style="color:#94a3b8;font-size:0.65rem;">17.1%</span></td><td class="num col26">1.0<br><span style="color:#94a3b8;font-size:0.65rem;">15.4%</span></td><td class="up">유일 증가 (모수작음)</td></tr>
          <tr><td>JP</td><td class="num">0.5</td><td class="num dn">0.2</td><td class="num">0.2</td><td class="num dn">0.1</td><td class="num col26">-</td><td>(모수작음)</td></tr>
          <tr><td>북미</td><td class="num">0.3</td><td class="num dn">0.1</td><td class="num up">0.2</td><td class="num">0.2</td><td class="num col26">-</td><td>(모수작음)</td></tr>
          <tr class="tot"><td>전체</td><td class="num">8.5</td><td class="num">8.2</td><td class="num">7.5</td><td class="num">6.9</td><td class="num col26">6.5</td><td class="dn">감소 -18%</td></tr>
        </tbody>
      </table>
      <div style="margin-top:16px;">
        <canvas id="chartPub12" width="700" height="360" style="max-width:100%;"></canvas>
      </div>
      <div class="ins"><strong>핵심:</strong> <strong>22~24년</strong>: KR이 3.8→2.4로 감소 주도, 중화권은 3.5→4.2→4.1로 오히려 증가/유지.  <strong>25~26.1Q</strong>: 중화권도 3.0으로 하락 합류, KR은 2.5→2.0 지속 감소, <strong>기타(글로벌) 그룹만 0.5→1.0개로 +100% 증가</strong>(모수 작지만 유일한 성장). 26.1Q 중화권 3.5 반등은 2개월 기준 단기 신호.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 퍼블국적 = publisher_country 기준 + NEXON → KR 강제 분류 · FUNFLY → 중화권 강제 분류<br>
        • 점유율 = 해당 국적 진입 수 / 전체 진입 수 × 100 (연간 기준)
      </div>
    </div>
  </div>

  <!-- Step 3: 국적별 장르 구성 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">3</div>
      <div class="step-info">
        <div class="step-q">퍼블국적별 신규 진입 장르 구성 변화</div>
        <div class="step-a">KR: <strong>RPG 외 전 장르 감소</strong> (비RPG 1.3→0.6, -54%) · 중화권: <strong>RPG 감소 + 비RPG 유지/확대</strong>로 다변화 · 기타: 25년부터 장르 다양화</div>
      </div>
    </div>
    <div class="step-body">
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;">
        <canvas id="chartGenreKR" width="320" height="240"></canvas>
        <canvas id="chartGenreCN" width="320" height="240"></canvas>
        <canvas id="chartGenreEtc" width="320" height="240"></canvas>
      </div>

      <details style="margin-top:20px;">
        <summary style="font-size:0.88rem;font-weight:600;color:#3b82f6;cursor:pointer;padding:6px 0;">🇰🇷 KR 퍼블리셔 장르 상세 (월평균)</summary>
        <table style="margin-top:8px;">
          <tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">26.1Q</th></tr>
          <tr><td>RPG</td><td class="num">2.5</td><td class="num">2.2</td><td class="num">1.8</td><td class="num">1.9</td><td class="num col26">2.0</td></tr>
          <tr><td>Strategy</td><td class="num">0.3</td><td class="num">0.2</td><td class="num">0</td><td class="num">0.3</td><td class="num col26">0</td></tr>
          <tr><td>Simulation</td><td class="num">0.4</td><td class="num">0.5</td><td class="num">0.1</td><td class="num">0.1</td><td class="num col26">0</td></tr>
          <tr><td>기타 (Adv·Sports·Action·Casino·Board·Puzzle)</td><td class="num">0.7</td><td class="num">0.5</td><td class="num">0.5</td><td class="num">0.2</td><td class="num col26">0</td></tr>
          <tr class="tot"><td>합계</td><td class="num">3.8</td><td class="num">3.3</td><td class="num">2.4</td><td class="num">2.5</td><td class="num col26">2.0</td></tr>
        </table>
        <div class="ins">RPG 외 전 장르가 감소. 비RPG가 <strong>1.3 → 0.6으로 반감</strong>하며 KR 전체 신작 공급 자체가 축소 중.</div>
      </details>

      <details>
        <summary style="font-size:0.88rem;font-weight:600;color:#ef4444;cursor:pointer;padding:6px 0;">🇨🇳 중화권 퍼블리셔 장르 상세 (월평균)</summary>
        <table style="margin-top:8px;">
          <tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">26.1Q</th></tr>
          <tr><td>RPG</td><td class="num">2.5</td><td class="num">2.6</td><td class="num">2.2</td><td class="num">1.8</td><td class="num col26">2.0</td></tr>
          <tr><td>Strategy</td><td class="num">0.4</td><td class="num">0.9</td><td class="num">0.5</td><td class="num">0.5</td><td class="num col26">0.5</td></tr>
          <tr><td>Casual</td><td class="num">0</td><td class="num">0.3</td><td class="num">0.3</td><td class="num">0.3</td><td class="num col26">0</td></tr>
          <tr><td>Action</td><td class="num">0.2</td><td class="num">0</td><td class="num">0.5</td><td class="num">0.2</td><td class="num col26">0</td></tr>
          <tr><td>Simulation</td><td class="num">0.2</td><td class="num">0.2</td><td class="num">0.1</td><td class="num">0</td><td class="num col26">0.5</td></tr>
          <tr><td>Puzzle</td><td class="num">0</td><td class="num">0.1</td><td class="num">0.2</td><td class="num">0.1</td><td class="num col26">0.5</td></tr>
          <tr><td>기타</td><td class="num">0.2</td><td class="num">0.1</td><td class="num">0.3</td><td class="num">0.2</td><td class="num col26">0</td></tr>
          <tr class="tot"><td>합계</td><td class="num">3.5</td><td class="num">4.2</td><td class="num">4.1</td><td class="num">3.0</td><td class="num col26">3.5</td></tr>
        </table>
        <div class="ins">Strategy·Casual이 23년부터 꾸준히 유지. Action·Puzzle·Simulation 등 다양한 장르로 진입하며 <strong>비RPG 비중 확대 중</strong>.</div>
      </details>

      <details>
        <summary style="font-size:0.88rem;font-weight:600;color:#64748b;cursor:pointer;padding:6px 0;">🌐 기타 퍼블리셔 장르 상세 (월평균, 모수 작음)</summary>
        <table style="margin-top:8px;">
          <tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">26.1Q</th></tr>
          <tr><td>RPG</td><td class="num">0.2</td><td class="num">0.1</td><td class="num">0.6</td><td class="num">0.5</td><td class="num col26">0</td></tr>
          <tr><td>Strategy</td><td class="num">0.2</td><td class="num">0.2</td><td class="num">0</td><td class="num">0.1</td><td class="num col26">0.5</td></tr>
          <tr><td>Puzzle</td><td class="num">0.2</td><td class="num">0.1</td><td class="num">0</td><td class="num">0.1</td><td class="num col26">0</td></tr>
          <tr><td>Simulation·Casual·기타</td><td class="num">0</td><td class="num">0.1</td><td class="num">0.1</td><td class="num">0.5</td><td class="num col26">0.5</td></tr>
          <tr class="tot"><td>합계</td><td class="num">0.5</td><td class="num">0.5</td><td class="num">0.7</td><td class="num">1.2</td><td class="num col26">1.0</td></tr>
        </table>
        <div class="ins">25년 진입 증가했으나 장르 불문 생존율 7.7%. 글로벌 스튜디오(이스라엘·터키·독일) 다양한 장르 시도.</div>
      </details>

      <div class="ins" style="margin-top:16px;"><strong>장르 변화 요약:</strong> 매출 TOP100 신규 진입의 주력은 <strong>RPG(60%)</strong>. 한국 퍼블리셔는 <strong>RPG 포함 전 장르 동반 감소</strong>, 중화권은 <strong>RPG 하락을 비RPG(Casual·Puzzle·Simulation)로 일부 대체</strong>하는 다변화 전략 채택.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 월평균 진입 = 연간 장르별 신규 진입 수 / 11개월 (22~25) · 26.1Q = 2개월 기준<br>
        • 장르 분류: Sensor Tower Unified Genre 기준 · RPG = Role Playing(MMORPG + 비MMORPG + 미분류) 통합
      </div>
    </div>
  </div>

  <!-- Step 4: 3개월 생존율 전체 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">4</div>
      <div class="step-info">
        <div class="step-q">신규 진입 3개월 생존율 — 전체</div>
        <div class="step-a">22~24년 <span class="up">45~49% 안정</span> → 25년 <span class="dn">36.8% 급락 (△-11.4%p)</span> · 중화권 RPG 양산 모델 효율 저하가 주 원인</div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>연도</th><th class="num">생존율</th><th class="num">생존 / 진입</th></tr></thead>
        <tbody>
          <tr><td>2022</td><td class="num"><strong>44.7%</strong></td><td class="num">42 / 94</td></tr>
          <tr><td>2023</td><td class="num up"><strong>48.9%</strong></td><td class="num">44 / 90</td></tr>
          <tr><td>2024</td><td class="num"><strong>48.2%</strong></td><td class="num">40 / 83</td></tr>
          <tr style="background:#fef3c7;"><td>2025</td><td class="num dn"><strong>36.8%</strong></td><td class="num">28 / 76</td></tr>
        </tbody>
      </table>
      <div style="margin-top:16px;">
        <canvas id="chartSurv" width="500" height="220" style="max-width:100%;"></canvas>
      </div>
      <div class="ins"><strong>핵심:</strong> 22~24년 <strong>45~49%로 안정적이었던 생존율이 25년 36.8%로 △11.4%p 급락</strong>. 전체 시장 구조 변화 신호 — 특히 중화권 RPG 장르 효율성 급감이 주도 (2-3 참조).</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 3개월 생존 = 신규 진입월 + 3개월 시점에 TOP100 잔류 여부<br>
        • 생존율 = 생존 게임 수 / 신규 진입 게임 수 × 100<br>
        • 26.1Q는 3개월 생존 측정 불가 (관측 시점 부족)로 제외
      </div>
    </div>
  </div>

  <!-- Step 5: 퍼블국적별 생존율 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">5</div>
      <div class="step-info">
        <div class="step-q">퍼블국적별 3개월 생존율</div>
        <div class="step-a">KR <span class="up">48~50% 안정</span> (23년 이후) · 중화권 <span class="dn">55→39% 급락</span> (25년) · 기타 <span class="dn">7.7%</span> 최하</div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>퍼블리셔</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th>추이</th></tr></thead>
        <tbody>
          <tr><td>KR</td><td class="num">35.7%<br><span style="color:#94a3b8;font-size:0.65rem;">15/42</span></td><td class="num up">50.0%<br><span style="color:#94a3b8;font-size:0.65rem;">18/36</span></td><td class="num">50.0%<br><span style="color:#94a3b8;font-size:0.65rem;">13/26</span></td><td class="num">48.1%<br><span style="color:#94a3b8;font-size:0.65rem;">13/27</span></td><td class="up">23년 이후 48~50% 안정</td></tr>
          <tr style="background:#fef3c7;"><td>중화권</td><td class="num">55.3%<br><span style="color:#94a3b8;font-size:0.65rem;">21/38</span></td><td class="num dn">50.0%<br><span style="color:#94a3b8;font-size:0.65rem;">23/46</span></td><td class="num up">53.3%<br><span style="color:#94a3b8;font-size:0.65rem;">24/45</span></td><td class="num dn"><strong>39.4%</strong><br><span style="color:#94a3b8;font-size:0.65rem;">13/33</span></td><td class="dn">25년 하락</td></tr>
          <tr><td>기타 (글로벌)</td><td class="num">33.3%<br><span style="color:#94a3b8;font-size:0.65rem;">2/6</span></td><td class="num">40.0%<br><span style="color:#94a3b8;font-size:0.65rem;">2/5</span></td><td class="num dn">25.0%<br><span style="color:#94a3b8;font-size:0.65rem;">2/8</span></td><td class="num dn"><strong>7.7%</strong><br><span style="color:#94a3b8;font-size:0.65rem;">1/13</span></td><td class="dn">(모수작음)</td></tr>
          <tr><td>JP</td><td class="num">40.0%</td><td class="num">50.0%</td><td class="num">50.0%</td><td class="num">100%</td><td>(모수작음)</td></tr>
          <tr><td>북미</td><td class="num">66.7%</td><td class="num">0%</td><td class="num">0%</td><td class="num">0%</td><td>(모수작음)</td></tr>
          <tr class="tot"><td>전체</td><td class="num">44.7%</td><td class="num">48.9%</td><td class="num">48.2%</td><td class="num dn">36.8%</td><td class="dn">25년 하락</td></tr>
        </tbody>
      </table>
      <div style="margin-top:16px;">
        <canvas id="chartSurvPub" width="600" height="240" style="max-width:100%;"></canvas>
      </div>
      <div class="ins"><strong>핵심:</strong> <strong>KR 퍼블리셔 생존율 48~50% 안정</strong>으로 3년간 일관. 반면 <strong>중화권 55→39%로 급락 (△-16%p)</strong>이 전체 생존율 하락 주 원인. 기타(글로벌) 7.7%는 모수 적지만 대부분 단기 이탈.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 퍼블국적별 생존율 = 해당 국적 진입 중 3개월 생존 게임 / 해당 국적 진입 총합 × 100<br>
        • 22년 KR 35.7% (15/42)는 당시 RPG-미분류 15개 진입 중 2개만 생존(13.3%)한 특이 해. 23년부터 50% 수준으로 정상화
      </div>
    </div>
  </div>

  <!-- Step 6: 중화권 장르별 생존율 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">6</div>
      <div class="step-info">
        <div class="step-q">중화권 퍼블리셔 장르별 3개월 생존율</div>
        <div class="step-a">RPG <span class="dn">57% → 30% (-27%p)</span> 꾸준한 하락 · 비RPG (Strategy·Casual) <span class="up">60%+ 유지</span> — <strong>중화권 생존율 하락의 핵심 = RPG 양산 모델 효율 저하</strong></div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th>추이</th></tr></thead>
        <tbody>
          <tr style="background:#fef3c7;"><td>RPG</td><td class="num">57.1%<br><span style="color:#94a3b8;font-size:0.65rem;">16/28</span></td><td class="num dn">48.3%<br><span style="color:#94a3b8;font-size:0.65rem;">14/29</span></td><td class="num dn">45.8%<br><span style="color:#94a3b8;font-size:0.65rem;">11/24</span></td><td class="num dn"><strong>30.0%</strong><br><span style="color:#94a3b8;font-size:0.65rem;">6/20</span></td><td class="dn">57→30% 꾸준히 하락</td></tr>
          <tr><td>Strategy·Casual (비RPG)</td><td class="num">50.0%<br><span style="color:#94a3b8;font-size:0.65rem;">2/4</span></td><td class="num up">53.8%<br><span style="color:#94a3b8;font-size:0.65rem;">7/13</span></td><td class="num up">62.5%<br><span style="color:#94a3b8;font-size:0.65rem;">5/8</span></td><td class="num"><strong>62.5%</strong><br><span style="color:#94a3b8;font-size:0.65rem;">5/8</span></td><td class="up">안정·양호</td></tr>
          <tr class="tot"><td>전체 (중화권)</td><td class="num">55.3%</td><td class="num">50.0%</td><td class="num">53.3%</td><td class="num dn">39.4%</td><td class="dn">25년 하락</td></tr>
        </tbody>
      </table>
      <div style="margin-top:16px;">
        <canvas id="chartSurvCN" width="700" height="240" style="max-width:100%;"></canvas>
      </div>
      <div class="ins"><strong>핵심:</strong> 중화권 생존율 하락의 <strong>단일 원인 = RPG 장르 (57% → 30%)</strong>. Strategy·Casual 비RPG는 <strong>4년 연속 60%+ 유지</strong>하며 오히려 상승 추세. <strong>"중화권 RPG 양산 모델 효율 저하 · 장르 차별화가 생존의 핵심 조건"</strong>이라는 시사점. 중화권 퍼블리셔들이 Strategy·Casual·Puzzle 등 비RPG로 장르 다변화 전환 중이라는 Step 3 결과와 정합.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 중화권 장르 구분: RPG vs 비RPG(Strategy·Casual·Simulation·Puzzle·Action 통합)<br>
        • 모수 기준: 22~25년 각 연도 중화권 진입 총합에서 해당 장르 게임 수
      </div>
    </div>
  </div>

  <!-- Step 7: KR 장르별 생존율 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">7</div>
      <div class="step-info">
        <div class="step-q">KR 퍼블리셔 장르별 3개월 생존율</div>
        <div class="step-a">RPG-MMORPG <span class="up">70~88%</span> 최상위 방어 · RPG-비MMORPG 25년 <span class="up">63% 회복</span> · RPG-미분류 <span class="dn">0~13% 일관 낮음</span></div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th>추이</th></tr></thead>
        <tbody>
          <tr><td>RPG-MMORPG</td><td class="num up"><strong>87.5%</strong><br><span style="color:#94a3b8;font-size:0.65rem;">7/8</span></td><td class="num up">83.3%<br><span style="color:#94a3b8;font-size:0.65rem;">10/12</span></td><td class="num">66.7%<br><span style="color:#94a3b8;font-size:0.65rem;">10/15</span></td><td class="num up">70.0%<br><span style="color:#94a3b8;font-size:0.65rem;">7/10</span></td><td class="up">22년 대비 하락, 양호</td></tr>
          <tr><td>RPG-비MMORPG</td><td class="num dn">25.0%<br><span style="color:#94a3b8;font-size:0.65rem;">1/4</span></td><td class="num up">50.0%<br><span style="color:#94a3b8;font-size:0.65rem;">3/6</span></td><td class="num dn">0.0%<br><span style="color:#94a3b8;font-size:0.65rem;">0/4</span></td><td class="num up"><strong>62.5%</strong><br><span style="color:#94a3b8;font-size:0.65rem;">5/8</span></td><td>변동 (모수작음)</td></tr>
          <tr><td>RPG-미분류</td><td class="num dn">13.3%<br><span style="color:#94a3b8;font-size:0.65rem;">2/15</span></td><td class="num dn">0.0%<br><span style="color:#94a3b8;font-size:0.65rem;">0/6</span></td><td class="num dn">0.0%<br><span style="color:#94a3b8;font-size:0.65rem;">0/1</span></td><td class="num dn">0.0%<br><span style="color:#94a3b8;font-size:0.65rem;">0/3</span></td><td class="dn">일관 낮음 (소규모)</td></tr>
          <tr><td>Strategy·Puzzle·Casual 등</td><td class="num">33.3%<br><span style="color:#94a3b8;font-size:0.65rem;">5/15</span></td><td class="num up">41.7%<br><span style="color:#94a3b8;font-size:0.65rem;">5/12</span></td><td class="num up">50.0%<br><span style="color:#94a3b8;font-size:0.65rem;">3/6</span></td><td class="num dn">16.7%<br><span style="color:#94a3b8;font-size:0.65rem;">1/6</span></td><td>변동 (모수작음)</td></tr>
          <tr class="tot"><td>전체 (KR)</td><td class="num">35.7%</td><td class="num up">50.0%</td><td class="num">50.0%</td><td class="num">48.1%</td><td class="up">22년 이후 안정</td></tr>
        </tbody>
      </table>
      <div class="ins"><strong>핵심:</strong> <strong>KR × MMORPG가 생존율 최상위 유지 (70~88%)</strong> — 리니지·HIT2·나이트 크로우·AION2 등 IP 기반 전통 장르 방어력 입증. <strong>RPG-비MMORPG는 25년 급반등 (0→63%)</strong>으로 MapleStory Idle·Seven Knights Re:BIRTH·Chaos Zero Nightmare 등 신작 성공. 반면 <strong>RPG-미분류는 4년 연속 0~13%</strong>로 기존 IP 리메이크·확장작 대부분 단기 이탈.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • RPG-MMORPG: 전통 MMORPG (리니지·HIT2·뱀피르·RF 온라인 등)<br>
        • RPG-비MMORPG: Idle·방치·서브컬처·캐릭터 RPG (MapleStory Idle·Seven Knights Re:BIRTH 등)<br>
        • RPG-미분류: 뮤오리진2·열혈강호W·트리 오브 세이비어M 등 기존 IP 리메이크·확장작 (22년 15개 진입, 13.3%만 생존)
      </div>
    </div>
  </div>

  <!-- Step 8: 25년 전후 종합 요약 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">8</div>
      <div class="step-info">
        <div class="step-q">25년 전후 종합 요약 — 물량 vs 성적</div>
        <div class="step-a">KR <strong>물량 감소, 성적 유지</strong> · 중화권 <strong>물량 감소 + 성적 하락</strong> (RPG 원인) · 기타 <strong>물량 증가, 성적 최하</strong></div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>퍼블리셔</th><th class="num">월평균 진입<br><span style="color:#94a3b8;font-size:0.68rem;font-weight:400;">22~24 → 25</span></th><th class="num">생존율<br><span style="color:#94a3b8;font-size:0.68rem;font-weight:400;">22~24 → 25</span></th><th>평가</th></tr></thead>
        <tbody>
          <tr><td>KR</td><td class="num dn">3.2 → 2.5<br><span style="color:#94a3b8;font-size:0.65rem;">(39% → 36%)</span></td><td class="num">44.2% → 48.1%</td><td>모든 장르 물량 감소, 성적 유지 — 대작 중심 집중 투자 기조</td></tr>
          <tr><td>중화권</td><td class="num dn">3.9 → 3.0<br><span style="color:#94a3b8;font-size:0.65rem;">(49% → 43%)</span></td><td class="num dn">52.7% → 39.4%</td><td>RPG 물량 감소 + 성적 하락. RPG 효율 저하 대응으로 <strong>비RPG(Strategy·Casual·Puzzle) 투입 확대 중</strong></td></tr>
          <tr><td>기타 (글로벌)</td><td class="num up">0.6 → 1.2<br><span style="color:#94a3b8;font-size:0.65rem;">(7% → 17%)</span></td><td class="num dn">31.6% → 7.7%</td><td>투입 증가로 비중 확대, 성적은 최하 (글로벌 스튜디오 다양한 장르 실험)</td></tr>
        </tbody>
      </table>
      <div class="ins" style="background:#e0f2fe;border-left:3px solid #0085ca;"><strong>🎯 핵심 결론</strong><br>
        <strong>① 물량 감소:</strong> 월 8.5→6.9개 (-18%). KR 주도, 25년부터 중화권 합류. 중화권은 비RPG 증가로 일부 상쇄.<br>
        <strong>② 생존율:</strong> KR 48~50% 안정 · 중화권 39%로 하락 (RPG 57→30% 원인) · 비RPG 60%+ 양호.<br>
        <strong>③ 중화권 다변화:</strong> RPG 효율 저하 대응으로 <strong>Strategy·Casual·Puzzle 투입 확대</strong> — Last War·Whiteout·Kingshot Survival 타이틀이 KR 시장에서 메가히트 중.<br>
        <strong>④ NHN 시사점:</strong> (a) KR × MMORPG는 방어 영역, (b) <strong>KR × 비MMORPG RPG (Idle·방치·캐릭터 기반)가 실제 확장 영역</strong>, (c) 중화권 RPG 양산 모델은 이제 한국 시장 안전지대 아님.
      </div>
    </div>
  </div>

</div>
</div>

'''

result = main[:start] + new_kr + main[end:]
with open('reports/NHN_market_analysis.html','w',encoding='utf-8') as f:
    f.write(result)
print('KR 신규진입 섹션 재구성 완료')
