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

@st.cache_data(ttl=300, show_spinner=False)
def csv_로드():
    기본경로 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "adventureworks_clean.csv")
    if os.path.exists(기본경로): return pd.read_csv(기본경로)
    현재경로 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adventureworks_clean.csv")
    if os.path.exists(현재경로): return pd.read_csv(현재경로)
    return None

@st.cache_data(ttl=30, show_spinner=False)
def 시즌별_B2C_예측(수량, 단가, 원가, 계절_월, 국가목록_t, 카테고리):
    결과 = []
    for 국가 in 국가목록_t:
        try:
            r = requests.post(f"{서버주소}/api/predict/strategy", timeout=5, json={
                "주문수량":수량,"제품단가":float(단가),"제조원가":float(원가),
                "월코드":계절_월,"선택국가":국가,"선택카테고리":카테고리}).json()
            매출 = float(r.get("예측매출액", 0.0))
        except:
            매출 = float(수량 * 단가 * 1.1)
        결과.append({"국가":국가,"예측매출":round(매출,2),"순수익":round(매출-(수량*원가),2)})
    return pd.DataFrame(결과)

@st.cache_data(ttl=30, show_spinner=False)
def 시즌별_B2B_예측(수량, 단가, 원가, 국가목록_t):
    결과 = []
    for 국가 in 국가목록_t:
        매출 = round(수량*단가*0.85, 2)
        결과.append({"국가":국가,"예측매출":매출,"순수익":round(매출-수량*원가,2)})
    return pd.DataFrame(결과)

메타 = 메타조회()
국가목록 = 메타["국가목록"]
원본df = csv_로드()

계절_키목록 = ["봄","여름","가을","겨울"]
계절_대표월 = {"봄":4,"여름":7,"가을":10,"겨울":1}
월_to_계절 = {12:"겨울",1:"겨울",2:"겨울",3:"봄",4:"봄",5:"봄",6:"여름",7:"여름",8:"여름",9:"가을",10:"가을",11:"가을"}

if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"
lang_init("p2")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

lang = lang_selector("p2")
def t(text): return translate(text, lang)

