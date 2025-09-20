import streamlit as st
import pandas as pd
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_manager import DataManager

st.set_page_config(page_title="收藏夾", layout="wide")

st.title("❤️ 收藏夾")

# --- 初始化收藏結構：以 dict 儲存（key = venue_id） ---
if "favorites" not in st.session_state:
    st.session_state["favorites"] = {}   # {id: {name, address, sport_type, rating, price_level, lat, lon}}

# --- 讀資料（依你的 DataManager 來） ---
dm = None
try:
    dm = DataManager()
    df = dm.load_data() if hasattr(dm, "load_data") else pd.DataFrame()
except Exception:
    df = pd.DataFrame()

# --- 工具函式 ---
def remove_fav(vid: str):
    st.session_state["favorites"].pop(vid, None)
    st.rerun()

def card(v):
    name = v.get("name", "場地")
    addr = v.get("address", "—")
    sport = v.get("sport_type", "—")
    rating = v.get("rating", "—")
    price = v.get("price_level", "—")
    vid = str(v.get("id", name))  # 如果沒有 id 就用 name 當 key

    with st.container(border=True):
        st.markdown(f"### {name}")
        st.write(f"📍 {addr}")
        st.write(f"🏷️ {sport}　⭐ {rating}　💲 {price}")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("🗺️ 在地圖查看", key=f"map_{vid}"):
                st.session_state["map_focus"] = {"lat": v.get("lat"), "lon": v.get("lon"), "name": name}
                st.switch_page("pages/2_🗺️_地圖檢視.py")
        with c2:
            if st.button("🗑️ 移除收藏", key=f"rm_{vid}"):
                remove_fav(vid)

# --- 內容 ---
if not st.session_state["favorites"]:
    st.info("目前沒有收藏的場地。回「場地搜尋」或「場地詳情」頁，按下『加入收藏』即可加入。")
else:
    favs = list(st.session_state["favorites"].values())
    # 可選排序
    sort_by = st.selectbox("排序", ["加入順序", "評分高→低", "價格低→高"])
    if sort_by == "評分高→低":
        favs = sorted(favs, key=lambda x: (x.get("rating") is None, x.get("rating", 0)), reverse=True)
    elif sort_by == "價格低→高":
        favs = sorted(favs, key=lambda x: x.get("price_level") if x.get("price_level") is not None else 9999)

    for v in favs:
        card(v)
