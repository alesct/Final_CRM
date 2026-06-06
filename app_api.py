from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_경로 = os.path.join(BASE_DIR, "adventureworks_clean.csv")

애플리케이션 = FastAPI(title="어드벤처웍스 CRM 및 매출 예측 API")

데이터프레임 = None
원본_전체 = None
예측모델 = None
분류모델 = None
국가목록 = []
카테고리목록 = []
피처중요도 = {}
분류_피처중요도 = {}
모델_r2 = 0.0
분류_정확도 = 0.0
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


class 분류입력(BaseModel):
    주문수량: int
    제품단가: float
    제조원가: float
    월코드: int
    선택국가: str
    선택카테고리: str


@애플리케이션.on_event("startup")
def 시스템초기화():
    global 데이터프레임, 원본_전체, 예측모델, 분류모델, 국가목록, 카테고리목록
    global 피처중요도, 분류_피처중요도, 모델_r2, 분류_정확도

    try:
        원본_전체 = pd.read_csv(CSV_경로)
        원본_전체.columns = 원본_전체.columns.str.strip()

        url = "https://github.com/microsoft/powerbi-desktop-samples/raw/main/AdventureWorks%20Sales%20Sample/AdventureWorks%20Sales.xlsx"

        if 원본_전체["Month_num"].max() == 0:
            날짜_데이터 = pd.read_excel(url, sheet_name="Date_data")
            판매_데이터 = pd.read_excel(url, sheet_name="Sales_data")
            날짜_병합 = 판매_데이터[["OrderDateKey"]].merge(
                날짜_데이터[["DateKey", "Month"]], left_on="OrderDateKey", right_on="DateKey", how="left"
            )
            월_순서 = ["January","February","March","April","May","June",
                      "July","August","September","October","November","December"]
            날짜_병합["Month_num"] = 날짜_병합["Month"].apply(
                lambda x: 월_순서.index(x) + 1 if x in 월_순서 else 0
            )
            원본_전체["Month_num"] = 날짜_병합["Month_num"].values

        데이터프레임 = 원본_전체.copy()
    except Exception:
        난수 = np.random.RandomState(42)
        n = 1500
        나라들 = ["United States", "Australia", "Canada", "United Kingdom", "France", "Germany"]
        카테고리들 = ["Bikes", "Accessories", "Clothing", "Components"]
        원본_전체 = pd.DataFrame({
            "Order Quantity": 난수.randint(1, 6, n),
            "Unit Price": 난수.uniform(10, 2200, n),
            "Standard Cost": 난수.uniform(5, 1100, n),
            "Sales Amount": 난수.uniform(20, 9000, n),
            "Month_num": 난수.randint(1, 13, n),
            "Country": 난수.choice(나라들, n),
            "Category": 난수.choice(카테고리들, n),
            "is_reseller": 난수.randint(0, 2, n),
            "CustomerKey": 난수.randint(1, 300, n),
            "OrderDateKey": 난수.randint(20130101, 20160101, n),
        })
        데이터프레임 = 원본_전체.copy()

    국가인코더 = LabelEncoder()
    카테고리인코더 = LabelEncoder()
    데이터프레임["Country_enc"] = 국가인코더.fit_transform(데이터프레임["Country"].astype(str))
    데이터프레임["Category_enc"] = 카테고리인코더.fit_transform(데이터프레임["Category"].astype(str))
    국가목록 = sorted(list(국가인코더.classes_))
    카테고리목록 = sorted(list(카테고리인코더.classes_))

    X = 데이터프레임[피처_컬럼]
    y_reg = 데이터프레임["Sales Amount"]
    X_학습, X_검증, y_학습, y_검증 = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    예측모델 = RandomForestRegressor(n_estimators=100, random_state=42)
    예측모델.fit(X_학습, y_학습)
    모델_r2 = round(float(r2_score(y_검증, 예측모델.predict(X_검증))), 4)
    피처중요도 = {
        피처: round(float(중요도), 4)
        for 피처, 중요도 in zip(피처_컬럼, 예측모델.feature_importances_)
    }

    if "is_reseller" in 데이터프레임.columns:
        y_clf = 데이터프레임["is_reseller"]
        X_clf_학습, X_clf_검증, y_clf_학습, y_clf_검증 = train_test_split(X, y_clf, test_size=0.2, random_state=42)
        분류모델 = RandomForestClassifier(n_estimators=100, random_state=42)
        분류모델.fit(X_clf_학습, y_clf_학습)
        분류_정확도 = round(float(accuracy_score(y_clf_검증, 분류모델.predict(X_clf_검증))), 4)
        분류_피처중요도 = {
            피처: round(float(중요도), 4)
            for 피처, 중요도 in zip(피처_컬럼, 분류모델.feature_importances_)
        }


