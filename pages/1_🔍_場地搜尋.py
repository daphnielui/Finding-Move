import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.recommendation_engine import RecommendationEngine

st.set_page_config(
    page_title="場地搜尋 - 台北運動場地搜尋引擎",
    page_icon="🔍",
    layout="wide"
)

# 確保 session state 已初始化
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'recommendation_engine' not in st.session_state:
    st.session_state.recommendation_engine = RecommendationEngine()

if 'search_filters' not in st.session_state:
    st.session_state.search_filters = {
        'sport_type': [],
        'district': [],
        'price_range': [0, 5000],
        'facilities': [],
        'rating_min': 0.0
    }

st.title("🔍 場地搜尋")
st.markdown("使用多種篩選條件找到最適合的運動場地")

# 側邊欄 - 搜尋篩選器
with st.sidebar:
    st.header("🎯 搜尋篩選")
    
    # 運動類型篩選
    available_sports = st.session_state.data_manager.get_sport_types()
    if available_sports:
        selected_sports = st.multiselect(
            "運動類型",
            available_sports,
            default=st.session_state.search_filters['sport_type']
        )
        st.session_state.search_filters['sport_type'] = selected_sports
    else:
        st.info("載入運動類型中...")
    
    # 地區篩選
    available_districts = st.session_state.data_manager.get_districts()
    if available_districts:
        selected_districts = st.multiselect(
            "地區",
            available_districts,
            default=st.session_state.search_filters['district']
        )
        st.session_state.search_filters['district'] = selected_districts
    else:
        st.info("載入地區資料中...")
    
    # 價格範圍
    price_range = st.slider(
        "價格範圍 (每小時)",
        0, 10000,
        value=st.session_state.search_filters['price_range'],
        step=100,
        format="NT$%d"
    )
    st.session_state.search_filters['price_range'] = price_range
    
    # 設施篩選
    available_facilities = st.session_state.data_manager.get_facilities()
    if available_facilities:
        selected_facilities = st.multiselect(
            "設施需求",
            available_facilities,
            default=st.session_state.search_filters['facilities']
        )
        st.session_state.search_filters['facilities'] = selected_facilities
    
    # 最低評分
    min_rating = st.slider(
        "最低評分",
        0.0, 5.0,
        value=st.session_state.search_filters['rating_min'],
        step=0.1,
        format="%.1f"
    )
    st.session_state.search_filters['rating_min'] = min_rating
    
    # 重置篩選
    if st.button("重置篩選", use_container_width=True):
        st.session_state.search_filters = {
            'sport_type': [],
            'district': [],
            'price_range': [0, 5000],
            'facilities': [],
            'rating_min': 0.0
        }
        st.rerun()

# 主要內容區域
col1, col2 = st.columns([2, 1])

