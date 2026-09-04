# -*- coding: utf-8 -*-
"""임원 보고용 최종 HTML 리포트 — 20개 인사이트 + 대화형 해석"""
import os

OUT = r"C:\Users\NHN\Documents\sensortower_api\reports\NHN_exec_report.html"

# ============================================================
# 인사이트 데이터 (20개)
# ============================================================
# 각 인사이트: {id, section, icon, headline, interpretation, evidence}

INSIGHTS = [
    # ============ PART 1: KR 시장 (5개) ============
    {
        'id': 'kr-1',
        'section': 'KR',
        'headline': '한국 시장은 망한 게 아니다 — 오히려 +13% 성장 중',
        'interpretation': '겉보기 KR 퍼블 -6%만 보면 "한국이 꺼진다"로 보이지만, 실제 <strong>전체 시장은 4,109억 → 4,654억으로 +545억(+13%) 성장</strong>. 그 성장을 누가 가져갔느냐가 핵심이다.',
        'evidence': [
            ('전체 시장', '4,109억 → 4,654억 (+545억, +13%)'),
            ('KR 퍼블', '2,463억 → 2,317억 (-146억, -6%)'),
            ('중화권', '1,154억 → 1,722억 (+568억, +49%)'),
            ('요점', 'KR 퍼블 감소분(-146)보다 <strong>중화권 증가분(+568)</strong>이 약 4배 큰 규모로 시장 성장을 단독 견인'),
        ],
    },
    {
        'id': 'kr-2',
        'section': 'KR',
        'headline': 'KR 퍼블 내부는 "죽은 기업" vs "성장 기업"으로 쪼개졌다',
        'interpretation': '"엔씨 1/3 토막"이라기보다는 <strong>카카오게임즈가 반토막(-57%)</strong>이 최대 충격. 그런데 같은 KR 퍼블 중에서도 <strong>넷마블은 +94% (2배)</strong>, 넥슨은 +34% 성장. "한국이 죽었다"가 아니라 <strong>"한국 기업이 양극화됐다"</strong>가 정확한 해석.',
        'evidence': [
            ('넷마블', '208억 → 404억 (+196억, +94%) — 2배 성장'),
            ('넥슨', '396억 → 530억 (+134억, +34%)'),
            ('NHN', '107억 → 130억 (+23억, +21%) — 웹보드 강자'),
            ('엔씨소프트', '103억 → 88억 (-15억, -15%) — 리니지 노후화'),
            ('카카오게임즈', '376억 → 162억 (-214억, -57%) ⚠️ 최대 충격'),
            ('요점', '카카오게임즈 혼자 한 달 -214억 빠짐 → KR 퍼블 전체 -146억의 주된 원인'),
        ],
    },
    {
        'id': 'kr-3',
        'section': 'KR',
        'headline': '카카오가 토해낸 200억+을 중화권 Survival이 가져갔다',
        'interpretation': '카카오게임즈 월 -214억 / 엔씨 -15억 / 합 -229억. 중화권은 <strong>+568억</strong> 유입. 단순 숫자 차이가 아니라 <strong>장르 대전환</strong> — MMORPG가 지는 자리를 중화권의 Survival/Strategy (Last War·Whiteout·Kingshot)가 채움.',
        'evidence': [
            ('Last War:Survival', 'FUNFLY PTE. LTD. (중화권 강제분류) — US 기준 409→725억 메가히트'),
            ('중화권 KR 유입', '+568억/월 (+49%)'),
            ('KR MMORPG', '1,818억 → 1,382억 (-436억, -24%)'),
            ('KR Strategy 장르', '515억 → 1,151억 (+636억, +123%) 단독 폭증'),
            ('요점', '"장르 교체" — MMORPG가 비운 자리(-436)를 Strategy(+636)가 덮어쓰는 구도'),
        ],
    },
    {
        'id': 'kr-4',
        'section': 'KR',
        'headline': '한국 점유율은 이미 10%p 넘어갔다 (60% → 50%)',
        'interpretation': '가장 중요한 시사점: 매출만 보면 -6% 감소이지만, <strong>점유율로 보면 20%p 가까이 빠짐</strong> (66.9% → 48.2%). 중화권이 약진하는 속도가 더 빠르다는 뜻. 지금 추세면 <strong>26~27년 사이 중화권이 KR 퍼블 점유율을 추월</strong>할 가능성 있음.',
        'evidence': [
            ("'22 KR 퍼블 점유율", '66.9%'),
            ("'26.1Q KR 퍼블 점유율", '48.2% (-18.7%p)'),
            ("'22 중화권 점유율", '21.8%'),
            ("'26.1Q 중화권 점유율", '37.7% (+15.9%p)'),
            ('격차', 'KR 퍼블 vs 중화권 격차 45%p → 10.5%p로 급축소'),
        ],
    },
    {
        'id': 'kr-5',
        'section': 'KR',
        'headline': '유저는 줄어들어도 돈은 더 쓴다 — "고래 유저화" 가속',
        'interpretation': 'MAU 10% 감소에도 매출은 13% 성장. 그 이유는 <strong>ARPMAU(1인당 과금)이 25% 뛰었기 때문</strong>. 일반적 시장 위축이 아니라 <strong>소수의 고과금 유저가 시장을 유지</strong>하는 구조 전환. 신규 유저 유입보다 기존 유저 LTV 극대화가 더 중요한 시장이 됨.',
        'evidence': [
            ('월평균 MAU', '4,291만 → 3,615만 (-676만, -16%)'),
            ('ARPMAU', '8,938원 → 13,263원 (+4,325원, +48%)'),
            ('다운로드', '582만건 → 539만건 (-43만, -7%)'),
            ('요점', '유저·다운로드는 감소 but 단가는 폭등 → "적은 유저가 더 많이 결제"하는 고래 시장'),
        ],
    },

    # ============ PART 2: JP 시장 (3개) ============
    {
        'id': 'jp-1',
        'section': 'JP',
        'headline': '일본은 정체 시장이다 — 자국 IP 노후화로 -4%',
        'interpretation': '표면적으로 -4% 소폭 감소이지만, 속을 보면 <strong>JP 자국 퍼블은 -13% (-748억/월) 급락</strong>. 모바일 게임 중심이던 일본 대형 IP들이 일제히 힘을 잃음. "일본 시장이 늙었다"는 표현이 정확.',
        'evidence': [
            ('전체 시장', '9,306억 → 8,969억 (-337억, -4%)'),
            ('JP 자국 퍼블', '5,704억 → 4,956억 (-748억, -13%)'),
            ('모스터스트라이크 (XFLAG)', '649 → 389억 (-259억, -40%)'),
            ('우마무스메 (Cygames)', '525 → 286억 (-238억, -45%)'),
            ('Fate/Grand Order (Aniplex)', '470 → 369억 (-101억, -21%)'),
            ('요점', '15년 넘은 대표 IP들이 일제히 쇠락 → 세대 교체 실패'),
        ],
    },
    {
        'id': 'jp-2',
        'section': 'JP',
        'headline': '일본도 중화권이 가져갔다 — 다만 속도 완만',
        'interpretation': '중화권 +13% (+358억/월) 성장으로 JP 자국 하락(-748억)의 절반 정도 상쇄. KR(49%)보다는 느리지만 <strong>JP도 중화권 침투가 진행 중</strong>. 일본 시장의 폐쇄성 때문에 속도가 상대적으로 느릴 뿐.',
        'evidence': [
            ('중화권 매출', '2,669억 → 3,027억 (+358억, +13%)'),
            ('중화권 점유율', '25.9% → 34.8% (+8.9%p)'),
            ('KR 퍼블 점유율', '3.1% → 0.9% (-2.2%p) ⚠️'),
            ('요점', 'KR 퍼블은 일본에서 급격히 위축 — NHN 진입 허들 상승'),
        ],
    },
    {
        'id': 'jp-3',
        'section': 'JP',
        'headline': 'JP 1위 타이틀 규모가 37% 줄었다 — 메가히트 부재 신호',
        'interpretation': 'JP 1위 게임 월매출이 <strong>748억 (22년) → 470억 (25년)</strong>으로 37% 축소. 1위 게임이 이 정도 빠진다는 건 <strong>신규 메가히트가 안 나오고 기존 IP만 조금씩 죽어간다</strong>는 의미. 시장 에너지 감소.',
        'evidence': [
            ("'22 JP 1위", '748억/월'),
            ("'25 JP 1위", '470억/월 (-37%)'),
            ("'22 JP 10위", '213억/월'),
            ("'25 JP 10위", '219억/월 (≈)'),
            ('요점', '상위권은 무너지는데 중위권은 제자리 → 시장 구조 자체가 축소 중'),
        ],
    },

    # ============ PART 3: US 시장 (3개) ============
    {
        'id': 'us-1',
        'section': 'US',
        'headline': '미국은 진짜 시장이다 — +17% 성장',
        'interpretation': 'KR·JP가 정체/축소 중일 때 US는 <strong>+2,935억/월 (+17%)</strong> 순증가. 매출 규모 자체도 KR의 4배 이상. <strong>"성장 시장에서 경쟁하느냐, 축소 시장에서 방어하느냐"의 전략 선택</strong>이 다음 3년을 가른다.',
        'evidence': [
            ('전체 시장', '1.68조 → 1.97조 (+2,935억, +17%)'),
            ('KR 대비 규모', 'US 1위 2,267억 vs KR 1위 510억 — 4.4배'),
            ('US 100위 규모', '43~86억/월 ≈ KR 20위권 (42~62억)'),
            ('요점', 'US는 100위 게임이 KR 상위권 매출과 맞먹음 → <strong>중위권만 노려도 규모 잡힘</strong>'),
        ],
    },
    {
        'id': 'us-2',
        'section': 'US',
        'headline': 'US도 중화권 Last War가 다 해먹었다 (+316억/월)',
        'interpretation': 'US 성장분 +2,935억 중 중화권이 <strong>+2,065억 (단독 70% 기여)</strong>. 그 중 대표 게임이 <strong>Last War:Survival</strong> — 409→725억으로 단독 +316억. KR에서도 동일 IP가 시장을 키우는 중.',
        'evidence': [
            ('중화권 매출', '2,633억 → 4,698억 (+2,065억, +78%)'),
            ('Last War:Survival (FUNFLY)', '409 → 725억 (+316억)'),
            ('Royal Match (Dream Games)', '624 → 904억 (+280억) — 터키 Puzzle 메가'),
            ('중화권 점유율', '15.7% → 26.7% (+11%p)'),
            ('요점', '중화권 1개 게임이 한 시장 +300억 단독 성장 견인 — KR·US 공통'),
        ],
    },
    {
        'id': 'us-3',
        'section': 'US',
        'headline': '미국은 진입 장벽 높지만 붙은 게임은 오래 간다',
        'interpretation': '3국 비교에서 US 3개월 생존율 <strong>58.7% (KR 40.6%, JP 36.0%)</strong>로 가장 높음. 진입 자체는 어려움 (연 30개 내외 신규 진입) but 한번 들어오면 안정적. <strong>"고비용·고수율" 시장</strong>.',
        'evidence': [
            ('US 3개월 생존율', '58.7% (1위)'),
            ('KR 3개월 생존율', '40.6%'),
            ('JP 3개월 생존율', '36.0%'),
            ('연 신규 진입 수 (22~25)', 'KR 100+ / JP 60+ / US 30 내외'),
            ('요점', 'US는 경쟁 빡세지만 안착하면 수명 김 → NHN 웹보드 진출 시 시간 투자 필요'),
        ],
    },

    # ============ PART 4: 3국 공통 (2개) ============
    {
        'id': 'common-1',
        'section': 'COMMON',
        'headline': '중화권이 3국 모두에서 점유율 뺏어가는 중',
        'interpretation': '<strong>국가 불문 공통 트렌드</strong>. KR +10%p, JP +9%p, US +11%p. 중화권 퍼블리셔가 <strong>글로벌 전체에서 동시 다발적으로 확장</strong> — 이건 한국만의 이슈가 아닌 업계 구조적 변화.',
        'evidence': [
            ('KR 중화권 점유율', "'22 21.8% → '26.1Q 37.7% (+15.9%p)"),
            ('JP 중화권 점유율', "'22 25.9% → '26.1Q 34.8% (+8.9%p)"),
            ('US 중화권 점유율', "'22 15.5% → '26.1Q 26.8% (+11.3%p)"),
            ('3국 중화권 합계', '25년 전후 +3,003억/월 단독 증가 (+46%)'),
            ('요점', '중화권 1개 퍼블리셔(FUNFLY 등)가 전 세계 시장을 동시에 흔드는 구도'),
        ],
    },
    {
        'id': 'common-2',
        'section': 'COMMON',
        'headline': 'MAU 감소·ARPMAU 상승은 3국 글로벌 트렌드다',
        'interpretation': '유저는 줄어도 매출은 증가 — 이게 <strong>글로벌 모바일 게임 시장의 뉴노멀</strong>. 신규 유입에 의존하던 시대는 끝. 기존 유저 LTV 극대화 + 고가 상품(50만원+ 패키지 등) 구축이 핵심.',
        'evidence': [
            ('3국 MAU 합계', '4,014만 → 3,615만 (-10%)'),
            ('3국 ARPMAU 합계', '10,328 → 12,873 (+25%)'),
            ('3국 DL 합계', '-7% 감소'),
            ('요점', '신규 유입 감소에도 매출 증가 → <strong>고래 유저화 + 고가 BM</strong> 전략 필수'),
        ],
    },

    # ============ PART 5: 웹보드 (5개) ============
    {
        'id': 'wb-1',
        'section': 'WEBBOARD',
        'headline': '웹보드 시장은 일반 시장의 1.6배 속도로 크고 있다',
        'interpretation': '일반 게임 시장 +13% 성장할 때 웹보드는 <strong>+21% 성장</strong>. 규제 시장임에도 성장성 유지. 이유는 ARPMAU가 <strong>일반 시장(13,263원) 대비 20% 높은 15,429원</strong> — 소수 고과금 유저의 결제 밀도가 매우 높음.',
        'evidence': [
            ('웹보드 시장 전후', '137억 → 168억 (+30억, +22%)'),
            ('일반 KR 시장 전후', '4,109 → 4,654억 (+13%)'),
            ('웹보드 ARPMAU', '15,429원 (일반 시장의 1.16배)'),
            ('웹보드 MAU', '-21% 감소'),
            ('요점', '규제 시장 + 고래 유저 + 중독성 → 매출 효율은 일반 시장 추월'),
        ],
    },
    {
        'id': 'wb-2',
        'section': 'WEBBOARD',
        'headline': 'NHN은 웹보드에서 절대 강자 (74% 점유)',
        'interpretation': 'KR 메인 게임 시장이 양극화되는 와중에 <strong>NHN은 웹보드 내에서 점유율 74%로 독점적 지위 유지</strong>. 경쟁사 네오위즈(피망) 15%대의 4~5배 격차. 이 도메인 자체는 NHN의 프리미엄 영역.',
        'evidence': [
            ('NHN 웹보드 점유율', "'22 62.7% → '25 79.2% 피크 → '26.1Q 73.6%"),
            ('네오위즈 점유율', "'22 25.1% → '26.1Q 15.4%"),
            ('Zempot WPL 점유율', "'22 0.4% → '26.1Q 9.4%"),
            ('요점', 'NHN 점유율은 4배 격차 유지 but 26.1Q에 Zempot 부상으로 79%→74% 소폭 조정'),
        ],
    },
    {
        'id': 'wb-3',
        'section': 'WEBBOARD',
        'headline': 'NHN 3종은 4년간 단 1개월도 안 빠졌다',
        'interpretation': '한게임 포커·섯다&맞고·포커클래식 <strong>3종 모두 TOP 100 51개월 전 기간 연속 체류</strong>. 일반 모바일 게임 평균 수명(12개월 생존율 40%)과 비교하면 웹보드는 완전히 다른 카테고리. 동시에 3종 모두 매출 <strong>+8%~+44% 성장</strong>.',
        'evidence': [
            ('한게임 포커', '40→43억 (+8%) · 51개월 무중단'),
            ('한게임 섯다&맞고', '27→39억 (+44%) · 51개월 무중단'),
            ('한게임포커 클래식', '27→34억 (+26%) · 51개월 무중단'),
            ('한게임 신맞고', '9→9억 (0%) · 51개월 무중단'),
            ('요점', '3종 모두 무중단 + 성장 = 포트폴리오의 강인함'),
        ],
    },
    {
        'id': 'wb-4',
        'section': 'WEBBOARD',
        'headline': 'WPL(Zempot)이 5배 급성장 — 신흥 위협 1순위',
        'interpretation': '25년 8월까지 3억대였던 WPL이 <strong>25년 9월 13.4억으로 급등, 현재 19억대</strong>. 원인은 <strong>오프라인 대회(WPH, 상금 10억) + 50만원 고단가 패키지 + 임요환 등 프로 선수 활용 스포츠 브랜딩</strong>. 단순 게임이 아닌 "이스포츠 플랫폼"으로 전환.',
        'evidence': [
            ('25.7월 WPL 매출', '3.2억'),
            ('25.8월 WPL 매출', '3.7억'),
            ('25.9월 WPL 매출', '13.4억 (3.6배 급등)'),
            ('26.3월 WPL 매출', '19.0억'),
            ('급성장 요인 (외부)', '① 오프라인 대회 WPH 상금 10억 확대 · ② 50만원+ 고단가 패키지 · ③ 임요환 라이브 콘텐츠 · ④ 리그 생태계 상설화'),
            ('요점', '"실력 기반 스포츠" 프레임 — 국내 웹보드 규제(5만원 한도) 우회 + 프리미엄 타겟'),
        ],
    },
    {
        'id': 'wb-5',
        'section': 'WEBBOARD',
        'headline': '네오위즈는 30억대에서 4년째 멈춰 있다',
        'interpretation': '피망 포커·뉴맞고 합계 <strong>30억대 정체 (2022~2026)</strong>. 광고 유입률이 NHN 대비 1/4~1/5 수준 — <strong>마케팅 투자 부재로 브랜드 영향력 약화</strong>. 이 틈을 WPL이 파고드는 중.',
        'evidence': [
            ('네오위즈 2게임 합', "'22 32.3억 → '26.1Q 30.2억 (-7%)"),
            ('Pmang Poker 광고유입률', '20.6% (NHN 포커 32.1% 대비 2/3)'),
            ('피망 뉴맞고 광고유입률', '9.3% (NHN 신맞고 45.1% 대비 1/5)'),
            ('요점', '정체된 네오위즈 + 급성장하는 WPL → 웹보드 3위 자리가 교체 중'),
        ],
    },

    # ============ 전략 시사점 (2개) ============
    {
        'id': 'strategy-1',
        'section': 'STRATEGY',
        'headline': 'NHN의 진짜 강점은 "도메인 독점"',
        'interpretation': 'KR 일반 게임 시장에서는 점유율 방어도 어려운 상황(중화권 급습). 반면 NHN은 <strong>웹보드라는 특수 도메인에서 74% 독점</strong>. 규제 시장이라 중화권도 진입 어렵고, 51개월 무중단 수명은 자산. <strong>웹보드는 NHN의 "해자(moat)"</strong>.',
        'evidence': [
            ('NHN KR 일반 시장 점유율', '약 3% (TOP5 중 5위)'),
            ('NHN 웹보드 점유율', '74% (독점적 지위)'),
            ('수명 비교', '일반 게임 12개월 생존율 40% vs 웹보드 NHN 3종 100%'),
            ('ARPMAU 비교', '일반 13,263원 vs 웹보드 15,429원'),
            ('요점', 'NHN 전략은 "일반 게임 확장"보다 "웹보드 강화 + 글로벌 확장"이 효율적'),
        ],
    },
    {
        'id': 'strategy-2',
        'section': 'STRATEGY',
        'headline': 'US 진출하면 KR 상위권 매출이 100위권에서 나온다',
        'interpretation': 'US 시장 100위 게임이 <strong>43~86억/월</strong> — KR 20위권 수준. 즉 US 중위권만 안착해도 KR 상위권 이상 매출. NHN 웹보드가 US 진출하면 <strong>중위권 포지션만 잡아도 현재 KR 매출의 2~3배</strong> 잠재력.',
        'evidence': [
            ('KR 1위 월평균', '510억'),
            ('KR 20위 월평균', '42~62억'),
            ('US 1위 월평균', '2,267억 (KR의 4.4배)'),
            ('US 100위 월평균', '43~86억 (≈ KR 20위)'),
            ('요점', 'US 100위 = KR 20위 수준 → 진입만 하면 KR 대비 3~4배 매출 가능성'),
        ],
    },
]

