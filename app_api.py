from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_경로 = os.path.join(BASE_DIR, "adventureworks_clean.csv")

애플리케이션 = FastAPI(title="어드벤처웍스 CRM 및 매출 예측 API")

데이터프레임 = None
원본_전체 = None
예측모델 = None
업셀_모델 = {}
업셀_정확도 = {}
국가목록 = []
카테고리목록 = []
국가인코더 = None
카테고리인코더 = None
피처중요도 = {}
모델_r2 = 0.0
피처_컬럼 = ["Order Quantity", "Unit Price", "Standard Cost", "Month_num", "Category_enc", "Country_enc"]

계절_월_매핑 = {
    "봄": [3, 4, 5],
    "여름": [6, 7, 8],
    "가을": [9, 10, 11],
    "겨울": [12, 1, 2],
}

US_식별자 = ["United States"]

def 계절_분류(월):
    for 계절, 월목록 in 계절_월_매핑.items():
        if 월 in 월목록:
            return 계절
    return "봄"

class 시뮬레이션입력(BaseModel):
    주문수량: int
    제품단가: float
    제조원가: float
    월코드: int
    선택국가: str
    선택카테고리: str

class 업셀입력(BaseModel):
    주문수량: int
    제품단가: float
    월코드: int
    선택국가: str

