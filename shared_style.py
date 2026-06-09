CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg:#f7f5f2; --surface:#ffffff; --surface2:#f0ede8; --border:#ddd8d0;
    --accent:#7b93a8; --accent2:#8aab8e; --warn:#8B6F47; --danger:#b56b6b;
    --text:#2e2a26; --muted:#8c8480;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;color:var(--text)!important;}
.stApp{background-color:var(--bg)!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stSidebarNav"],[data-testid="stSidebarNavItems"],[data-testid="stSidebarNavSeparator"]{display:none!important;}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span,[data-testid="stSidebar"] div{color:var(--muted)!important;font-family:'DM Sans',sans-serif!important;font-size:15px!important;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:var(--text)!important;font-family:'DM Sans',sans-serif!important;font-size:13px!important;letter-spacing:0.1em!important;text-transform:uppercase!important;font-weight:600!important;}
[data-baseweb="radio"] label span:first-child{border-color:var(--border)!important;background:transparent!important;}
[data-baseweb="radio"] [aria-checked="true"] span:first-child{background-color:var(--accent)!important;border-color:var(--accent)!important;}
[data-testid="stSlider"] [role="slider"]{background-color:var(--accent)!important;border-color:var(--accent)!important;box-shadow:none!important;}
div[data-testid="stSlider"]>div>div>div>div{background:var(--border)!important;}
[data-testid="stSlider"]>div>div>div>div>div[style]{background:var(--accent)!important;}
input,[data-baseweb="input"]>div,[data-baseweb="select"]>div{background-color:var(--surface2)!important;border-color:var(--border)!important;color:var(--text)!important;border-radius:4px!important;}
h1{font-family:'Libre Baskerville',serif!important;font-size:54px!important;font-weight:700!important;color:var(--text)!important;line-height:1.15!important;letter-spacing:-0.5px!important;margin:0 0 8px 0!important;padding:0!important;border:none!important;}
h2{font-family:'DM Sans',sans-serif!important;font-size:15px!important;font-weight:600!important;color:var(--muted)!important;text-transform:uppercase!important;letter-spacing:0.12em!important;}
h3{font-family:'DM Sans',sans-serif!important;font-size:14px!important;color:var(--muted)!important;text-transform:uppercase!important;letter-spacing:0.08em!important;}
p,li,span,td,th{font-size:16px!important;}
label{font-size:15px!important;font-family:'DM Sans',sans-serif!important;}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px;}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:22px 26px;position:relative;overflow:hidden;}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--accent);}
.kpi-card.green::before{background:var(--accent2);}
.kpi-card.warn::before{background:var(--warn);}
.kpi-val{font-family:'Cormorant',serif;font-size:44px;font-weight:600;color:var(--text);line-height:1.1;margin-bottom:6px;}
.kpi-label{font-size:13px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:0.12em;}
.section-header{display:flex;align-items:center;gap:8px;margin:28px 0 14px 0;padding-bottom:9px;border-bottom:1px solid var(--border);}
.section-header span{font-family:'DM Sans',sans-serif!important;font-size:13px!important;font-weight:600!important;color:var(--muted)!important;text-transform:uppercase;letter-spacing:0.14em;}
.section-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);flex-shrink:0;}
.fin-card{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:24px;}
.fin-card .fin-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);font-size:16px;}
.fin-card .fin-row:last-of-type{border-bottom:none;}
.fin-card .fin-label{color:var(--muted);font-size:15px;}
.fin-card .fin-value{font-family:'Cormorant',serif;font-size:20px;color:var(--text);font-weight:600;}
.fin-card .fin-total{margin-top:14px;padding-top:14px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:baseline;}
.fin-card .fin-total .fin-label{font-size:15px;color:var(--muted);}
.fin-card .fin-total .fin-value{font-family:'Cormorant',serif;font-size:36px;font-weight:700;}
.fin-card .fin-total .pos{color:var(--accent2);}
.fin-card .fin-total .neg{color:var(--danger);}
.strat-card{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:4px;padding:16px 20px;margin-bottom:10px;font-size:15px;line-height:1.8;}
.strat-card .strat-country{font-family:'DM Sans',sans-serif;font-size:13px;font-weight:600;color:#5a4a3a;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;}
.strat-card .strat-text{color:var(--muted);font-size:15px;}
.alert-box{border-radius:4px;padding:14px 18px;font-size:15px;margin-top:14px;line-height:1.7;}
.alert-box.ok{background:#f0f6f1;border:1px solid #c2d9c5;color:#4e7a54;}
.alert-box.bad{background:#fdf1f1;border:1px solid #e0bcbc;color:var(--danger);}
.custom-footer{position:fixed;right:20px;bottom:15px;background:var(--surface);border:1px solid var(--border);color:var(--muted);padding:8px 16px;border-radius:4px;font-family:'DM Sans',sans-serif;font-size:12px;font-weight:500;letter-spacing:0.05em;z-index:999;display:flex;align-items:center;gap:8px;}
.footer-logo{height:22px;width:auto;opacity:0.6;}
.main-content{margin-bottom:60px;}
hr{border-color:var(--border)!important;}
*:focus{outline:none!important;box-shadow:none!important;}
button[data-baseweb="tab"]{font-family:'DM Sans',sans-serif!important;font-size:16px!important;font-weight:600!important;letter-spacing:0.04em!important;}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--accent)!important;}
button[data-baseweb="tab"][aria-selected="false"]{color:var(--muted)!important;}
[data-testid="stAlert"]{display:none!important;}
div[data-testid="stAppViewContainer"] > section > div:first-child{padding-top:0.5rem!important;}
div[data-testid="block-container"]{padding-top:0.8rem!important;}
div[data-testid="stAppViewBlockContainer"]{padding-top:0.5rem!important;}
.block-container{padding-top:0.5rem!important;}
</style>
"""

LANG_CODES = {"🇰🇷": "ko", "🇬🇧": "en", "🇪🇸": "es", "🇷🇺": "ru"}
DEST_TO_GOOGLETRANS = {"ko": "ko", "en": "en", "es": "es", "ru": "ru"}

import json, os, hashlib

_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations_cache.json")

def _load_cache():
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def _save_cache(cache):
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except: pass

def translate(text, dest):
    if dest == "ko" or not text or not text.strip():
        return text
    key = f"{dest}::{hashlib.md5(text.encode()).hexdigest()}"
    cache = _load_cache()
    if key in cache:
        return cache[key]
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source="ko", target=dest).translate(text)
        cache[key] = result
        _save_cache(cache)
        return result
    except:
        try:
            from googletrans import Translator
            result = Translator().translate(text, src="ko", dest=dest).text
            cache[key] = result
            _save_cache(cache)
            return result
        except:
            return text

def translate_bulk(texts, dest):
    if dest == "ko":
        return texts
    cache = _load_cache()
    to_fetch = []
    keys = []
    for text in texts:
        key = f"{dest}::{hashlib.md5(text.encode()).hexdigest()}"
        keys.append(key)
        if key not in cache:
            to_fetch.append(text)
    if to_fetch:
        try:
            from deep_translator import GoogleTranslator
            results = GoogleTranslator(source="ko", target=dest).translate_batch(to_fetch)
            fetch_keys = [f"{dest}::{hashlib.md5(t.encode()).hexdigest()}" for t in to_fetch]
            for k, r in zip(fetch_keys, results):
                cache[k] = r
            _save_cache(cache)
        except:
            pass
    return [cache.get(k, texts[i]) for i, k in enumerate(keys)]

def lang_init(key_prefix):
    import streamlit as st
    if "lang" not in st.session_state:
        st.session_state["lang"] = "ko"
    params = st.query_params
    for code in ["ko","en","es","ru"]:
        if params.get(f"lang_{key_prefix}") == code:
            st.session_state["lang"] = code
            st.query_params.clear()
            st.rerun()
    return st.session_state["lang"]

def lang_selector(key_prefix):
    import streamlit as st
    lang = st.session_state.get("lang","ko")
    flags = [("ko","KR"),("en","GB"),("es","ES"),("ru","RU")]
    twemoji = {"KR":"1f1f0-1f1f7","GB":"1f1ec-1f1e7","ES":"1f1ea-1f1f8","RU":"1f1f7-1f1fa"}
    _, c1, c2, c3, c4 = st.columns([5,1,1,1,1])
    for col,(code,cc) in zip([c1,c2,c3,c4], flags):
        active = lang == code
        img_url = f"https://twemoji.maxcdn.com/v/latest/svg/{twemoji[cc]}.svg"
        border = "#7b93a8" if active else "#ddd8d0"
        bg = "#eef2f5" if active else "#fff"
        with col:
            st.markdown(f"""<div style="text-align:center;">
            <a href="?lang_{key_prefix}={code}" target="_self"
               style="display:inline-flex;align-items:center;justify-content:center;
                      width:100%;padding:5px 2px;background:{bg};
                      border:1.5px solid {border};border-radius:6px;
                      cursor:pointer;text-decoration:none;">
                <img src="{img_url}" style="height:22px;width:22px;">
            </a></div>""", unsafe_allow_html=True)
    return lang

def get_base64_image(image_path):
    import base64, os
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def render_footer():
    import streamlit as st
    logo_base64 = get_base64_image("logo.png")
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="footer-logo">' if logo_base64 else ""
    st.markdown(f'''
<style>
.clickable-footer {{
    position:fixed;right:20px;bottom:15px;
    background:var(--surface);border:1px solid var(--border);
    color:var(--muted);padding:8px 16px;border-radius:4px;
    font-family:'DM Sans',sans-serif;font-size:12px;font-weight:500;
    letter-spacing:0.05em;z-index:999;display:flex;
    align-items:center;gap:8px;cursor:pointer;
    text-decoration:none;transition:border-color 0.2s;
}}
.clickable-footer:hover{{border-color:var(--accent);color:var(--accent);}}
</style>
<a href="/" class="clickable-footer" title="홈으로 돌아가기">
    {logo_html}<span>2555041</span>
</a>''', unsafe_allow_html=True)

def pastel_layout(fig, height=380, margin=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
        font=dict(family="DM Sans, sans-serif", color="#8c8480", size=14),
        height=height, margin=margin or dict(l=10, r=10, t=28, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#ddd8d0", borderwidth=1, font=dict(size=14)),
        xaxis=dict(gridcolor="#ede9e4", zerolinecolor="#ddd8d0", linecolor="#ddd8d0", tickfont=dict(size=13)),
        yaxis=dict(gridcolor="#ede9e4", zerolinecolor="#ddd8d0", linecolor="#ddd8d0", tickfont=dict(size=13)),
    )
    return fig

import os
서버주소 = os.getenv("API_URL", "http://localhost:8000")
카테고리_색상 = {"Bikes":"#7b93a8","Accessories":"#8aab8e","Clothing":"#c4956a","Components":"#a98baa"}
계절_색상 = {"봄":"#8aab8e","여름":"#7b93a8","가을":"#c4956a","겨울":"#a98baa"}
피처_한글명 = {
    "Order Quantity":"주문 수량","Unit Price":"제품 단가",
    "Standard Cost":"제조 원가","Month_num":"월 코드",
    "Category_enc":"카테고리","Country_enc":"국가",
}