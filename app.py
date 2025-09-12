import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.recommendation_engine import RecommendationEngine
import os

# 設定頁面配置
st.set_page_config(
    page_title="台北運動場地搜尋引擎",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'recommendation_engine' not in st.session_state:
    st.session_state.recommendation_engine = RecommendationEngine()

if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'preferred_sports': [],
        'preferred_districts': [],
        'price_range': [0, 10000],
        'search_history': []
    }

if 'selected_venue' not in st.session_state:
    st.session_state.selected_venue = None

# 主頁面
st.title("🏃‍♂️ 台北運動場地搜尋引擎")
st.markdown("### 尋找最適合您的運動場地")

# 側邊欄 - 用戶偏好設定
with st.sidebar:
    st.header("🎯 個人偏好設定")
    
    # 運動類型偏好
    available_sports = st.session_state.data_manager.get_sport_types()
    if available_sports:
        preferred_sports = st.multiselect(
            "偏好的運動類型",
            available_sports,
            default=st.session_state.user_preferences['preferred_sports']
        )
        st.session_state.user_preferences['preferred_sports'] = preferred_sports
    else:
        st.info("運動類型資料載入中...")
    
    # 地區偏好
    available_districts = st.session_state.data_manager.get_districts()
    if available_districts:
        preferred_districts = st.multiselect(
            "偏好的地區",
            available_districts,
            default=st.session_state.user_preferences['preferred_districts']
        )
        st.session_state.user_preferences['preferred_districts'] = preferred_districts
    else:
        st.info("地區資料載入中...")
    
    # 價格範圍偏好
    price_range = st.slider(
        "價格範圍 (每小時)",
        0, 5000, 
        value=st.session_state.user_preferences['price_range'],
        step=100,
        format="NT$%d"
    )
    st.session_state.user_preferences['price_range'] = price_range

# 主要內容區域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 統計概覽")
    
    # 顯示場地統計
    stats = st.session_state.data_manager.get_venue_stats()
    
    if stats:
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("總場地數", stats.get('total_venues', 0))
        
        with metric_col2:
            st.metric("運動類型", stats.get('sport_types', 0))
        
        with metric_col3:
            st.metric("服務地區", stats.get('districts', 0))
        
        with metric_col4:
            avg_price = stats.get('avg_price', 0)
            st.metric("平均價格", f"NT${avg_price:.0f}/hr" if avg_price else "N/A")
    else:
        st.info("正在載入場地統計資料...")

    # 快速搜尋
    st.subheader("🔍 快速搜尋")
    
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input("搜尋場地名稱或關鍵字", placeholder="例如：籃球場、游泳池、大安區...")
    
    with search_col2:
        if st.button("搜尋", type="primary", use_container_width=True):
            if search_query:
                # 記錄搜尋歷史
                if search_query not in st.session_state.user_preferences['search_history']:
                    st.session_state.user_preferences['search_history'].append(search_query)
                    # 只保留最近10次搜尋
                    if len(st.session_state.user_preferences['search_history']) > 10:
                        st.session_state.user_preferences['search_history'].pop(0)
                
                # 執行搜尋
                results = st.session_state.data_manager.search_venues(search_query)
                
                if results is not None and not results.empty:
                    st.success(f"找到 {len(results)} 個相關場地")
                    
                    # 顯示搜尋結果
                    for idx, venue in results.iterrows():
                        with st.expander(f"📍 {venue.get('name', '未知場地')} - {venue.get('district', '未知地區')}"):
                            venue_col1, venue_col2 = st.columns([2, 1])
                            
                            with venue_col1:
                                st.write(f"**地址:** {venue.get('address', '地址未提供')}")
                                st.write(f"**運動類型:** {venue.get('sport_type', '未指定')}")
                                st.write(f"**設施:** {venue.get('facilities', '設施資訊未提供')}")
                                if venue.get('description'):
                                    st.write(f"**描述:** {venue.get('description')}")
                            
                            with venue_col2:
                                if venue.get('price_per_hour'):
                                    st.metric("每小時費用", f"NT${venue.get('price_per_hour')}")
                                if venue.get('rating'):
                                    st.metric("評分", f"{venue.get('rating'):.1f}/5.0")
                                
                                if st.button(f"查看詳情", key=f"detail_{idx}"):
                                    st.session_state.selected_venue = venue.to_dict()
                                    st.switch_page("pages/1_🔍_Search_Venues.py")
                else:
                    st.warning("未找到相關場地，請嘗試其他關鍵字或使用進階搜尋功能。")

with col2:
    st.subheader("🏆 為您推薦")
    
    # 基於用戶偏好的推薦
    if (st.session_state.user_preferences['preferred_sports'] or 
        st.session_state.user_preferences['preferred_districts']):
        
        recommendations = st.session_state.recommendation_engine.get_personalized_recommendations(
            st.session_state.user_preferences
        )
        
        if recommendations is not None and not recommendations.empty:
            for idx, venue in recommendations.head(5).iterrows():
                with st.container():
                    st.markdown(f"**📍 {venue.get('name', '未知場地')}**")
                    st.markdown(f"🏃‍♂️ {venue.get('sport_type', '未指定')}")
                    st.markdown(f"📍 {venue.get('district', '未知地區')}")
                    
                    if venue.get('price_per_hour'):
                        st.markdown(f"💰 NT${venue.get('price_per_hour')}/hr")
                    
                    if venue.get('rating'):
                        rating = venue.get('rating', 0)
                        stars = "⭐" * int(rating) if rating else ""
                        st.markdown(f"{stars} {venue.get('rating'):.1f}")
                    
                    if st.button(f"查看", key=f"rec_{idx}", use_container_width=True):
                        st.session_state.selected_venue = venue.to_dict()
                        st.switch_page("pages/1_🔍_Search_Venues.py")
                    
                    st.divider()
        else:
            st.info("設定您的偏好以獲得個人化推薦")
    else:
        st.info("請在側邊欄設定您的偏好，我們將為您推薦最適合的場地！")
    
    # 搜尋歷史
    if st.session_state.user_preferences['search_history']:
        st.subheader("🕒 最近搜尋")
        for query in reversed(st.session_state.user_preferences['search_history'][-5:]):
            if st.button(f"🔍 {query}", key=f"history_{query}", use_container_width=True):
                results = st.session_state.data_manager.search_venues(query)
                if results is not None and not results.empty:
                    st.session_state.selected_venue = results.iloc[0].to_dict()
                    st.switch_page("pages/1_🔍_Search_Venues.py")

# 頁面導航提示
st.markdown("---")
st.markdown("""
### 🧭 功能導航
- **🔍 搜尋場地**: 詳細的場地搜尋和篩選功能
- **🗺️ 地圖檢視**: 在地圖上查看所有場地位置
- **⭐ 個人推薦**: 基於您偏好的個人化推薦
- **📊 資料分析**: 場地使用趨勢和統計分析
""")

# 應用資訊
with st.expander("ℹ️ 關於本應用"):
    st.markdown("""
    **台北運動場地搜尋引擎** 是一個專為台北市民設計的運動場地搜尋平台。
    
    **主要功能:**
    - 🔍 智慧搜尋：根據關鍵字快速找到相關場地
    - 📍 地圖定位：視覺化場地位置，方便規劃路線
    - ⭐ 個人推薦：基於您的偏好和搜尋歷史推薦場地
    - 📊 數據洞察：了解場地使用趨勢和熱門選擇
    
    **支援的運動類型:**
    籃球、足球、網球、羽毛球、游泳、健身房、跑步、桌球等多種運動項目
    """)