with col1:
    # 搜尋欄
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])
    
    with search_col1:
        search_query = st.text_input(
            "搜尋場地",
            placeholder="輸入場地名稱或關鍵字...",
            key="venue_search"
        )
    
    with search_col2:
        search_button = st.button("🔍 搜尋", type="primary", use_container_width=True)
    
    with search_col3:
        sort_option = st.selectbox(
            "排序方式",
            ["評分", "價格", "距離", "名稱"],
            key="sort_venues"
        )
    
    # 執行搜尋和篩選
    if search_button or any(st.session_state.search_filters.values()):
        # 獲取篩選後的場地
        filtered_venues = st.session_state.data_manager.get_filtered_venues(
            sport_types=st.session_state.search_filters['sport_type'],
            districts=st.session_state.search_filters['district'],
            price_range=st.session_state.search_filters['price_range'],
            facilities=st.session_state.search_filters['facilities'],
            min_rating=st.session_state.search_filters['rating_min'],
            search_query=search_query if search_button else None
        )
        
        if filtered_venues is not None and not filtered_venues.empty:
            # 排序
            if sort_option == "評分":
                filtered_venues = filtered_venues.sort_values('rating', ascending=False, na_last=True)
            elif sort_option == "價格":
                filtered_venues = filtered_venues.sort_values('price_per_hour', ascending=True, na_last=True)
            elif sort_option == "名稱":
                filtered_venues = filtered_venues.sort_values('name', ascending=True, na_last=True)
            
            st.success(f"找到 {len(filtered_venues)} 個符合條件的場地")
            
            # 分頁顯示
            venues_per_page = 10
            total_pages = (len(filtered_venues) - 1) // venues_per_page + 1
            
            if total_pages > 1:
                page = st.selectbox(f"頁面 (共 {total_pages} 頁)", range(1, total_pages + 1))
                start_idx = (page - 1) * venues_per_page
                end_idx = start_idx + venues_per_page
                page_venues = filtered_venues.iloc[start_idx:end_idx]
            else:
                page_venues = filtered_venues
            
            # 顯示場地列表
            for idx, venue in page_venues.iterrows():
                with st.expander(
                    f"📍 {venue.get('name', '未知場地')} - {venue.get('district', '未知地區')} "
                    f"{'⭐' * int(venue.get('rating', 0)) if venue.get('rating') else ''}"
                ):
                    venue_detail_col1, venue_detail_col2 = st.columns([2, 1])
                    
                    with venue_detail_col1:
                        st.markdown(f"**📍 地址:** {venue.get('address', '地址未提供')}")
                        st.markdown(f"**🏃‍♂️ 運動類型:** {venue.get('sport_type', '未指定')}")
                        
                        if venue.get('facilities'):
                            facilities_list = venue.get('facilities', '').split(',') if isinstance(venue.get('facilities'), str) else venue.get('facilities', [])
                            st.markdown(f"**🏢 設施:** {', '.join(facilities_list)}")
                        
                        if venue.get('description'):
                            st.markdown(f"**📝 描述:** {venue.get('description')}")
                        
                        if venue.get('contact_phone'):
                            st.markdown(f"**📞 聯絡電話:** {venue.get('contact_phone')}")
                        
                        if venue.get('opening_hours'):
                            st.markdown(f"**🕒 營業時間:** {venue.get('opening_hours')}")
                    
                    with venue_detail_col2:
                        # 價格資訊
                        if venue.get('price_per_hour'):
                            st.metric("每小時費用", f"NT${venue.get('price_per_hour')}")
                        
                        # 評分資訊
                        if venue.get('rating'):
                            st.metric("評分", f"{venue.get('rating'):.1f}/5.0")
                        
                        # 操作按鈕
                        button_col1, button_col2 = st.columns(2)
                        
                        with button_col1:
                            if st.button(f"📍 地圖", key=f"map_{idx}"):
                                st.session_state.selected_venue = venue.to_dict()
                                st.switch_page("pages/2_🗺️_Map_View.py")
                        
                        with button_col2:
                            if st.button(f"❤️ 收藏", key=f"fav_{idx}"):
                                # 添加到收藏列表
                                if 'favorites' not in st.session_state:
                                    st.session_state.favorites = []
                                
                                venue_id = venue.get('id', idx)
                                if venue_id not in st.session_state.favorites:
                                    st.session_state.favorites.append(venue_id)
                                    st.success("已加入收藏！")
                                else:
                                    st.info("已在收藏列表中")
        
        elif search_query:
            st.warning("未找到符合搜尋條件的場地。請嘗試：")
            st.markdown("""
            - 使用不同的關鍵字
            - 調整篩選條件
            - 擴大價格或評分範圍
            """)
        else:
            st.info("請設定搜尋條件或輸入關鍵字來搜尋場地")
    
    else:
        # 顯示所有場地
        all_venues = st.session_state.data_manager.get_all_venues()
        
        if all_venues is not None and not all_venues.empty:
            st.info(f"共有 {len(all_venues)} 個場地可供選擇。使用左側篩選器來縮小搜尋範圍。")
            
            # 顯示前10個場地作為預覽
            preview_venues = all_venues.head(10)
            
            for idx, venue in preview_venues.iterrows():
                with st.container():
                    venue_preview_col1, venue_preview_col2, venue_preview_col3 = st.columns([3, 1, 1])
                    
                    with venue_preview_col1:
                        st.markdown(f"**📍 {venue.get('name', '未知場地')}**")
                        st.markdown(f"🏃‍♂️ {venue.get('sport_type', '未指定')} | 📍 {venue.get('district', '未知地區')}")
                    
                    with venue_preview_col2:
                        if venue.get('price_per_hour'):
                            st.markdown(f"💰 NT${venue.get('price_per_hour')}/hr")
                        if venue.get('rating'):
                            st.markdown(f"⭐ {venue.get('rating'):.1f}")
                    
                    with venue_preview_col3:
                        if st.button(f"查看詳情", key=f"preview_{idx}"):
                            st.session_state.selected_venue = venue.to_dict()
                            st.rerun()
                    
                    st.divider()
        else:
            st.error("無法載入場地資料。請檢查資料來源或稍後再試。")