SECTION_META = {
    'KR':       ('🇰🇷 한국 시장',    '#3b82f6', '#dbeafe'),
    'JP':       ('🇯🇵 일본 시장',    '#ef4444', '#fee2e2'),
    'US':       ('🇺🇸 미국 시장',    '#a855f7', '#f3e8ff'),
    'COMMON':   ('🌏 3국 공통 트렌드', '#64748b', '#f1f5f9'),
    'WEBBOARD': ('🎴 웹보드 심층',   '#0085ca', '#e0f2fe'),
    'STRATEGY': ('🎯 전략 시사점',   '#d97706', '#fef3c7'),
}

def build_insight(ins):
    color, bg = SECTION_META[ins['section']][1], SECTION_META[ins['section']][2]
    evidence_html = ''
    for label, value in ins['evidence']:
        is_summary = label == '요점'
        if is_summary:
            evidence_html += f'<li class="evidence-item summary"><span class="ev-label">💡 요점</span><span class="ev-value">{value}</span></li>'
        else:
            evidence_html += f'<li class="evidence-item"><span class="ev-label">{label}</span><span class="ev-value">{value}</span></li>'

    return f'''<details class="insight" id="{ins['id']}" style="--accent:{color}; --bg:{bg};">
      <summary>
        <div class="headline">{ins['headline']}</div>
        <div class="expand-hint">근거 보기 ▸</div>
      </summary>
      <div class="body">
        <div class="interpretation">{ins['interpretation']}</div>
        <ul class="evidence-list">{evidence_html}</ul>
      </div>
    </details>'''

