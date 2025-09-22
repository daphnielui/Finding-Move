import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.responsive import apply_responsive_design

st.set_page_config(page_title="收藏夾", page_icon="❤️", layout="wide")
apply_responsive_design()

if "favorites" not in st.session_state:
    st.session_state["favorites"] = {}  # id -> venue dict

dm = DataManager()

st.title("❤️ 我的收藏")

if not st.session_state["favorites"]:
    st.info("目前沒有收藏的場地。回「場地搜尋」或「場地詳情」頁按『收藏』即可加入。")
else:
    favs = list(st.session_state["favorites"].values())
    sort_by = st.selectbox("排序", ["加入順序", "評分高→低", "價格低→高"])
    if sort_by == "評分高→低":
        favs = sorted(favs, key=lambda x: (x.get("rating") is None, x.get("rating", 0)), reverse=True)
    elif sort_by == "價格低→高":
        favs = sorted(favs, key=lambda x: x.get("price_per_hour") if x.get("price_per_hour") is not None else 999999)

    for v in favs:
        vid = str(v.get("id", v.get("name")))
        with st.container(border=True):
            c1, c2 = st.columns([3,1])
            with c1:
                st.markdown(f"### {v.get('name','場地')}")
                st.write(f"📍 {v.get('address','—')}｜{v.get('district','—')}｜{v.get('sport_type','—')}")
                if v.get('rating'):
                    st.write(f"⭐ {float(v.get('rating')):.1f}")
                if v.get('price_per_hour'):
                    st.write(f"💰 NT${int(v.get('price_per_hour'))}/hr")
            with c2:
                if st.button("🗺️ 地圖", key=f"map_{vid}"):
                    st.session_state["map_focus"] = {"lat": v.get("latitude"), "lon": v.get("longitude"), "name": v.get("name")}
                    st.switch_page("pages/2_🗺️_地圖檢視.py")
                if st.button("🗑️ 移除", key=f"rm_{vid}"):
                    st.session_state["favorites"].pop(vid, None)
                    st.rerun()
