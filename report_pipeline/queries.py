"""
report_pipeline / queries.py
============================
보고서 각 섹션의 SQL을 **config.py 기준으로 생성**한다.
공통 규칙(국적분류·effective_genre·달력분모)은 여기 한 곳에만 있으므로,
기간을 바꿔도(다음 업데이트) 이 파일은 손대지 않는다 — config.py만 수정.

사용:
    from report_pipeline import queries as Q
    sql = Q.step3_genre("KR")          # KR 장르별(Step3) SQL 문자열
    # 이 문자열을 mcp__postgres__query 또는 psycopg2 로 실행

모든 SQL은 dw_app_monthly, in_revenue_top100_unified_os=TRUE 기준.
매출은 revenue_krw_100 (환율 반영 완료 컬럼), 단위 억원(/1e8).
"""
from . import config as C

KST = "(date AT TIME ZONE 'Asia/Seoul')"
YR  = f"EXTRACT(YEAR FROM {KST})::int"


# ── 공통 CASE 조각 ────────────────────────────────────────────
def nat_case(pub_name="publisher_name", pub_country="publisher_country", agg=False):
    """퍼블리셔 국적 5분류. agg=True면 MAX()로 감싼다(그룹 집계용)."""
    p  = f"MAX({pub_name})"    if agg else pub_name
    pc = f"MAX({pub_country})" if agg else pub_country
    china = ",".join(f"'{c}'" for c in C.CHINA_REGION)
    na    = ",".join(f"'{c}'" for c in C.NORTH_AMERICA)
    return (
        f"CASE WHEN {p} ILIKE '%FUNFLY%' THEN '중화권' "
        f"WHEN {p} ILIKE '%NEXON%' THEN 'KR' "
        f"WHEN {pc} IN ({china}) THEN '중화권' "
        f"WHEN {pc} IN ({na}) THEN '북미' "
        f"WHEN {pc}='Japan' THEN 'JP' "
        f"WHEN {pc}='South Korea' THEN 'KR' "
        f"ELSE '기타' END"
    )


def eff_genre(market):
    """effective_genre. KR만 sub_genre로 RPG를 MMORPG/비MMORPG로 분리."""
    if market == "KR":
        return "COALESCE(lv2_genre, sub_genre, genre)"
    return "COALESCE(lv2_genre, genre)"          # JP/US


# ── 달력분모 월평균 집계 컬럼들 ───────────────────────────────
def _year_col(y, alias):
    return f"ROUND(SUM(krw) FILTER (WHERE yr={y})/12/1e8) AS {alias}"

def _partial_col(alias):
    p = C.PARTIAL
    return (f"ROUND(SUM(krw) FILTER (WHERE d>='{p['start']}' AND d<'{p['end_exclusive']}')"
            f"/{p['months']}/1e8) AS {alias}")

def _pre_col(alias="pre"):
    yrs = ",".join(str(y) for y in C.PRE["years"])
    return f"ROUND(SUM(krw) FILTER (WHERE yr IN ({yrs}))/{C.PRE['months']}/1e8) AS {alias}"

def _post_expr():
    """후(2025+부분) 합계식 (원시, /1e8 전)."""
    fy = ",".join(str(y) for y in C.POST["full_years"])
    p  = C.PARTIAL
    return (f"(SUM(krw) FILTER (WHERE yr IN ({fy}))"
            f"+COALESCE(SUM(krw) FILTER (WHERE d>='{p['start']}' AND d<'{p['end_exclusive']}'),0))")

def _post_col(alias="post"):
    return f"ROUND({_post_expr()}/{C.POST['months']}/1e8) AS {alias}"

def _chg_col(alias="chg"):
    yrs = ",".join(str(y) for y in C.PRE["years"])
    return (f"ROUND({_post_expr()}/{C.POST['months']}/1e8 "
            f"- SUM(krw) FILTER (WHERE yr IN ({yrs}))/{C.PRE['months']}/1e8) AS {alias}")

def _all_period_cols():
    cols = [_year_col(y, f"y{str(y)[2:]}") for y in C.FULL_YEARS]
    cols += [_partial_col("h_partial"), _pre_col(), _post_col(), _chg_col()]
    return ",\n  ".join(cols)


# ── 섹션 쿼리 빌더 ────────────────────────────────────────────
def _base_cte(market, extra_select=""):
    return (
        f"WITH base AS (\n"
        f"  SELECT {YR} AS yr, {KST} AS d, revenue_krw_100 AS krw{extra_select}\n"
        f"  FROM dw_app_monthly\n"
        f"  WHERE country='{market}' AND in_revenue_top100_unified_os=TRUE\n"
        f")"
    )