if lang != "ko":
    translate_bulk([
        "시즌별 전략 추천", "← 홈",
        "미국 실적을 기준으로 시즌별 최고 카테고리를 타국가에 이식하기 위한 전략과, 자전거 구매와 연계한 크로스셀링 분석을 제공합니다.",
        "분석 시즌", "국가 필터", "전체 국가",
        "봄", "여름", "가을", "겨울",
        "시즌별 매출 예측", "크로스셀링 분석",
        "시즌별 AI 매출 예측 — 판매 시뮬레이션",
        "선택한 시즌·카테고리·수량·단가로 각 국가별 예상 매출과 순수익을 실시간으로 예측합니다.",
        "거래 유형", "일반 개인 고객 (B2C)", "도매 및 대리점 (B2B)",
        "판매 카테고리", "서브카테고리", "전체 (평균)", "판매 수량", "제품 단가 ($)", "제조 원가 ($)",
        "시즌별 예측 계산 중…", "전체 예측 총 매출", "전체 예측 순수익", "최고 예측 국가",
        "매출 산출 방식", "도매 단가 기반", "예측 매출", "순수익", "금액 ($)", "마진율",
        "예측 매출 ($)", "순수익 ($)",
        "3D 예측 곡면 — 수량 × 단가 × 예측 매출",
        "X축: 수량, Y축: 단가 범위 (현재 설정 ±50%), Z축: AI 예측 매출. 드래그로 회전하세요.",
        "수량", "단가($)", "예측매출($)", "순수익($)",
        "자전거 구매 연계 크로스셀링 분석",
        "자전거(Bikes) 구매 고객이 함께 구매한 카테고리·서브카테고리 패턴과 시즌별 분포를 CSV 실제 데이터 기반으로 분석합니다.",
        "adventureworks_clean.csv 파일을 찾을 수 없습니다.",
        "카테고리 또는 매출 컬럼을 찾을 수 없습니다.",
        "Bikes 총 매출", "전체 매출 중 Bikes 비중", "최다 동반 구매 카테고리",
        "Bikes 구매 고객의 동반 구매 카테고리", "카테고리별 시즌 매출 패턴",
        "매출 ($)", "시즌별 데이터를 계산할 수 없습니다.",
        "크로스셀 전략 추천", "전체 국가", "주요 서브카테고리", "시즌 인사이트",
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
st.markdown(f"<p style='color:#8c8480;font-size:14px;margin-bottom:24px;'>{t('미국 실적을 기준으로 시즌별 최고 카테고리를 타국가에 이식하기 위한 전략과, 자전거 구매와 연계한 크로스셀링 분석을 제공합니다.')}</p>", unsafe_allow_html=True)

계절_표시목록 = [t(k) for k in 계절_키목록]

f1, f2 = st.columns(2)
with f1:
    선택계절_표시 = st.select_slider(t("분석 시즌"), options=계절_표시목록)
    선택계절_키 = 계절_키목록[계절_표시목록.index(선택계절_표시)]
with f2:
    country_options = [t("전체 국가")] + 국가목록
    선택국가 = st.selectbox(t("국가 필터"), country_options)
    선택국가_내부 = "전체 국가" if 선택국가 == t("전체 국가") else 선택국가

탭2, 탭3 = st.tabs([t("시즌별 매출 예측"), t("크로스셀링 분석")])

with 탭2:
    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("시즌별 AI 매출 예측 — 판매 시뮬레이션")}</span></div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8c8480;font-size:14px;margin-bottom:20px;'>{t('선택한 시즌·카테고리·수량·단가로 각 국가별 예상 매출과 순수익을 실시간으로 예측합니다.')}</p>", unsafe_allow_html=True)

    서브카테고리_단가표_탭2 = {
        "Road Bikes":(980,618),"Mountain Bikes":(667,364),"Touring Bikes":(935,581),
        "Mountain Frames":(300,200),"Road Frames":(280,180),"Touring Frames":(250,160),
        "Wheels":(120,60),"Helmets":(35,13),"Jerseys":(52,40),
        "Tires and Tubes":(14,5),"Shorts":(70,26),"Gloves":(24,9),
        "Bike Racks":(120,45),"Bottles and Cages":(7,3),"Hydration Packs":(55,21),
        "Fenders":(22,8),"Bike Stands":(159,59),"Vests":(64,24),
    }
    카테고리별_서브_탭2 = {
        "Bikes":["Road Bikes","Mountain Bikes","Touring Bikes"],
        "Components":["Mountain Frames","Road Frames","Touring Frames","Wheels","Cranksets","Handlebars","Pedals"],
        "Accessories":["Helmets","Tires and Tubes","Bike Racks","Bottles and Cages","Hydration Packs","Fenders","Bike Stands"],
        "Clothing":["Jerseys","Shorts","Gloves","Vests","Caps","Socks"],
    }

    t2_r1, t2_r2, t2_r3 = st.columns(3)
    with t2_r1:
        거래유형 = st.radio(t("거래 유형"), [t("일반 개인 고객 (B2C)"), t("도매 및 대리점 (B2B)")], horizontal=True)
    with t2_r2:
        선택카테고리_탭2 = st.selectbox(t("판매 카테고리"), 메타["카테고리목록"], key="tab2_cat")
    with t2_r3:
        서브목록_탭2 = 카테고리별_서브_탭2.get(선택카테고리_탭2, [])
        선택서브_탭2 = st.selectbox(t("서브카테고리"), [t("전체 (평균)")] + 서브목록_탭2, key="tab2_sub")

    is_b2b = 거래유형 == t("도매 및 대리점 (B2B)")
    이전키_탭2 = f"{선택카테고리_탭2}_{선택서브_탭2}"

    if st.session_state.get("tab2_이전키") != 이전키_탭2:
        if 선택서브_탭2 in 서브카테고리_단가표_탭2:
            기본단가, 기본원가 = 서브카테고리_단가표_탭2[선택서브_탭2]
        else:
            기본단가, 기본원가 = 500, 350
        st.session_state["tab2_단가"] = 기본단가
        st.session_state["tab2_원가"] = 기본원가
        st.session_state["tab2_이전키"] = 이전키_탭2

    p1, p2, p3 = st.columns(3)
    with p1:
        pred_수량 = st.slider(t("판매 수량"), 1, 100 if is_b2b else 10, 20 if is_b2b else 5, key="pred_qty")
    with p2:
        pred_단가 = st.number_input(t("제품 단가 ($)"), min_value=1,
            value=st.session_state.get("tab2_단가", 500), key="tab2_단가")
    with p3:
        pred_원가 = st.number_input(t("제조 원가 ($)"), min_value=1,
            value=st.session_state.get("tab2_원가", 350), key="tab2_원가")
    if is_b2b:
        st.markdown(f"<p style='color:#8c8480;font-size:12px;margin:-10px 0 10px;'>💡 {t('단가')} = {t('정상가')} (${pred_단가:,}) → {t('도매 실제 청구단가')} ${int(pred_단가*0.85):,} (15% {t('할인 적용')})</p>", unsafe_allow_html=True)

    서브표시_탭2 = 선택서브_탭2 if 선택서브_탭2 not in [t("전체 (평균)"), "전체 (평균)"] else 선택카테고리_탭2
    대표월 = 계절_대표월[선택계절_키]
    분析국가 = 국가목록 if 선택국가_내부 == "전체 국가" else [선택국가_내부]

    with st.spinner(t("시즌별 예측 계산 중…")):
        if is_b2b:
            pred_df = 시즌별_B2B_예측(pred_수량, pred_단가, pred_원가, tuple(분析국가))
            매출방식 = f"{t('도매 단가 기반')} — {서브표시_탭2}"
        else:
            pred_df = 시즌별_B2C_예측(pred_수량, pred_단가, pred_원가, 대표월, tuple(분析국가), 선택카테고리_탭2)
            매출방식 = f"Random Forest AI — {서브표시_탭2}"

    총예측매출 = pred_df["예측매출"].sum()
    총순수익 = pred_df["순수익"].sum()
    최고국가 = pred_df.loc[pred_df["예측매출"].idxmax(),"국가"] if len(pred_df) > 0 else "—"

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
            textposition="outside", textfont=dict(size=12,color="#8c8480")))
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
            마진 = int(행["순수익"]/행["예측매출"]*100) if 행["예측매출"] > 0 else 0
            box = "ok" if 행["순수익"] > 0 else "bad"
            st.markdown(f'<div class="alert-box {box}" style="margin-bottom:6px;padding:10px 14px;"><b>{행["국가"]}</b> — {t("마진율")} {마진}%, {t("순수익")} ${행["순수익"]:,.0f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("3D 예측 곡면 — 수량 × 단가 × 예측 매출")}</span></div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8c8480;font-size:13px;margin-bottom:12px;'>{t('X축: 수량, Y축: 단가 범위 (현재 설정 ±50%), Z축: AI 예측 매출. 드래그로 회전하세요.')}</p>", unsafe_allow_html=True)
    if not is_b2b:
        _q2 = list(range(1,11))
        _p2 = [int(pred_단가*r) for r in [0.5,0.7,0.85,1.0,1.15,1.3,1.5]]
        _Q2,_P2 = np.meshgrid(_q2,_p2)
        _Z2 = np.zeros_like(_Q2, dtype=float)
        for _ii in range(_Q2.shape[0]):
            for _jj in range(_Q2.shape[1]):
                try:
                    _r2 = requests.post(f"{서버주소}/api/predict/strategy", timeout=3, json={
                        "주문수량":int(_Q2[_ii,_jj]),"제품단가":float(_P2[_ii,_jj]),
                        "제조원가":float(pred_원가),"월코드":대표월,
                        "선택국가":분析국가[0] if 분析국가 else 국가목록[0],
                        "선택카테고리":선택카테고리_탭2}).json()
                    _Z2[_ii,_jj] = float(_r2.get("예측매출액",_Q2[_ii,_jj]*_P2[_ii,_jj]))
                except: _Z2[_ii,_jj] = float(_Q2[_ii,_jj]*_P2[_ii,_jj]*1.1)
        cs = [[0,"#e8e4df"],[0.5,"#a8b8c8"],[1,"#7b93a8"]]
        cb_title = t("예측매출($)")
    else:
        _q2 = list(range(5,101,5))
        _p2 = [int(pred_단가*r) for r in [0.5,0.7,0.85,1.0,1.15,1.3,1.5]]
        _Q2,_P2 = np.meshgrid(_q2,_p2)
        _Z2 = _Q2*_P2*0.85-_Q2*pred_원가
        cs = [[0,"#b56b6b"],[0.4,"#e8e4df"],[1,"#8aab8e"]]
        cb_title = t("순수익($)")
    fig_3d2 = go.Figure(data=[go.Surface(z=_Z2,x=_q2,y=_p2,colorscale=cs,showscale=True,
        colorbar=dict(title=cb_title,tickformat="$,.0f",tickfont=dict(size=10,color="#8c8480"),title_font=dict(size=10,color="#8c8480")))])
    fig_3d2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(bgcolor="#f7f5f2",
            xaxis=dict(title=t("수량"),gridcolor="#ddd8d0",backgroundcolor="#f7f5f2",color="#8c8480"),
            yaxis=dict(title=t("단가($)"),gridcolor="#ddd8d0",backgroundcolor="#f7f5f2",color="#8c8480"),
            zaxis=dict(title=cb_title,gridcolor="#ddd8d0",backgroundcolor="#f7f5f2",color="#8c8480",tickformat="$,.0f"),
            camera=dict(eye=dict(x=1.8,y=-1.8,z=1.2))),
        height=480,margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig_3d2, use_container_width=True)

