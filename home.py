import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_style import CSS, render_footer, pastel_layout, 서버주소, 피처_한글명, get_base64_image, translate, translate_bulk, lang_selector, lang_init

st.set_page_config(page_title="AdventureWorks CRM", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown("<style>[data-testid='stSidebar']{display:none!important;}[data-testid='collapsedControl']{display:none!important;}</style>", unsafe_allow_html=True)

logo_base64 = get_base64_image("logo.png")

@st.cache_data(ttl=60)
def 메타조회():
    try: return requests.get(f"{서버주소}/api/metadata", timeout=5).json()
    except: return {"총레코드수":0,"모델R2":0.0,"피처수":6,"피처중요도":{"Order Quantity":0.15,"Unit Price":0.32,"Standard Cost":0.45,"Month_num":0.01,"Category_enc":0.02,"Country_enc":0.05}}

메타 = 메타조회()
레코드수 = 메타["총레코드수"] if 메타["총레코드수"] > 0 else 84350
r2값 = 메타["모델R2"] if 메타["모델R2"] > 0 else 1.0
r2 = f"{r2값:.4f}"

피처_원본 = 메타.get("피처중요도", {})
월_중요도 = 피처_원본.get("Month_num", 0)
월_중요도_pct = f"{월_중요도*100:.1f}%"

if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"
lang_init("home")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

lang = lang_selector("home")
def t(text): return translate(text, lang)

if lang != "ko":
    translate_bulk([
        "마케팅 이론의 관점에서", "분석 및 예측", "학습 레코드 수", "모델 R² Score", "입력 피처 수",
        "매출 및 예측 리포트", "시즌별 전략 추천", "피처 중요도 — Random Forest Gini",
        "알고리즘", "트리 수", "학습/검증 분할", "데이터 소스", "전처리",
        "IQR 이상치 제거, LabelEncoder", "타겟 변수", "API 프레임워크",
        "FastAPI 백엔드 연결됨", "서버 연결 실패 — uvicorn 실행 여부 확인",
        "주문 수량", "제품 단가", "제조 원가", "월 코드", "카테고리", "국가",
        "월별 계절성 피처 (Month_num) 실제 중요도",
    ], lang)

_, mid, _ = st.columns([1, 3, 1])
with mid:
    logo_tag = f'<img src="data:image/png;base64,{logo_base64}" style="height:52px;margin-bottom:20px;opacity:0.85;">' if logo_base64 else ""
    st.markdown(f"""
    <div style="text-align:center;padding:40px 0 32px 0;">
        {logo_tag}
        <div style="font-family:'Playfair Display',serif;font-size:64px;font-weight:700;color:#2e2a26;line-height:1.2;margin-bottom:12px;letter-spacing:-0.5px;">
            {t("마케팅 이론의 관점에서")} <br>{t("분석 및 예측")}
        </div>
        <div style="font-family:'DM Sans',sans-serif;font-size:15px;color:#8c8480;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:40px;">
            AdventureWorks CRM Intelligence System
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid" style="max-width:860px;margin:0 auto 36px auto;">
    <div class="kpi-card"><div class="kpi-val">{레코드수:,}</div><div class="kpi-label">{t("학습 레코드 수")}</div></div>
    <div class="kpi-card green"><div class="kpi-val">{r2}</div><div class="kpi-label">{t("모델 R² Score")}</div></div>
    <div class="kpi-card warn"><div class="kpi-val">{메타['피처수']}</div><div class="kpi-label">{t("입력 피처 수")}</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="column"] > div > div > div > div[data-testid="stButton"] > button {
    width:100%;background:
    padding:22px 16px;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:600;
    color:
}
div[data-testid="column"] > div > div > div > div[data-testid="stButton"] > button:hover {
    border-color:
}
</style>
""", unsafe_allow_html=True)

_, b1, b2, _ = st.columns([0.5, 2, 2, 0.5])
with b1:
    if st.button(t("매출 및 예측 리포트"), key="btn_report", use_container_width=True):
        st.switch_page("pages/1_매출_및_예측_리포트.py")
with b2:
    if st.button(t("시즌별 전략 추천"), key="btn_season", use_container_width=True):
        st.switch_page("pages/2_시즌별_전략_추천.py")

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

_, mid3, _ = st.columns([0.5, 3, 0.5])
with mid3:
    st.markdown(f'<div class="section-header"><div class="section-dot"></div><span>{t("피처 중요도 — Random Forest Gini")}</span></div>', unsafe_allow_html=True)

    피처df = pd.DataFrame([
        {"피처": t(피처_한글명.get(k, k)), "중요도": v, "pct": f"{v*100:.1f}%"}
        for k, v in sorted(피처_원본.items(), key=lambda x: x[1])
    ])

    bar_colors = []
    for k in sorted(피처_원본.items(), key=lambda x: x[1]):
        if k[0] == "Month_num":
            bar_colors.append("#8aab8e")
        else:
            bar_colors.append("#7b93a8")

    fig1 = go.Figure(go.Bar(
        x=피처df["중요도"], y=피처df["피처"], orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=피처df["pct"], textposition="outside",
        textfont=dict(family="DM Sans", size=14, color="#8c8480"),
    ))
    pastel_layout(fig1, height=320, margin=dict(l=10, r=120, t=10, b=10))
    fig1.update_xaxes(showticklabels=False, showgrid=False)
    fig1.update_yaxes(tickfont=dict(family="DM Sans", size=15, color="#2e2a26"))
    st.plotly_chart(fig1, use_container_width=True)

    월_색 = "#4e7a54" if 월_중요도 > 0.02 else "#8B6F47"
    월_bg = "#f0f6f1" if 월_중요도 > 0.02 else "#f5f0eb"
    월_bd = "#c2d9c5" if 월_중요도 > 0.02 else "#d9c9b5"
    st.markdown(f'<div style="text-align:center;margin-bottom:20px;padding:12px 16px;background:{월_bg};border:1px solid {월_bd};border-radius:4px;color:{월_색};font-size:15px;">{t("월별 계절성 피처 (Month_num) 실제 중요도")} — <b>{월_중요도_pct}</b></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="fin-card">
            <div class="fin-row"><span class="fin-label">{t("알고리즘")}</span><span class="fin-value">Random Forest Regressor</span></div>
            <div class="fin-row"><span class="fin-label">{t("트리 수")}</span><span class="fin-value">100</span></div>
            <div class="fin-row"><span class="fin-label">{t("학습/검증 분할")}</span><span class="fin-value">80% / 20%</span></div>
            <div class="fin-row"><span class="fin-label">random_state</span><span class="fin-value">42</span></div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="fin-card">
            <div class="fin-row"><span class="fin-label">{t("데이터 소스")}</span><span class="fin-value">adventureworks_clean.csv</span></div>
            <div class="fin-row"><span class="fin-label">{t("전처리")}</span><span class="fin-value">{t("IQR 이상치 제거, LabelEncoder")}</span></div>
            <div class="fin-row"><span class="fin-label">{t("타겟 변수")}</span><span class="fin-value">Sales Amount ($)</span></div>
            <div class="fin-row"><span class="fin-label">{t("API 프레임워크")}</span><span class="fin-value">FastAPI</span></div>
        </div>""", unsafe_allow_html=True)

    연결ok = 메타["총레코드수"] > 0
    연결상태 = t("FastAPI 백엔드 연결됨") if 연결ok else t("서버 연결 실패 — uvicorn 실행 여부 확인")
    색 = "#4e7a54" if 연결ok else "#b56b6b"
    bg = "#f0f6f1" if 연결ok else "#fdf1f1"
    bd = "#c2d9c5" if 연결ok else "#e0bcbc"
    st.markdown(f'<div style="text-align:center;margin-top:20px;padding:12px 16px;background:{bg};border:1px solid {bd};border-radius:4px;color:{색};font-size:15px;">{연결상태}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
render_footer()