with col2:
    st.subheader("🎯 搜尋建議")
    
    # 熱門搜尋
    popular_searches = st.session_state.data_manager.get_popular_searches()
    if popular_searches:
        st.markdown("**🔥 熱門搜尋:**")
        for search_term in popular_searches[:5]:
            if st.button(f"🔍 {search_term}", key=f"popular_{search_term}", use_container_width=True):
                st.session_state.venue_search = search_term
                st.rerun()
    
    # 推薦場地
    st.subheader("💡 推薦場地")
    
    recommendations = st.session_state.recommendation_engine.get_trending_venues()
    if recommendations is not None and not recommendations.empty:
        for idx, venue in recommendations.head(5).iterrows():
            with st.container():
                st.markdown(f"**📍 {venue.get('name', '未知場地')}**")
                st.markdown(f"🏃‍♂️ {venue.get('sport_type', '未指定')}")
                st.markdown(f"📍 {venue.get('district', '未知地區')}")
                
                if venue.get('rating'):
                    stars = "⭐" * int(venue.get('rating', 0))
                    st.markdown(f"{stars} {venue.get('rating'):.1f}")
                
                if st.button(f"查看", key=f"trend_rec_{idx}", use_container_width=True):
                    st.session_state.selected_venue = venue.to_dict()
                    st.rerun()
                
                st.divider()
    else:
        st.info("推薦場地載入中...")

# 顯示選中場地的詳細資訊
if st.session_state.get('selected_venue'):
    st.markdown("---")
    st.subheader(f"📍 {st.session_state.selected_venue.get('name', '場地詳情')}")
    
    detail_col1, detail_col2 = st.columns([2, 1])
    
    with detail_col1:
        venue = st.session_state.selected_venue
        
        st.markdown(f"**📍 地址:** {venue.get('address', '地址未提供')}")
        st.markdown(f"**🏃‍♂️ 運動類型:** {venue.get('sport_type', '未指定')}")
        st.markdown(f"**🏢 所在地區:** {venue.get('district', '未知地區')}")
        
        if venue.get('facilities'):
            facilities_list = venue.get('facilities', '').split(',') if isinstance(venue.get('facilities'), str) else venue.get('facilities', [])
            st.markdown(f"**🏢 設施:** {', '.join(facilities_list)}")
        
        if venue.get('description'):
            st.markdown(f"**📝 描述:** {venue.get('description')}")
        
        if venue.get('contact_phone'):
            st.markdown(f"**📞 聯絡電話:** {venue.get('contact_phone')}")
        
        if venue.get('opening_hours'):
            st.markdown(f"**🕒 營業時間:** {venue.get('opening_hours')}")
        
        if venue.get('website'):
            st.markdown(f"**🌐 官方網站:** {venue.get('website')}")
    
    with detail_col2:
        # 場地評分和價格
        if venue.get('rating'):
            st.metric("評分", f"{venue.get('rating'):.1f}/5.0")
        
        if venue.get('price_per_hour'):
            st.metric("每小時費用", f"NT${venue.get('price_per_hour')}")
        
        # 操作按鈕
        if st.button("📍 在地圖上查看", use_container_width=True):
            st.switch_page("pages/2_🗺️_Map_View.py")
        
        if st.button("❤️ 加入收藏", use_container_width=True):
            if 'favorites' not in st.session_state:
                st.session_state.favorites = []
            
            venue_id = venue.get('id', venue.get('name'))
            if venue_id not in st.session_state.favorites:
                st.session_state.favorites.append(venue_id)
                st.success("已加入收藏！")
            else:
                st.info("已在收藏列表中")
        
        if st.button("🔄 清除選擇", use_container_width=True):
            st.session_state.selected_venue = None
            st.rerun()