@애플리케이션.on_event("startup")
def 시스템초기화():
    global 데이터프레임, 원본_전체, 예측모델, 업셀_모델, 업셀_정확도, 국가목록, 카테고리목록
    global 피처중요도, 모델_r2, 국가인코더, 카테고리인코더

    try:
        원본_전체 = pd.read_csv(CSV_경로)
        원본_전체.columns = 원본_전체.columns.str.strip()
        print(f"CSV loaded: {len(원본_전체)} rows")

        월_유효비율 = ((원본_전체["Month_num"] >= 1) & (원본_전체["Month_num"] <= 12)).mean()
        print(f"Month_num valid ratio: {월_유효비율:.2%}")

        if 월_유효비율 < 0.5:
            try:
                url = "https://github.com/microsoft/powerbi-desktop-samples/raw/main/AdventureWorks%20Sales%20Sample/AdventureWorks%20Sales.xlsx"
                날짜_데이터 = pd.read_excel(url, sheet_name="Date_data")
                월_순서 = ["January","February","March","April","May","June",
                          "July","August","September","October","November","December"]
                날짜_데이터["Month_num_fixed"] = 날짜_데이터["Month"].apply(
                    lambda x: next((i+1 for i,m in enumerate(월_순서) if m.lower() in str(x).lower()), 0)
                )
                datekey_to_month = 날짜_데이터.set_index("DateKey")["Month_num_fixed"].to_dict()
                if "OrderDateKey" in 원본_전체.columns:
                    원본_전체["Month_num"] = 원본_전체["OrderDateKey"].map(datekey_to_month).fillna(0).astype(int)
                    print(f"Month repair done: {((원본_전체['Month_num'] >= 1) & (원본_전체['Month_num'] <= 12)).mean():.2%}")
            except Exception as ex:
                print(f"Month repair failed: {ex}")

        데이터프레임 = 원본_전체.copy()

    except Exception as e:
        print(f"CSV load error: {e} — using fallback")
        난수 = np.random.RandomState(42)
        n = 2000
        나라들 = ["United States", "Australia", "Canada", "United Kingdom", "France", "Germany"]
        카테고리들 = ["Bikes", "Accessories", "Clothing", "Components"]
        월목록 = 난수.randint(1, 13, n)
        카t목록 = 난수.choice(카테고리들, n)
        나라목록 = 난수.choice(나라들, n)
        단가_베이스 = np.where(카t목록 == "Bikes", 난수.uniform(400, 2000, n),
                     np.where(카t목록 == "Components", 난수.uniform(50, 400, n),
                     np.where(카t목록 == "Accessories", 난수.uniform(10, 150, n),
                     난수.uniform(20, 120, n))))
        원가_베이스 = 단가_베이스 * 난수.uniform(0.35, 0.75, n)
        수량 = 난수.randint(1, 6, n)
        매출 = 단가_베이스 * 수량 * (1 + (월목록 / 12) * 0.15)
        원본_전체 = pd.DataFrame({
            "Order Quantity": 수량,
            "Unit Price": 단가_베이스,
            "Standard Cost": 원가_베이스,
            "Sales Amount": 매출,
            "Month_num": 월목록,
            "Country": 나라목록,
            "Category": 카t목록,
            "CustomerKey": 난수.randint(1, 500, n),
            "OrderDateKey": 난수.randint(20130101, 20160101, n),
        })
        데이터프레임 = 원본_전체.copy()

    국가인코더 = LabelEncoder()
    카테고리인코더 = LabelEncoder()
    데이터프레임["Country_enc"] = 국가인코더.fit_transform(데이터프레임["Country"].astype(str))
    데이터프레임["Category_enc"] = 카테고리인코더.fit_transform(데이터프레임["Category"].astype(str))
    국가목록 = list(국가인코더.classes_)
    카테고리목록 = list(카테고리인코더.classes_)
    print(f"Countries: {국가목록}")
    print(f"Categories: {카테고리목록}")

    X = 데이터프레임[피처_컬럼].copy()

    total_revenue = 데이터프레임["Sales Amount"].clip(lower=1)
    total_cost = 데이터프레임["Standard Cost"] * 데이터프레임["Order Quantity"]
    gross_margin = (total_revenue - total_cost) / total_revenue
    gross_margin = gross_margin.clip(-1, 1)

    y_reg = gross_margin

    X_학습, X_검증, y_학습, y_검증 = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    예측모델 = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=3,
        max_features="sqrt",
        random_state=42
    )
    예측모델.fit(X_학습, y_학습)
    모델_r2 = round(float(r2_score(y_검증, 예측모델.predict(X_검증))), 4)
    피처중요도 = {
        피처: round(float(중요도), 4)
        for 피처, 중요도 in zip(피처_컬럼, 예측모델.feature_importances_)
    }
    print(f"Model R²: {모델_r2}")
    print(f"Feature importances: {피처중요도}")

    업셀_피처 = ["Order Quantity", "Unit Price", "Month_num", "Country_enc"]
    업셀_타겟_카테고리 = ["Accessories", "Clothing", "Components"]

    if "CustomerKey" in 데이터프레임.columns:
        bikes_df = 데이터프레임[데이터프레임["Category"] == "Bikes"].copy()

        for 타겟 in 업셀_타겟_카테고리:
            타겟_고객 = set(
                데이터프레임[데이터프레임["Category"] == 타겟]["CustomerKey"]
                .dropna().apply(lambda x: int(float(x))).unique()
            )
            bikes_df[f"bought_{타겟}"] = bikes_df["CustomerKey"].apply(
                lambda k: 1 if int(float(k)) in 타겟_고객 else 0
            )

        for 타겟 in 업셀_타겟_카테고리:
            y_col = f"bought_{타겟}"
            학습용 = bikes_df[업셀_피처 + [y_col]].dropna()
            if len(학습용) < 50 or 학습용[y_col].nunique() < 2:
                continue
            X_u = 학습용[업셀_피처]
            y_u = 학습용[y_col]
            X_u_학습, X_u_검증, y_u_학습, y_u_검증 = train_test_split(
                X_u, y_u, test_size=0.2, random_state=42
            )
            clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
            clf.fit(X_u_학습, y_u_학습)
            업셀_모델[타겟] = clf
            업셀_정확도[타겟] = round(float(clf.score(X_u_검증, y_u_검증)), 4)
            print(f"Upsell [{타겟}] accuracy: {업셀_정확도[타겟]}")

@애플리케이션.get("/api/metadata")
def 메타데이터조회():
    서브카테고리목록 = sorted(데이터프레임["Subcategory"].dropna().unique().tolist()) if "Subcategory" in 데이터프레임.columns else []
    노출_국가목록 = sorted([c for c in 국가목록 if c not in US_식별자])
    return {
        "국가목록": 노출_국가목록,
        "카테고리목록": sorted(카테고리목록),
        "서브카테고리목록": 서브카테고리목록,
        "총레코드수": len(데이터프레임),
        "모델R2": 모델_r2,
        "피처중요도": 피처중요도,
        "업셀정확도": 업셀_정확도,
        "피처수": len(피처_컬럼),
    }

