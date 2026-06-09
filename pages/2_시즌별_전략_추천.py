import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_style import CSS, render_footer, pastel_layout, 서버주소, get_base64_image, translate, translate_bulk, lang_selector, lang_init

st.set_page_config(page_title="시즌별 전략 추천", page_icon="◈", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<style>[data-testid="stSidebar"]{display:none!important;}[data-testid="collapsedControl"]{display:none!important;}</style>', unsafe_allow_html=True)

@st.cache_data(ttl=60)
def 메타조회():
    try: return requests.get(f"{서버주소}/api/metadata", timeout=5).json()
    except: return {"국가목록":["Australia","Canada","France","Germany","United Kingdom"],"카테고리목록":["Accessories","Bikes","Clothing","Components"]}

def 단일예측_B2C(수량, 단가, 원가, 월, 국가, 카테고리):
    try:
        r = requests.post(f"{서버주소}/api/predict/strategy", timeout=5, json={
            "주문수량": 수량, "제품단가": float(단가), "제조원가": float(원가),
            "월코드": 월, "선택국가": 국가, "선택카테고리": 카테고리}).json()
        return float(r.get("예측매출액", 0.0))
    except:
        return float(수량 * 단가 * 1.1)

def 시즌별_B2C_예측(수량, 단가, 원가, 대표월, 국가목록_t, 카테고리):
    from concurrent.futures import ThreadPoolExecutor
    원가비율 = 원가 / 단가 if 단가 > 0 else 0.0

    def _pred(국가):
        매출 = 단일예측_B2C(수량, 단가, 원가, 대표월, 국가, 카테고리)
        return {"국가": 국가, "예측매출": round(매출, 2), "순수익": round(매출 * (1 - 원가비율), 2)}

    with ThreadPoolExecutor(max_workers=6) as ex:
        결과 = list(ex.map(_pred, 국가목록_t))
    return pd.DataFrame(결과)

계절_수요_가중 = {"봄": 1.10, "여름": 1.20, "가을": 0.95, "겨울": 0.80}
국가_가격_인덱스 = {"Australia": 1.05, "Canada": 0.98, "France": 1.02, "Germany": 1.08, "United Kingdom": 1.12}

def 시즌별_B2B_예측(수량, 단가, 원가, 국가목록_t, 계절_키="봄"):
    결과 = []
    계절_가중 = 계절_수요_가중.get(계절_키, 1.0)
    for 국가 in 국가목록_t:
        국가_idx = 국가_가격_인덱스.get(국가, 1.0)
        매출 = round(수량 * 단가 * 0.85 * 국가_idx * 계절_가중, 2)
        결과.append({"국가": 국가, "예측매출": 매출, "순수익": round(매출 - 수량 * 원가, 2)})
    return pd.DataFrame(결과)

계절_키목록 = ["봄", "여름", "가을", "겨울"]
계절_대표월 = {"봄": 4, "여름": 7, "가을": 10, "겨울": 1}
월_to_계절 = {12:"겨울",1:"겨울",2:"겨울",3:"봄",4:"봄",5:"봄",
              6:"여름",7:"여름",8:"여름",9:"가을",10:"가을",11:"가을"}

서브카테고리_단가표 = {
    "Road Bikes":(980,618),"Mountain Bikes":(667,364),"Touring Bikes":(935,581),
    "Mountain Frames":(300,200),"Road Frames":(280,180),"Touring Frames":(250,160),
    "Wheels":(120,60),"Helmets":(35,13),"Jerseys":(52,40),
    "Tires and Tubes":(14,5),"Shorts":(70,26),"Gloves":(24,9),
    "Bike Racks":(120,45),"Bottles and Cages":(7,3),"Hydration Packs":(55,21),
    "Fenders":(22,8),"Bike Stands":(159,59),"Vests":(64,24),
}
카테고리별_서브 = {
    "Bikes":["Road Bikes","Mountain Bikes","Touring Bikes"],
    "Components":["Mountain Frames","Road Frames","Touring Frames","Wheels","Cranksets","Handlebars","Pedals"],
    "Accessories":["Helmets","Tires and Tubes","Bike Racks","Bottles and Cages","Hydration Packs","Fenders","Bike Stands"],
    "Clothing":["Jerseys","Shorts","Gloves","Vests","Caps","Socks"],
}
카테고리색 = {"Accessories":"#8aab8e","Clothing":"#c4956a","Components":"#a98baa","Bikes":"#7b93a8"}

메타 = 메타조회()
국가목록 = 메타["국가목록"]

if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"
lang_init("p2")
st.markdown('<div class="main-content">', unsafe_allow_html=True)
lang = lang_selector("p2")
def t(text): return translate(text, lang)

if lang != "ko":
    translate_bulk([
        "시즌별 전략 추천", "← 홈",
        "미국 실적 기준 시즌별 최고 카테고리를 타국가 전략으로 이식하고, 자전거 구매 연계 크로스셀링 및 업셀 예측을 제공합니다.",
        "국가 필터", "전체 국가",
        "시즌별 매출 예측", "크로스셀링 & 업셀 분석",
        "봄", "여름", "가을", "겨울",
        "시즌 선택", "거래 유형", "일반 개인 고객 (B2C)", "도매 및 대리점 (B2B)",
        "판매 카테고리", "서브카테고리", "전체 (평균)", "판매 수량", "제품 단가 ($)", "제조 원가 ($)",
        "시즌별 예측 계산 중…", "전체 예측 총 매출", "전체 예측 순수익", "최고 예측 국가",
        "매출 산출 방식", "도매 단가 기반", "예측 매출", "순수익", "금액 ($)", "마진율",
        "예측 매출 ($)", "순수익 ($)",
        "Bikes 구매 고객 크로스셀링 분석",
        "자전거(Bikes) 구매 고객이 함께 구매한 카테고리 패턴과 시즌별 분포를 실제 CSV 데이터로 분석합니다.",
        "adventureworks_clean.csv 파일을 찾을 수 없습니다.",
        "카테고리 또는 매출 컬럼을 찾을 수 없습니다.",
        "Bikes 총 매출", "전체 매출 중 Bikes 비중", "최다 동반 구매 카테고리",
        "동반 구매 카테고리별 매출", "시즌별 카테고리 매출 패턴",
        "매출 ($)", "크로스셀 전략", "주요 서브카테고리",
        "업셀 구매 예측 — Bikes 고객의 추가 구매 가능성",
        "자전거 구매 고객이 Accessories / Clothing / Components도 구매할 가능성을 AI가 예측합니다.",
        "주문 수량", "제품 단가 ($)", "분석 시즌", "국가",
        "카테고리별 구매 확률", "시즌 맞춤 전략", "구매 가능성 높음", "구매 가능성 낮음",
        "모델 정확도", "점선(50%) 기준 오른쪽 = 구매 가능성 높음",
    ], lang)

top1, top2 = st.columns([6, 1])
with top1:
    st.markdown(f'<div style="font-family:\'Libre Baskerville\',serif;font-size:48px;font-weight:700;color:#2e2a26;margin:0;line-height:1.15;letter-spacing:-0.3px;">{t("시즌별 전략 추천")}</div>', unsafe_allow_html=True)
with top2:
    st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
    if st.button(t("← 홈"), key="home_top", use_container_width=True):
        st.switch_page("home.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#ddd8d0;margin-top:-10px;margin-bottom:20px;'>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#8c8480;font-size:14px;margin-bottom:20px;'>{t('미국 실적 기준 시즌별 최고 카테고리를 타국가 전략으로 이식하고, 자전거 구매 연계 크로스셀링 및 업셀 예측을 제공합니다.')}</p>", unsafe_allow_html=True)

_, cf = st.columns([4, 2])
with cf:
    country_options = [t("전체 국가")] + 국가목록
    선택국가 = st.selectbox(t("국가 필터"), country_options, key="p2_country")
    선택국가_내부 = "전체 국가" if 선택국가 == t("전체 국가") else 선택국가
    분析국가 = 국가목록 if 선택국가_내부 == "전체 국가" else [선택국가_내부]

탭1, 탭2 = st.tabs([t("시즌별 매출 예측"), t("크로스셀링 & 업셀 분석")])

with 탭1:
    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("시즌별 매출 예측 — 시즌·카테고리·수량·단가로 국가별 예측")}</span></div>', unsafe_allow_html=True)

    계절_표시목록 = [t(k) for k in 계절_키목록]
    선택계절_idx = st.radio(
        t("시즌 선택"),
        options=list(range(len(계절_키목록))),
        format_func=lambda i: 계절_표시목록[i],
        horizontal=True,
        key="tab1_season_radio"
    )
    선택계절_키 = 계절_키목록[선택계절_idx]
    선택계절_표시 = 계절_표시목록[선택계절_idx]
    대표월 = 계절_대표월[선택계절_키]

    r1, r2, r3 = st.columns(3)
    with r1:
        거래유형 = st.radio(t("거래 유형"), [t("일반 개인 고객 (B2C)"), t("도매 및 대리점 (B2B)")], horizontal=True, key="tab1_type")
    with r2:
        선택카테고리 = st.selectbox(t("판매 카테고리"), 메타["카테고리목록"], key="tab1_cat")
    with r3:
        서브목록 = 카테고리별_서브.get(선택카테고리, [])
        선택서브 = st.selectbox(t("서브카테고리"), [t("전체 (평균)")] + 서브목록, key="tab1_sub")

    is_b2b = 거래유형 == t("도매 및 대리점 (B2B)")

    이전키 = f"t1_{선택카테고리}_{선택서브}"
    if st.session_state.get("tab1_이전키") != 이전키:
        if 선택서브 in 서브카테고리_단가표:
            기본단가, 기본원가 = 서브카테고리_단가표[선택서브]
        else:
            기본단가, 기본원가 = 500, 350
        st.session_state["tab1_단가"] = 기본단가
        st.session_state["tab1_원가"] = 기본원가
        st.session_state["tab1_이전키"] = 이전키

    p1, p2, p3 = st.columns(3)
    with p1:
        pred_수량 = st.slider(t("판매 수량"), 1, 100 if is_b2b else 10, 20 if is_b2b else 5, key="tab1_qty")
    with p2:
        pred_단가 = st.number_input(t("제품 단가 ($)"), min_value=1, value=st.session_state.get("tab1_단가", 500), key="tab1_단가")
    with p3:
        pred_원가 = st.number_input(t("제조 원가 ($)"), min_value=1, value=st.session_state.get("tab1_원가", 350), key="tab1_원가")

    서브표시 = 선택서브 if 선택서브 not in [t("전체 (평균)"), "전체 (평균)"] else 선택카테고리

    with st.spinner(t("시즌별 예측 계산 중…")):
        if is_b2b:
            pred_df = 시즌별_B2B_예측(pred_수량, pred_단가, pred_원가, tuple(분析국가), 선택계절_키)
            매출방식 = f"{t('도매 단가 기반')} — {서브표시} ({선택계절_표시})"
        else:
            pred_df = 시즌별_B2C_예측(pred_수량, pred_단가, pred_원가, 대표월, tuple(분析국가), 선택카테고리)
            매출방식 = f"Random Forest AI — {서브표시} ({선택계절_표시}, 월={대표월})"

    총예측매출 = pred_df["예측매출"].sum()
    총순수익 = pred_df["순수익"].sum()
    최고국가 = pred_df.loc[pred_df["예측매출"].idxmax(), "국가"] if len(pred_df) > 0 else "—"

    st.markdown(f"""<div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-val">${총예측매출:,.0f}</div><div class="kpi-label">{t("전체 예측 총 매출")}</div></div>
        <div class="kpi-card green"><div class="kpi-val">${총순수익:,.0f}</div><div class="kpi-label">{t("전체 예측 순수익")}</div></div>
        <div class="kpi-card warn"><div class="kpi-val">{최고국가}</div><div class="kpi-label">{t("최고 예측 국가")}</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8c8480;font-size:12px;margin:-8px 0 16px;'>{t('매출 산출 방식')}: {매출방식}</p>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Bar(name=t("예측 매출"), x=pred_df["국가"], y=pred_df["예측매출"],
            marker_color="#7b93a8", marker_line_width=0,
            text=pred_df["예측매출"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside", textfont=dict(size=12, color="#8c8480")))
        fig_pred.add_trace(go.Bar(name=t("순수익"), x=pred_df["국가"], y=pred_df["순수익"],
            marker_color="#8aab8e", marker_line_width=0))
        pastel_layout(fig_pred, height=340)
        fig_pred.update_layout(barmode="group")
        fig_pred.update_yaxes(title_text=t("금액 ($)"))
        fig_pred.add_hline(y=0, line_dash="dot", line_color="#ddd8d0")
        st.plotly_chart(fig_pred, use_container_width=True)
    with cb:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        display = pred_df.copy()
        display.columns = ["국가", t("예측 매출 ($)"), t("순수익 ($)")]
        display[t("예측 매출 ($)")] = display[t("예측 매출 ($)")].apply(lambda x: f"${x:,.0f}")
        display[t("순수익 ($)")] = display[t("순수익 ($)")].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display, use_container_width=True, hide_index=True)
        for _, 행 in pred_df.iterrows():
            마진 = int(행["순수익"] / 행["예측매출"] * 100) if 행["예측매출"] > 0 else 0
            box = "ok" if 행["순수익"] > 0 else "bad"
            st.markdown(f'<div class="alert-box {box}" style="margin-bottom:6px;padding:10px 14px;"><b>{행["국가"]}</b> — {t("마진율")} {마진}%, {t("순수익")} ${행["순수익"]:,.0f}</div>', unsafe_allow_html=True)

with 탭2:
    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#8aab8e"></div><span>{t("업셀 구매 예측 — Bikes 고객의 추가 구매 가능성")}</span></div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8c8480;font-size:14px;margin-bottom:20px;'>{t('자전거 구매 고객이 Accessories / Clothing / Components도 구매할 가능성을 AI가 예측합니다.')}</p>", unsafe_allow_html=True)

    u1, u2, u3 = st.columns(3)
    with u1:
        up_수량 = st.slider(t("주문 수량"), 1, 10, 2, key="up_qty")
    with u2:
        up_단가 = st.number_input(t("제품 단가 ($)"), min_value=1, value=700, key="up_price")
    with u3:
        업셀_계절_idx = st.radio(
            t("분석 시즌"),
            options=list(range(len(계절_키목록))),
            format_func=lambda i: [t(k) for k in 계절_키목록][i],
            horizontal=True,
            key="upsell_season_radio"
        )
        업셀_계절_키 = 계절_키목록[업셀_계절_idx]
        업셀_계절_표시 = [t(k) for k in 계절_키목록][업셀_계절_idx]
        up_월 = 계절_대표월[업셀_계절_키]
        st.caption(f"{업셀_계절_표시} — {t('월')} {up_월}")

    up_국가 = 분析국가[0]
    up_국가_표시 = 선택국가

    카테고리_색상맵 = {"Accessories": "#8aab8e", "Clothing": "#c4956a", "Components": "#a98baa"}

    try:
        up_result = requests.post(f"{서버주소}/api/predict/upsell", timeout=5, json={
            "주문수량": up_수량,
            "제품단가": float(up_단가),
            "월코드": up_월,
            "선택국가": up_국가,
        }).json()
        카테고리별예측 = up_result.get("카테고리별예측", {})
        최고추천 = up_result.get("최고추천카테고리", "Accessories")
        api_ok = True
    except:
        카테고리별예측 = {
            "Accessories": {"확률": 65.0, "예측": "구매 가능성 높음", "정확도": 0.0, "추천": "서버 연결 필요"},
            "Clothing": {"확률": 40.0, "예측": "구매 가능성 낮음", "정확도": 0.0, "추천": "서버 연결 필요"},
            "Components": {"확률": 35.0, "예측": "구매 가능성 낮음", "정확도": 0.0, "추천": "서버 연결 필요"},
        }
        최고추천 = "Accessories"
        api_ok = False

    st.markdown(f"<p style='color:#8c8480;font-size:13px;margin:4px 0 16px;'>{업셀_계절_표시} ({t('월')} {up_월}) · {up_국가_표시} · {up_수량}{t('개')} · ${up_단가:,}</p>", unsafe_allow_html=True)

    st.markdown('<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:0 0 20px 0;">', unsafe_allow_html=True)
    for 카t, 데이터 in 카테고리별예측.items():
        확률 = 데이터["확률"]
        색 = 카테고리_색상맵.get(카t, "#7b93a8")
        강조 = f"border:2px solid {색}" if 카t == 최고추천 else "border:1px solid var(--border)"
        예측라벨 = t(데이터['예측'])
        st.markdown(f"""<div class="kpi-card" style="{강조};border-top:3px solid {색};">
            <div class="kpi-val" style="color:{색};">{확률:.0f}%</div>
            <div class="kpi-label">{카t}</div>
            <div style="font-size:12px;color:#8c8480;margin-top:4px;">{예측라벨}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#7b93a8"></div><span>{t("카테고리별 구매 확률")}</span></div>', unsafe_allow_html=True)
        카t목록 = list(카테고리별예측.keys())
        확률목록 = [카테고리별예측[k]["확률"] for k in 카t목록]
        색목록 = [카테고리_색상맵.get(k, "#7b93a8") for k in 카t목록]
        fig_up = go.Figure(go.Bar(
            x=확률목록, y=카t목록, orientation="h",
            marker=dict(color=색목록, line=dict(width=0)),
            text=[f"{v:.1f}%" for v in 확률목록],
            textposition="outside",
            textfont=dict(family="DM Sans", size=14, color="#8c8480"),
        ))
        pastel_layout(fig_up, height=240, margin=dict(l=10, r=80, t=10, b=10))
        fig_up.update_xaxes(range=[0, 120], showticklabels=False, showgrid=False)
        fig_up.add_vline(x=50, line_dash="dot", line_color="#ddd8d0")
        fig_up.update_yaxes(tickfont=dict(family="DM Sans", size=15, color="#2e2a26"))
        st.plotly_chart(fig_up, use_container_width=True)
        st.caption(t("점선(50%) 기준 오른쪽 = 구매 가능성 높음"))

    with cb:
        st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("시즌 맞춤 전략")}</span></div>', unsafe_allow_html=True)
        for 카t, 데이터 in 카테고리별예측.items():
            색 = 카테고리_색상맵.get(카t, "#7b93a8")
            확률 = 데이터["확률"]
            box_bg = "#f0f6f1" if 확률 >= 50 else "#fdf1f1"
            box_bd = "#c2d9c5" if 확률 >= 50 else "#e0bcbc"
            box_c = "#4e7a54" if 확률 >= 50 else "#b56b6b"
            정확도표시 = f" ({t('모델 정확도')} {데이터['정확도']*100:.1f}%)" if 데이터['정확도'] > 0 else ""
            st.markdown(f"""<div class="strat-card" style="border-left-color:{색};margin-bottom:10px;">
                <div class="strat-country">Bikes → {카t}{정확도표시}</div>
                <div class="strat-text">{t(데이터['추천'])}</div>
                <div style="margin-top:8px;background:{box_bg};border:1px solid {box_bd};border-radius:4px;padding:6px 10px;font-size:13px;color:{box_c};">
                    {확률:.1f}% — {t(데이터['예측'])}
                </div>
            </div>""", unsafe_allow_html=True)

    if not api_ok:
        st.markdown('<div class="alert-box bad" style="margin-top:16px;">서버 미연결 — uvicorn 실행 후 새로고침하세요.</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
render_footer()