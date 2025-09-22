import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

from utils.data_manager import DataManager
from utils.map_utils import MapUtils
from utils.responsive import apply_responsive_design

st.set_page_config(page_title="地圖檢視 - 台北運動場地搜尋引擎", page_icon="🗺️", layout="wide")
apply_responsive_design()

if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'map_utils' not in st.session_state:
    st.session_state.map_utils = MapUtils()

dm: DataManager = st.session_state.data_manager
mu: MapUtils = st.session_state.map_utils

st.title("🗺️ 場地地圖檢視")
st.markdown("在地圖上探索台北市的運動場地")

with st.sidebar:
    st.header("🗺️ 地圖控制")
    center = st.selectbox("地圖中心", list(mu.district_centers.keys()), index=0, key="map_center")
    st.subheader("📍 顯示篩選")
    sports = dm.get_sport_types()
    show_sports = st.multiselect("顯示運動類型", sports, default=sports[:5] if sports else [])
    dists = dm.get_districts()
    show_districts = st.multiselect("顯示地區", dists, default=dists[:5] if dists else [])
    price_range = st.slider("價格範圍 (每小時)", 0, 10000, value=(0, 5000), step=100, format="NT$%d")
    min_rating = st.slider("最低評分", 0.0, 5.0, value=0.0, step=0.1, format="%.1f")
    st.subheader("🎨 地圖樣式")
    style = st.selectbox("地圖樣式", ["OpenStreetMap","CartoDB positron","CartoDB dark_matter","Stamen Terrain"])
    show_heatmap = st.checkbox("顯示熱力圖", value=False)
    show_clusters = st.checkbox("群集顯示", value=True)

col1, col2 = st.columns([3,1])

with col1:
    center_latlng = mu.get_district_center(center)
    m = folium.Map(location=center_latlng, zoom_start=12, tiles=None)
    tile_mapping = {
        "OpenStreetMap": folium.TileLayer('openstreetmap', attr='OpenStreetMap contributors'),
        "CartoDB positron": folium.TileLayer('cartodbpositron', attr='CartoDB contributors'),
        "CartoDB dark_matter": folium.TileLayer('cartodbdark_matter', attr='CartoDB contributors'),
        "Stamen Terrain": folium.TileLayer('stamenterrain', attr='Stamen Design + OSM')
    }
    tile_mapping.get(style, folium.TileLayer('openstreetmap')).add_to(m)

    data = dm.get_filtered_venues(sport_types=show_sports, districts=show_districts, price_range=list(price_range), min_rating=min_rating)
    if data is not None and not data.empty:
        if show_clusters:
            from folium.plugins import MarkerCluster
            container = MarkerCluster().add_to(m)
        else:
            container = m

        sport_colors = mu.get_sport_colors()
        for _, v in data.iterrows():
            if pd.notna(v.get('latitude')) and pd.notna(v.get('longitude')):
                stype = v.get('sport_type', '其他')
                color = sport_colors.get(stype, 'gray')
                popup_html = f"""
                <div style="width:240px">
                  <h4 style="margin:0 0 6px 0">{v.get('name','場地')}</h4>
                  <div>🏃‍♂️ {v.get('sport_type','—')}</div>
                  <div>📍 {v.get('district','—')}</div>
                  <div>{'💰 NT$%s/hr' % int(v.get('price_per_hour')) if v.get('price_per_hour') else ''}</div>
                  <div>{'⭐ %.1f' % float(v.get('rating')) if v.get('rating') else ''}</div>
                </div>
                """
                folium.Marker(
                    location=[v.get('latitude'), v.get('longitude')],
                    popup=folium.Popup(popup_html, max_width=280),
                    tooltip=f"{v.get('name','場地')} - {stype}",
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(container)

        if show_heatmap:
            from folium.plugins import HeatMap
            heat = []
            for _, v in data.iterrows():
                if pd.notna(v.get('latitude')) and pd.notna(v.get('longitude')):
                    weight = float(v.get('rating', 3.0) or 3.0)
                    heat.append([v.get('latitude'), v.get('longitude'), weight])
            if heat:
                HeatMap(heat, radius=15, max_zoom=18).add_to(m)

    map_data = st_folium(m, width=750, height=520, returned_objects=["last_clicked"])

    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lng = map_data['last_clicked']['lng']
        nearest = mu.find_nearest_venue(data, lat, lng)
        if nearest:
            st.session_state.selected_venue = nearest

with col2:
    st.subheader("📊 地圖統計")
    if data is not None and not data.empty:
        st.metric("顯示場地數", len(data))
        if 'rating' in data.columns:
            st.metric("平均評分", f"{data['rating'].mean():.1f}")
        if 'price_per_hour' in data.columns:
            st.metric("平均價格", f"NT${data['price_per_hour'].mean():.0f}/hr")
        if 'district' in data.columns:
            st.markdown("**各區域場地數量（Top 10）**")
            for d, c in data['district'].value_counts().head(10).items():
                st.write(f"• {d}: {c}")
    else:
        st.info("選擇篩選條件以顯示統計資訊")

# 選中場地的資訊
if st.session_state.get('selected_venue'):
    st.markdown("---")
    v = st.session_state.selected_venue
    st.subheader(f"📍 {v.get('name','選中場地')}")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        st.write(f"**地址:** {v.get('address','—')}")
        st.write(f"**運動類型:** {v.get('sport_type','—')}")
        st.write(f"**地區:** {v.get('district','—')}")
        if v.get('contact_phone'):
            st.write(f"**電話:** {v.get('contact_phone')}")
    with c2:
        if v.get('rating'): st.metric("評分", f"{float(v.get('rating')):.1f}/5.0")
        if v.get('price_per_hour'): st.metric("價格", f"NT${int(v.get('price_per_hour'))}/hr")
    with c3:
        if st.button("🔍 詳細資訊", use_container_width=True):
            st.query_params["id"] = int(v.get('id', 0))
            st.switch_page("pages/5_🏢_場地詳情.py")
        if st.button("❤️ 加入收藏", use_container_width=True):
            if 'favorites' not in st.session_state:
                st.session_state['favorites'] = {}
            st.session_state['favorites'][str(v.get('id', v.get('name')))] = v
            st.success("已加入收藏！")