@애플리케이션.get("/api/season/strategy")
def 시즌전략조회():
    us_df = 데이터프레임[데이터프레임["Country"].isin(US_식별자)].copy()
    us_df["계절"] = us_df["Month_num"].apply(계절_분류)

    결과 = {}
    for 계절 in 계절_월_매핑.keys():
        us_계절 = us_df[us_df["계절"] == 계절]
        if len(us_계절) == 0:
            continue

        카테고리별_매출 = (
            us_계절.groupby("Category")["Sales Amount"].sum().sort_values(ascending=False)
        )
        추천카테고리 = 카테고리별_매출.index[0]
        us_계절_총매출 = float(카테고리별_매출.iloc[0])
        us_월목록 = 계절_월_매핑[계절]

        국가별분석 = []
        비US_국가들 = [c for c in 국가목록 if c not in US_식별자]
        for 국가 in 비US_국가들:
            국가_계절_df = 데이터프레임[
                (데이터프레임["Country"] == 국가) &
                (데이터프레임["Month_num"].isin(us_월목록))
            ]
            국가_카테고리_매출 = float(
                국가_계절_df[국가_계절_df["Category"] == 추천카테고리]["Sales Amount"].sum()
            )
            격차 = round(us_계절_총매출 - 국가_카테고리_매출, 2)
            침투율 = round(
                (국가_카테고리_매출 / us_계절_총매출 * 100) if us_계절_총매출 > 0 else 0.0, 1
            )
            국가별분석.append({
                "국가": 국가,
                "현재매출": round(국가_카테고리_매출, 2),
                "미국매출": round(us_계절_총매출, 2),
                "격차": 격차,
                "미국대비침투율": 침투율,
            })

        국가별분석.sort(key=lambda x: x["격차"], reverse=True)

        us_계절_카테고리_전체 = (
            us_계절.groupby("Category")["Sales Amount"]
            .sum().reset_index()
            .rename(columns={"Sales Amount": "매출"})
            .sort_values("매출", ascending=False)
            .to_dict("records")
        )

        결과[계절] = {
            "추천카테고리": 추천카테고리,
            "미국_계절_총매출": round(us_계절_총매출, 2),
            "카테고리별_미국매출": us_계절_카테고리_전체,
            "국가별분석": 국가별분석,
        }

    return 결과

@애플리케이션.get("/api/crosssell")
def 크로스셀분석():
    df = 데이터프레임.copy()

    if "CustomerKey" in df.columns and "OrderDateKey" in df.columns:
        주문그룹 = df.groupby(["CustomerKey", "OrderDateKey"])["Category"].apply(list).reset_index()
        주문그룹.columns = ["CustomerKey", "OrderDateKey", "카테고리목록"]
        복수주문 = 주문그룹[주문그룹["카테고리목록"].apply(len) > 1]

        페어_카운트: dict = {}
        for _, 행 in 복수주문.iterrows():
            카테고리들 = sorted(set(행["카테고리목록"]))
            for i in range(len(카테고리들)):
                for j in range(i + 1, len(카테고리들)):
                    페어 = (카테고리들[i], 카테고리들[j])
                    페어_카운트[페어] = 페어_카운트.get(페어, 0) + 1

        페어_목록 = [
            {"카테고리A": k[0], "카테고리B": k[1], "동반구매횟수": v}
            for k, v in sorted(페어_카운트.items(), key=lambda x: -x[1])
        ]
    else:
        카테고리_매출 = df.groupby("Category")["Sales Amount"].sum()
        페어_목록 = [
            {"카테고리A": c, "카테고리B": "기타", "동반구매횟수": int(v / 1000)}
            for c, v in 카테고리_매출.items()
        ]

    카테고리별_평균단가 = df.groupby("Category")["Unit Price"].mean().round(2).to_dict()
    카테고리별_총매출 = df.groupby("Category")["Sales Amount"].sum().round(2).to_dict()

    return {
        "동반구매페어": 페어_목록[:10],
        "카테고리별_평균단가": 카테고리별_평균단가,
        "카테고리별_총매출": 카테고리별_총매출,
    }