# 섹션별 그룹핑
sections_html = ''
for sec_key in ['KR','JP','US','COMMON','WEBBOARD','STRATEGY']:
    sec_name, color, bg = SECTION_META[sec_key]
    items = [i for i in INSIGHTS if i['section'] == sec_key]
    if not items: continue
    insight_html = ''.join(build_insight(i) for i in items)
    sections_html += f'''
<div class="section" style="--sec-color:{color}; --sec-bg:{bg};">
  <div class="section-header">
    <div class="section-title">{sec_name}</div>
    <div class="section-count">{len(items)}개 인사이트</div>
  </div>
  {insight_html}
</div>'''

# TL;DR 카드들
tldr_cards = f'''
<div class="tldr-grid">
  <div class="tldr-card" style="--c:#3b82f6;">
    <div class="tldr-label">KR 시장</div>
    <div class="tldr-value">+13%</div>
    <div class="tldr-sub">4,109억 → 4,654억<br>중화권이 단독 견인</div>
  </div>
  <div class="tldr-card" style="--c:#ef4444;">
    <div class="tldr-label">JP 시장</div>
    <div class="tldr-value">-4%</div>
    <div class="tldr-sub">9,306억 → 8,969억<br>자국 IP 노후화</div>
  </div>
  <div class="tldr-card" style="--c:#a855f7;">
    <div class="tldr-label">US 시장</div>
    <div class="tldr-value">+17%</div>
    <div class="tldr-sub">1.68조 → 1.97조<br>Last War 메가히트</div>
  </div>
  <div class="tldr-card" style="--c:#0085ca;">
    <div class="tldr-label">웹보드 시장</div>
    <div class="tldr-value">+22%</div>
    <div class="tldr-sub">137억 → 168억<br>NHN 점유율 74%</div>
  </div>
</div>'''

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NHN 시장 분석 — 임원 보고용 핵심 인사이트</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Noto Sans KR',sans-serif; background:#f5f7fa; color:#1e293b; padding:40px 20px; line-height:1.6; }}
  .container {{ max-width:980px; margin:0 auto; }}

  /* Header */
  .header {{ background:linear-gradient(135deg,#1e293b,#0f172a); color:#fff; border-radius:14px; padding:32px 36px; margin-bottom:24px; box-shadow:0 4px 16px rgba(0,0,0,0.1); }}
  h1 {{ font-size:1.6rem; font-weight:800; margin-bottom:8px; letter-spacing:-0.5px; }}
  .header .subtitle {{ font-size:0.88rem; color:#cbd5e1; font-weight:400; line-height:1.6; }}
  .header .meta {{ margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.1); font-size:0.78rem; color:#94a3b8; }}

  /* TL;DR */
  .tldr-section {{ margin-bottom:28px; }}
  .tldr-label-main {{ font-size:0.82rem; font-weight:700; color:#475569; margin-bottom:12px; display:flex; align-items:center; gap:8px; }}
  .tldr-label-main::before {{ content:""; width:4px; height:16px; background:#0f172a; border-radius:2px; }}
  .tldr-grid {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; }}
  .tldr-card {{ background:#fff; border-radius:10px; padding:16px 18px; border-top:4px solid var(--c); box-shadow:0 2px 8px rgba(0,0,0,0.05); }}
  .tldr-label {{ font-size:0.72rem; color:#64748b; font-weight:600; }}
  .tldr-value {{ font-size:1.8rem; color:var(--c); font-weight:800; margin:4px 0; letter-spacing:-1px; }}
  .tldr-sub {{ font-size:0.68rem; color:#94a3b8; line-height:1.5; }}

  /* Section */
  .section {{ margin-bottom:28px; }}
  .section-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; padding-bottom:8px; border-bottom:2px solid var(--sec-color); }}
  .section-title {{ font-size:1.15rem; font-weight:800; color:var(--sec-color); }}
  .section-count {{ font-size:0.78rem; color:#94a3b8; font-weight:600; background:var(--sec-bg); padding:3px 10px; border-radius:12px; }}

  /* Insight */
  .insight {{ background:#fff; border:1px solid #e2e8f0; border-radius:10px; margin-bottom:10px; overflow:hidden; transition:all 0.2s; }}
  .insight[open] {{ box-shadow:0 4px 16px rgba(0,0,0,0.08); border-color:var(--accent); }}
  .insight summary {{ list-style:none; cursor:pointer; padding:18px 22px; display:flex; align-items:center; justify-content:space-between; gap:16px; background:#fff; transition:background 0.2s; }}
  .insight summary::-webkit-details-marker {{ display:none; }}
  .insight summary:hover {{ background:var(--bg); }}
  .insight[open] summary {{ background:var(--bg); border-bottom:1px solid #e2e8f0; }}
  .insight .headline {{ font-size:1rem; font-weight:700; color:#1e293b; flex:1; }}
  .insight .expand-hint {{ font-size:0.75rem; color:var(--accent); font-weight:600; white-space:nowrap; }}
  .insight[open] .expand-hint::after {{ content:""; }}
  .insight[open] .expand-hint {{ opacity:0.6; }}

  .insight .body {{ padding:20px 22px; background:#fafbfc; }}
  .interpretation {{ font-size:0.92rem; color:#334155; line-height:1.75; padding:14px 18px; background:#fff; border-left:4px solid var(--accent); border-radius:0 6px 6px 0; margin-bottom:16px; }}
  .interpretation strong {{ color:var(--accent); font-weight:700; }}

  /* Evidence */
  .evidence-list {{ list-style:none; display:flex; flex-direction:column; gap:6px; }}
  .evidence-item {{ display:grid; grid-template-columns:180px 1fr; gap:14px; font-size:0.82rem; padding:8px 12px; background:#fff; border-radius:6px; border:1px solid #f1f5f9; }}
  .evidence-item .ev-label {{ color:#64748b; font-weight:600; }}
  .evidence-item .ev-value {{ color:#1e293b; font-variant-numeric:tabular-nums; }}
  .evidence-item .ev-value strong {{ color:var(--accent); }}
  .evidence-item.summary {{ background:#fef3c7; border-color:#fbbf24; }}
  .evidence-item.summary .ev-label {{ color:#b45309; font-weight:700; }}
  .evidence-item.summary .ev-value {{ color:#78350f; font-weight:600; }}

  /* Footer */
  .footer {{ text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:32px; padding:16px; border-top:1px solid #e2e8f0; }}

  @media (max-width:768px) {{
    .tldr-grid {{ grid-template-columns:1fr 1fr; }}
    .evidence-item {{ grid-template-columns:1fr; gap:4px; }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>📊 NHN 시장 분석 — 핵심 인사이트 리포트</h1>
    <div class="subtitle">
      KR · JP · US 3국 시장 + 웹보드 심층 · 2022 ~ 2026.1Q 기간 분석<br>
      각 인사이트를 클릭하면 근거 데이터가 펼쳐집니다 (20개 핵심)
    </div>
    <div class="meta">
      기준: dw_app_monthly · in_revenue_top100_unified_os=TRUE · iOS+Android 합산 · revenue_krw_100 (ST 100% 보정 + 연도별 환율)<br>
      전/후 비교: 전(22~24, 36개월 월평균) vs 후(25~26.1Q, 15개월 월평균)
    </div>
  </div>

  <div class="tldr-section">
    <div class="tldr-label-main">한 줄 요약 (TL;DR)</div>
    {tldr_cards}
  </div>

  {sections_html}

  <div class="footer">
    출처: Sensor Tower · AI_mobilegame DB · 퍼블 국적 분류: NEXON→KR, FUNFLY→중화권 강제<br>
    총 {len(INSIGHTS)}개 핵심 인사이트
  </div>
</div>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f: f.write(html)
print(f"[저장] {OUT}")
print(f"[크기] {os.path.getsize(OUT)/1024:.1f} KB")
print(f"[인사이트 수] {len(INSIGHTS)}개")
