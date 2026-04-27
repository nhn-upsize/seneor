#!/usr/bin/env python3
"""
Fix: Insert missing JP Steps 2-4 between JP Step 1 and JP Step 5.
Content reconstructed from earlier reads of the original file.
"""

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

# JP Steps 2-4 content (from original file)
jp_steps_234 = """
  <!-- Step 2: 퍼블리셔 국적별 매출 변화 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">2</div>
      <div class="step-info">
        <div class="step-q">퍼블리셔 국적별 월평균 매출 변화 <span style="font-size:0.7rem;color:#64748b;font-weight:500;">(매출 / 점유율 / 게임수)</span></div>
        <div class="step-a">JP <span class="dn">5,574 → 4,849억 (-13%)</span> | 중화권 <span class="up">2,623 → 2,963억 (+13%)</span> | 기타 <span class="up">+45%</span> | KR <span class="dn">-50%</span></div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>퍼블리셔 국적</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화 (월평균)<br><small style="color:#94a3b8;font-weight:400;">전 22~24 / 후 25~26.1Q</small></th></tr></thead>
        <tbody>
          <tr><td><strong>일본 (JP)</strong></td><td class="num">6,102억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">62.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">52게임</span></td><td class="num dn">5,583억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">61.6%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">52게임</span></td><td class="num dn">5,038억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">55.0%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">49게임</span></td><td class="num dn">4,953억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">54.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">49게임</span></td><td class="num col26 dn">4,434억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">51.5%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">47게임</span></td><td class="num dn"><strong>5,574억 → 4,849억</strong><br>-725억 (-13%)</td></tr>
          <tr><td>중화권 <span style="font-size:0.65rem;color:var(--amber);">(FUNFLY 포함)</span></td><td class="num">2,511억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">25.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">29게임</span></td><td class="num dn">2,421억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">26.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">30게임</span></td><td class="num up">2,938억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">32.1%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">32게임</span></td><td class="num up">2,954억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">32.6%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">32게임</span></td><td class="num col26 up">3,001억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">34.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">33게임</span></td><td class="num up"><strong>2,623억 → 2,963억</strong><br>+340억 (+13%)</td></tr>
          <tr><td>기타 (글로벌)</td><td class="num">418억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">4.3%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">9게임</span></td><td class="num up">520억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">5.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">10게임</span></td><td class="num up">660억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">7.2%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">10게임</span></td><td class="num up">747억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">8.2%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">12게임</span></td><td class="num col26 up">871억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">10.1%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">15게임</span></td><td class="num up"><strong>533억 → 772억</strong><br>+239억 (+45%)</td></tr>
          <tr><td>북미</td><td class="num">374억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">3.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">5게임</span></td><td class="num dn">351억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">3.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">4게임</span></td><td class="num up">370억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">4.0%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">5게임</span></td><td class="num dn">291억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">3.2%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">4게임</span></td><td class="num col26 dn">229억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">2.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">3게임</span></td><td class="num dn"><strong>365억 → 279억</strong><br>-86억 (-24%)</td></tr>
          <tr class="nhn"><td class="nhn">한국 (KR)</td><td class="num">296억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">3.1%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">7게임</span></td><td class="num dn">187억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">2.1%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">5게임</span></td><td class="num dn">151억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">1.6%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">4게임</span></td><td class="num dn">114억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">1.3%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">3게임</span></td><td class="num col26 dn">76억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">0.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">3게임</span></td><td class="num dn"><strong>211억 → 106억</strong><br>-105억 (-50%)</td></tr>
          <tr class="tot"><td>합계</td><td class="num">9,701억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num">9,062억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num">9,157억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num">9,059억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num col26">8,611억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num dn"><strong>9,307억 → 8,969억</strong><br>-338억 (-4%)</td></tr>
        </tbody>
      </table>
      <div class="ins"><strong>핵심:</strong> 25년 전후로 일본 시장 -4% 소폭 감소. <strong>JP 자국 퍼블 -725억(-13%)</strong> 가속 노후화가 주도하나, 중화권 +340억(+13%) · 기타 +239억(+45%) 성장이 부분 상쇄. 점유율로는 JP가 59.9%→54.1%(-5.8%p), 중화권 28.2%→33.0%(+4.9%p), 기타 5.7%→8.6%(+2.9%p). <strong>한국 퍼블은 211→106억(-50%, 점유율 2.3%→1.2%)로 사실상 반토막</strong> → "NHN의 일본 진출 허들은 점점 더 높아지는 중".</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong> 동일 (Step 2 KR 참조) · 환율 연도별 평균 적용 · revenue_usd_100p 기준 · <strong>25년 전후: 전 22~24 36개월 / 후 25~26.1Q 15개월 월평균</strong>
      </div>
    </div>
  </div>

  <!-- Step 3: 장르별 변화 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">3</div>
      <div class="step-info">
        <div class="step-q">장르별 월평균 매출 변화</div>
        <div class="step-a">Strategy <span class="up">+686억 (+78%)</span> · Arcade <span class="up">+432억 (+220%)</span> · Simulation <span class="up">+161억 (+31%)</span> · Puzzle <span class="up">+70억</span> 신흥 폭발 | RPG <span class="dn">-901억 (-27%)</span> · Adventure <span class="dn">-499억 (-36%)</span> 노후화로 시장 -4% 정체</div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화 (월평균)<br><small style="color:#94a3b8;font-weight:400;">전 22~24 / 후 25~26.1Q</small></th></tr></thead>
        <tbody>
          <tr><td><strong>Arcade</strong></td><td class="num">109</td><td class="num">108</td><td class="num up">374</td><td class="num up">667</td><td class="num col26 dn">476</td><td class="num up"><strong>197 → 629</strong><br>+432억 (+220%)</td></tr>
          <tr><td><strong>Strategy</strong></td><td class="num">889</td><td class="num dn">692</td><td class="num up">1,063</td><td class="num up">1,563</td><td class="num col26 up">1,584</td><td class="num up"><strong>861 → 1,530</strong><br>+686억 (+78%)</td></tr>
          <tr><td>Simulation</td><td class="num">397</td><td class="num up">525</td><td class="num up">638</td><td class="num up">686</td><td class="num col26 dn">663</td><td class="num up"><strong>520 → 681</strong><br>+161억 (+31%)</td></tr>
          <tr><td>Card</td><td class="num">149</td><td class="num up">189</td><td class="num">185</td><td class="num up">230</td><td class="num col26 dn">222</td><td class="num up"><strong>174 → 228</strong><br>+54억 (+31%)</td></tr>
          <tr><td>Puzzle</td><td class="num">907</td><td class="num up">951</td><td class="num up">970</td><td class="num">975</td><td class="num col26 up">1,167</td><td class="num up"><strong>943 → 1,013</strong><br>+70억 (+7%)</td></tr>
          <tr><td style="color:var(--muted);">기타 장르</td><td class="num">80</td><td class="num">78</td><td class="num up">93</td><td class="num">72</td><td class="num col26 up">95</td><td class="num dn"><strong>82 → 78</strong><br>-4억 (-5%)</td></tr>
          <tr><td>Action</td><td class="num">1,011</td><td class="num dn">929</td><td class="num up">1,013</td><td class="num dn">910</td><td class="num col26">912</td><td class="num dn"><strong>985 → 910</strong><br>-75억 (-8%)</td></tr>
          <tr><td>Sports</td><td class="num">532</td><td class="num up">658</td><td class="num dn">580</td><td class="num dn">528</td><td class="num col26 up">561</td><td class="num dn"><strong>590 → 535</strong><br>-55억 (-9%)</td></tr>
          <tr><td><strong>Role Playing</strong></td><td class="num">3,559</td><td class="num dn">3,433</td><td class="num dn">3,054</td><td class="num dn">2,524</td><td class="num col26 dn">2,139</td><td class="num dn"><strong>3,262 → 2,358</strong><br>-901억 (-27%)</td></tr>
          <tr><td>Adventure</td><td class="num">1,777</td><td class="num dn">1,326</td><td class="num dn">1,101</td><td class="num dn">917</td><td class="num col26 dn">842</td><td class="num dn"><strong>1,385 → 902</strong><br>-499억 (-36%)</td></tr>
          <tr><td>Music</td><td class="num">499</td><td class="num dn">408</td><td class="num dn">304</td><td class="num dn">200</td><td class="num col26 dn">153</td><td class="num dn"><strong>404 → 191</strong><br>-213억 (-53%)</td></tr>
          <tr class="tot"><td>합계</td><td class="num">9,909</td><td class="num">9,297</td><td class="num">9,375</td><td class="num">9,272</td><td class="num">8,814</td><td class="num">-344억</td></tr>
        </tbody>
      </table>
      <div class="ins"><strong>핵심:</strong> JP는 25년 전후로 <strong>RPG -901억 + Adventure -499억 + Music -213억 = -1,613억 노후화</strong>가 시장 하락 주도. 반면 <strong>Strategy +686억(중화권 Survival) + Arcade +432억(포켓몬 TCG Pocket) + Simulation +161억(우마무스메 등) + Puzzle +70 + Card +54 = +1,403억</strong>이 부분 상쇄 — 신구 교체 진행 중인 정체 시장.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong> 동일 (Step 3 KR 참조) · <strong>25년 전후: 전 22~24 36개월 / 후 25~26.1Q 15개월 월평균</strong> · 환율 연도별 평균 적용 · revenue_usd_100p 기준
      </div>
    </div>
  </div>

  <!-- Step 4: 퍼블리셔 국적 × 장르 매출 변화 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">4</div>
      <div class="step-info">
        <div class="step-q">퍼블리셔 국적 × 장르 매출 변화 (변화량 순)</div>
        <div class="step-a"><span style="color:#f59e0b;">중화권</span> Strategy <span class="up">+489억</span> · <span style="color:#ef4444;">JP</span> Arcade <span class="up">+343억</span> · <span style="color:#ef4444;">JP</span> Strategy <span class="up">+207억</span> · <span style="color:#ef4444;">JP</span> Simulation <span class="up">+180억</span> 신규 메가 성장 | <span style="color:#ef4444;">JP</span> RPG <span class="dn">-674억</span> · <span style="color:#ef4444;">JP</span> Adventure <span class="dn">-433억</span> · <span style="color:#ef4444;">JP</span> Music <span class="dn">-170억</span> 노후화</div>
      </div>
    </div>
    <div class="step-body">
      <h4 style="font-size:0.82rem;margin-top:16px;color:#059669;">▲ 증가 Top 조합 (25년 전후 변화 기준)</h4>
      <table>
        <thead><tr><th>퍼블국적 × 장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화</th></tr></thead>
        <tbody>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Strategy</strong></td><td class="num">523</td><td class="num">398</td><td class="num">640</td><td class="num">1,083</td><td class="num col26">1,123</td><td class="num up">+489억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Arcade</strong></td><td class="num">109</td><td class="num">108</td><td class="num">367</td><td class="num">575</td><td class="num col26">348</td><td class="num up">+343억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Strategy</strong></td><td class="num">111</td><td class="num">133</td><td class="num">129</td><td class="num">302</td><td class="num col26">357</td><td class="num up">+207억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Simulation</strong></td><td class="num">397</td><td class="num">525</td><td class="num">599</td><td class="num">650</td><td class="num col26">644</td><td class="num up">+180억</td></tr>
          <tr><td><span style="color:#64748b;">기타</span> × <strong>Puzzle</strong></td><td class="num">311</td><td class="num">337</td><td class="num">397</td><td class="num">400</td><td class="num col26">549</td><td class="num up">+130억</td></tr>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Puzzle</strong></td><td class="num">38</td><td class="num">49</td><td class="num">48</td><td class="num">87</td><td class="num col26">112</td><td class="num up">+55억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Card</strong></td><td class="num">149</td><td class="num">189</td><td class="num">185</td><td class="num">230</td><td class="num col26">222</td><td class="num up">+54억</td></tr>
          <tr class="tot"><td>TOP 7 증가 합계</td><td class="num">1,638</td><td class="num">1,739</td><td class="num">2,365</td><td class="num">3,327</td><td class="num">3,355</td><td class="num up">+1,458억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:18px;color:#dc2626;">▼ 감소 Top 조합 (25년 전후 변화 기준)</h4>
      <table>
        <thead><tr><th>퍼블국적 × 장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화</th></tr></thead>
        <tbody>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Role Playing</strong></td><td class="num">3,189</td><td class="num">3,096</td><td class="num">2,638</td><td class="num">2,170</td><td class="num col26">1,825</td><td class="num dn">-674억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Adventure</strong></td><td class="num">1,623</td><td class="num">1,205</td><td class="num">974</td><td class="num">831</td><td class="num col26">754</td><td class="num dn">-433억</td></tr>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Role Playing</strong></td><td class="num">371</td><td class="num">337</td><td class="num">409</td><td class="num">303</td><td class="num col26">277</td><td class="num dn">-81억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Music</strong></td><td class="num">499</td><td class="num">408</td><td class="num">304</td><td class="num">200</td><td class="num col26">153</td><td class="num dn">-170억</td></tr>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Action</strong></td><td class="num">82</td><td class="num">70</td><td class="num">96</td><td class="num">69</td><td class="num col26">58</td><td class="num dn">-16억</td></tr>
          <tr class="tot"><td>TOP 5 감소 합계</td><td class="num">5,764</td><td class="num">5,116</td><td class="num">4,421</td><td class="num">3,573</td><td class="num">3,067</td><td class="num dn">-1,374억</td></tr>
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> JP 시장의 핵심 축은 <strong>JP 자국 퍼블의 내부 교체</strong> — (1) <strong>JP RPG -674억 + Adventure -433억 + Music -170억 = JP 전통 3대 장르 -1,277억</strong>이 급속 노후화 (2) 동시에 <strong>JP Arcade +343억(Pokémon TCG) + JP Strategy +207억 + JP Simulation +180억 = JP 신규 3대 장르 +730억</strong> 성장하나 완전 상쇄 불가. 중화권은 <strong>Strategy +489억(Whiteout·Last War) 단독 메가 성장</strong>으로 점유율 확장 중.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 퍼블리셔 국적 (5개): KR / JP / 중화권(FUNFLY 포함) / 북미 / 기타<br>
        • 장르: TOP 100 게임은 사전 매핑, 그 외 게임은 매출 최대 장르 자동 매핑<br>
        • 5시점 표시: '22, '23, '24, '25 = 12개월 월평균, '26.1Q = 3개월 월평균 (단위: 억원)<br>
        • <strong>25년 전후 비교 (월평균):</strong> 전 = 22~24 3개년 평균 / 후 = (25년×12 + 26.1Q×3) / 15<br>
        • 매출: revenue_usd_100p × 연도별 평균환율 (22:1292, 23:1307, 24:1364, 25:1422, 26:1409)<br>
        • 전 또는 후 월평균 5억 이상 조합만, 변화량 절대값 내림차순 정렬
      </div>
    </div>
  </div>
"""


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find JP Step 1 end (formula-box close + step-body close + step close)
    # Then insert Steps 2-4 before the JP Step 5
    marker = '\n\n\n  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->\n  <div class="step">\n    <div class="step-head">\n      <div class="step-num">5</div>\n      <div class="step-info">\n        <div class="step-q">퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)</div>\n        <div class="step-a">SDガンダム'

    idx = html.find(marker)
    if idx < 0:
        # Try with just 2 newlines
        marker = '\n\n  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->\n  <div class="step">\n    <div class="step-head">\n      <div class="step-num">5</div>\n      <div class="step-info">\n        <div class="step-q">퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)</div>\n        <div class="step-a">SDガンダム'
        idx = html.find(marker)

    if idx < 0:
        print("ERROR: Could not find JP Step 5 marker")
        # Try simpler match
        simple = '  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->'
        all_pos = []
        pos = 0
        while True:
            pos = html.find(simple, pos)
            if pos < 0:
                break
            all_pos.append(pos)
            pos += 1
        print(f"Found Step 5 comments at positions: {all_pos}")
        # The JP one should be the one with SDガンダム nearby
        for p in all_pos:
            context = html[p:p+300]
            if 'SDガンダム' in context:
                idx = p
                # Adjust to include preceding newlines
                while idx > 0 and html[idx-1] == '\n':
                    idx -= 1
                marker = html[idx:p+len(simple)]
                print(f"Found JP Step 5 at position {p}")
                break

    if idx < 0:
        print("FATAL: Could not locate JP Step 5")
        return

    # Insert Steps 2-4 before the JP Step 5
    html = html[:idx] + jp_steps_234 + html[idx:]

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("=" * 60)
    print("FIX COMPLETE")
    print("=" * 60)
    print("  [OK] Inserted JP Steps 2, 3, 4")
    print("  JP panel now has Steps 1, 2, 3, 4, 5")


if __name__ == '__main__':
    main()
