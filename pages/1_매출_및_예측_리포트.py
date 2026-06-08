import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_style import CSS, pastel_layout, 서버주소, get_base64_image, translate, translate_bulk, lang_selector, lang_init

st.set_page_config(page_title="매출 및 예측 리포트", page_icon="◈", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<style>[data-testid="stSidebar"]{display:none!important;}[data-testid="collapsedControl"]{display:none!important;}</style>', unsafe_allow_html=True)

@st.cache_data(ttl=60)
def 메타조회():
    try: return requests.get(f"{서버주소}/api/metadata", timeout=5).json()
    except: return {"국가목록":["Australia","Canada","France","Germany","United Kingdom"],"카테고리목록":["Accessories","Bikes","Clothing","Components"],"총레코드수":0,"모델R2":0.0,"피처중요도":{},"피처수":6}

@st.cache_data(ttl=300, show_spinner=False)
def csv_로드():
    기본경로 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "adventureworks_clean.csv")
    if os.path.exists(기본경로): return pd.read_csv(기본경로)
    현재경로 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adventureworks_clean.csv")
    if os.path.exists(현재경로): return pd.read_csv(현재경로)
    return None

# FIX: month is now part of the cache key so changing the slider triggers a new API call
@st.cache_data(ttl=30, show_spinner=False)
def 단일예측(수량, 단가, 원가, 월, 국가, 카테고리):
    try:
        r = requests.post(f"{서버주소}/api/predict/strategy", timeout=5, json={
            "주문수량":수량,"제품단가":float(단가),"제조원가":float(원가),
            "월코드":월,"선택국가":국가,"선택카테고리":카테고리}).json()
        return float(r.get("예측매출액", 0.0))
    except: return float(수량 * 단가 * 1.1)

@st.cache_data(ttl=30, show_spinner=False)
def 국가별_전체예측(수량, 단가, 원가, 월, 국가목록_t, is_reseller, 카테고리):
    결과 = []
    for 국가 in 국가목록_t:
        if is_reseller:
            매출 = int(수량 * 단가 * 0.85)
        else:
            try:
                r = requests.post(f"{서버주소}/api/predict/strategy", timeout=5, json={
                    "주문수량":수량,"제품단가":float(단가),"제조원가":float(원가),
                    "월코드":월,"선택국가":국가,"선택카테고리":카테고리}).json()
                매출 = float(r.get("예측매출액", 0.0))
            except: 매출 = float(수량 * 단가 * 1.1)
        총원가 = 수량 * 원가
        순수익 = 매출 - 총원가
        결과.append({"국가":국가,"예측매출":round(매출,2),"총원가":총원가,"순수익":round(순수익,2)})
    return pd.DataFrame(결과)

메타 = 메타조회()
국가목록 = 메타["국가목록"]
logo_base64 = get_base64_image("logo.png")
원본df = csv_로드()

if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"
lang_init("p1")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

lang = lang_selector("p1")
def t(text): return translate(text, lang)

if lang != "ko":
    translate_bulk([
        "매출 및 예측 리포트", "← 홈",
        "AdventureWorks 판매 데이터 기반 실적 분석 및 AI 예측. 핵심 제품은 자전거(Bikes)로 전체 매출의 약 70~80%를 차지합니다.",
        "실적 현황 — 실제 데이터", "예측 시뮬레이션 — 판매 계획",
        "전체 매출 요약 — 실제 데이터 기준", "총 매출액", "총 주문 수량", "평균 단가", "전체 레코드 수",
        "서브카테고리별 총 매출", "국가별 총 매출", "카테고리별 매출 비중",
        "세계 판매 지도 — 국가별 매출 현황", "총매출($)",
        "판매 계획 설정 — 수량·단가·국가를 선택하면 AI가 수익을 예측합니다",
        "거래 유형", "일반 개인 고객", "도매 및 대리점", "판매 카테고리", "서브카테고리", "전체 (평균)",
        "수량", "단가 ($)", "원가 ($)", "분석 월", "국가", "전체 국가",
        "카테고리", "매출 산출 방식", "개", "제품 단가", "예측 총 매출", "총 제조 원가", "마진율", "순수익 추정",
        "도매 매출", "총 원가", "순수익", "주문 수량", "금액 ($)", "예측 매출", "구매 수량", "예측 매출 ($)",
        "전체 국가 비교 — 동일 조건으로 국가별 예측 매출 및 순수익", "국가별 예측 계산 중…",
        "예측 매출 ($)", "총 원가 ($)", "순수익 ($)",
        "3D 예측 곡면 — 수량 × 단가 × 예측 매출",
        "X축: 수량, Y축: 단가 범위 (현재 설정 ±50%), Z축: AI 예측 매출. 드래그로 회전하세요.",
        "예측매출($)", "순수익($)", "단가($)",
    ], lang)

