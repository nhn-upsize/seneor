"""verify/*.py 가 실제로 실행하는 SQL을 가로채서 queries/manual/ 로 추출.

사용:  python -m report_pipeline.extract_manual_sql

verify 스크립트를 고쳤으면 이걸 다시 돌려 queries/manual/ 을 갱신하세요.
그래야 파이썬(정본)과 .sql 사본이 갈라지지 않습니다.


psycopg2.connect 를 가짜 객체로 바꿔치기해 DB 없이 실행하고,
cursor.execute() 에 넘어온 최종 SQL(치환 완료)을 수집한다.
스크립트 1개 → .sql 파일 1개, 그 안에 쿼리들을 주석으로 구분.
"""
import io, re, runpy, sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "queries" / "manual"

SECTIONS = {
    "01_시장총계": ["verify_all_sum", "verify_jp_all", "verify_us_all",
                    "verify_kr_dl", "verify_mau_arpmau"],
    "02_퍼블리셔": ["verify_kr_top5", "verify_kr_market_composition",
                    "verify_kr_etc_game_count", "verify_kr_etc_pub_monthly",
                    "verify_kr_etc_pub_v2", "verify_kr_etc_pub_v3",
                    "verify_kr_etc_publisher_count", "check_publisher_share"],
    "03_장르":     ["verify_kr_strategy", "check_step4_values"],
    "04_웹보드":   ["verify_wb_quarterly", "verify_wb_all4",
                    "verify_wb_exclude_disney", "verify_wb_kr_pub",
                    "query_webboard_data", "query_wpl_check"],
    "05_신규진입": ["verify_kr_newgame_genre"],
}
SECTION_OF = {s: sec for sec, lst in SECTIONS.items() for s in lst}

collected = []


class Buf(io.StringIO):
    def reconfigure(self, *a, **k):   # 스크립트의 sys.stdout.reconfigure 대응
        pass


class FakeCursor:
    description = None

    def execute(self, sql, params=None):
        collected.append(str(sql))

    def fetchone(self):
        return (0,) * 40

    def fetchall(self):
        return []

    def close(self):
        pass

    def __iter__(self):
        return iter([])


class FakeConn:
    def cursor(self, *a, **k):
        return FakeCursor()

    def __getattr__(self, n):
        return lambda *a, **k: None


import psycopg2
psycopg2.connect = lambda *a, **k: FakeConn()


def norm(sql):
    lines = [l.rstrip() for l in sql.strip("\n").split("\n") if l.strip()]
    if not lines:
        return ""
    pad = min(len(l) - len(l.lstrip()) for l in lines)
    return "\n".join(l[pad:] for l in lines).strip()


def dedup(sqls):
    """리터럴·숫자만 다른 반복 실행을 하나로."""
    seen, out = set(), []
    for s in sqls:
        n = norm(s)
        if len(n) < 40 or not re.search(r"\bSELECT\b", n, re.I):
            continue
        key = re.sub(r"'[^']*'", "'X'", n)
        key = re.sub(r"\d+", "N", key)
        key = re.sub(r"\s+", " ", key)
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out


HEAD = """\
-- ============================================================
--  {title}
--  출처: verify/{stem}.py  (SQL을 실행 시점에 추출)
--  기준 기간: 26년 2분기 보고서 (2022~2026.1H)
--
--  ⚠️ 3분기에 쓰려면 쿼리 안의 날짜를 직접 늘려야 합니다.
--     이 섹션은 report_pipeline 이 자동화하지 않는 범위입니다.
--     집계 표준은 docs/QUARTERLY.md 참조.
-- ============================================================
"""


def main():
    sys.path.insert(0, str(REPO))
    total = 0
    rows = []

    for py in sorted((REPO / "verify").glob("*.py")):
        stem = py.stem
        collected.clear()
        try:
            with redirect_stdout(Buf()), redirect_stderr(Buf()):
                runpy.run_path(str(py), run_name="__main__")
        except BaseException:
            pass  # 가짜 데이터라 중간에 죽는 건 정상

        uniq = dedup(collected)
        if not uniq:
            print(f"  (SQL 없음) {stem}")
            continue

        title = ""
        m = re.search(r'"""(.*?)"""', py.read_text(encoding="utf-8"), re.S)
        if m:
            title = m.group(1).strip().split("\n")[0]
        title = title or stem

        sec = SECTION_OF.get(stem, "99_기타")
        (OUT / sec).mkdir(parents=True, exist_ok=True)

        body = [HEAD.format(title=title, stem=stem)]
        for i, sql in enumerate(uniq, 1):
            body.append(f"\n-- ── [{i}/{len(uniq)}] ──────────────────────────\n{sql}\n")
        (OUT / sec / f"{stem}.sql").write_text("".join(body), encoding="utf-8")

        rows.append((sec, stem, len(uniq), title))
        total += len(uniq)
        print(f"  {sec}/{stem}.sql — 쿼리 {len(uniq)}개")

    print(f"\n파일 {len(rows)}개 / 쿼리 {total}개")
    return rows


if __name__ == "__main__":
    main()