@애플리케이션.get("/api/subcategory/bikes")
def 자전거서브카테고리분석():
    필요컬럼 = ["Subcategory", "Category", "Sales Amount", "Month_num", "Unit Price"]
    누락컬럼 = [c for c in 필요컬럼 if c not in 데이터프레임.columns]
    if 누락컬럼:
        bike_서브카테고리 = ["Mountain Bikes", "Road Bikes", "Touring Bikes"]
        결과 = {}
        for 서브 in bike_서브카테고리:
            결과[서브] = {
                "총매출": 0.0, "평균단가": 0.0,
                "동반구매카테고리": [],
                "계절별매출": [{"계절": s, "매출": 0.0} for s in ["봄", "여름", "가을", "겨울"]],
            }
        return 결과

    bike_서브카테고리 = 데이터프레임[데이터프레임["Category"] == "Bikes"]["Subcategory"].dropna().unique().tolist()
    결과 = {}

    for 서브카테고리 in sorted(bike_서브카테고리):
        서브_구매자 = 데이터프레임[데이터프레임["Subcategory"] == 서브카테고리]

        if "CustomerKey" in 데이터프레임.columns:
            유효_고객키 = pd.to_numeric(
                서브_구매자["CustomerKey"], errors="coerce"
            ).dropna().apply(lambda x: int(float(x))).unique()
            유효_고객키 = [k for k in 유효_고객키 if k > 0]
        else:
            유효_고객키 = []

        if len(유효_고객키) > 0:
            ck_series = pd.to_numeric(데이터프레임["CustomerKey"], errors="coerce")
            동반구매_df = 데이터프레임[
                ck_series.isin(유효_고객키) & (데이터프레임["Category"] != "Bikes")
            ]
        else:
            동반구매_df = 데이터프레임[데이터프레임["Category"] != "Bikes"]

        동반카테고리 = (
            동반구매_df.groupby("Category")["Sales Amount"]
            .agg(총매출="sum", 구매건수="count")
            .reset_index()
            .sort_values("총매출", ascending=False)
            .to_dict("records")
        )

        계절별_매출 = []
        서브_df = 데이터프레임[데이터프레임["Subcategory"] == 서브카테고리].copy()
        서브_df["계절"] = 서브_df["Month_num"].apply(계절_분류)
        for 계절 in ["봄", "여름", "가을", "겨울"]:
            매출합 = float(서브_df[서브_df["계절"] == 계절]["Sales Amount"].sum())
            계절별_매출.append({"계절": 계절, "매출": round(매출합, 2)})

        총매출 = float(서브_df["Sales Amount"].sum())
        평균단가 = float(서브_df["Unit Price"].mean()) if len(서브_df) > 0 else 0.0

        결과[서브카테고리] = {
            "총매출": round(총매출, 2),
            "평균단가": round(평균단가, 2),
            "동반구매카테고리": 동반카테고리,
            "계절별매출": 계절별_매출,
        }

    return 결과

@애플리케이션.post("/api/predict/strategy")
def 전략예측실행(요청데이터: 시뮬레이션입력):
    국가_arr = list(국가인코더.classes_)
    카테고리_arr = list(카테고리인코더.classes_)
    국가인덱스 = 국가_arr.index(요청데이터.선택국가) if 요청데이터.선택국가 in 국가_arr else 0
    카테고리인덱스 = 카테고리_arr.index(요청데이터.선택카테고리) if 요청데이터.선택카테고리 in 카테고리_arr else 0

    예측입력 = pd.DataFrame([{
        "Order Quantity": 요청데이터.주문수량,
        "Unit Price": 요청데이터.제품단가,
        "Standard Cost": 요청데이터.제조원가,
        "Month_num": 요청데이터.월코드,
        "Category_enc": 카테고리인덱스,
        "Country_enc": 국가인덱스,
    }])

    예측_마진율 = float(예측모델.predict(예측입력)[0])
    예측_마진율 = max(-1.0, min(1.0, 예측_마진율))
    예측매출 = 요청데이터.제품단가 * 요청데이터.주문수량 * (1 + 예측_마진율 * 0.15)

    조건df = 데이터프레임[
        (데이터프레임["Country"] == 요청데이터.선택국가) &
        (데이터프레임["Month_num"] == 요청데이터.월코드)
    ]
    if len(조건df) == 0:
        조건df = 데이터프레임[데이터프레임["Country"] == 요청데이터.선택국가]

    카테고리건수 = len(조건df[조건df["Category"] == 요청데이터.선택카테고리])
    총건수 = len(조건df)
    시장점유율 = (카테고리건수 / 총건수) if 총건수 > 0 else 0.25

    return {
        "예측매출액": max(0.0, round(예측매출, 2)),
        "시장점유율": round(시장점유율 * 100, 1),
        "예측마진율": round(예측_마진율 * 100, 1),
    }

