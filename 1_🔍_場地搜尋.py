import streamlit as st
import pandas as pd

from utils.data_manager import DataManager
from utils.weather_manager import WeatherManager
from utils.responsive import apply_responsive_design

st.set_page_config(page_title="Finding Move 尋地寳", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

# CSS
apply_responsive_design()

# 初始化 managers
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()
if "weather_manager" not in st.session_state:
    st.session_state.weather_manager = WeatherManager()

dm: DataManager = st.session_state.data_manager
wm: WeatherManager = st.session_state.weather_manager

# 預設行政區
districts = dm.get_districts() or ["中正區","信義區","大安區","內湖區"]
default_district = districts[0]
if "selected_district" not in st.session_state:
    st.session_state.selected_district = default_district

# ---- Header 區：位置與天氣 ----
colH1, colH2 = st.columns([2, 1])
with colH1:
    st.title("🔍 台北運動場地搜尋引擎")
    sel = st.selectbox("📍 選擇行政區", options=districts, index=districts.index(st.session_state.selected_district) if st.session_state.selected_district in districts else 0)
    if sel != st.session_state.selected_district:
        st.session_state.selected_district = sel
with colH2:
    w = wm.get_current_weather(st.session_state.selected_district)
    icon = WeatherManager.get_weather_icon(w.get("weather_description",""), w.get("temperature", 28))
    st.metric("現在天氣", f"{icon} {w.get('weather_description','--')}")
    st.metric("溫度", f"{w.get('temperature','--')}°C (體感 {w.get('apparent_temperature','--')}°C)")
    st.caption(f"💧 濕度 {w.get('humidity','--')}%｜💨 {w.get('wind_direction','')} {w.get('wind_speed','')}｜降雨 {w.get('precipitation_probability','--')}%｜更新 {w.get('update_time','')}" )

st.divider()

# ---- 搜尋與篩選 ----
if "search_filters" not in st.session_state:
    st.session_state.search_filters = {
        "sport_type": [],
        "district": [st.session_state.selected_district],
        "price_range": [0, 5000],
        "facilities": [],
        "rating_min": 0.0,
    }

left, right = st.columns([3, 1])
with left:
    q = st.text_input("輸入關鍵字（場地/運動/地區）", placeholder="例如：籃球、羽毛球、信義區...")
with right:
    do_search = st.button("開始搜尋", type="primary", use_container_width=True)

with st.sidebar:
    st.header("🎯 搜尋篩選")
    sports = dm.get_sport_types()
    if sports:
        st.session_state.search_filters["sport_type"] = st.multiselect("運動類型", sports, default=st.session_state.search_filters["sport_type"])
    d_opts = dm.get_districts()
    if d_opts:
        st.session_state.search_filters["district"] = st.multiselect("地區", d_opts, default=st.session_state.search_filters["district"] or [st.session_state.selected_district])
    # 價格
    if not dm.get_all_venues().empty and "price_per_hour" in dm.get_all_venues().columns:
        min_p = int(pd.to_numeric(dm.get_all_venues()["price_per_hour"], errors="coerce").min(skipna=True) or 0)
        max_p = int(pd.to_numeric(dm.get_all_venues()["price_per_hour"], errors="coerce").max(skipna=True) or 5000)
        st.session_state.search_filters["price_range"] = st.slider("價格範圍 (每小時)", min_p, max_p, value=tuple(st.session_state.search_filters["price_range"]), step=50, format="NT$%d")
    # 設施
    facs = dm.get_facilities()
    if facs:
        st.session_state.search_filters["facilities"] = st.multiselect("設施需求", facs, default=st.session_state.search_filters["facilities"])
    # 評分
    st.session_state.search_filters["rating_min"] = st.slider("最低評分", 0.0, 5.0, value=float(st.session_state.search_filters["rating_min"]), step=0.1, format="%.1f")

# 執行查詢
filters = st.session_state.search_filters
if do_search or q:
    df = dm.get_filtered_venues(
        sport_types=filters["sport_type"],
        districts=filters["district"],
        price_range=list(filters["price_range"]),
        facilities=filters["facilities"],
        min_rating=filters["rating_min"],
        search_query=q
    )
else:
    df = dm.get_all_venues()

# ---- 顯示結果 ----
if df is None or df.empty:
    st.info("沒有找到符合條件的場地，請嘗試不同關鍵字或調整篩選。")
else:
    st.subheader(f"搜尋結果（{len(df)} 筆）")
    for idx, row in df.head(30).iterrows():
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3,1,1,1,2])
            c1.markdown(f"**{row.get('name','場地')}**\n\n{row.get('address','—')}\n\n{row.get('district','—')}｜{row.get('sport_type','—')}")
            if row.get('rating'):
                c2.metric("評分", f"{float(row.get('rating')):.1f}")
            if row.get('price_per_hour'):
                c3.metric("價格", f"NT${int(row.get('price_per_hour'))}/hr")
            if row.get('facilities'):
                fac_short = str(row.get('facilities'))[:16] + ('…' if len(str(row.get('facilities'))) > 16 else '')
                c4.write(f"設施：{fac_short}")
            b1, b2 = c5.columns(2)
            if b1.button("📋 詳情", key=f"detail_{row.get('id',idx)}"):
                st.query_params["id"] = int(row.get('id', idx))
                st.switch_page("pages/5_🏢_場地詳情.py")
            if b2.button("❤️ 收藏", key=f"fav_{row.get('id',idx)}"):
                if "favorites" not in st.session_state:
                    st.session_state["favorites"] = {}
                st.session_state["favorites"][str(row.get('id',idx))] = row.to_dict()
                st.success("已加入收藏")

st.divider()
st.caption("提示：可在左側調整篩選條件，或切換至『🗺️ 地圖檢視』查看地圖上的分佈。")