with 탭3:
    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("자전거 구매 연계 크로스셀링 분석")}</span></div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8c8480;font-size:13px;margin-bottom:20px;'>{t('자전거(Bikes) 구매 고객이 함께 구매한 카테고리·서브카테고리 패턴과 시즌별 분포를 CSV 실제 데이터 기반으로 분석합니다.')}</p>", unsafe_allow_html=True)

    if 원본df is None:
        st.error(t("adventureworks_clean.csv 파일을 찾을 수 없습니다."))
    else:
        df = 원본df.copy()
        매출컬럼 = next((c for c in df.columns if c.lower().replace(" ","").replace("_","") in ["salesamount","salesamt"]), None)
        if not 매출컬럼: 매출컬럼 = next((c for c in df.columns if "sales" in c.lower() and "amount" in c.lower()), None)
        카테고리컬럼 = next((c for c in df.columns if "category" in c.lower() and "sub" not in c.lower()), None)
        서브카테고리컬럼 = next((c for c in df.columns if "subcategory" in c.lower() or "sub_category" in c.lower()), None)
        고객컬럼 = next((c for c in df.columns if "customerkey" in c.lower() or "customer_key" in c.lower()), None)
        날짜컬럼 = None
        for c in df.columns:
            if c.lower().replace(" ","").replace("_","") in ["orderdate","salesdate"]:
                날짜컬럼 = c; break
        if not 날짜컬럼:
            날짜컬럼 = next((c for c in df.columns if "date" in c.lower() and "key" not in c.lower() and "due" not in c.lower()), None)

        if not 카테고리컬럼 or not 매출컬럼:
            st.warning(t("카테고리 또는 매출 컬럼을 찾을 수 없습니다."))
        else:
            df[매출컬럼] = pd.to_numeric(df[매출컬럼], errors="coerce").fillna(0)
            국가필터df = df.copy()
            if 선택국가_내부 != "전체 국가" and "Country" in 국가필터df.columns:
                국가필터df = 국가필터df[국가필터df["Country"] == 선택국가_내부]

            bikes_mask = 국가필터df[카테고리컬럼].str.strip().str.lower() == "bikes"
            bikes_고객 = set()
            if 고객컬럼 and bikes_mask.sum() > 0:
                bikes_고객 = set(국가필터df[bikes_mask & (국가필터df[고객컬럼] > 0)][고객컬럼].unique())

            동반구매_원본 = pd.DataFrame()
            동반df_raw = pd.DataFrame()
            if 고객컬럼 and len(bikes_고객) > 0:
                동반구매_원본 = 국가필터df[(국가필터df[고객컬럼].isin(bikes_고객)) & (~bikes_mask)]
                if len(동반구매_원본) > 0:
                    동반df_raw = (동반구매_원본.groupby(카테고리컬럼)[매출컬럼]
                        .agg(총매출="sum",구매건수="count").reset_index().sort_values("총매출",ascending=False))
            else:
                동반구매_원본 = 국가필터df[~bikes_mask]
                동반df_raw = (동반구매_원본.groupby(카테고리컬럼)[매출컬럼]
                    .agg(총매출="sum",구매건수="count").reset_index().sort_values("총매출",ascending=False))

            bikes_총매출 = 국가필터df[bikes_mask][매출컬럼].sum()

            k1,k2,k3 = st.columns(3)
            with k1: st.markdown(f'<div class="kpi-card" style="border-top-color:#7b93a8;"><div class="kpi-val">${bikes_총매출/1_000_000:.2f}M</div><div class="kpi-label">{t("Bikes 총 매출")}</div></div>', unsafe_allow_html=True)
            with k2:
                bikes_비중 = bikes_총매출/df[매출컬럼].sum()*100 if df[매출컬럼].sum() > 0 else 0
                st.markdown(f'<div class="kpi-card" style="border-top-color:#8aab8e;"><div class="kpi-val">{bikes_비중:.1f}%</div><div class="kpi-label">{t("전체 매출 중 Bikes 비중")}</div></div>', unsafe_allow_html=True)
            with k3:
                top카테고리 = 동반df_raw.iloc[0][카테고리컬럼] if len(동반df_raw) > 0 else "—"
                st.markdown(f'<div class="kpi-card" style="border-top-color:#8B6F47;"><div class="kpi-val">{top카테고리}</div><div class="kpi-label">{t("최다 동반 구매 카테고리")}</div></div>', unsafe_allow_html=True)

            계절순서 = ["봄","여름","가을","겨울"]
            계절카테고리 = pd.DataFrame()
            if 날짜컬럼:
                try: 국가필터df["_월번호"] = pd.to_datetime(국가필터df[날짜컬럼], errors="coerce").dt.month
                except: 국가필터df["_월번호"] = np.nan
            else:
                월컬럼 = next((c for c in 국가필터df.columns if "month" in c.lower()), None)
                국가필터df["_월번호"] = pd.to_numeric(국가필터df[월컬럼], errors="coerce").replace(0,np.nan) if 월컬럼 else np.nan
            국가필터df["_계절"] = 국가필터df["_월번호"].map(월_to_계절)
            비bikes_df = 국가필터df[국가필터df[카테고리컬럼].str.strip().str.lower() != "bikes"]
            유효df = 비bikes_df[비bikes_df["_계절"].notna()]
            if len(유효df) > 0:
                계절카테고리 = (유효df.groupby(["_계절",카테고리컬럼])[매출컬럼].sum().reset_index())
                계절카테고리.columns = ["계절","카테고리","매출"]
                계절카테고리 = 계절카테고리[계절카테고리["계절"].isin(계절순서)]
            else:
                계절가중 = {"봄":0.28,"여름":0.26,"가을":0.25,"겨울":0.21}
                카테고리총매출 = 비bikes_df.groupby(카테고리컬럼)[매출컬럼].sum()
                행들 = [{"계절":계절,"카테고리":카t,"매출":round(총매출*가중,2)} for 카t,총매출 in 카테고리총매출.items() for 계절,가중 in 계절가중.items()]
                계절카테고리 = pd.DataFrame(행들)

            c1, c2 = st.columns(2)
            카테고리색 = {"Accessories":"#8aab8e","Clothing":"#c4956a","Components":"#a98baa"}

            with c1:
                st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#c4956a"></div><span>{t("Bikes 구매 고객의 동반 구매 카테고리")}</span></div>', unsafe_allow_html=True)
                if len(동반df_raw) > 0:
                    fig3 = go.Figure(go.Bar(
                        x=동반df_raw[카테고리컬럼], y=동반df_raw["총매출"],
                        marker=dict(color=[카테고리색.get(c,"#b8b0a8") for c in 동반df_raw[카테고리컬럼]],line=dict(width=0)),
                        text=동반df_raw["총매출"].apply(lambda x: f"${x/1000:.0f}K"),
                        textposition="outside",textfont=dict(size=13,color="#8c8480"),
                        customdata=동반df_raw["구매건수"],
                        hovertemplate="카테고리: %{x}<br>총매출: $%{y:,.0f}<br>건수: %{customdata}<extra></extra>"))
                    pastel_layout(fig3,height=280,margin=dict(l=10,r=20,t=20,b=10))
                    fig3.update_yaxes(title_text=t("매출 ($)"),tickformat="$,.0f")
                    st.plotly_chart(fig3,use_container_width=True)

                st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#7b93a8"></div><span>{t("카테고리별 시즌 매출 패턴")}</span></div>', unsafe_allow_html=True)
                if len(계절카테고리) > 0:
                    fig4 = go.Figure()
                    for 카t in 계절카테고리["카테고리"].unique():
                        sub = 계절카테고리[계절카테고리["카테고리"]==카t]
                        sub = sub.set_index("계절").reindex(계절순서).reset_index().fillna(0)
                        fig4.add_trace(go.Bar(name=카t,x=sub["계절"],y=sub["매출"],marker_color=카테고리색.get(카t,"#b8b0a8"),marker_line_width=0))
                    pastel_layout(fig4,height=280)
                    fig4.update_layout(barmode="group")
                    fig4.update_yaxes(title_text=t("매출 ($)"),tickformat="$,.0f")
                    st.plotly_chart(fig4,use_container_width=True)
                else:
                    st.info(t("시즌별 데이터를 계산할 수 없습니다."))

            with c2:
                st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("크로스셀 전략 추천")}</span></div>', unsafe_allow_html=True)
                if len(동반df_raw) > 0:
                    국가명표시 = 선택국가_내부 if 선택국가_내부 != "전체 국가" else t("전체 국가")
                    전략맵_ko = {
                        "Accessories": lambda 행, 국가, 계절: f"{국가} 자전거 구매 고객 {int(행['구매건수']):,}명이 Accessories를 동반 구매했습니다 (${행['총매출']/1000:.0f}K, {행['총매출']/bikes_총매출*100:.1f}%). {계절} 자전거 판매 시점에 헬멧·타이어·잠금장치 번들을 제안하십시오.",
                        "Components": lambda 행, 국가, 계절: f"{국가} 자전거 구매 고객 {int(행['구매건수']):,}명이 Components를 동반 구매했습니다 (${행['총매출']/1000:.0f}K, {행['총매출']/bikes_총매출*100:.1f}%). {계절} 고관여 고객에게 프레임·휠 업그레이드 패키지를 추가 제안하십시오.",
                        "Clothing": lambda 행, 국가, 계절: f"{국가} 자전거 구매 고객 {int(행['구매건수']):,}명이 Clothing을 동반 구매했습니다 (${행['총매출']/1000:.0f}K, {행['총매출']/bikes_총매출*100:.1f}%). {계절} 결제 완료 화면에서 저지·반바지 세트를 즉시 추천하십시오.",
                    }
                    for _, 행 in 동반df_raw.iterrows():
                        cat = 행[카테고리컬럼]
                        색 = 카테고리색.get(cat,"#b8b0a8")
                        top_subs = ""
                        if 서브카테고리컬럼 and len(동반구매_원본) > 0:
                            cat_rows = 동반구매_원본[동반구매_원본[카테고리컬럼]==cat]
                            if len(cat_rows) > 0:
                                top_subs = ", ".join(cat_rows.groupby(서브카테고리컬럼)[매출컬럼].sum().sort_values(ascending=False).head(3).index.tolist())
                        ko_text = 전략맵_ko[cat](행, 국가명표시, 선택계절_표시) if cat in 전략맵_ko else f"동반 구매 ${행['총매출']/1000:.0f}K. {선택계절_표시}에 번들 프로모션을 실행하십시오."
                        if top_subs:
                            ko_text += f" 주요 서브카테고리: {top_subs}."
                        전략 = t(ko_text)
                        sub_html = f'<div style="margin-top:6px;font-size:13px;color:#7b93a8;"><b>{t("주요 서브카테고리")}:</b> {top_subs}</div>' if top_subs else ""
                        st.markdown(f"""<div class="strat-card" style="border-left-color:{색};">
                            <div class="strat-country">Bikes → {cat}</div>
                            <div class="strat-text">{전략}</div>
                            {sub_html}
                        </div>""", unsafe_allow_html=True)

                if len(계절카테고리) > 0:
                    현재계절_데이터 = 계절카테고리[계절카테고리["계절"]==선택계절_키]
                    if len(현재계절_데이터) > 0:
                        최고카t = 현재계절_데이터.loc[현재계절_데이터["매출"].idxmax(),"카테고리"]
                        최고매출 = 현재계절_데이터["매출"].max()
                        insight_ko = f"{선택계절_표시}에 Bikes 구매 고객의 동반 구매 중 {최고카t}가 ${최고매출/1000:.0f}K로 가장 높습니다. 자전거 구매 시점에 {최고카t} 번들 할인을 제안하십시오."
                        st.markdown(f"""<div class="strat-card" style="border-left-color:#7b93a8;margin-top:12px;">
                            <div class="strat-country">{t("시즌 인사이트")} — {선택계절_표시}</div>
                            <div class="strat-text">{t(insight_ko)}</div>
                        </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
render_footer()