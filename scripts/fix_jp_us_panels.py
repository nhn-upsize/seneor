#!/usr/bin/env python3
"""
Fix: Restore JP Step 5, JP conclusion, US panel (Steps 1-4), and restructure US Step 5.
The previous script accidentally merged JP Step 5 + US panel content.
"""

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

def calc_y(values):
    mn, mx = min(values), max(values)
    if mx == mn:
        return [35.0] * 5
    return [round(60 - (v - mn) / (mx - mn) * 50, 1) for v in values]

# US SVG data
us_mau = [30580, 29394, 29386, 29698, 30371]
us_dl = [2953, 3059, 3152, 3175, 3197]

us_mau_ys = calc_y(us_mau)
us_dl_ys = calc_y(us_dl)

def svg_points(ys):
    xs = [20, 85, 150, 215, 280]
    return ' '.join(f"{xs[i]},{ys[i]}" for i in range(5))

def svg_polygon(ys):
    xs = [20, 85, 150, 215, 280]
    pts = ' '.join(f"{xs[i]},{ys[i]}" for i in range(5))
    return pts + f" {xs[4]},68 {xs[0]},68"

# Build the replacement content: everything between JP Step 4 end and US conclusion start
# This replaces from "<!-- Step 5:" (JP's) through the "</div>" before "<div class="conclusion us">"

JP_STEP5_BODY = """
      <h4 style="font-size:0.82rem;margin-top:16px;color:#ef4444;">\\U0001f1ef\\U0001f1f5 JP \\ud37c\\ube14\\ub9ac\\uc154</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">\\u25b2 \\uc99d\\uac00 TOP 5 (25\\ub144 \\uc804\\ud6c4 \\uc6d4\\ud3c9\\uade0)</div>"""

# Actually, let me build this properly using the original Korean text

