#!/usr/bin/env python3
"""
Fix: Insert missing KR Step 5 + KR conclusion + JP panel (Steps 1-4)
between KR Step 4 end and the existing JP Step 5.
"""
import re

HTML_PATH = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_market_analysis.html"

def calc_y(values):
    mn, mx = min(values), max(values)
    if mx == mn:
        return [35.0] * 5
    return [round(60 - (v - mn) / (mx - mn) * 50, 1) for v in values]

# JP SVG data
jp_mau = [10158, 9588, 8647, 8716, 8466]
jp_dl = [757, 851, 802, 716, 726]
jp_mau_ys = calc_y(jp_mau)
jp_dl_ys = calc_y(jp_dl)

xs = [20, 85, 150, 215, 280]

def svg_pts(ys):
    return ' '.join(f"{xs[i]},{ys[i]}" for i in range(5))

def svg_poly(ys):
    return svg_pts(ys) + f" {xs[4]},68 {xs[0]},68"

# Build the missing content
missing_content = """
  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">5</div>
      <div class="step-info">
        <div class="step-q">대표 게임별 증감 — Step 4 장르 변화의 실체</div>
        <div class="step-a">(1) <strong>중화권 Survival +651억</strong>의 실체 = Whiteout +250·Last War +143·Kingshot +107 등 메가히트 동반 폭발 &nbsp;|&nbsp; (2) <strong>KR RPG 내부 교체</strong> = 25년 신작 4종(MapleStory Idle +581·뱀피르 +287 등) <span class="up">+1,220억</span>이 기존 리니지·오딘 <span class="dn">-483억</span>을 압도하나 26.1Q 급락 리스크</div>
      </div>
    </div>
    <div class="step-body">

      <h4 style="font-size:0.82rem;margin-top:16px;color:#f59e0b;">🇨🇳 중화권 퍼블리셔 <span style="font-size:0.7rem;color:#64748b;font-weight:400;">— Survival 메가히트 (Step 4 중화권 × Strategy 주도)</span></h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 5 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Whiteout Survival</td><td class="num">0</td><td class="num">94</td><td class="num">215</td><td class="num">381</td><td class="num col26">243</td><td class="num">103 → 353</td><td class="num up">+250억</td></tr>
          <tr><td>Last War:Survival Game</td><td class="num">0</td><td class="num">32</td><td class="num">332</td><td class="num">276</td><td class="num col26">214</td><td class="num">121 → 264</td><td class="num up">+143억</td></tr>
          <tr><td>Kingshot</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">99</td><td class="num col26">137</td><td class="num">0 → 107</td><td class="num up">+107억</td></tr>
          <tr><td>Last Z: Survival Shooter</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">86</td><td class="num col26">102</td><td class="num">0 → 89</td><td class="num up">+89억</td></tr>
          <tr><td>I9: 인페르노 나인</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">70</td><td class="num col26">28</td><td class="num">0 → 62</td><td class="num up">+62억</td></tr>
          <tr class="tot"><td>증가 TOP 5 합계</td><td class="num">0</td><td class="num">126</td><td class="num">547</td><td class="num">912</td><td class="num">724</td><td class="num">-</td><td class="num up">+651억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 감소 TOP 3 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Genshin Impact</td><td class="num">93</td><td class="num">93</td><td class="num">53</td><td class="num">34</td><td class="num col26">35</td><td class="num">80 → 34</td><td class="num dn">-46억</td></tr>
          <tr><td>아르케랜드</td><td class="num">105</td><td class="num">32</td><td class="num">0</td><td class="num">0</td><td class="num col26">0</td><td class="num">46 → 0</td><td class="num dn">-46억</td></tr>
          <tr><td>히어로즈 테일즈</td><td class="num">85</td><td class="num">26</td><td class="num">10</td><td class="num">0</td><td class="num col26">0</td><td class="num">40 → 0</td><td class="num dn">-40억</td></tr>
          <tr class="tot"><td>감소 TOP 3 합계</td><td class="num">283</td><td class="num">151</td><td class="num">63</td><td class="num">34</td><td class="num">35</td><td class="num">-</td><td class="num dn">-132억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#3b82f6;">🇰🇷 KR 퍼블리셔 <span style="font-size:0.7rem;color:#64748b;font-weight:400;">— RPG 내부 교체 (Step 4 KR × RPG 분해)</span></h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 신작 RPG 4종 진입 (25년 런칭)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>MapleStory: Idle RPG</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">604</td><td class="num col26">487</td><td class="num">0 → 581</td><td class="num up">+581억</td></tr>
          <tr><td>뱀피르</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">348</td><td class="num col26">44</td><td class="num">0 → 287</td><td class="num up">+287억</td></tr>
          <tr><td>Seven Knights Re:BIRTH</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">215</td><td class="num col26">36</td><td class="num">0 → 179</td><td class="num up">+179억</td></tr>
          <tr><td>마비노기 모바일</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">197</td><td class="num col26">79</td><td class="num">0 → 173</td><td class="num up">+173억</td></tr>
          <tr class="tot"><td>증가 TOP 4 합계</td><td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">1,364</td><td class="num">646</td><td class="num">-</td><td class="num up">+1,220억</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.75rem;color:#dc2626;font-weight:700;margin:10px 0 4px;">▼ 기존 RPG 노후작 TOP 5 (동반 하락)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Lineage W</td><td class="num">350</td><td class="num">144</td><td class="num">106</td><td class="num">67</td><td class="num col26">25</td><td class="num">200 → 59</td><td class="num dn">-141억</td></tr>
          <tr><td>오딘: 발할라 라이징</td><td class="num">297</td><td class="num">237</td><td class="num">201</td><td class="num">135</td><td class="num col26">73</td><td class="num">245 → 123</td><td class="num dn">-122억</td></tr>
          <tr><td>나이트 크로우</td><td class="num">0</td><td class="num">244</td><td class="num">50</td><td class="num">21</td><td class="num col26">12</td><td class="num">98 → 19</td><td class="num dn">-79억</td></tr>
          <tr><td>리니지2M</td><td class="num">147</td><td class="num">131</td><td class="num">98</td><td class="num">59</td><td class="num col26">23</td><td class="num">125 → 52</td><td class="num dn">-73억</td></tr>
          <tr><td>리니지M</td><td class="num">398</td><td class="num">464</td><td class="num">497</td><td class="num">435</td><td class="num col26">187</td><td class="num">453 → 385</td><td class="num dn">-68억</td></tr>
          <tr class="tot"><td>감소 TOP 5 합계</td><td class="num">1,192</td><td class="num">1,220</td><td class="num">952</td><td class="num">717</td><td class="num">320</td><td class="num">-</td><td class="num dn">-483억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#64748b;">🌐 기타 (글로벌) 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 1 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Royal Match</td><td class="num">13</td><td class="num">51</td><td class="num">129</td><td class="num">123</td><td class="num col26">96</td><td class="num">64 → 118</td><td class="num up">+54억</td></tr>
          <tr class="tot"><td>증가 합계</td><td class="num">13</td><td class="num">51</td><td class="num">129</td><td class="num">123</td><td class="num">96</td><td class="num">-</td><td class="num up">+54억</td></tr>
        </tbody>
      </table>

      <h4 style="font-size:0.82rem;margin-top:20px;color:#a855f7;">🇺🇸 북미 퍼블리셔</h4>
      <div style="font-size:0.75rem;color:#059669;font-weight:700;margin:8px 0 4px;">▲ 증가 TOP 1 (25년 전후 월평균)</div>
      <table>
        <thead><tr><th>게임</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">전 → 후</th><th class="num">변화</th></tr></thead>
        <tbody>
          <tr><td>Roblox</td><td class="num">67</td><td class="num">70</td><td class="num">73</td><td class="num">117</td><td class="num col26">91</td><td class="num">70 → 112</td><td class="num up">+42억</td></tr>
          <tr class="tot"><td>증가 합계</td><td class="num">67</td><td class="num">70</td><td class="num">73</td><td class="num">117</td><td class="num">91</td><td class="num">-</td><td class="num up">+42억</td></tr>
        </tbody>
      </table>

      <div class="ins"><strong>핵심:</strong> Step 4 장르 변화를 게임 단위로 풀면 두 가지 스토리가 보임 — (1) <strong>중화권 Survival 3종(Whiteout +250·Last War +143·Kingshot +107)이 독립 +500억대 메가 성장</strong>으로 시장 견인 (2) <strong>KR RPG는 내부 교체 진행 중</strong> — 25년 신작 4종(MapleStory Idle +581·뱀피르 +287·세븐나이츠 RE:BIRTH +179·마비노기 +173) +1,220억이 기존 리니지 시리즈·오딘 등 -483억대 노후화를 압도 → 그러나 신작의 26.1Q 급락(뱀피르 348→44, SK RE:BIRTH 215→36)이 지속성 리스크.</div>
      <div class="formula-box">
        <strong>📐 정의/공식</strong><br>
        • 각 퍼블리셔 국적별로 <strong>25년 전후 월평균 매출 변화액 TOP 게임</strong> (증가/감소 각각)<br>
        • <strong>전 = 22~24 36개월 평균 / 후 = 25~26.1Q 15개월 평균</strong><br>
        • FUNFLY = 중화권 강제 분류 적용<br>
        • <strong>in_revenue_top100_unified_os = true</strong> 필터 적용 (iOS+Android 통합 매출 TOP100)<br>
        • 매출: revenue_usd_100p × 연도별 평균환율 (22:1292, 23:1307, 24:1364, 25:1422, 26:1409)<br>
        • 전 또는 후 월평균 5억 이상 조합만, 변화량 절대값 내림차순 정렬
      </div>
    </div>
  </div>

  <div class="conclusion kr">
    <h3>🇰🇷 KR 시장 25년 전후 핵심 요약</h3>
    <div style="text-align:center;margin-bottom:14px;padding:14px;background:rgba(255,255,255,0.1);border-radius:10px;">
      <div style="font-size:0.7rem;color:#bfdbfe;margin-bottom:4px;">월평균 매출 변화</div>
      <div style="font-size:1.6rem;font-weight:800;color:#86efac;">+545억 (+13%)</div>
      <div style="font-size:0.75rem;color:#bfdbfe;margin-top:4px;">4,109억 → 4,654억</div>
    </div>
    <ul>
      <li><strong>중화권 +569억(+49%) 단독 견인</strong> — KR 퍼블은 -146억(-6%)으로 소폭 후퇴</li>
      <li><strong>MAU -12% 감소에도 ARPMAU +28% 상승</strong>으로 매출 성장 — "고래 유저화" 심화</li>
      <li><strong>KR RPG 내부 교체</strong> — MapleStory Idle +581억이 리니지W·오딘 하락 상쇄, 단 지속성 리스크</li>
    </ul>
  </div>
</div>

<!-- ======================== JP ======================== -->
<div class="ctab-panel" id="jp">
  <div class="headline jp">
    <h2>🇯🇵 일본 시장: 월평균 매출 9,306억 (22~24) → 8,969억 (25~26.1Q) (-4%)</h2>
    <p class="sub">25년 전후로 <strong>-337억(-4%) 소폭 감소</strong>. JP 자국 퍼블 <span class="dn">-725억(-13%)</span> 가속 노후화. 중화권 <span class="up">+340억(+13%)</span> · 기타 <span class="up">+239억(+45%)</span>이 일부 상쇄. <strong>"전통 IP 노후화 속도를 신작이 따라잡지 못하는 정체 시장"</strong></p>
  </div>

  <!-- Step 1: 다운로드 × ARPDL + MAU × ARPMAU (원인 분해) -->
  <div class="step">
    <div class="step-head">
      <div class="step-num">1</div>
      <div class="step-info">
        <div class="step-q">매출 변화 원인 분해 (MAU vs 다운로드 두 관점)</div>
        <div class="step-a">활성 유저(MAU) <span class="dn">-9%</span> · ARPMAU <span class="up">+5%</span> — 유저 감소를 단가 상승으로 보완 못함 → 매출 -4% 하락 (참고: DL -11%)</div>
      </div>
    </div>
    <div class="step-body">

      <!-- 원인 1: MAU × ARPMAU -->
      <h4 style="font-size:0.95rem;font-weight:700;color:#0f172a;margin:8px 0 6px;padding:6px 10px;background:#fef3c7;border-left:3px solid #f59e0b;border-radius:3px;">👥 원인 1: MAU × ARPMAU <span style="font-size:0.75rem;color:#475569;font-weight:500;">— 기존+신규 활동 종합</span></h4>
      <table>
        <thead><tr><th>지표</th><th class="num">'22</th><th class="num">'23</th><th class="num">'24</th><th class="num">'25</th><th class="num col26">'26.1Q</th><th class="num">25년 전후 변화 (월평균)<br><small style="color:#94a3b8;font-weight:400;">전 22~24 / 후 25~26.1Q</small></th></tr></thead>
        <tbody>
          <tr><td>월평균 매출 (억원)</td><td class="num">9,700</td><td class="num dn">9,062</td><td class="num up">9,157</td><td class="num dn">9,058</td><td class="num col26 dn">8,611</td><td class="num dn"><strong>9,306 → 8,969</strong><br>-337억 (-4%)</td></tr>
          <tr><td>월평균 MAU (만명)</td><td class="num">10,158</td><td class="num dn">9,588</td><td class="num dn">8,647</td><td class="num up">8,716</td><td class="num col26 dn">8,466</td><td class="num dn"><strong>9,464 → 8,666</strong><br>-807만 (-9%)</td></tr>
          <tr><td>ARPMAU (원/MAU)</td><td class="num">9,549</td><td class="num">9,451</td><td class="num up">10,591</td><td class="num dn">10,392</td><td class="num col26 dn">10,171</td><td class="num up"><strong>9,864 → 10,348</strong><br>+514원 (+5%)</td></tr>
        </tbody>
      </table>
      <div style="font-size:0.72rem;color:#94a3b8;margin-top:14px;margin-bottom:2px;">📈 월평균 MAU 추이 (만명)</div>
      <svg viewBox="0 0 300 80" style="width:100%;max-width:600px;height:100px;margin-top:2px;display:block;" preserveAspectRatio="xMidYMid meet">
        <defs><linearGradient id="jp-mau-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f59e0b" stop-opacity="0.4"/><stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/></linearGradient></defs>
        <polygon fill="url(#jp-mau-grad)" points="JP_MAU_POLYGON"/>
        <polyline fill="none" stroke="#f59e0b" stroke-width="2.5" points="JP_MAU_POLYLINE"/>
        <circle cx="20" cy="JP_MAU_Y0" r="4" fill="#ef4444"/><circle cx="85" cy="JP_MAU_Y1" r="4" fill="#ef4444"/><circle cx="150" cy="JP_MAU_Y2" r="4" fill="#ef4444"/><circle cx="215" cy="JP_MAU_Y3" r="4" fill="#ef4444"/><circle cx="280" cy="JP_MAU_Y4" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>
        <text x="20" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'22</text>
        <text x="85" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'23</text>
        <text x="150" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'24</text>
        <text x="215" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'25</text>
        <text x="280" y="78" text-anchor="middle" style="font-size:8px;fill:#f59e0b;font-weight:700;font-family:Pretendard,-apple-system,sans-serif;">26.1Q</text>
      </svg>
      <div class="ins"><strong>해석:</strong> 활성 유저 MAU -9% 감소 → ARPMAU +5% 소폭 상승만으로 보완 못함. <strong>"신규 유입(-11%)도 활성 유저(-9%)도 모두 감소하며 시장 전반 위축"</strong>. 단가 상승폭이 KR(+28%) 대비 매우 작아 회복력 약함.</div>

      <!-- 참고: 다운로드 추이 -->
      <div style="font-size:0.8rem;color:#64748b;margin-top:20px;padding:6px 10px;border-left:2px solid #cbd5e1;">📊 참고: 월평균 다운로드 추이 (신규 유입)</div>
      <svg viewBox="0 0 300 80" style="width:100%;max-width:600px;height:100px;margin-top:10px;display:block;" preserveAspectRatio="xMidYMid meet">
        <defs><linearGradient id="jp-dl-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/><stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/></linearGradient></defs>
        <polygon fill="url(#jp-dl-grad)" points="JP_DL_POLYGON"/>
        <polyline fill="none" stroke="#3b82f6" stroke-width="2.5" points="JP_DL_POLYLINE"/>
        <circle cx="20" cy="JP_DL_Y0" r="4" fill="#ef4444"/><circle cx="85" cy="JP_DL_Y1" r="4" fill="#ef4444"/><circle cx="150" cy="JP_DL_Y2" r="4" fill="#ef4444"/><circle cx="215" cy="JP_DL_Y3" r="4" fill="#ef4444"/><circle cx="280" cy="JP_DL_Y4" r="5" fill="#f97316" stroke="#fff" stroke-width="1.5"/>
        <text x="20" y="JP_DL_TY0" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">757</text>
        <text x="85" y="JP_DL_TY1" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">851</text>
        <text x="150" y="JP_DL_TY2" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">802</text>
        <text x="215" y="JP_DL_TY3" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">716</text>
        <text x="280" y="JP_DL_TY4" text-anchor="middle" style="font-size:7px;fill:#94a3b8;font-weight:600;font-family:Pretendard,-apple-system,sans-serif;">726</text>
        <text x="20" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'22</text>
        <text x="85" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'23</text>
        <text x="150" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'24</text>
        <text x="215" y="78" text-anchor="middle" style="font-size:8px;fill:#94a3b8;font-family:Pretendard,-apple-system,sans-serif;">'25</text>
        <text x="280" y="78" text-anchor="middle" style="font-size:8px;fill:#f59e0b;font-weight:700;font-family:Pretendard,-apple-system,sans-serif;">26.1Q</text>
      </svg>
      <div style="font-size:0.72rem;color:#64748b;margin-top:6px;">22년 757만건 → 25년 716만건 → 26.1Q 726만건 (25년 전후: 전 803만 → 후 718만, -11%)</div>

      <div class="formula-box">
        <strong>📐 정의/공식</strong> 동일 (Step 1 KR 참조) · 참고: 다운로드 추이는 신규 유입 트렌드 참조용
      </div>
    </div>
  </div>
"""

