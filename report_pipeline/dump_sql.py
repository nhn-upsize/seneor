"""
report_pipeline / dump_sql.py
=============================
config.py 기준으로 생성되는 섹션 SQL을 **읽을 수 있는 .sql 파일로 떨군다.**

파이프라인 SQL은 파이썬 안에서 만들어지기 때문에, DB 툴에 붙여넣거나
남에게 전달하려면 파일이 필요하다. 기간을 바꾼 뒤 이걸 다시 돌리면
`queries/generated/<기간>/` 아래에 그 기간용 SQL이 새로 떨어진다.

사용:  python -m report_pipeline.dump_sql
       python -m report_pipeline.dump_sql --out queries/generated

주의:  generated/ 는 **손으로 고치지 말 것.** config.py 를 고치고 다시 덤프한다.
"""
import argparse
import sys
from pathlib import Path

from . import config as C
from . import queries as Q

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent

HEADER = """\
-- ============================================================
--  {name}
--  자동 생성 — report_pipeline/queries.py  (직접 수정 금지)
--
--  기간   : 완전연도 {years} + 부분 {plabel}({pstart}~, {pmonths}개월)
--           전 {pre}개월 / 후 {post}개월
--  월평균 : 달력 개월수 고정 분모 (활동월 수 아님)
--  매출   : revenue_krw_100 (환율 반영 완료)
--  국적   : NEXON→KR · FUNFLY→중화권 / 중화권={china}
--
--  기간을 바꾸려면 report_pipeline/config.py 의 PERIOD 블록을 고치고
--  python -m report_pipeline.dump_sql 을 다시 실행하세요.
-- ============================================================

"""


def period_slug():
    """생성물 폴더 이름. 예: 26Y2Q(26.1H) → '26.1H'"""
    return C.PARTIAL["label"].replace("/", "-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="queries/generated",
                    help="출력 폴더 (기본: queries/generated)")
    args = ap.parse_args()

    out_dir = (REPO_ROOT / args.out / period_slug())
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = dict(
        years=", ".join(str(y) for y in C.FULL_YEARS),
        plabel=C.PARTIAL["label"],
        pstart=C.PARTIAL["start"],
        pmonths=C.PARTIAL["months"],
        pre=C.PRE["months"],
        post=C.POST["months"],
        china="/".join(C.CHINA_REGION),
    )

    qs = Q.all_queries()
    for name, sql in qs.items():
        (out_dir / f"{name}.sql").write_text(
            HEADER.format(name=name, **meta) + sql.strip() + "\n",
            encoding="utf-8",
        )

    print(f"[dump_sql] {len(qs)}개 SQL → {out_dir.relative_to(REPO_ROOT).as_posix()}/")
    for name in qs:
        print("  -", f"{name}.sql")
    return 0


if __name__ == "__main__":
    sys.exit(main())