replacement_block = r"""  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">5</div>
      <div class="step-info">
        <div class="step-q">퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)</div>
        <div class="step-a">SDガンダム <span class="up">+295억</span> · Pokémon TCG Pocket <span class="up">+144억</span> · Shadowverse <span class="up">+141억</span> · 중화권 Whiteout/Last War 합 <span class="up">+583억</span> 신규 메가 | モンスト <span class="dn">-260억</span> · ウマ娘 <span class="dn">-239억</span> · NIKKE <span class="dn">-213억</span> 노후화</div>
      </div>
    </div>
    <div class="step-body">

      <h4 style="font-size:0.82rem;margin-top:16px;color:#ef4444;">🇯🇵 JP 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 5 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>SDガンダム ジージェネレーション エターナル</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">324</td><td class="num col26">179</td><td class="num">0 → 295</td><td class="num up">+295억</td></tr>
          <tr><td>Pokémon TCG Pocket</td><td class="num">0</td><td class="num">0</td><td class="num">504</td><td class="num">343</td><td class="num col26">186</td><td class="num">168 → 312</td><td class="num up">+144억</td></tr>
          <tr><td>Shadowverse: Worlds Beyond</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">160</td><td class="num col26">67</td><td class="num">0 → 141</td><td class="num up">+141억</td></tr>
          <tr><td>学園アイドルマスター</td><td class="num">0</td><td class="num">0</td><td class="num">243</td><td class="num">184</td><td class="num col26">86</td><td class="num">81 → 164</td><td class="num up">+83억</td></tr>
          <tr><td>eFootball</td><td class="num">58</td><td class="num">173</td><td class="num">225</td><td class="num">235</td><td class="num col26">228</td><td class="num">152 → 234</td><td class="num up">+82억</td></tr>
          <tr class="tot"><td>증가 TOP 5 합계</td><td class="num">58</td><td class="num">173</td><td class="num">972</td><td class="num">1,246</td><td class="num">746</td><td class="num">-</td><td class="num up">+745억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 7 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>モンスターストライク</td><td class="num">748</td><td class="num">640</td><td class="num">559</td><td class="num">398</td><td class="num col26">355</td><td class="num">649 → 389</td><td class="num dn">-260억</td></tr>
          <tr><td>ウマ娘 プリティーダービー</td><td class="num">747</td><td class="num">482</td><td class="num">345</td><td class="num">273</td><td class="num col26">337</td><td class="num">525 → 286</td><td class="num dn">-239억</td></tr>
          <tr><td>Fate/Grand Order</td><td class="num">562</td><td class="num">466</td><td class="num">383</td><td class="num">397</td><td class="num col26">255</td><td class="num">470 → 369</td><td class="num dn">-101억</td></tr>
          <tr><td>プロ野球スピリッツＡ</td><td class="num">331</td><td class="num">324</td><td class="num">237</td><td class="num">185</td><td class="num col26">253</td><td class="num">297 → 199</td><td class="num dn">-98억</td></tr>
          <tr><td>プロジェクトセカイ</td><td class="num">193</td><td class="num">163</td><td class="num">124</td><td class="num">80</td><td class="num col26">57</td><td class="num">160 → 75</td><td class="num dn">-85억</td></tr>
          <tr><td>ヘブンバーンズレッド</td><td class="num">189</td><td class="num">131</td><td class="num">104</td><td class="num">59</td><td class="num col26">43</td><td class="num">141 → 56</td><td class="num dn">-85억</td></tr>
          <tr><td>パズル＆ドラゴンズ</td><td class="num">292</td><td class="num">229</td><td class="num">207</td><td class="num">150</td><td class="num col26">205</td><td class="num">243 → 161</td><td class="num dn">-82억</td></tr>
          <tr class="tot"><td>감소 TOP 7 합계</td><td class="num">3,062</td><td class="num">2,435</td><td class="num">1,959</td><td class="num">1,542</td><td class="num">1,505</td><td class="num">-</td><td class="num dn">-950억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#f59e0b;">🇨🇳 중화권 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 6 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Whiteout Survival</td><td class="num">0</td><td class="num">44</td><td class="num">139</td><td class="num">278</td><td class="num col26">288</td><td class="num">61 → 280</td><td class="num up">+219억</td></tr>
          <tr><td>Last War:Survival</td><td class="num">0</td><td class="num">0</td><td class="num">191</td><td class="num">276</td><td class="num col26">239</td><td class="num">64 → 269</td><td class="num up">+205억</td></tr>
          <tr><td>Last War:Survival Game</td><td class="num">0</td><td class="num">0</td><td class="num">105</td><td class="num">194</td><td class="num col26">194</td><td class="num">35 → 194</td><td class="num up">+159억</td></tr>
          <tr><td>Wuthering Waves</td><td class="num">0</td><td class="num">0</td><td class="num">63</td><td class="num">105</td><td class="num col26">130</td><td class="num">21 → 110</td><td class="num up">+89억</td></tr>
          <tr><td>Kingshot</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">77</td><td class="num col26">101</td><td class="num">0 → 82</td><td class="num up">+82억</td></tr>
          <tr><td>Last Z: Survival Shooter</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">78</td><td class="num col26">85</td><td class="num">0 → 79</td><td class="num up">+79억</td></tr>
          <tr class="tot"><td>증가 TOP 6 합계</td><td class="num">0</td><td class="num">44</td><td class="num">498</td><td class="num">1,008</td><td class="num">1,037</td><td class="num">-</td><td class="num up">+833억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 4 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>GODDESS OF VICTORY: NIKKE</td><td class="num">611</td><td class="num">249</td><td class="num">173</td><td class="num">135</td><td class="num col26">117</td><td class="num">344 → 131</td><td class="num dn">-213억</td></tr>
          <tr><td>Genshin Impact</td><td class="num">363</td><td class="num">257</td><td class="num">206</td><td class="num">144</td><td class="num col26">179</td><td class="num">275 → 151</td><td class="num dn">-124억</td></tr>
          <tr><td>ドット勇者</td><td class="num">0</td><td class="num">183</td><td class="num">61</td><td class="num">29</td><td class="num col26">0</td><td class="num">81 → 23</td><td class="num dn">-58억</td></tr>
          <tr><td>あんさんぶるスターズ</td><td class="num">171</td><td class="num">143</td><td class="num">116</td><td class="num">101</td><td class="num col26">97</td><td class="num">143 → 100</td><td class="num dn">-43억</td></tr>
          <tr class="tot"><td>감소 TOP 4 합계</td><td class="num">1,145</td><td class="num">832</td><td class="num">556</td><td class="num">409</td><td class="num">393</td><td class="num">-</td><td class="num dn">-438억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#64748b;">🌐 기타 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 4 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Royal Match</td><td class="num">30</td><td class="num">103</td><td class="num">178</td><td class="num">161</td><td class="num col26">138</td><td class="num">104 → 156</td><td class="num up">+52억</td></tr>
          <tr><td>杖と剣の伝説</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">56</td><td class="num col26">31</td><td class="num">0 → 51</td><td class="num up">+51억</td></tr>
          <tr><td>Disney Solitaire</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">46</td><td class="num col26">57</td><td class="num">0 → 48</td><td class="num up">+48억</td></tr>
          <tr><td>Toon Blast</td><td class="num">58</td><td class="num">50</td><td class="num">83</td><td class="num">106</td><td class="num col26">112</td><td class="num">64 → 107</td><td class="num up">+43억</td></tr>
          <tr class="tot"><td>증가 TOP 4 합계</td><td class="num">88</td><td class="num">153</td><td class="num">261</td><td class="num">369</td><td class="num">338</td><td class="num">-</td><td class="num up">+194억</td></tr>
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> 25년 전후로 <strong>JP 신작 SDガンダム +295·Pokémon TCG Pocket +144·Shadowverse +141·学園アイマス +83·eFootball +82 = JP 퍼블 +745억</strong> 신규 IP 메가 성장. <strong>중화권 Whiteout +219 + Last War 2종 합 +364 + Wuthering Waves +89 + Kingshot +82 + Last Z +79 = 중화권 +833억</strong> 추가 성장. 동시에 <strong>モンスト -260·ウマ娘 -239·FGO -101·プロスピA -98 등 JP 전통 IP -950억대 노후화</strong> — 신규(+745)가 노후화(-950)를 완전 상쇄 못해 JP 퍼블 순감소.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 각 퍼블리셔 국적별로 <strong>25년 전후 월평균 매출 변화액 TOP 게임</strong> (증가/감소 각각)<br>
        • <strong>전 = 22~24 36개월 평균 / 후 = 25~26.1Q 15개월 평균</strong><br>
        • FUNFLY = 중화권 강제 분류 적용<br>
        • <strong>in_revenue_top100_unified_os = true</strong> 필터 적용 (iOS+Android 통합 매출 TOP100)<br>
        • 변화 절대값 30억 이상 게임만 표시
      </div>
    </div>
  </div>

  <div class="conclusion jp">
    <h3>🇯🇵 JP 시장 25년 전후 핵심 요약</h3>
    <div style="text-align:center;margin-bottom:14px;padding:14px;background:rgba(255,255,255,0.1);border-radius:10px;">
      <div style="font-size:0.7rem;color:#fecaca;margin-bottom:4px;">월평균 매출 변화</div>
      <div style="font-size:1.6rem;font-weight:800;color:#fde68a;">-346억 (-4%)</div>
      <div style="font-size:0.75rem;color:#fecaca;margin-top:4px;">9,527억 → 9,181억</div>
    </div>
    <ul>
      <li><strong>3국 중 유일한 감소 시장</strong> — 신규·기존 유저 동반 이탈(DL -11%·MAU -9%)</li>
      <li><strong>자국 IP 노후화 속도 최고</strong> — モンスト·ウマ娘·FGO·プロスピA 4종만 약 -700억</li>
      <li><strong>신작이 있어도 상쇄 불가</strong> — Pokémon TCG·SDガンダム +500억 &lt;&lt; 노후화 속도</li>
    </ul>
  </div>
</div>

<!-- ======================== US ======================== -->
<div class="ctab-panel" id="us">
  <div class="headline us">
    <h2>🇺🇸 미국 시장: 월평균 매출 16,801억 (22~24) → 19,736억 (25~26.1Q) (+17%)</h2>
    <p class="sub">25년 전후로 <strong>+2,935억(+17%) 대형 성장</strong>. <strong>중화권 +2,067억(+83%) 단독 메가 성장</strong> 주도, 기타 +1,178억(+15%) 동반 확장. <strong>"중화권 Survival/Puzzle 메가히트가 미국 시장 +17% 성장 단독 견인"</strong></p>
  </div>

  <!-- Step 1: 다운로드 × ARPDL + MAU × ARPMAU (원인 분해) -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">1</div>
      <div class="step-info">
        <div class="step-q">매출 변화 원인 분해 (MAU vs 다운로드 두 관점)</div>
        <div class="step-a">활성 유저(MAU) <span class="dn">-3%</span> · ARPMAU <span class="up">+21%</span> — 유저 풀 유지 + 단가 동반 상승 → 매출 +17% 폭발 성장 (참고: DL +4%)</div>
      </div>
    </div>
    <div class="step-body">

      <!-- 원인 1: MAU × ARPMAU -->
      <h4 style="font-size:0.95rem;font-weight:700;color:#0f172a;margin:8px 0 6px;padding:6px 10px;background:#fef3c7;border-left:3px solid #f59e0b;border-radius:3px;">👥 원인 1: MAU × ARPMAU <span style="font-size:0.75rem;color:#475569;font-weight:500;">— 기존+신규 활동 종합</span></h4>
      <table>
        <thead><tr><th>지표</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화 (월평균)<br><small style="color:#94a3b8;font-weight:400;">전 22~24 / 후 25~26.1Q</small></th></tr></thead>
        <tbody>
          <tr><td>월평균 매출 (억원)</td><td class="num">14,687</td><td class="num up">16,355</td><td class="num up">19,360</td><td class="num up">19,999</td><td class="num col26 dn">18,686</td><td class="num up"><strong>16,801 → 19,736</strong><br>+2,935억 (+17%)</td></tr>
          <tr><td>월평균 MAU (만명)</td><td class="num">30,580</td><td class="num dn">29,394</td><td class="num up">29,386</td><td class="num dn">29,698</td><td class="num col26 up">30,371</td><td class="num dn"><strong>29,787 → 29,833</strong><br>-842만 (-3%)</td></tr>
          <tr><td>ARPMAU (원/MAU)</td><td class="num">4,803</td><td class="num up">5,564</td><td class="num up">6,588</td><td class="num up">6,734</td><td class="num col26 dn">6,153</td><td class="num up"><strong>5,652 → 6,618</strong><br>+1,257원 (+21%)</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.72rem;color:#94a3b8;margin-top:14px;margin-bottom:2px;">📈 월평균 MAU 추이 (만명)</div>
      <svg viewBox="0 0 300 80" style="width:100%;max-width:600px;height:100px;margin-top:2px;display:block;" preserveAspectRatio="xMidYMid meet">
        <defs><linearGradient id="us-mau-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f59e0b" stop-opacity="0.4"/><stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/></linearGradient></defs>
        <polygon fill="url(#us-mau-grad)" points="USMAU_POLYGON"/>
        <polyline fill="none" stroke="#f59e0b" stroke-width="2.5" points="USMAU_POLYLINE"/>
        <circle cx="20" cy="USMAU_Y0" r="4" fill="#a855f7"/><circle cx="85" cy="USMAU_Y1" r="4" fill="#a855f7"/><circle cx="150" cy="USMAU_Y2" r="4" fill="#a855f7"/><circle cx="215" cy="USMAU_Y3" r="4" fill="#a855f7"/><circle cx="280" cy="USMAU_Y4" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>
        <text x="20" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'22</text>
        <text x="85" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'23</text>
        <text x="150" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'24</text>
        <text x="215" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'25</text>
        <text x="280" y="78" text-anchor="middle" style="font-size:8px;fill:#f59e0b;font-weight:700;font-family:Pretendard,-apple-system,sans-serif;">26.1Q</text>
      </svg>
      <div class="ins"><strong>해석:</strong> 활성 유저 MAU -3% 미세 감소 → ARPMAU <strong>+21% 큰 폭 상승</strong>. <strong>"기존 유저 풀은 거의 유지되면서 유저당 과금이 21% 점프"</strong> — 유저 충성도+단가 동시 상승의 가장 건강한 성장 패턴.</div>

      <!-- 참고: 다운로드 추이 -->
      <div style="font-size:0.8rem;color:#64748b;margin-top:20px;padding:6px 10px;border-left:2px solid #cbd5e1;">📊 참고: 월평균 다운로드 추이 (신규 유입)</div>
      <svg viewBox="0 0 300 80" style="width:100%;max-width:600px;height:100px;margin-top:10px;display:block;" preserveAspectRatio="xMidYMid meet">
        <defs><linearGradient id="us-dl-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/><stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/></linearGradient></defs>
        <polygon fill="url(#us-dl-grad)" points="USDL_POLYGON"/>
        <polyline fill="none" stroke="#3b82f6" stroke-width="2.5" points="USDL_POLYLINE"/>
        <circle cx="20" cy="USDL_Y0" r="4" fill="#a855f7"/><circle cx="85" cy="USDL_Y1" r="4" fill="#a855f7"/><circle cx="150" cy="USDL_Y2" r="4" fill="#a855f7"/><circle cx="215" cy="USDL_Y3" r="4" fill="#a855f7"/><circle cx="280" cy="USDL_Y4" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>
        <text x="20" y="USDL_TY0" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">2,953</text>
        <text x="85" y="USDL_TY1" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">3,059</text>
        <text x="150" y="USDL_TY2" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">3,152</text>
        <text x="215" y="USDL_TY3" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">3,175</text>
        <text x="280" y="USDL_TY4" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">3,197</text>
        <text x="20" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'22</text>
        <text x="85" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'23</text>
        <text x="150" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'24</text>
        <text x="215" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'25</text>
        <text x="280" y="78" text-anchor="middle" style="font-size:8px;fill:#f59e0b;font-weight:700;font-family:Pretendard,-apple-system,sans-serif;">26.1Q</text>
      </svg>
      <div style="font-size:0.72rem;color:#64748b;margin-top:6px;">22년 2,953만건 → 25년 3,175만건 → 26.1Q 3,197만건 (25년 전후: 전 3,055만 → 후 3,180만, +4%)</div>

      <div class="formula-box">
        <strong>📐 정의/공식</strong> 동일 (Step 1 KR 참조) · 참고: 다운로드 추이는 신규 유입 트렌드 참조용
      </div>
    </div>
  </div>

  <!-- Step 2: 퍼블리셔 국적별 매출 변화 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">2</div>
      <div class="step-info">
        <div class="step-q">퍼블리셔 국적별 월평균 매출 변화 <span style="font-size:0.7rem;color:#64748b;font-weight:500;">(매출 / 점유율 / 게임수)</span></div>
        <div class="step-a">중화권 <span class="up">2,501 → 4,568억 (+83%)</span> 메가 성장 | 기타 <span class="up">+15%</span> 동반 확장 | JP <span class="up">+86%</span> 신작 효과 | 북미 <span class="dn">-10%</span> 노후화 | KR <span class="up">+23%</span></div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>퍼블리셔 국적</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화 (월평균)<br><small style="color:#94a3b8;font-weight:400;">전 22~24 / 후 25~26.1Q</small></th></tr></thead>
        <tbody>
          <tr><td><strong>기타 (글로벌)</strong></td><td class="num">6,841억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">46.6%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">41게임</span></td><td class="num up">7,464억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">45.6%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">42게임</span></td><td class="num up">8,521억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">44.0%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">45게임</span></td><td class="num up">8,879억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">44.4%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">45게임</span></td><td class="num col26 dn">8,421억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">45.1%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">47게임</span></td><td class="num up"><strong>7,609억 → 8,787억</strong><br>+1,178억 (+15%)</td></tr>
          <tr><td>북미</td><td class="num">5,067억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">34.5%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">36게임</span></td><td class="num up">6,174억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">37.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">35게임</span></td><td class="num up">7,326억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">37.8%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">33게임</span></td><td class="num dn">5,782억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">28.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">30게임</span></td><td class="num col26 dn">4,607억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">24.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">27게임</span></td><td class="num dn"><strong>6,189억 → 5,547억</strong><br>-642억 (-10%)</td></tr>
          <tr><td>중화권 <span style="font-size:0.65rem;color:var(--amber);">(FUNFLY 포함)</span></td><td class="num">2,281억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">15.5%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">20게임</span></td><td class="num dn">2,249억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">13.8%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">21게임</span></td><td class="num up">2,972억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">15.4%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">21게임</span></td><td class="num up">4,458억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">22.3%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">21게임</span></td><td class="num col26 up">5,010억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">26.8%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">26게임</span></td><td class="num up"><strong>2,501억 → 4,568억</strong><br>+2,067억 (+83%)</td></tr>
          <tr><td>일본</td><td class="num">301억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">2.0%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">3게임</span></td><td class="num up">332억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">2.0%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">3게임</span></td><td class="num up">397억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">2.1%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">2게임</span></td><td class="num up">675억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">3.4%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">4게임</span></td><td class="num col26 dn">487억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">2.6%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">4게임</span></td><td class="num up"><strong>343억 → 637억</strong><br>+294억 (+86%)</td></tr>
          <tr class="nhn"><td class="nhn">한국 (KR)</td><td class="num">198억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">1.3%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">3게임</span></td><td class="num dn">136억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">0.8%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">2게임</span></td><td class="num up">144억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">0.7%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">2게임</span></td><td class="num up">205억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">1.0%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">2게임</span></td><td class="num col26 dn">161억<br><span style="color:#334155;font-weight:500;font-size:0.72rem;">0.9%</span><br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">2게임</span></td><td class="num up"><strong>159억 → 196억</strong><br>+37억 (+23%)</td></tr>
          <tr class="tot"><td>합계</td><td class="num">14,688억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num">16,355억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num">19,360억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num">19,999억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num col26">18,686억<br><span style="color:#64748b;font-weight:400;font-size:0.68rem;">100게임</span></td><td class="num up"><strong>16,801억 → 19,736억</strong><br>+2,935억 (+17%)</td></tr>
        </tbody>
      </table>
      <div class="ins"><strong>핵심:</strong> 25년 전후로 미국 시장 +17% 대형 성장. <strong>중화권이 +2,067억(+83%) 단독 메가 견인</strong>해 점유율 14.9%→23.1%(+8.3%p)로 폭발적 확장. <strong>북미 자국은 -642억(-10%) 후퇴</strong>이며 점유율 36.8%→28.1%(-8.7%p)로 시장 1위 자리 위협 받음(기타 글로벌 44.5% 1위). 기타 +1,178·JP +294·KR +37억까지 모두 성장. NHN 시사점은 KR 퍼블도 절대 매출 +23% 성장이지만 시장 +17%에 못미쳐 점유율 0.9%→1.0%로 근소 후퇴.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong> 동일 (Step 2 KR 참조) · <strong>25년 전후: 전 22~24 36개월 / 후 25~26.1Q 15개월 월평균</strong> · 환율 연도별 평균 적용 · revenue_usd_100p 기준
      </div>
    </div>
  </div>

  <!-- Step 3: 장르별 변화 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">3</div>
      <div class="step-info">
        <div class="step-q">장르별 월평균 매출 변화</div>
        <div class="step-a">Puzzle <span class="up">+1,534억 (+37%)</span> · Strategy <span class="up">+1,507억 (+63%)</span> 양대 메가 견인 | Board <span class="up">+578억 (+37%)</span> · Arcade <span class="up">+349억 (+57%)</span> · Simulation <span class="up">+137억</span> 동반 폭발 | RPG <span class="dn">-336억</span> · Casino <span class="dn">-444억</span> 노후화</div>
      </div>
    </div>
    <div class="step-body">
      <table>
        <thead><tr><th>장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화 (월평균)<br><small style="color:#94a3b8;font-weight:400;">전 22~24 / 후 25~26.1Q</small></th></tr></thead>
        <tbody>
          <tr><td><strong>Strategy</strong></td><td class="num">2,268</td><td class="num dn">2,110</td><td class="num up">2,852</td><td class="num up">3,941</td><td class="num col26 dn">3,820</td><td class="num up"><strong>2,297 → 3,806</strong><br>+1,507억 (+63%)</td></tr>
          <tr><td><strong>Arcade</strong></td><td class="num">472</td><td class="num dn">426</td><td class="num up">943</td><td class="num up">994</td><td class="num col26 dn">837</td><td class="num up"><strong>614 → 963</strong><br>+349억 (+57%)</td></tr>
          <tr><td><strong>Puzzle</strong></td><td class="num">3,382</td><td class="num up">4,228</td><td class="num up">4,886</td><td class="num up">5,618</td><td class="num col26 up">6,024</td><td class="num up"><strong>4,121 → 5,641</strong><br>+1,534억 (+37%)</td></tr>
          <tr><td><strong>Board</strong></td><td class="num">391</td><td class="num up">1,522</td><td class="num up">2,804</td><td class="num dn">2,234</td><td class="num col26 dn">1,812</td><td class="num up"><strong>1,572 → 2,150</strong><br>+578억 (+37%)</td></tr>
          <tr><td>Simulation</td><td class="num">450</td><td class="num dn">427</td><td class="num dn">382</td><td class="num up">556</td><td class="num col26 up">560</td><td class="num up"><strong>420 → 557</strong><br>+137억 (+33%)</td></tr>
          <tr><td style="color:var(--muted);">기타 장르 (Casual/Sports/Word/Family/Social/Music)</td><td class="num">880</td><td class="num up">893</td><td class="num up">903</td><td class="num dn">867</td><td class="num col26 up">984</td><td class="num dn"><strong>1,084 → 1,056</strong><br>-28억 (-3%)</td></tr>
          <tr><td>Card</td><td class="num">481</td><td class="num up">506</td><td class="num">504</td><td class="num dn">493</td><td class="num col26 dn">416</td><td class="num dn"><strong>497 → 477</strong><br>-20억 (-4%)</td></tr>
          <tr><td>Adventure</td><td class="num">1,383</td><td class="num up">1,478</td><td class="num up">1,814</td><td class="num dn">1,420</td><td class="num col26 dn">1,203</td><td class="num dn"><strong>1,558 → 1,377</strong><br>-181억 (-12%)</td></tr>
          <tr><td>Action</td><td class="num">1,053</td><td class="num dn">1,036</td><td class="num dn">975</td><td class="num dn">884</td><td class="num col26 dn">776</td><td class="num dn"><strong>936 → 862</strong><br>-159억 (-16%)</td></tr>
          <tr><td><strong>Casino</strong></td><td class="num">2,601</td><td class="num up">2,657</td><td class="num dn">2,472</td><td class="num dn">2,220</td><td class="num col26 dn">1,782</td><td class="num dn"><strong>2,518 → 2,066</strong><br>-444억 (-17%)</td></tr>
          <tr><td>Role Playing</td><td class="num">1,601</td><td class="num dn">1,335</td><td class="num dn">1,135</td><td class="num dn">1,070</td><td class="num col26 dn">828</td><td class="num dn"><strong>1,357 → 1,021</strong><br>-336억 (-25%)</td></tr>
          <tr class="tot"><td>합계</td><td class="num">14,962</td><td class="num">16,618</td><td class="num">19,670</td><td class="num">20,297</td><td class="num">19,042</td><td class="num">+2,937억</td></tr>
        </tbody>
      </table>
      <div class="ins"><strong>핵심:</strong> 25년 전후로 미국은 <strong>5대 장르 동반 폭발: Puzzle +1,534 + Strategy +1,507 + Board +578 + Arcade +349 + Simulation +137 = +4,105억 메가 성장</strong>이 시장 +2,935억 견인. 반면 Casino -444·RPG -336·Adventure -181·Action -159·Card -20 = -1,140억 노후화 — 신흥 5대 장르가 노후 5개를 압도하며 시장 +17% 점프.</div>
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
        <div class="step-a"><strong><span style="color:#f59e0b;">중화권</span> Strategy <span class="up">+1,560억</span></strong> 단독 메가 성장 + <span style="color:#64748b;">기타</span> Puzzle <span class="up">+1,033억</span> + <span style="color:#f59e0b;">중화권</span> Puzzle <span class="up">+545억</span> + <span style="color:#a855f7;">북미</span> Board <span class="up">+524억</span> · <span style="color:#a855f7;">북미</span> Adventure <span class="dn">-514억</span> 노후화</div>
      </div>
    </div>
    <div class="step-body">
      <h4 style="font-size:0.82rem;margin-top:16px;color:#059669;">▲ 증가 Top 조합 (25년 전후 변화 기준)</h4>
      <table>
        <thead><tr><th>퍼블국적 × 장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화</th></tr></thead>
        <tbody>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Strategy</strong></td><td class="num">1,168</td><td class="num">1,109</td><td class="num">1,898</td><td class="num">2,917</td><td class="num col26">3,091</td><td class="num up">+1,560억</td></tr>
          <tr><td><span style="color:#64748b;">기타</span> × <strong>Puzzle</strong></td><td class="num">3,142</td><td class="num">4,051</td><td class="num">4,552</td><td class="num">4,942</td><td class="num col26">4,971</td><td class="num up">+1,033억</td></tr>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Puzzle</strong></td><td class="num">-</td><td class="num">34</td><td class="num">185</td><td class="num">541</td><td class="num col26">926</td><td class="num up">+545억</td></tr>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Board</strong></td><td class="num">329</td><td class="num">1,419</td><td class="num">2,564</td><td class="num">2,036</td><td class="num col26">1,661</td><td class="num up">+524억</td></tr>
          <tr><td><span style="color:#ef4444;">JP</span> × <strong>Arcade</strong></td><td class="num">-</td><td class="num">-</td><td class="num">106</td><td class="num">338</td><td class="num col26">179</td><td class="num up">+271억</td></tr>
          <tr><td><span style="color:#64748b;">기타</span> × <strong>Adventure</strong></td><td class="num">224</td><td class="num">131</td><td class="num">189</td><td class="num">419</td><td class="num col26">491</td><td class="num up">+252억</td></tr>
          <tr><td><span style="color:#64748b;">기타</span> × <strong>Simulation</strong></td><td class="num">256</td><td class="num">261</td><td class="num">306</td><td class="num">411</td><td class="num col26">418</td><td class="num up">+138억</td></tr>
          <tr><td><span style="color:#64748b;">기타</span> × <strong>Arcade</strong></td><td class="num">472</td><td class="num">426</td><td class="num">837</td><td class="num">656</td><td class="num col26">658</td><td class="num up">+78억</td></tr>
          <tr class="tot"><td>TOP 8 증가 합계</td><td class="num">5,591</td><td class="num">7,431</td><td class="num">10,637</td><td class="num">12,260</td><td class="num">12,395</td><td class="num up">+4,401억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:18px;color:#dc2626;">▼ 감소 Top 조합 (25년 전후 변화 기준)</h4>
      <table>
        <thead><tr><th>퍼블국적 × 장르</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화</th></tr></thead>
        <tbody>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Adventure</strong></td><td class="num">1,131</td><td class="num">1,334</td><td class="num">1,595</td><td class="num">895</td><td class="num col26">619</td><td class="num dn">-514억</td></tr>
          <tr><td><span style="color:#64748b;">기타</span> × <strong>Casino</strong></td><td class="num">665</td><td class="num">644</td><td class="num">584</td><td class="num">454</td><td class="num col26">265</td><td class="num dn">-215억</td></tr>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Casino</strong></td><td class="num">1,503</td><td class="num">1,594</td><td class="num">1,503</td><td class="num">1,379</td><td class="num col26">1,167</td><td class="num dn">-196억</td></tr>
          <tr><td><span style="color:#f59e0b;">중화권</span> × <strong>Role Playing</strong></td><td class="num">427</td><td class="num">473</td><td class="num">386</td><td class="num">277</td><td class="num col26">227</td><td class="num dn">-161억</td></tr>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Role Playing</strong></td><td class="num">619</td><td class="num">457</td><td class="num">396</td><td class="num">350</td><td class="num col26">275</td><td class="num dn">-156억</td></tr>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Strategy</strong></td><td class="num">224</td><td class="num">171</td><td class="num">154</td><td class="num">108</td><td class="num col26">93</td><td class="num dn">-78억</td></tr>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Action</strong></td><td class="num">474</td><td class="num">471</td><td class="num">409</td><td class="num">390</td><td class="num col26">324</td><td class="num dn">-74억</td></tr>
          <tr><td><span style="color:#a855f7;">북미</span> × <strong>Casual</strong></td><td class="num">95</td><td class="num">85</td><td class="num">65</td><td class="num">27</td><td class="num col26">-</td><td class="num dn">-60억</td></tr>
          <tr class="tot"><td>TOP 8 감소 합계</td><td class="num">5,138</td><td class="num">5,229</td><td class="num">5,092</td><td class="num">3,880</td><td class="num">2,970</td><td class="num dn">-1,454억</td></tr>
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> 25년 전후로 <strong>중화권 Strategy +1,560억(Last War·Whiteout·Kingshot 메가) + 기타 Puzzle +1,033억(Royal Match 등) + 중화권 Puzzle +545억(Gossip Harbor) + 북미 Board +524억(MONOPOLY GO) + JP Arcade +271억(Pokémon TCG Pocket) + 기타 Adventure +252억 = +4,200억대 신규 메가 성장</strong>이 시장 견인. 반면 <strong>북미 Adventure -514(Roblox 등) + 기타 Casino -215 + 북미 Casino -196 + 중화권 RP -161 + 북미 RP -156 + 북미 Strategy -78 + 북미 Action -74 = -1,394억 노후화</strong>로 부분 상쇄. 북미 자국 퍼블의 광범위한 약세 두드러짐.</div>
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

    # Calculate SVG coordinates
    xs = [20, 85, 150, 215, 280]

    # US MAU
    mau_pts = svg_points(us_mau_ys)
    mau_poly = svg_polygon(us_mau_ys)

    # US DL
    dl_pts = svg_points(us_dl_ys)
    dl_poly = svg_polygon(us_dl_ys)

    # Fill in SVG placeholders
    block = replacement_block
    block = block.replace('USMAU_POLYGON', mau_poly)
    block = block.replace('USMAU_POLYLINE', mau_pts)
    for i in range(5):
        block = block.replace(f'USMAU_Y{i}', str(us_mau_ys[i]))

    block = block.replace('USDL_POLYGON', dl_poly)
    block = block.replace('USDL_POLYLINE', dl_pts)
    for i in range(5):
        block = block.replace(f'USDL_Y{i}', str(us_dl_ys[i]))
        block = block.replace(f'USDL_TY{i}', str(us_dl_ys[i] - 5))

    # Find the current broken section and replace it
    # Current state: line 2386 starts "<!-- Step 5:" with JP summary but US body
    # We need to replace from "  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->" (first remaining after KR)
    # through the end of the current US Step 5 body (which ends before "  <div class="conclusion us">")

    marker_start = '  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->\n  <div class="step">\n    <div class="step-head">\n      <div class="step-num">5</div>\n      <div class="step-info">\n        <div class="step-q">퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)</div>\n        <div class="step-a">SDガンダム'

    # Find the start
    idx = html.find('  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->')
    if idx < 0:
        print("ERROR: Could not find JP Step 5 marker")
        return

    # Find the end: just before <div class="conclusion us">
    end_marker = '\n\n  <div class="conclusion us">'
    end_idx = html.find(end_marker, idx)
    if end_idx < 0:
        print("ERROR: Could not find US conclusion marker")
        return

    # The content to replace is from idx to end_idx
    old_content = html[idx:end_idx]
    print(f"Replacing {len(old_content)} characters starting at position {idx}")

    # Now build the full replacement: JP Step 5 + JP conclusion + US panel (Steps 1-4) + US Step 5
    # The US Step 5 is already in the old content, we need to extract it and keep it

    # Actually, the US Step 5 body in the current file is correct (already replaced with new data)
    # So we need to keep it. Let me extract the US Step 5 from the current content.

    # The US Step 5 data starts from the 중화권 section header after the JP data
    # But actually, the current content is a SINGLE Step 5 div with JP header and mixed body
    # It's simpler to just build the entire US Step 5 fresh here

    us_step5 = """  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">5</div>
      <div class="step-info">
        <div class="step-q">퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)</div>
        <div class="step-a">중화권 Survival 4종(Last War +589·Kingshot +516·Whiteout +337·Last War SG +311) <span class="up">+2,277억</span> 메가 | MONOPOLY GO <span class="up">+415억</span> | 기타 Royal Kingdom +337·Royal Match +288·Clash Royale +246 동반 폭발 | Roblox <span class="dn">-562억</span> 단독 노후화</div>
      </div>
    </div>
    <div class="step-body">

      <h4 style="font-size:0.82rem;margin-top:16px;color:#f59e0b;">🇨🇳 중화권 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 6 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Last War:Survival</td><td class="num">0</td><td class="num">0</td><td class="num">409</td><td class="num">724</td><td class="num col26">731</td><td class="num">136 → 725</td><td class="num up">+589억</td></tr>
          <tr><td>Kingshot</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">491</td><td class="num col26">614</td><td class="num">0 → 516</td><td class="num up">+516억</td></tr>
          <tr><td>Whiteout Survival</td><td class="num">0</td><td class="num">204</td><td class="num">533</td><td class="num">602</td><td class="num col26">508</td><td class="num">246 → 583</td><td class="num up">+337억</td></tr>
          <tr><td>Last War:Survival Game</td><td class="num">0</td><td class="num">0</td><td class="num">222</td><td class="num">383</td><td class="num col26">393</td><td class="num">74 → 385</td><td class="num up">+311억</td></tr>
          <tr><td>Gossip Harbor Merge</td><td class="num">0</td><td class="num">41</td><td class="num">89</td><td class="num">268</td><td class="num col26">476</td><td class="num">43 → 310</td><td class="num up">+267억</td></tr>
          <tr><td>Last Z: Survival Shooter</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">223</td><td class="num col26">392</td><td class="num">0 → 257</td><td class="num up">+257억</td></tr>
          <tr class="tot"><td>증가 TOP 6 합계</td><td class="num">0</td><td class="num">245</td><td class="num">1,253</td><td class="num">2,691</td><td class="num">3,114</td><td class="num">-</td><td class="num up">+2,277억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 4 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Top War</td><td class="num">147</td><td class="num">130</td><td class="num">76</td><td class="num">34</td><td class="num col26">0</td><td class="num">118 → 27</td><td class="num dn">-91억</td></tr>
          <tr><td>Last Shelter</td><td class="num">104</td><td class="num">92</td><td class="num">49</td><td class="num">0</td><td class="num col26">0</td><td class="num">82 → 0</td><td class="num dn">-82억</td></tr>
          <tr><td>Genshin Impact</td><td class="num">279</td><td class="num">159</td><td class="num">107</td><td class="num">96</td><td class="num col26">125</td><td class="num">182 → 102</td><td class="num dn">-80억</td></tr>
          <tr><td>Puzzles & Survival</td><td class="num">212</td><td class="num">189</td><td class="num">153</td><td class="num">129</td><td class="num col26">85</td><td class="num">185 → 120</td><td class="num dn">-65억</td></tr>
          <tr class="tot"><td>감소 TOP 4 합계</td><td class="num">742</td><td class="num">570</td><td class="num">385</td><td class="num">259</td><td class="num">210</td><td class="num">-</td><td class="num dn">-318억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#64748b;">🌐 기타 (글로벌) 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 5 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Royal Kingdom</td><td class="num">0</td><td class="num">0</td><td class="num">79</td><td class="num">342</td><td class="num col26">446</td><td class="num">26 → 363</td><td class="num up">+337억</td></tr>
          <tr><td>Royal Match</td><td class="num">430</td><td class="num">950</td><td class="num">1,352</td><td class="num">1,227</td><td class="num col26">1,088</td><td class="num">911 → 1,199</td><td class="num up">+288억</td></tr>
          <tr><td>Clash Royale</td><td class="num">161</td><td class="num">117</td><td class="num">159</td><td class="num">435</td><td class="num col26">222</td><td class="num">146 → 392</td><td class="num up">+246억</td></tr>
          <tr><td>Match Factory</td><td class="num">0</td><td class="num">63</td><td class="num">205</td><td class="num">275</td><td class="num col26">258</td><td class="num">89 → 272</td><td class="num up">+183억</td></tr>
          <tr><td>Disney Solitaire</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">133</td><td class="num col26">169</td><td class="num">0 → 140</td><td class="num up">+140억</td></tr>
          <tr class="tot"><td>증가 TOP 5 합계</td><td class="num">591</td><td class="num">1,130</td><td class="num">1,795</td><td class="num">2,412</td><td class="num">2,183</td><td class="num">-</td><td class="num up">+1,194억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 3 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>State of Survival</td><td class="num">241</td><td class="num">149</td><td class="num">79</td><td class="num">56</td><td class="num col26">0</td><td class="num">156 → 45</td><td class="num dn">-111억</td></tr>
          <tr><td>Clash of Clans</td><td class="num">359</td><td class="num">319</td><td class="num">329</td><td class="num">267</td><td class="num col26">181</td><td class="num">336 → 250</td><td class="num dn">-86억</td></tr>
          <tr><td>Solitaire Grand Harvest</td><td class="num">170</td><td class="num">214</td><td class="num">202</td><td class="num">141</td><td class="num col26">76</td><td class="num">195 → 128</td><td class="num dn">-67억</td></tr>
          <tr class="tot"><td>감소 TOP 3 합계</td><td class="num">770</td><td class="num">682</td><td class="num">610</td><td class="num">464</td><td class="num">257</td><td class="num">-</td><td class="num dn">-264억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#a855f7;">🇺🇸 북미 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 2 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>MONOPOLY GO!</td><td class="num">0</td><td class="num">1,680</td><td class="num">2,267</td><td class="num">1,793</td><td class="num col26">1,483</td><td class="num">1,316 → 1,731</td><td class="num up">+415억</td></tr>
          <tr><td>Umamusume (JP)</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">163</td><td class="num col26">80</td><td class="num">0 → 146</td><td class="num up">+146억</td></tr>
          <tr class="tot"><td>증가 TOP 2 합계</td><td class="num">0</td><td class="num">1,680</td><td class="num">2,267</td><td class="num">1,956</td><td class="num">1,563</td><td class="num">-</td><td class="num up">+561억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 3 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Roblox</td><td class="num">739</td><td class="num">903</td><td class="num">1,151</td><td class="num">422</td><td class="num col26">158</td><td class="num">931 → 369</td><td class="num dn">-562억</td></tr>
          <tr><td>Star Trek Fleet Command</td><td class="num">126</td><td class="num">83</td><td class="num">63</td><td class="num">0</td><td class="num col26">0</td><td class="num">91 → 0</td><td class="num dn">-91억</td></tr>
          <tr><td>Diablo Immortal</td><td class="num">171</td><td class="num">55</td><td class="num">41</td><td class="num">0</td><td class="num col26">36</td><td class="num">89 → 7</td><td class="num dn">-82억</td></tr>
          <tr class="tot"><td>감소 TOP 3 합계</td><td class="num">1,036</td><td class="num">1,041</td><td class="num">1,255</td><td class="num">422</td><td class="num">194</td><td class="num">-</td><td class="num dn">-735억</td></tr>
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> 25년 전후로 미국 시장은 <strong>중화권 Survival 4종(Last War +589·Kingshot +516·Whiteout +337·Last War SG +311) + Gossip Harbor +267 + Last Z +257 = 중화권 +2,277억 메가 성장</strong>이 시장의 핵심 엔진. 기타에서 <strong>Royal Kingdom +337·Royal Match +288·Clash Royale +246·Match Factory +183·Disney Solitaire +140 = +1,194억</strong> 동반 폭발. 북미는 MONOPOLY GO +415 + Umamusume +146 = +561억이나 Roblox -562·Star Trek -91·Diablo -82 = -735억으로 순 손실.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 각 퍼블리셔 국적별로 <strong>25년 전후 월평균 매출 변화액 TOP 게임</strong> (증가/감소 각각)<br>
        • <strong>전 = 22~24 36개월 평균 / 후 = 25~26.1Q 15개월 평균</strong><br>
        • FUNFLY = 중화권 강제 분류 적용<br>
        • <strong>in_revenue_top100_unified_os = true</strong> 필터 적용 (iOS+Android 통합 매출 TOP100)<br>
        • 변화 절대값 50억 이상 게임만 표시
      </div>
    </div>
  </div>"""

    # Full replacement
    new_content = block + '\n\n' + us_step5

    html = html[:idx] + new_content + html[end_idx:]

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("=" * 60)
    print("FIX COMPLETE")
    print("=" * 60)
    print("  [OK] Restored JP Step 5 with correct data")
    print("  [OK] Restored JP conclusion")
    print("  [OK] Restored US panel (headline + Steps 1-4)")
    print("  [OK] Added US MAU SVG chart with new data")
    print("  [OK] Added US DL SVG chart with new data")
    print("  [OK] Restored US Step 5 with correct data")
    print(f"  US MAU y-coords: {us_mau_ys}")
    print(f"  US DL y-coords: {us_dl_ys}")


if __name__ == '__main__':
    main()