@애플리케이션.post("/api/predict/upsell")
def 업셀예측(요청데이터: 업셀입력):
    국가_arr = list(국가인코더.classes_)
    국가인덱스 = 국가_arr.index(요청데이터.선택국가) if 요청데이터.선택국가 in 국가_arr else 0

    입력df = pd.DataFrame([{
        "Order Quantity": 요청데이터.주문수량,
        "Unit Price": 요청데이터.제품단가,
        "Month_num": 요청데이터.월코드,
        "Country_enc": 국가인덱스,
    }])

    결과 = {}
    업셀_타겟_카테고리 = ["Accessories", "Clothing", "Components"]
    계절 = 계절_분류(요청데이터.월코드)

    추천문구 = {
        "Accessories": {
            "봄": "봄 시즌 라이딩에 헬멧·타이어·잠금장치 번들을 함께 제안하세요.",
            "여름": "여름 장거리 라이딩 시즌, 수분팩·캐리어 번들이 효과적입니다.",
            "가을": "가을 통근 수요에 맞춰 라이트·펜더 패키지를 추천하세요.",
            "겨울": "겨울 실내 훈련 고객에게 바이크 스탠드·보틀 세트를 제안하세요.",
        },
        "Clothing": {
            "봄": "봄 시즌 라이더에게 저지·장갑 세트로 스타일 업셀을 노리세요.",
            "여름": "여름 고온 대비 통기성 저지·반바지 세트가 잘 팔립니다.",
            "가을": "가을 방풍 조끼·긴 타이즈 세트로 시즌 전환 수요를 잡으세요.",
            "겨울": "겨울 방한 저지·양말·장갑 풀세트 번들을 체크아웃 시점에 제안하세요.",
        },
        "Components": {
            "봄": "봄 시즌 업그레이드 수요에 맞춰 프레임·휠 패키지를 제안하세요.",
            "여름": "여름 레이싱 시즌, 경량 크랭크셋·핸들바 업그레이드를 추천하세요.",
            "가을": "가을 오버홀 시즌, 페달·휠 교체 패키지가 유효합니다.",
            "겨울": "겨울 비수기, 컴포넌트 선구매 할인으로 재방문을 유도하세요.",
        },
    }

    for 타겟 in 업셀_타겟_카테고리:
        if 타겟 not in 업셀_모델:
            결과[타겟] = {"확률": 50.0, "예측": "알 수 없음", "정확도": 0.0, "추천": 추천문구[타겟][계절]}
            continue
        clf = 업셀_모델[타겟]
        확률배열 = clf.predict_proba(입력df)[0]
        클래스목록 = list(clf.classes_)
        확률 = float(확률배열[클래스목록.index(1)]) * 100 if 1 in 클래스목록 else 50.0
        결과[타겟] = {
            "확률": round(확률, 1),
            "예측": "구매 가능성 높음" if 확률 >= 50 else "구매 가능성 낮음",
            "정확도": 업셀_정확도.get(타겟, 0.0),
            "추천": 추천문구[타겟][계절],
        }

    결과_정렬 = dict(sorted(결과.items(), key=lambda x: x[1]["확률"], reverse=True))
    최고카테고리 = list(결과_정렬.keys())[0]

    return {
        "카테고리별예측": 결과_정렬,
        "최고추천카테고리": 최고카테고리,
        "계절": 계절,
    }

@애플리케이션.get("/api/country/price_range")
def 국가별단가범위조회():
    결과 = {}
    비US = [c for c in 국가목록 if c not in US_식별자]
    for 국가 in 비US:
        국가df = 데이터프레임[데이터프레임["Country"] == 국가]
        cat_가격 = {}
        for 카t in 카테고리목록:
            sub = 국가df[국가df["Category"] == 카t]["Unit Price"]
            if len(sub) > 0:
                cat_가격[카t] = {
                    "mean": round(float(sub.mean()), 2),
                    "std": round(float(sub.std()), 2),
                    "min": round(float(sub.min()), 2),
                    "max": round(float(sub.max()), 2),
                }
            else:
                cat_가격[카t] = {"mean": 462.0, "std": 200.0, "min": 10.0, "max": 2000.0}
        결과[국가] = cat_가격
    return 결과
