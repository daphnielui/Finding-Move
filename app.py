import streamlit as st
import pandas as pd
import time
import random
from utils.data_manager import DataManager
from utils.recommendation_engine import RecommendationEngine
from utils.weather_manager import WeatherManager
import os

# 設定頁面配置
st.set_page_config(
    page_title="台北運動場地搜尋引擎",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定義灰藍色主題CSS
st.markdown("""
<style>
    /* 主背景顏色 */
    .stApp {
        background-color: #f8fafb;
    }
    
    /* 區塊背景 */
    .block-container {
        background-color: #ecf0f3;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 主標題區域 */
    .main-header {
        background: linear-gradient(135deg, #a6bee2 0%, #8fadd9 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .location-selector-inline {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 10px 15px;
        min-width: 200px;
    }
    
    .location-selector-inline .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.9);
        border-radius: 8px;
    }
    
    /* 天氣區塊特殊樣式 */
    .weather-block {
        background: linear-gradient(135deg, #a6bee2 0%, #8fadd9 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* 搜尋區塊 */
    .search-block {
        background-color: #e1e8ea;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    
    /* 推薦區塊 */
    .recommend-block {
        background-color: #d4dde0;
        padding: 25px;
        border-radius: 15px;
    }
    
    /* icon按鈕樣式 */
    .icon-button {
        background-color: #a6bee2;
        border: none;
        border-radius: 50%;
        padding: 15px;
        font-size: 20px;
        margin: 5px;
        color: white;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .icon-button:hover {
        background-color: #8fadd9;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* 動態運動icon */
    .rotating-icon {
        animation: rotation 3s infinite linear;
        display: inline-block;
        font-size: 24px;
    }
    
    @keyframes rotation {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* 轉場動畫覆蓋層 */
    .page-transition-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(245, 245, 245, 0.95);
        z-index: 9999;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    
    .page-transition-overlay.show {
        display: flex;
    }
    
    /* 載入動畫 */
    .loading-spinner {
        width: 80px;
        height: 80px;
        border: 8px solid #e8e8e8;
        border-top: 8px solid #9e9e9e;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* 載入文字 */
    .loading-text {
        color: #424242;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* 輸入欄樣式 */
    .stTextInput > div > div > input {
        background-color: #f0f0f0;
        border: 2px solid #9e9e9e;
        border-radius: 25px;
        padding: 10px 20px;
        font-size: 16px;
    }
    
    /* 場館卡片樣式 */
    .venue-card {
        background-color: #f8f8f8;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #9e9e9e;
    }
    
    /* 標題樣式 */
    h1, h2, h3 {
        color: #424242;
    }
    
    /* 按鈕點擊效果 */
    .stButton > button {
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>

<!-- 轉場動畫HTML -->
<div id="pageTransition" class="page-transition-overlay">
    <div class="loading-spinner"></div>
    <div class="loading-text">載入中...</div>
</div>

<script>
// 頁面轉場動畫功能
function showPageTransition() {
    const overlay = document.getElementById('pageTransition');
    if (overlay) {
        overlay.classList.add('show');
        
        // 2秒後隱藏動畫 (Streamlit通常需要這個時間來載入新頁面)
        setTimeout(function() {
            overlay.classList.remove('show');
        }, 2000);
    }
}

// 監聽所有按鈕點擊事件
document.addEventListener('click', function(e) {
    // 檢查點擊的是否為導航按鈕
    const button = e.target.closest('button');
    if (button && (
        button.textContent.includes('場地搜尋') ||
        button.textContent.includes('地圖檢視') ||
        button.textContent.includes('個人推薦') ||
        button.textContent.includes('場地比較') ||
        button.textContent.includes('查看詳情')
    )) {
        showPageTransition();
    }
});

// 頁面載入完成後隱藏轉場動畫
window.addEventListener('load', function() {
    const overlay = document.getElementById('pageTransition');
    if (overlay) {
        overlay.classList.remove('show');
    }
});
</script>
""", unsafe_allow_html=True)

# 初始化 session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'recommendation_engine' not in st.session_state:
    st.session_state.recommendation_engine = RecommendationEngine()

if 'weather_manager' not in st.session_state:
    st.session_state.weather_manager = WeatherManager()

if 'current_sport_icon' not in st.session_state:
    st.session_state.current_sport_icon = 0

if 'selected_district' not in st.session_state:
    st.session_state.selected_district = '中正區'

if 'user_location' not in st.session_state:
    st.session_state.user_location = None

# 運動icon列表
sports_icons = ["🏀", "⚽", "🏸", "🏐", "🎾", "🏊‍♂️", "🏃‍♂️", "🚴‍♂️", "🏋️‍♂️", "🤸‍♂️"]

# 更新運動icon（每3秒換一次）
if 'last_icon_update' not in st.session_state:
    st.session_state.last_icon_update = time.time()

current_time = time.time()
if current_time - st.session_state.last_icon_update > 3:
    st.session_state.current_sport_icon = (st.session_state.current_sport_icon + 1) % len(sports_icons)
    st.session_state.last_icon_update = current_time

current_icon = sports_icons[st.session_state.current_sport_icon]

# ===== 主標題區域與位置選擇器 =====
available_districts = ['中正區', '大同區', '中山區', '松山區', '大安區', '萬華區', 
                      '信義區', '士林區', '北投區', '內湖區', '南港區', '文山區']

# 讀取當前選擇的區域
if hasattr(st, 'query_params') and st.query_params.get('district'):
    current_district = st.query_params.get('district')
    if current_district in available_districts:
        st.session_state.selected_district = current_district

# 主標題區域 - 包含logo和位置選擇器
st.markdown('<div class="main-header">', unsafe_allow_html=True)

# 使用兩列布局：左側logo，右側位置選擇器
header_col1, header_col2 = st.columns([3, 2])

with header_col1:
    st.markdown(f"""
    <div class="logo-section">
        <div style="font-size: 2.5em;">{current_icon}</div>
        <div>
            <h1 style="margin: 0; font-size: 2em;">台北運動場地搜尋引擎</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1.1em;">找到最適合您的運動場地</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown('<div class="location-selector-inline">', unsafe_allow_html=True)
    
    # 區域選擇下拉選單
    selected_district = st.selectbox(
        "📍 選擇位置",
        available_districts,
        index=available_districts.index(st.session_state.selected_district) if st.session_state.selected_district in available_districts else 0,
        key="district_selector",
        help="選擇您所在的台北市行政區"
    )
    
    # 檢查是否有變更
    if selected_district != st.session_state.selected_district:
        st.session_state.selected_district = selected_district
        # 使用query_params來觸發頁面重新載入
        st.query_params["district"] = selected_district
        st.rerun()
    
    # 自動定位按鈕
    if st.button("🎯 自動定位", help="使用GPS自動選擇最近的行政區"):
        st.info("請在瀏覽器中允許定位權限")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== 第一區塊：天氣資訊 =====
# 獲取選擇的區域 - 優先順序：URL參數 > session_state > 預設值
selected_district = '中正區'  # 預設值

# 讀取 URL 查詢參數
try:
    if hasattr(st, 'query_params') and st.query_params:
        district_param = st.query_params.get('district')
        if district_param:
            selected_district = district_param
            st.session_state.selected_district = district_param
    elif 'selected_district' in st.session_state:
        selected_district = st.session_state.selected_district
except Exception as e:
    print(f"讀取URL參數時發生錯誤: {e}")
    # 使用 session_state 中的值作為備選
    if 'selected_district' in st.session_state:
        selected_district = st.session_state.selected_district

# 獲取即時天氣資料
weather_info = st.session_state.weather_manager.get_current_weather(selected_district)
weather_icon = st.session_state.weather_manager.get_weather_icon(
    weather_info['weather_description'], 
    weather_info['temperature']
)

# 根據運動適宜性給出建議
def get_exercise_advice(temp, humidity, precipitation):
    if precipitation > 60:
        return "🌧️ 今日有雨，建議室內運動"
    elif temp > 35:
        return "🌡️ 高溫警告，請注意防曬補水"
    elif temp < 15:
        return "🧥 氣溫較低，請注意保暖"
    elif humidity > 80:
        return "💦 濕度較高，運動時多補水"
    else:
        return "☀️ 今日適合戶外運動"

exercise_advice = get_exercise_advice(
    weather_info['temperature'], 
    weather_info['humidity'], 
    weather_info['precipitation_probability']
)

st.markdown(f"""
<div class="weather-block">
    <h2>🌤️ {selected_district} 即時天氣</h2>
    <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 20px;">
        <div>
            <div style="font-size: 3em;">{weather_icon}</div>
            <div style="font-size: 1.8em; font-weight: bold;">{weather_info['temperature']}°C</div>
            <div style="font-size: 1.1em;">{weather_info['weather_description']}</div>
        </div>
        <div>
            <div style="font-size: 2em;">💨</div>
            <div style="font-size: 1.1em;">{weather_info['wind_direction']} {weather_info['wind_speed']}級</div>
            <div style="font-size: 1.1em;">濕度 {weather_info['humidity']}%</div>
        </div>
        <div>
            <div style="font-size: 2em;">📍</div>
            <div style="font-weight: bold; font-size: 1.2em;">台北市</div>
            <div style="font-size: 1.1em; color: #ffeb3b;">{weather_info['district']}</div>
        </div>
    </div>
    <div style="margin-top: 15px; font-size: 1em; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
        <strong>{exercise_advice}</strong>
    </div>
    <div style="margin-top: 10px; font-size: 0.9em; display: flex; justify-content: space-between;">
        <span>🌡️ 體感 {weather_info['apparent_temperature']}°C</span>
        <span>🌧️ 降雨 {weather_info['precipitation_probability']}%</span>
        <span>😊 {weather_info['comfort_index']}</span>
    </div>
    <div style="margin-top: 8px; font-size: 0.8em; opacity: 0.8; text-align: center;">
        更新時間: {weather_info['update_time']}
    </div>
</div>
""", unsafe_allow_html=True)

# ===== 第二區塊：搜尋功能 =====
st.markdown('<div class="search-block">', unsafe_allow_html=True)

# 搜尋標題
st.markdown(f"""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #424242;">
        <span class="rotating-icon">{current_icon}</span>
        尋找最適合的運動場地
        <span class="rotating-icon">{current_icon}</span>
    </h2>
</div>
""", unsafe_allow_html=True)

# 搜尋輸入欄
search_col1, search_col2 = st.columns([4, 1])

with search_col1:
    search_placeholder = f"{current_icon} 輸入場地名稱、運動類型或地區..."
    search_query = st.text_input("搜尋", placeholder=search_placeholder, label_visibility="collapsed")

with search_col2:
    search_button = st.button("🔍", help="開始搜尋", use_container_width=True, type="primary")

# 篩選條件
st.markdown('<div style="margin-top: 20px;"><h4 style="color: #424242;">📋 篩選條件</h4></div>', unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    # 運動類型篩選
    sport_types = ["全部", "籃球", "足球", "網球", "羽毛球", "游泳", "健身", "跑步", "桌球"]
    selected_sport = st.selectbox("🏃‍♂️ 運動類型", sport_types)

with filter_col2:
    # 地區篩選
    districts = ["全部", "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"]
    selected_district = st.selectbox("📍 地區", districts)

with filter_col3:
    # 價格範圍
    price_range = st.selectbox("💰 價格範圍", ["全部", "免費", "NT$1-100", "NT$101-300", "NT$301-500", "NT$500以上"])

with filter_col4:
    # 評分篩選
    rating_filter = st.selectbox("⭐ 評分", ["全部", "4.5分以上", "4.0分以上", "3.5分以上", "3.0分以上"])

st.markdown('</div>', unsafe_allow_html=True)

# ===== 第三區塊：推薦場館 =====
st.markdown('<div class="recommend-block">', unsafe_allow_html=True)

st.markdown('<h2 style="color: #424242; text-align: center; margin-bottom: 25px;">🏆 推薦場館</h2>', unsafe_allow_html=True)

# 獲取推薦場地
venues_data = st.session_state.data_manager.get_all_venues()
if venues_data is not None and not venues_data.empty:
    # 隨機選擇6個場地作為推薦
    recommended_venues = venues_data.sample(n=min(6, len(venues_data)))
    
    # 以3列2行方式展示推薦場館
    for i in range(0, len(recommended_venues), 3):
        cols = st.columns(3)
        row_venues = recommended_venues.iloc[i:i+3]
        
        for j, (_, venue) in enumerate(row_venues.iterrows()):
            with cols[j]:
                # 場館圖片（暫時用emoji替代）
                sport_type = venue.get('sport_type', '運動')
                venue_icon = "🏟️"
                if "籃球" in sport_type:
                    venue_icon = "🏀"
                elif "游泳" in sport_type:
                    venue_icon = "🏊‍♂️"
                elif "網球" in sport_type:
                    venue_icon = "🎾"
                elif "足球" in sport_type:
                    venue_icon = "⚽"
                elif "羽毛球" in sport_type:
                    venue_icon = "🏸"
                elif "健身" in sport_type:
                    venue_icon = "🏋️‍♂️"
                
                st.markdown(f"""
                <div class="venue-card">
                    <div style="text-align: center; font-size: 3em; margin-bottom: 10px;">
                        {venue_icon}
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: #424242; margin-bottom: 8px;">{venue.get('name', '未知場地')}</h4>
                        <p style="color: #666; font-size: 0.9em; margin-bottom: 5px;">
                            📍 {venue.get('district', '未知地區')}
                        </p>
                        <p style="color: #666; font-size: 0.9em; margin-bottom: 5px;">
                            🏃‍♂️ {venue.get('sport_type', '未指定')}
                        </p>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <span style="color: #e91e63; font-weight: bold;">
                                💰 NT${venue.get('price_per_hour', 0)}/小時
                            </span>
                            <span style="color: #ff9800; font-weight: bold;">
                                ⭐ {venue.get('rating', 0):.1f}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 詳情按鈕
                if st.button(f"📋 查看詳情", key=f"venue_detail_{venue.get('id', i)}_{j}", use_container_width=True):
                    venue_id = venue.get('id')
                    if venue_id:
                        st.query_params.id = venue_id
                        st.switch_page("pages/5_🏢_場地詳情.py")

else:
    st.info("正在載入場地資料...")

st.markdown('</div>', unsafe_allow_html=True)

# 底部功能導航
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h3 style="color: #424242; margin-bottom: 20px;">🧭 功能導航</h3>
</div>
""", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("🔍\n場地搜尋", use_container_width=True):
        st.switch_page("pages/1_🔍_場地搜尋.py")

with nav_col2:
    if st.button("🗺️\n地圖檢視", use_container_width=True):
        st.switch_page("pages/2_🗺️_地圖檢視.py")

with nav_col3:
    if st.button("⭐\n個人推薦", use_container_width=True):
        st.switch_page("pages/3_⭐_個人推薦.py")

with nav_col4:
    if st.button("⚖️\n場地比較", use_container_width=True):
        st.switch_page("pages/4_⚖️_場地比較.py")

# 定期更新動態icon (避免無限重載)
if current_time - st.session_state.last_icon_update > 3:
    # 每3秒自動更新一次頁面
    time.sleep(0.1)