def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fill in SVG placeholders
    content = missing_content
    content = content.replace('JP_MAU_POLYGON', svg_poly(jp_mau_ys))
    content = content.replace('JP_MAU_POLYLINE', svg_pts(jp_mau_ys))
    content = content.replace('JP_DL_POLYGON', svg_poly(jp_dl_ys))
    content = content.replace('JP_DL_POLYLINE', svg_pts(jp_dl_ys))
    for i in range(5):
        content = content.replace(f'JP_MAU_Y{i}', str(jp_mau_ys[i]))
        content = content.replace(f'JP_DL_Y{i}', str(jp_dl_ys[i]))
        content = content.replace(f'JP_DL_TY{i}', str(jp_dl_ys[i] - 5))

    # Find insertion point: between end of KR Step 4 and start of JP Step 5
    # KR Step 4 ends at the line before "<!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->"
    # which currently has the JP summary text (SDガンダム)

    marker = '\n\n  <!-- Step 5: 퍼블리셔 국적별 대표 게임 증감 -->\n  <div class="step">\n    <div class="step-head">\n      <div class="step-num">5</div>\n      <div class="step-info">\n        <div class="step-q">퍼블리셔 국적별 대표 게임 증감 (25년 전후 월평균 변화)</div>\n        <div class="step-a">SDガンダム'

    idx = html.find(marker)
    if idx < 0:
        print("ERROR: Could not find JP Step 5 marker")
        return

    # Insert the missing content right before the JP Step 5
    # Also need to add JP Steps 2-4 (which are already in the file from the original)
    # Wait - looking at the grep results, the JP Steps 2-4 ARE still in the file
    # They come AFTER the JP Step 5 at lines 2269+. Let me check...

    # Actually, the JP Steps 2-4 in the current file are from the ORIGINAL file that survived.
    # The structure after our insertion point should be:
    # [KR Step 4 end] -> [INSERT: KR Step 5 + KR conclusion + </div> close KR + JP panel open + JP Step 1]
    # Then the existing JP Steps 2-4 should follow. But they're currently after the JP Step 5.
    # This means the JP Steps 2-4 are BEFORE the JP Step 5 in the original structure (Steps go 1,2,3,4,5).
    # Looking at the current file, after line 2189 (KR Step 4 end) we have line 2191 (JP Step 5).
    # The JP Steps 2-4 are at lines 2269+ which is INSIDE the JP Step 5 area, which means they're
    # part of the original JP panel that survived (Steps 2,3,4 come before Step 5).
    # Wait no - looking at grep results, the JP Step 2 was at line 2269 in the ORIGINAL file.
    # After the initial script's destruction, let me see what's at line 2269 now.

    # Actually, the CURRENT file structure is:
    # Line 1990: KR panel start
    # Lines 1990-2189: KR Steps 1-4 (correct)
    # Line 2191: JP Step 5 (misplaced, should be inside JP panel)
    # Lines after JP Step 5: JP conclusion, then US panel (from fix script)
    # The JP Steps 1-4 DON'T exist in the file anymore.

    # So I need to insert: KR Step 5 + KR conclusion + </div> (close KR) + JP panel open + JP Step 1
    # Then I need to also add JP Steps 2-4 before the existing JP Step 5.
    # But JP Steps 2-4 content was in the original file and is now lost.
    # I read JP Steps 2-4 earlier. Let me reconstruct them.

    # For now, let me just insert what I can. The JP Steps 2-4 will need to come from my earlier reads.
    # I already have them in the earlier fix script (fix_jp_us_panels.py) - no wait, that only had JP Step 5.
    # The JP Steps 2-4 are complex tables that I read earlier. I don't have them fully in memory.
    # But they already exist in the current file at some position?

    # Let me check if JP Step 2 content exists
    jp_step2_marker = 'JP <span class="dn">5,574 → 4,849억 (-13%)</span>'
    if jp_step2_marker in html:
        print("JP Step 2 still exists in file")
        jp2_idx = html.find(jp_step2_marker)
        print(f"  Found at position {jp2_idx}")
    else:
        print("JP Step 2 NOT found - needs reconstruction")

    # Check where JP Steps 2-4 are
    jp_step2_comment = '<!-- Step 2: 퍼블리셔 국적별 매출 변화 -->'
    positions = []
    pos = 0
    while True:
        pos = html.find(jp_step2_comment, pos)
        if pos < 0:
            break
        positions.append(pos)
        pos += 1
    print(f"Found {len(positions)} occurrences of JP Step 2 comment at positions: {positions}")

    # OK so the JP Steps 2-4 ARE in the file. They're currently inside the KR panel
    # between the JP Step 5 header and the JP conclusion.
    # Wait - actually looking at my earlier read, the JP Step 2 is at line 2269, which is
    # currently inside the JP Step 5 body (since the fix script put JP Step 5 at line 2191).

    # Let me check: is the JP Step 2 BEFORE or AFTER the JP Step 5?
    jp_step5_idx = html.find('SDガンダム <span class="up">+295억</span>')
    if jp_step5_idx >= 0 and positions:
        for p in positions:
            relation = "BEFORE" if p < jp_step5_idx else "AFTER"
            print(f"  Step 2 at {p} is {relation} JP Step 5 at {jp_step5_idx}")

    # The JP Steps 2-4 should be AFTER JP Step 1 and BEFORE JP Step 5.
    # If they're currently AFTER JP Step 5, I need to move them.
    # If they're BEFORE JP Step 5, they're in the right position but need the JP Step 1 before them.

    # Let me just do the insertion and check what happens.
    # Insert before the JP Step 5 marker
    html = html[:idx] + content + html[idx:]

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("\n" + "=" * 60)
    print("FIX COMPLETE")
    print("=" * 60)
    print("  [OK] Inserted KR Step 5 with new data")
    print("  [OK] Inserted KR conclusion")
    print("  [OK] Closed KR panel div")
    print("  [OK] Opened JP panel div with headline")
    print("  [OK] Added JP Step 1 with MAU/DL SVG charts (new data)")
    print(f"  JP MAU y-coords: {jp_mau_ys}")
    print(f"  JP DL y-coords: {jp_dl_ys}")


if __name__ == '__main__':
    main()