def step1_market(market):
    """Step1: 국가 시장규모 월평균(연도별 + 전/후). 카드/헤드라인/합계의 원천."""
    return (
        _base_cte(market) + "\n"
        f"SELECT {_all_period_cols()}\nFROM base;"
    )


def step3_genre(market):
    """Step3: 장르별 월평균(달력분모). 행 합 = 합계."""
    eg = eff_genre(market)
    return (
        _base_cte(market, extra_select=f",\n         {eg} AS eg") + "\n"
        f"SELECT eg,\n  {_all_period_cols()}\n"
        f"FROM base\nGROUP BY eg\nORDER BY post DESC NULLS LAST;"
    )


def step2_nationality(market):
    """Step2: 퍼블리셔 국적별 월평균 + 점유율은 후처리(각 nat / 합계)."""
    nat = nat_case()
    return (
        _base_cte(market, extra_select=f",\n         {nat} AS nat") + "\n"
        f"SELECT nat,\n  {_all_period_cols()}\n"
        f"FROM base\nGROUP BY nat\nORDER BY post DESC NULLS LAST;"
    )


def step4_nat_genre(market):
    """Step4: 국적 × 장르 월평균. 표시임계 pre/post>=30억, 변화액 정렬."""
    eg, nat = eff_genre(market), nat_case()
    return (
        _base_cte(market, extra_select=f",\n         {nat} AS nat,\n         {eg} AS eg") + "\n"
        f"SELECT nat, eg,\n  {_all_period_cols()}\n"
        f"FROM base\nGROUP BY nat, eg\n"
        f"HAVING COALESCE(ROUND(SUM(krw) FILTER (WHERE yr IN "
        f"({','.join(str(y) for y in C.PRE['years'])}))/{C.PRE['months']}/1e8),0)>=30 "
        f"OR COALESCE(ROUND({_post_expr()}/{C.POST['months']}/1e8),0)>=30\n"
        f"ORDER BY chg DESC;"
    )


def step5_games(market, threshold=30, nat=None):
    """Step5: 국적별 대표게임 증감(게임=unified_app_id 단위, 달력분모).
    threshold=표시임계(억, 시장 규모에 맞춰 US는 90 등으로 조정). nat 지정 시 필터."""
    natc = nat_case(agg=True)
    yrs  = ",".join(str(y) for y in C.PRE["years"])
    pre_expr  = f"SUM(krw) FILTER (WHERE yr IN ({yrs}))/{C.PRE['months']}/1e8"
    post_expr = f"{_post_expr()}/{C.POST['months']}/1e8"
    nat_filter = f" AND {natc} = '{nat}'" if nat else ""   # HAVING 절 (nat는 집계식)
    return (
        f"WITH base AS (\n"
        f"  SELECT unified_app_id, {YR} AS yr, {KST} AS d, revenue_krw_100 AS krw,\n"
        f"         publisher_name, publisher_country, name\n"
        f"  FROM dw_app_monthly\n"
        f"  WHERE country='{market}' AND in_revenue_top100_unified_os=TRUE\n"
        f")\n"
        f"SELECT {natc} AS nat, MAX(name) AS name,\n"
        f"  {_all_period_cols()}\n"
        f"FROM base\nGROUP BY unified_app_id\n"
        f"HAVING (COALESCE({pre_expr},0)>={threshold} OR COALESCE({post_expr},0)>={threshold}){nat_filter}\n"
        f"ORDER BY nat, ({post_expr} - COALESCE({pre_expr},0)) DESC;"
    )


def combined_genre():
    """3국합산 전체 장르표 (raw genre 기준)."""
    return (
        "WITH base AS (\n"
        f"  SELECT genre AS eg, {YR} AS yr, {KST} AS d, revenue_krw_100 AS krw\n"
        "  FROM dw_app_monthly\n"
        f"  WHERE country IN ({','.join(chr(39)+m+chr(39) for m in C.MARKETS)}) "
        "AND in_revenue_top100_unified_os=TRUE\n"
        ")\n"
        f"SELECT eg,\n  {_all_period_cols()}\n"
        "FROM base GROUP BY eg ORDER BY post DESC NULLS LAST;"
    )


# 각 섹션 → SQL 매핑 (runner가 순회)
def all_queries():
    q = {}
    for m in C.MARKETS:
        q[f"step1_{m}"]  = step1_market(m)
        q[f"step2_{m}"]  = step2_nationality(m)
        q[f"step3_{m}"]  = step3_genre(m)
        q[f"step4_{m}"]  = step4_nat_genre(m)
    q["combined_genre"] = combined_genre()
    return q


if __name__ == "__main__":
    # 생성되는 SQL 확인용
    for name, sql in all_queries().items():
        print(f"\n===== {name} =====\n{sql}")
