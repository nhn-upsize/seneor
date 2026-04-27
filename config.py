"""
프로젝트 공통 설정
"""

# ── 중화권 국가 코드 ──────────────────────────────────────────────
# 중국 본토(CN) + 홍콩(HK) + 대만(TW) + 마카오(MO)를 모두 CN으로 통합
CHINESE_REGION_CODES = ["CN", "HK", "TW", "MO"]

# 분석에서 표시되는 레이블 → 실제 API 조회 국가코드 목록 매핑
COUNTRY_GROUP = {
    "KR": ["KR"],
    "JP": ["JP"],
    "US": ["US"],
    "CN": CHINESE_REGION_CODES,  # 중화권 전체
}

# 기본 분석 대상 국가 레이블 (이 순서 유지)
DEFAULT_COUNTRIES = ["KR", "JP", "US", "CN"]


def expand_country(label: str) -> list:
    """
    분석 레이블 → 실제 API 조회에 쓸 국가 코드 리스트 반환.
    예) "CN" → ["CN", "HK", "TW", "MO"]
        "KR" → ["KR"]
    """
    return COUNTRY_GROUP.get(label, [label])


def normalize_country(cc: str) -> str:
    """
    API 응답의 cc 필드 → 분석 레이블로 변환.
    예) "HK" → "CN", "TW" → "CN", "MO" → "CN"
        "KR" → "KR"
    """
    if cc in CHINESE_REGION_CODES:
        return "CN"
    return cc


def is_target_country(cc: str, label: str) -> bool:
    """
    API 응답의 cc가 분석 레이블에 해당하는지 확인.
    예) is_target_country("HK", "CN") → True
        is_target_country("KR", "CN") → False
    """
    return cc in expand_country(label)
