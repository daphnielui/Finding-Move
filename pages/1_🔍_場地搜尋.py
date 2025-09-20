# pages/1_🔍_場地搜尋.py  —— 乾淨版（簡化搜尋、保留熱門/推薦/收藏/詳情）

import streamlit as st
import pandas as pd
from pathlib import Path
import sys, os

# 讓 utils 可匯入
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data_manager import DataManager

# ---------- 頁面基本設定 ----------
st.set_page_config(
    page_title="Finding Move | 場地搜尋",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- 全域 CSS（可選，若 app.py 已引入可移除） ----------
css_path = Path(".streamlit/responsive.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ---------- Session 初始化 ----------
if "data_manager" not in st.session_state:
    st.session_state["data_manager"] = DataManager()

if "favorites" not in st.session_state:
    st.session_state["favorites"] = {}   # {id: {name, address, ...}}

# 採用「方案 A」：widget key 與自家 key 分離
if "venue_search" not in st.session_state:
    st.session_state["venue_search"] = ""

dm: DataManager = st.session_state["data_manager"]

# ---------- 頁首 ----------
st.markdown('<h1 style="margin-bottom:0.2rem;">🔎 場地搜尋</h1>', unsafe_allow_html=True)
st.caption("輸入關鍵字（名稱、行政區、運動類型、設施…）或直接點選熱門搜尋")

# ---------- 搜尋欄 ----------
search_term = st.text_input(
    "關鍵字搜尋",
    value=st.session_state["venue_search"],
    key="w_venue_search",
    placeholder="例：籃球、松山、羽毛球、停車場…",
)

# 同步 widget → 自家狀態；避免與 widget key 打架
if st.session_state.get("w_venue_search", "") != st.session_state["venue_search"]:
    st.session_state["venue_search"] = st.session_state["w_venue_search"]
    st.rerun()

# ---------- 熱門搜尋 ----------
st.divider()
st.subheader("🔥 熱門搜尋")
try:
    hot = dm.get_popular_searches()
except Exception:
    hot = []

if hot:
    cols = st.columns(min(5, len(hot)))
    for i, term in enumerate(hot[:5]):
        with cols[i % len(cols)]:
            if st.button(term, key=f"popular_{i}", use_container_width=True):
                st.session_state["venue_search"] = term
                st.session_state["w_venue_search"] = term
                st.rerun()
else:
    st.caption("（暫無熱門搜尋建議）")

# ---------- 推薦場館 ----------
st.divider()
st.markdown('<h2 style="margin-top:0.2rem;">🏆 推薦場館</h2>', unsafe_allow_html=True)
all_df = dm.get_all_venues()
if all_df is not None and not all_df.empty:
    rec_df = all_df.sample(n=min(6, len(all_df)), random_state=42)
    # 三欄卡片
    for i in range(0, len(rec_df), 3):
        cols = st.columns(3)
        for j, (_, r) in enumerate(rec_df.iloc[i:i+3].iterrows()):
            with cols[j]:
                name = str(r.get("name", "場地"))
                district = str(r.get("district", "—"))
                rating = r.get("rating")
                price = r.get("price_per_hour")
                st.container(border=True)
                st.markdown(f"**{name}**")
                st.caption(f"📍 {district}")
                meta = []
                if pd.notna(rating): meta.append(f"⭐ {rating:.1f}")
                if pd.notna(price): meta.append(f"💲 NT${int(price):,}/h")
                if meta: st.write("　".join(meta))
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("詳情", key=f"rec_detail_{r.get('id', i)}", use_container_width=True):
                        st.query_params.id = int(r.get("id", 0)) if pd.notna(r.get("id", None)) else None
                        st.switch_page("pages/5_🏢_場地詳情.py")
                with c2:
                    vid = str(r.get("id", name))
                    already = vid in st.session_state["favorites"]
                    label = "✓ 已收藏" if already else "加入收藏"
                    if st.button(label, key=f"rec_fav_{vid}", disabled=already, use_container_width=True):
                        st.session_state["favorites"][vid] = {
                            "id": vid,
                            "name": name,
                            "address": r.get("address",""),
                            "sport_type": r.get("sport_type",""),
                            "rating": r.get("rating"),
                            "price_level": r.get("price_per_hour"),
                            "lat": r.get("lat") or r.get("latitude"),
                            "lon": r.get("lon") or r.get("longitude"),
                        }
                        st.toast("已加入收藏", icon="✅")
else:
    st.info("尚無資料，請稍後再試。")

# ---------- 搜尋結果 ----------
st.divider()
st.subheader("🔍 搜尋結果")

query = st.session_state["venue_search"].strip()
if not query:
    st.caption("輸入關鍵字後顯示結果。")
else:
    filtered = dm.get_filtered_venues(search_query=query)
    if filtered is None or filtered.empty:
        st.warning("找不到符合條件的場地，換個關鍵字試試看！")
    else:
        # 分頁（每頁 9 筆）
        per_page = 9
        total = len(filtered)
        pages = (total + per_page - 1) // per_page
        page = st.segmented_control("頁碼", options=list(range(1, pages+1))) if pages > 1 else 1
        start, end = (page-1)*per_page, (page-1)*per_page + per_page
        page_df = filtered.iloc[start:end]

        # 顯示卡片
        for i in range(0, len(page_df), 3):
            cols = st.columns(3)
            for j, (_, row) in enumerate(page_df.iloc[i:i+3].iterrows()):
                with cols[j]:
                    name = str(row.get("name","場地"))
                    district = str(row.get("district","—"))
                    rating = row.get("rating")
                    price = row.get("price_per_hour")
                    st.container(border=True)
                    st.markdown(f"**{name}**")
                    st.caption(f"📍 {district}　|　{row.get('address','')[:26]}…")
                    meta = []
                    if pd.notna(rating): meta.append(f"⭐ {rating:.1f}")
                    if pd.notna(price): meta.append(f"💲 NT${int(price):,}/h")
                    if meta: st.write("　".join(meta))

                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("詳情", key=f"detail_{row.get('id', i)}", use_container_width=True):
                            st.query_params.id = int(row.get("id", 0)) if pd.notna(row.get("id", None)) else None
                            st.switch_page("pages/5_🏢_場地詳情.py")
                    with c2:
                        vid = str(row.get("id", name))
                        already = vid in st.session_state["favorites"]
                        label = "✓ 已收藏" if already else "加入收藏"
                        if st.button(label, key=f"fav_{vid}", disabled=already, use_container_width=True):
                            st.session_state["favorites"][vid] = {
                                "id": vid,
                                "name": name,
                                "address": row.get("address",""),
                                "sport_type": row.get("sport_type",""),
                                "rating": row.get("rating"),
                                "price_level": row.get("price_per_hour"),
                                "lat": row.get("lat") or row.get("latitude"),
                                "lon": row.get("lon") or row.get("longitude"),
                            }
                            st.toast("已加入收藏", icon="❤️")

# ---------- 側邊欄（簡化版資訊） ----------
with st.sidebar:
    st.header("📊 簡要統計")
    stats = dm.get_venue_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("總場地數", f"{stats.get('total_venues',0):,}")
    c2.metric("運動類型", f"{stats.get('sport_types',0)}")
    c3.metric("行政區", f"{stats.get('districts',0)}")

    st.caption("收藏夾在左側選單的 ❤️ 收藏夾")
