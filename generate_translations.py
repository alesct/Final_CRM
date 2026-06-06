import json, os, hashlib
from deep_translator import GoogleTranslator

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations_cache.json")

ALL_STRINGS = [
    "마케팅 이론의 관점에서", "분석 및 예측", "학습 레코드 수", "모델 R² Score", "입력 피처 수",
    "매출 및 예측 리포트", "시즌별 전략 추천", "피처 중요도 — Random Forest Gini",
    "알고리즘", "트리 수", "학습/검증 분할", "데이터 소스", "전처리",
    "IQR 이상치 제거, LabelEncoder", "타겟 변수", "API 프레임워크",
    "FastAPI 백엔드 연결됨", "서버 연결 실패 — uvicorn 실행 여부 확인",
    "주문 수량", "제품 단가", "제조 원가", "월 코드", "카테고리", "국가",
    "매출 및 예측 리포트", "← 홈",
    "AdventureWorks 판매 데이터 기반 실적 분석 및 AI 예측. 핵심 제품은 자전거(Bikes)로 전체 매출의 약 70~80%를 차지합니다.",
    "실적 현황 — 실제 데이터", "예측 시뮬레이션 — 판매 계획",
    "전체 매출 요약 — 실제 데이터 기준", "총 매출액", "총 주문 수량", "평균 단가", "전체 레코드 수",
    "서브카테고리별 총 매출", "국가별 총 매출", "카테고리별 매출 비중",
    "세계 판매 지도 — 국가별 매출 현황", "총매출($)",
    "판매 계획 설정 — 수량·단가·국가를 선택하면 AI가 수익을 예측합니다",
    "거래 유형", "일반 개인 고객", "도매 및 대리점", "판매 카테고리", "서브카테고리", "전체 (평균)",
    "수량", "단가 ($)", "원가 ($)", "분석 월", "전체 국가",
    "매출 산출 방식", "개", "제품 단가", "예측 총 매출", "총 제조 원가", "마진율", "순수익 추정",
    "도매 매출", "총 원가", "순수익", "주문 수량", "금액 ($)", "예측 매출", "구매 수량", "예측 매출 ($)",
    "전체 국가 비교 — 동일 조건으로 국가별 예측 매출 및 순수익", "국가별 예측 계산 중…",
    "예측 매출 ($)", "총 원가 ($)", "순수익 ($)",
    "3D 예측 곡면 — 수량 × 단가 × 예측 매출",
    "X축: 수량, Y축: 단가 범위 (현재 설정 ±50%), Z축: AI 예측 매출. 드래그로 회전하세요.",
    "예측매출($)", "순수익($)", "단가($)",
    "시즌별 전략 추천",
    "미국 실적을 기준으로 시즌별 최고 카테고리를 타국가에 이식하기 위한 전략과, 자전거 구매와 연계한 크로스셀링 분석을 제공합니다.",
    "분석 시즌", "국가 필터",
    "봄", "여름", "가을", "겨울",
    "시즌별 매출 예측", "크로스셀링 분석",
    "시즌별 AI 매출 예측 — 판매 시뮬레이션",
    "선택한 시즌·카테고리·수량·단가로 각 국가별 예상 매출과 순수익을 실시간으로 예측합니다.",
    "일반 개인 고객 (B2C)", "도매 및 대리점 (B2B)",
    "판매 수량", "제품 단가 ($)", "제조 원가 ($)",
    "시즌별 예측 계산 중…", "전체 예측 총 매출", "전체 예측 순수익", "최고 예측 국가",
    "도매 단가 기반",
    "자전거 구매 연계 크로스셀링 분석",
    "자전거(Bikes) 구매 고객이 함께 구매한 카테고리·서브카테고리 패턴과 시즌별 분포를 CSV 실제 데이터 기반으로 분석합니다.",
    "adventureworks_clean.csv 파일을 찾을 수 없습니다.",
    "카테고리 또는 매출 컬럼을 찾을 수 없습니다.",
    "Bikes 총 매출", "전체 매출 중 Bikes 비중", "최다 동반 구매 카테고리",
    "Bikes 구매 고객의 동반 구매 카테고리", "카테고리별 시즌 매출 패턴",
    "매출 ($)", "시즌별 데이터를 계산할 수 없습니다.",
    "크로스셀 전략 추천", "주요 서브카테고리", "시즌 인사이트",
]

ALL_STRINGS = list(set(ALL_STRINGS))

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

cache = load_cache()

for dest in ["en", "es", "ru"]:
    to_fetch = []
    for text in ALL_STRINGS:
        key = f"{dest}::{hashlib.md5(text.encode()).hexdigest()}"
        if key not in cache:
            to_fetch.append(text)

    if not to_fetch:
        print(f"[{dest}] 이미 모두 캐시됨 — 스킵")
        continue

    print(f"[{dest}] {len(to_fetch)}개 번역 중...", end=" ", flush=True)
    try:
        results = GoogleTranslator(source="ko", target=dest).translate_batch(to_fetch)
        for text, result in zip(to_fetch, results):
            key = f"{dest}::{hashlib.md5(text.encode()).hexdigest()}"
            cache[key] = result
        save_cache(cache)
        print(f"완료 ✓")
    except Exception as e:
        print(f"오류: {e}")

print("\n✅ translations_cache.json 생성 완료! 이제 앱이 즉시 번역됩니다.")