@애플리케이션.get("/api/metadata")
def 메타데이터조회():
    서브카테고리목록 = sorted(데이터프레임["Subcategory"].dropna().unique().tolist()) if "Subcategory" in 데이터프레임.columns else []
    return {
        "국가목록": [c for c in 국가목록 if c not in US_식별자],
        "카테고리목록": 카테고리목록,
        "서브카테고리목록": 서브카테고리목록,
        "총레코드수": len(데이터프레임),
        "모델R2": 모델_r2,
        "분류정확도": 분류_정확도,
        "피처중요도": 피처중요도,
        "분류피처중요도": 분류_피처중요도,
        "피처수": len(피처_컬럼),
    }


@애플리케이션.post("/api/predict/classify")
def 고객분류예측(요청데이터: 분류입력):
    if 분류모델 is None:
        return {"예측결과": "B2C", "B2C확률": 0.7, "B2B확률": 0.3, "정확도": 0.0}

    국가인덱스 = 국가목록.index(요청데이터.선택국가) if 요청데이터.선택국가 in 국가목록 else 0
    카테고리인덱스 = 카테고리목록.index(요청데이터.선택카테고리) if 요청데이터.선택카테고리 in 카테고리목록 else 0

    입력df = pd.DataFrame([{
        "Order Quantity": 요청데이터.주문수량,
        "Unit Price": 요청데이터.제품단가,
        "Standard Cost": 요청데이터.제조원가,
        "Month_num": 요청데이터.월코드,
        "Category_enc": 카테고리인덱스,
        "Country_enc": 국가인덱스,
    }])

    확률 = 분류모델.predict_proba(입력df)[0]
    예측 = int(분류모델.predict(입력df)[0])

    return {
        "예측결과": "B2B" if 예측 == 1 else "B2C",
        "B2C확률": round(float(확률[0]) * 100, 1),
        "B2B확률": round(float(확률[1]) * 100, 1),
        "정확도": 분류_정확도,
        "피처중요도": 분류_피처중요도,
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
            .sum()
            .reset_index()
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
            ).dropna().astype(int).unique()
            유효_고객키 = [k for k in 유효_고객키 if k > 0]
        else:
            유효_고객키 = []

        if len(유효_고객키) > 0:
            ck_series = pd.to_numeric(데이터프레임["CustomerKey"], errors="coerce")
            동반구매_df = 데이터프레임[
                ck_series.isin(유효_고객키) &
                (데이터프레임["Category"] != "Bikes")
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
    국가인덱스 = 국가목록.index(요청데이터.선택국가) if 요청데이터.선택국가 in 국가목록 else 0
    카테고리인덱스 = 카테고리목록.index(요청데이터.선택카테고리) if 요청데이터.선택카테고리 in 카테고리목록 else 0

    예측입력 = pd.DataFrame([{
        "Order Quantity": 요청데이터.주문수량,
        "Unit Price": 요청데이터.제품단가,
        "Standard Cost": 요청데이터.제조원가,
        "Month_num": 요청데이터.월코드,
        "Category_enc": 카테고리인덱스,
        "Country_enc": 국가인덱스,
    }])

    예측매출 = float(예측모델.predict(예측입력)[0])

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
    }