top1, top2 = st.columns([6, 1])
with top1:
    st.markdown(f'<div style="font-family:\'Libre Baskerville\',serif;font-size:48px;font-weight:700;color:#2e2a26;margin:0;line-height:1.15;letter-spacing:-0.3px;">{t("매출 및 예측 리포트")}</div>', unsafe_allow_html=True)
with top2:
    st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
    if st.button(t("← 홈"), key="home_top", use_container_width=True):
        st.switch_page("home.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#ddd8d0;margin-top:-10px;margin-bottom:20px;'>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#8c8480;font-size:14px;margin-bottom:24px;'>{t('AdventureWorks 판매 데이터 기반 실적 분석 및 AI 예측. 핵심 제품은 자전거(Bikes)로 전체 매출의 약 70~80%를 차지합니다.')}</p>", unsafe_allow_html=True)

탭1, 탭2 = st.tabs([t("실적 현황 — 실제 데이터"), t("예측 시뮬레이션 — 판매 계획")])

with 탭1:
    if 원본df is None:
        st.error(t("adventureworks_clean.csv 파일을 찾을 수 없습니다. 프로젝트 루트 디렉토리를 확인해주세요."))
    else:
        df = 원본df.copy()
        매출컬럼 = next((c for c in df.columns if c.lower().replace(" ","").replace("_","") in ["salesamount","salesamt"]), None)
        if not 매출컬럼: 매출컬럼 = next((c for c in df.columns if "sales" in c.lower() and "amount" in c.lower()), None)
        수량컬럼 = next((c for c in df.columns if c.lower().replace(" ","").replace("_","") in ["orderquantity","orderqty"]), None)
        단가컬럼 = next((c for c in df.columns if "unit price" in c.lower() or "unitprice" in c.lower()), None)
        카테고리컬럼 = next((c for c in df.columns if "category" in c.lower() and "sub" not in c.lower()), None)
        서브카테고리컬럼 = next((c for c in df.columns if "subcategory" in c.lower() or "sub_category" in c.lower()), None)

        if 매출컬럼: df[매출컬럼] = pd.to_numeric(df[매출컬럼], errors="coerce").fillna(0)
        if 수량컬럼: df[수량컬럼] = pd.to_numeric(df[수량컬럼], errors="coerce").fillna(0)

        총매출 = df[매출컬럼].sum() if 매출컬럼 else 0
        총주문 = int(df[수량컬럼].sum()) if 수량컬럼 else len(df)
        평균단가 = df[단가컬럼].mean() if 단가컬럼 else (총매출/총주문 if 총주문>0 else 0)
        총레코드 = len(df)

        st.markdown(f'<div class="section-header"><div class="section-dot"></div><span>{t("전체 매출 요약 — 실제 데이터 기준")}</span></div>', unsafe_allow_html=True)
        k1,k2,k3,k4 = st.columns(4)
        with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">${총매출/1_000_000:.2f}M</div><div class="kpi-label">{t("총 매출액")}</div></div>', unsafe_allow_html=True)
        with k2: st.markdown(f'<div class="kpi-card green"><div class="kpi-val">{총주문:,}</div><div class="kpi-label">{t("총 주문 수량")}</div></div>', unsafe_allow_html=True)
        with k3: st.markdown(f'<div class="kpi-card warn"><div class="kpi-val">${평균단가:,.0f}</div><div class="kpi-label">{t("평균 단가")}</div></div>', unsafe_allow_html=True)
        with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{총레코드:,}</div><div class="kpi-label">{t("전체 레코드 수")}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        차트1, 차트2 = st.columns(2)

        with 차트1:
            st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#c4956a"></div><span>{t("서브카테고리별 총 매출")}</span></div>', unsafe_allow_html=True)
            if 서브카테고리컬럼 and 매출컬럼:
                서브df = df.groupby(서브카테고리컬럼)[매출컬럼].sum().sort_values(ascending=True).reset_index().tail(12)
                서브df.columns = ["서브카테고리","매출"]
                카테고리색 = {"Bikes":"#7b93a8","Accessories":"#8aab8e","Clothing":"#c4956a","Components":"#a98baa"}
                색상팔레트 = ["#7b93a8"]*len(서브df)
                if 카테고리컬럼:
                    카테고리맵 = df.drop_duplicates(서브카테고리컬럼).set_index(서브카테고리컬럼)[카테고리컬럼].to_dict()
                    색상팔레트 = [카테고리색.get(카테고리맵.get(s,""),"#b8b0a8") for s in 서브df["서브카테고리"]]
                fig_sub = go.Figure(go.Bar(x=서브df["매출"],y=서브df["서브카테고리"],orientation="h",
                    marker=dict(color=색상팔레트,line=dict(width=0)),
                    text=[f"${v/1000:.0f}K" for v in 서브df["매출"]],textposition="outside",
                    textfont=dict(family="DM Sans",size=12,color="#8c8480")))
                pastel_layout(fig_sub,height=360,margin=dict(l=10,r=70,t=10,b=10))
                fig_sub.update_xaxes(showticklabels=False,showgrid=False)
                st.plotly_chart(fig_sub,use_container_width=True)
                if 카테고리컬럼:
                    범례 = "".join([f"<span style='font-size:12px;color:#8c8480;display:flex;align-items:center;gap:5px;'><span style='width:10px;height:10px;border-radius:2px;background:{c};display:inline-block;'></span>{k}</span>" for k,c in 카테고리색.items()])
                    st.markdown(f"<div style='display:flex;gap:20px;flex-wrap:wrap;margin-top:-8px;margin-bottom:12px;'>{범례}</div>", unsafe_allow_html=True)

        with 차트2:
            st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#7b93a8"></div><span>{t("국가별 총 매출")}</span></div>', unsafe_allow_html=True)
            if 매출컬럼 and "Country" in df.columns:
                국가df = df.groupby("Country")[매출컬럼].sum().sort_values(ascending=True).reset_index()
                국가df.columns = ["국가","매출"]
                국가색 = {"United States":"#7b93a8","Canada":"#8aab8e","Australia":"#a8b8c8","United Kingdom":"#a98baa","France":"#c4956a","Germany":"#b8b0a8"}
                fig_국가 = go.Figure(go.Bar(x=국가df["매출"],y=국가df["국가"],orientation="h",
                    marker=dict(color=[국가색.get(c,"#b8b0a8") for c in 국가df["국가"]],line=dict(width=0)),
                    text=[f"${v/1_000_000:.2f}M" for v in 국가df["매출"]],textposition="outside",
                    textfont=dict(family="DM Sans",size=13,color="#8c8480")))
                pastel_layout(fig_국가,height=360,margin=dict(l=10,r=80,t=10,b=10))
                fig_국가.update_xaxes(showticklabels=False,showgrid=False)
                st.plotly_chart(fig_국가,use_container_width=True)

        if 카테고리컬럼 and 매출컬럼:
            st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("카테고리별 매출 비중")}</span></div>', unsafe_allow_html=True)
            카df = df.groupby(카테고리컬럼)[매출컬럼].sum().reset_index()
            카df.columns = ["카테고리","매출"]
            카df = 카df.sort_values("매출",ascending=False)
            카테고리색2 = {"Bikes":"#7b93a8","Accessories":"#8aab8e","Clothing":"#c4956a","Components":"#a98baa"}
            p1,p2 = st.columns([1,2])
            with p1:
                fig_pie = go.Figure(go.Pie(labels=카df["카테고리"],values=카df["매출"],hole=0.55,
                    marker=dict(colors=[카테고리색2.get(c,"#b8b0a8") for c in 카df["카테고리"]],line=dict(color="#f7f5f2",width=3)),
                    textfont=dict(family="DM Sans",size=13),textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>"))
                pastel_layout(fig_pie,height=280,margin=dict(l=10,r=10,t=10,b=10))
                fig_pie.update_layout(showlegend=False)
                st.plotly_chart(fig_pie,use_container_width=True)
            with p2:
                for _,행 in 카df.iterrows():
                    비중 = 행["매출"]/카df["매출"].sum()*100
                    색 = 카테고리색2.get(행["카테고리"],"#b8b0a8")
                    st.markdown(f"""<div style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <span style="font-size:14px;color:#2e2a26;font-weight:500;">{행["카테고리"]}</span>
                            <span style="font-size:13px;color:#8c8480;">${행["매출"]/1_000_000:.2f}M &nbsp;·&nbsp; {비중:.1f}%</span>
                        </div>
                        <div style="background:#e8e4df;border-radius:3px;height:6px;overflow:hidden;">
                            <div style="background:{색};width:{비중:.1f}%;height:100%;border-radius:3px;"></div>
                        </div></div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#7b93a8"></div><span>{t("세계 판매 지도 — 국가별 매출 현황")}</span></div>', unsafe_allow_html=True)
        국가_좌표 = {"United States":(37.1,-95.7),"Canada":(56.1,-106.3),"Australia":(-25.3,133.8),"United Kingdom":(55.4,-3.4),"France":(46.2,2.2),"Germany":(51.2,10.4)}
        if 매출컬럼 and "Country" in df.columns:
            국가매출_map = df.groupby("Country")[매출컬럼].sum().reset_index()
            국가매출_map.columns = ["국가","총매출"]
            유효국가 = [c for c in 국가매출_map["국가"] if c in 국가_좌표]
            map_lats=[국가_좌표[c][0] for c in 유효국가]
            map_lons=[국가_좌표[c][1] for c in 유효국가]
            map_vals=[국가매출_map[국가매출_map["국가"]==c]["총매출"].values[0] for c in 유효국가]
            fig_map = go.Figure(go.Scattergeo(lat=map_lats,lon=map_lons,mode="markers+text",
                marker=dict(size=[max(18,v/120000) for v in map_vals],color=map_vals,
                    colorscale=[[0,"#e8c9a8"],[0.4,"#a8b8c8"],[1,"#7b93a8"]],showscale=True,sizemode="diameter",
                    colorbar=dict(title=t("총매출($)"),tickformat="$,.0f",tickfont=dict(size=11,color="#8c8480"),title_font=dict(size=11,color="#8c8480")),
                    line=dict(color="#f7f5f2",width=2)),
                text=유효국가,textposition="top center",textfont=dict(size=13,color="#2e2a26"),
                hovertemplate="<b>%{text}</b><br>$%{marker.color:,.0f}<extra></extra>"))
            fig_map.update_layout(geo=dict(showland=True,landcolor="#f0ede8",showocean=True,oceancolor="#eaf0f5",
                showcoastlines=True,coastlinecolor="#ddd8d0",showcountries=True,countrycolor="#ddd8d0",
                showframe=False,projection_type="natural earth",bgcolor="rgba(0,0,0,0)"),
                paper_bgcolor="rgba(0,0,0,0)",height=380,margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_map,use_container_width=True)

with 탭2:
    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("판매 계획 설정 — 수량·단가·국가를 선택하면 AI가 수익을 예측합니다")}</span></div>', unsafe_allow_html=True)

    서브카테고리_단가표 = {
        "Road Bikes":(980,618),"Mountain Bikes":(667,364),"Touring Bikes":(935,581),
        "Mountain Frames":(300,200),"Road Frames":(280,180),"Touring Frames":(250,160),
        "Wheels":(120,60),"Helmets":(35,13),"Jerseys":(52,40),"Tires and Tubes":(14,5),
        "Shorts":(70,26),"Gloves":(24,9),"Bike Racks":(120,45),"Bottles and Cages":(7,3),
        "Hydration Packs":(55,21),"Fenders":(22,8),"Bike Stands":(159,59),"Vests":(64,24),
        "Caps":(9,7),"Socks":(9,3),"Cranksets":(150,80),"Handlebars":(90,45),"Pedals":(80,40),
    }
    카테고리별_서브 = {
        "Bikes":["Road Bikes","Mountain Bikes","Touring Bikes"],
        "Components":["Mountain Frames","Road Frames","Touring Frames","Wheels","Cranksets","Handlebars","Pedals"],
        "Accessories":["Helmets","Tires and Tubes","Bike Racks","Bottles and Cages","Hydration Packs","Fenders","Bike Stands"],
        "Clothing":["Jerseys","Shorts","Gloves","Vests","Caps","Socks"],
    }

    sim1,sim2,sim3 = st.columns(3)
    with sim1:
        고객유형 = st.radio(t("거래 유형"), [t("일반 개인 고객"), t("도매 및 대리점")], horizontal=True)
    with sim2:
        선택카테고리 = st.selectbox(t("판매 카테고리"), 메타["카테고리목록"])
    with sim3:
        서브목록 = 카테고리별_서브.get(선택카테고리,[])
        선택서브카테고리 = st.selectbox(t("서브카테고리"), [t("전체 (평균)")]+서브목록, key="sim_sub")

    is_reseller = 고객유형 == t("도매 및 대리점")
    이전키 = f"이전_{선택카테고리}_{선택서브카테고리}"
    if st.session_state.get("이전선택키") != 이전키:
        if 선택서브카테고리 not in [t("전체 (평균)"), "전체 (평균)"] and 선택서브카테고리 in 서브카테고리_단가표:
            기본단가, 기본원가 = 서브카테고리_단가표[선택서브카테고리]
        else:
            기본단가, 기본원가 = 462, 250
        st.session_state["sim_price"] = 기본단가
        st.session_state["sim_cost"] = 기본원가
        st.session_state["이전선택키"] = 이전키

    p1,p2,p3,p4,p5 = st.columns(5)
    with p1: 수량 = st.slider(t("수량"), 1, 100 if is_reseller else 6, 20 if is_reseller else 1, key="sim_qty")
    with p2: 단가 = st.number_input(t("단가 ($)"), min_value=1, key="sim_price", value=st.session_state.get("sim_price",462))
    with p3: 원가 = st.number_input(t("원가 ($)"), min_value=1, key="sim_cost", value=st.session_state.get("sim_cost",250))
    with p4: 월 = st.slider(t("분석 월"), 1, 12, 6, key="sim_month")
    with p5: 선택국가 = st.selectbox(t("국가"), [t("전체 국가")]+국가목록, key="sim_country")
    if is_reseller:
        st.markdown(f"<p style='color:#8c8480;font-size:12px;margin:-10px 0 10px;'>💡 {t('단가')} = {t('정상가')} (${단가:,}) → {t('도매 실제 청구단가')} ${int(단가*0.85):,} (15% {t('할인 적용')})</p>", unsafe_allow_html=True)

    # show month label so user knows which season they're simulating
    월_to_계절 = {12:"겨울",1:"겨울",2:"겨울",3:"봄",4:"봄",5:"봄",6:"여름",7:"여름",8:"여름",9:"가을",10:"가을",11:"가을"}
    계절표시 = 월_to_계절.get(월, "")
    st.markdown(f"<p style='color:#8c8480;font-size:12px;margin:-8px 0 12px;'>📅 {월}월 — {t(계절표시)} 시즌</p>", unsafe_allow_html=True)

    기본국가 = 국가목록[0] if 선택국가 == t("전체 국가") else 선택국가
    서브표시 = 선택서브카테고리 if 선택서브카테고리 not in [t("전체 (평균)"), "전체 (평균)"] else 선택카테고리

    if is_reseller:
        예측매출 = int(수량 * 단가 * 0.85)
        단가after = int(단가 * 0.85)
        매출출처 = t(f"도매 단가 기반 (수량 {수량} × 단가 ${단가:,} × 도매할인 85% = 실제단가 ${단가after:,})")
    else:
        예측매출 = int(단일예측(수량,단가,원가,월,기본국가,선택카테고리))
        매출출처 = f"{t('Random Forest AI 모델 예측')} ({서브표시})"

    총원가 = int(수량*원가)
    순수익 = 예측매출-총원가
    마진율 = int(round(순수익/예측매출*100)) if 예측매출>0 else 0
    profit_class = "pos" if 순수익>=0 else "neg"

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="fin-card">
            <div class="fin-row"><span class="fin-label">{t("거래 유형")}</span><span class="fin-value">{고객유형}</span></div>
            <div class="fin-row"><span class="fin-label">{t("카테고리")}</span><span class="fin-value">{서브표시}</span></div>
            <div class="fin-row"><span class="fin-label">{t("매출 산출 방식")}</span><span class="fin-value" style="font-size:13px;">{매출출처}</span></div>
            <div class="fin-row"><span class="fin-label">{t("수량")}</span><span class="fin-value">{수량}{t("개")}</span></div>
            <div class="fin-row"><span class="fin-label">{t("제품 단가")}</span><span class="fin-value">${단가:,}</span></div>
            <div class="fin-row"><span class="fin-label">{t("분석 월")}</span><span class="fin-value">{월}월 ({t(계절표시)})</span></div>
            <div class="fin-row"><span class="fin-label">{t("예측 총 매출")}</span><span class="fin-value">${예측매출:,}</span></div>
            <div class="fin-row"><span class="fin-label">{t("총 제조 원가")}</span><span class="fin-value">${총원가:,}</span></div>
            <div class="fin-row"><span class="fin-label">{t("마진율")}</span><span class="fin-value">{마진율}%</span></div>
            <div class="fin-total"><span class="fin-label">{t("순수익 추정")}</span><span class="fin-value {profit_class}">${순수익:,}</span></div>
        </div>""", unsafe_allow_html=True)
        if is_reseller and 순수익>0:
            insight = t(f"도매 주문 {수량}개 기준 추정 수익. 도매 할인율 15% 적용.")
        elif 순수익>0:
            insight = t(f"마진율 {마진율}% — 현재 파라미터는 안정적입니다.")
        elif is_reseller:
            insight = t(f"손익분기 최소 단가: ${int(총원가/수량/0.85):,}")
        else:
            insight = t("현재 설정은 손실이 예상됩니다. 단가를 높이거나 원가를 줄여보세요.")
        st.markdown(f'<div class="alert-box {"ok" if 순수익>0 else "bad"}">{insight}</div>', unsafe_allow_html=True)

    with c2:
        if is_reseller:
            qty_range = list(range(5,max(수량+50,60),max(1,수량//8)))
            rev=[int(q*단가*0.85) for q in qty_range]
            cost_=[int(q*원가) for q in qty_range]
            profit_=[r-c for r,c in zip(rev,cost_)]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=qty_range,y=rev,name=t("도매 매출"),mode="lines",line=dict(color="#7b93a8",width=2),fill="tozeroy",fillcolor="rgba(123,147,168,0.07)"))
            fig.add_trace(go.Scatter(x=qty_range,y=cost_,name=t("총 원가"),mode="lines",line=dict(color="#c4956a",width=2,dash="dot")))
            fig.add_trace(go.Scatter(x=qty_range,y=profit_,name=t("순수익"),mode="lines+markers",line=dict(color="#8aab8e",width=2),marker=dict(size=5)))
            pastel_layout(fig,height=320)
            fig.update_xaxes(title_text=t("주문 수량"))
            fig.update_yaxes(title_text=t("금액 ($)"))
            fig.add_hline(y=0,line_dash="dot",line_color="#ddd8d0")
        else:
            vals=[단일예측(q,단가,원가,월,기본국가,선택카테고리) for q in range(1,7)]
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=list(range(1,7)),y=vals,mode="lines+markers",
                line=dict(color="#7b93a8",width=2),marker=dict(color="#7b93a8",size=7,line=dict(color="#f7f5f2",width=2)),
                fill="tozeroy",fillcolor="rgba(123,147,168,0.08)",name=t("예측 매출")))
            pastel_layout(fig,height=320)
            fig.update_xaxes(title_text=t("구매 수량"),tickmode="linear",dtick=1)
            fig.update_yaxes(title_text=t("예측 매출 ($)"))
        st.plotly_chart(fig,use_container_width=True)

    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#7b93a8"></div><span>{t("전체 국가 비교 — 동일 조건으로 국가별 예측 매출 및 순수익")}</span></div>', unsafe_allow_html=True)
    분析국가목록 = 국가목록 if 선택국가==t("전체 국가") else [선택국가]
    with st.spinner(t("국가별 예측 계산 중…")):
        pred_all = 국가별_전체예측(수량,단가,원가,월,tuple(분析국가목록),is_reseller,선택카테고리)

    ga,gb = st.columns(2)
    with ga:
        fig3=go.Figure()
        fig3.add_trace(go.Bar(name=t("예측 매출"),x=pred_all["국가"],y=pred_all["예측매출"],marker_color="#7b93a8",marker_line_width=0))
        fig3.add_trace(go.Bar(name=t("순수익"),x=pred_all["국가"],y=pred_all["순수익"],marker_color="#8aab8e",marker_line_width=0))
        pastel_layout(fig3,height=320)
        fig3.update_layout(barmode="group")
        fig3.update_yaxes(title_text=t("금액 ($)"))
        fig3.add_hline(y=0,line_dash="dot",line_color="#ddd8d0")
        st.plotly_chart(fig3,use_container_width=True)
    with gb:
        display_df=pred_all.copy()
        display_df.columns=["국가",t("예측 매출 ($)"),t("총 원가 ($)"),t("순수익 ($)")]
        display_df[t("예측 매출 ($)")]=display_df[t("예측 매출 ($)")].apply(lambda x:f"${x:,.0f}")
        display_df[t("총 원가 ($)")]=display_df[t("총 원가 ($)")].apply(lambda x:f"${x:,.0f}")
        display_df[t("순수익 ($)")]=display_df[t("순수익 ($)")].apply(lambda x:f"${x:,.0f}")
        st.dataframe(display_df,use_container_width=True,hide_index=True)
        for _,행 in pred_all.iterrows():
            마진=int(행["순수익"]/행["예측매출"]*100) if 행["예측매출"]>0 else 0
            box="ok" if 행["순수익"]>0 else "bad"
            st.markdown(f'<div class="alert-box {box}" style="margin-bottom:6px;padding:10px 14px;"><b>{행["국가"]}</b> — {t("마진율")} {마진}%, {t("순수익")} ${행["순수익"]:,.0f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-header"><div class="section-dot" style="background:#a98baa"></div><span>{t("3D 예측 곡면 — 수량 × 단가 × 예측 매출")}</span></div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8c8480;font-size:13px;margin-bottom:12px;'>{t('X축: 수량, Y축: 단가 범위 (현재 설정 ±50%), Z축: AI 예측 매출. 드래그로 회전하세요.')}</p>", unsafe_allow_html=True)
    if not is_reseller:
        _q_range=list(range(1,7))
        _p_range=[int(단가*r) for r in [0.5,0.7,0.85,1.0,1.15,1.3,1.5]]
        _Q,_P=np.meshgrid(_q_range,_p_range)
        _Z=np.array([[단일예측(int(_Q[i,j]),_P[i,j],원가,월,기본국가,선택카테고리) for j in range(_Q.shape[1])] for i in range(_Q.shape[0])])
        cs=[[0,"#e8e4df"],[0.5,"#a8b8c8"],[1,"#7b93a8"]]
        cb_title=t("예측매출($)")
    else:
        _q_range=list(range(5,101,5))
        _p_range=[int(단가*r) for r in [0.5,0.7,0.85,1.0,1.15,1.3,1.5]]
        _Q,_P=np.meshgrid(_q_range,_p_range)
        _Z=_Q*_P*0.85-_Q*원가
        cs=[[0,"#b56b6b"],[0.4,"#e8e4df"],[1,"#8aab8e"]]
        cb_title=t("순수익($)")
    fig_3d=go.Figure(data=[go.Surface(z=_Z,x=_q_range,y=_p_range,colorscale=cs,showscale=True,
        colorbar=dict(title=cb_title,tickformat="$,.0f",tickfont=dict(size=10,color="#8c8480"),title_font=dict(size=10,color="#8c8480")))])
    fig_3d.update_layout(paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(bgcolor="#f7f5f2",
            xaxis=dict(title=t("수량"),gridcolor="#ddd8d0",backgroundcolor="#f7f5f2",color="#8c8480"),
            yaxis=dict(title=t("단가($)"),gridcolor="#ddd8d0",backgroundcolor="#f7f5f2",color="#8c8480"),
            zaxis=dict(title=cb_title,gridcolor="#ddd8d0",backgroundcolor="#f7f5f2",color="#8c8480",tickformat="$,.0f"),
            camera=dict(eye=dict(x=1.8,y=-1.8,z=1.2))),
        height=480,margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig_3d,use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

logo_tag = f'<img src="data:image/png;base64,{logo_base64}" class="footer-logo">' if logo_base64 else ""
st.markdown(f"""<style>.clickable-footer{{position:fixed;right:20px;bottom:15px;background:var(--surface);border:1px solid var(--border);color:var(--muted);padding:8px 16px;border-radius:4px;font-size:12px;font-weight:500;letter-spacing:0.05em;z-index:999;display:flex;align-items:center;gap:8px;cursor:pointer;text-decoration:none;transition:border-color 0.2s;}}.clickable-footer:hover{{border-color:var(--accent);color:var(--accent);}}</style>
<a href="/" class="clickable-footer">{logo_tag}<span>2555041</span></a>""", unsafe_allow_html=True)