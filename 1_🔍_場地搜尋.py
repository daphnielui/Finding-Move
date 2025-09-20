import streamlit as st
import pandas as pd
import time
from utils.data_manager import DataManager
from utils.recommendation_engine import RecommendationEngine
from utils.weather_manager import WeatherManager

st.set_page_config(
    page_title="Finding Move 尋地寳 ",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 启动动画逻辑 - 如果是首次访问，显示启动动画
if 'startup_done' not in st.session_state:
    # 读取logo文件
    with open('attached_assets/FM logo_1757941352267.jpg', 'rb') as f:
        logo_data = f.read()
    
    # 编码为base64
    import base64
    logo_base64 = base64.b64encode(logo_data).decode()
    
    # 显示启动动画
    startup_html = f'''
    <div id="appStartup" class="app-startup-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100vh; z-index: 99999; display: flex !important;">
        <img src="data:image/jpeg;base64,{logo_base64}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; animation: logoFadeIn 1.5s ease-out;" alt="Finding Move Logo">
        <div class="text-overlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, calc(-50% + 4.5cm)); text-align: center; z-index: 1; color: white;">
            <div style="font-size: 1.5em; font-weight: bold;">
                <span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0s;">尋</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.1s;">地</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.2s;">寳</span>
                <span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.3s;"> - </span>
                <span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.4s;">根</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.5s;">據</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.6s;">您</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.7s;">的</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.8s;">節</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 0.9s;">奏</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.0s;">，</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.1s;">找</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.2s;">到</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.3s;">最</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.4s;">適</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.5s;">合</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.6s;">您</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.7s;">的</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.8s;">運</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 1.9s;">動</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 2.0s;">場</span><span style="display: inline-block; animation: charBounce 0.6s ease-in-out 2.1s;">所</span>
            </div>
        </div>
    </div>
    
    <style>
        @keyframes logoFadeIn {{
            0% {{ opacity: 0; transform: scale(0.8) translateY(20px); }}
            100% {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}
        @keyframes charBounce {{
            0% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
            100% {{ transform: translateY(0); }}
        }}
        header[data-testid="stHeader"] {{ display: none !important; }}
        
        /* 响应式设计 - 手机设备 */
        @media only screen and (max-width: 768px) {{
            #appStartup img {{
                width: 100% !important;
                height: 100% !important;
                object-fit: cover !important;
            }}
            #appStartup .text-overlay {{
                font-size: 1.2em !important;
                transform: translate(-50%, calc(-50% + 2cm)) !important;
                padding: 0 10px !important;
                line-height: 1.3 !important;
            }}
        }}
        
        /* 响应式设计 - 平板设备 */
        @media only screen and (min-width: 769px) and (max-width: 1024px) {{
            #appStartup img {{
                width: 100% !important;
                height: 100% !important;
                object-fit: cover !important;
            }}
            #appStartup .text-overlay {{
                font-size: 1.4em !important;
                transform: translate(-50%, calc(-50% + 3cm)) !important;
            }}
        }}
        
        /* 响应式设计 - 电脑设备 */
        @media only screen and (min-width: 1025px) {{
            #appStartup img {{
                width: 80% !important;
                height: 80% !important;
                object-fit: cover !important;
            }}
            #appStartup .text-overlay {{
                font-size: 1.5em !important;
                transform: translate(-50%, calc(-50% + 4.5cm)) !important;
            }}
        }}
    </style>
    
    <script>
        // 确保页面完全加载后执行
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                var overlay = document.getElementById('appStartup');
                if (overlay) {{
                    overlay.style.opacity = '0';
                    overlay.style.transition = 'opacity 0.8s ease-out';
                    setTimeout(function() {{
                        overlay.style.display = 'none';
                    }}, 800);
                }}
            }}, 3000);
        }});
        
        // 备用方案：如果DOM已经加载，立即执行
        if (document.readyState === 'loading') {{
            // 如果文档还在加载，等待DOMContentLoaded
        }} else {{
            // 如果文档已经加载完成，立即执行定时器
            setTimeout(function() {{
                var overlay = document.getElementById('appStartup');
                if (overlay) {{
                    overlay.style.opacity = '0';
                    overlay.style.transition = 'opacity 0.8s ease-out';
                    setTimeout(function() {{
                        overlay.style.display = 'none';
                    }}, 800);
                }}
            }}, 3000);
        }}
    </script>
    '''
    
    st.markdown(startup_html, unsafe_allow_html=True)
    
    # 等待动画播放
    import time
    time.sleep(3.5)
    
    # 设置标志
    st.session_state.startup_done = True
    st.rerun()

# 自定義灰藍色主題CSS與響應式設計
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes, minimum-scale=0.5, maximum-scale=3.0">
<style>
    /* 响应式设计全局设置 */
    * {
        box-sizing: border-box;
    }
    
    html, body {
        width: 100%;
        overflow-x: hidden;
    }
    
    /* 主背景顏色 */
    .stApp {
        background-color: #f8fafb;
        width: 100%;
        max-width: 100vw;
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
        background-color: #ecf0f3;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    /* 推薦區塊 */
    .recommend-block {
        background-color: #ecf0f3;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    /* 運動icon旋轉動畫 */
    @keyframes rotation {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* 動態運動icon */
    .rotating-icon {
        animation: rotation 3s infinite linear;
        display: inline-block;
        font-size: 24px;
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
    
    /* ===== 全面响应式设计媒体查询 ===== */
    
    /* 手机设备 (最高优先级) */
    @media only screen and (max-width: 768px) {
        .stApp {
            padding: 10px !important;
        }
        
        /* 天气区块响应式 */
        .weather-block {
            padding: 15px !important;
            font-size: 14px !important;
            margin-bottom: 20px !important;
        }
        
        /* 搜索区块响应式 */
        .search-block, .recommend-block {
            padding: 15px !important;
            margin-bottom: 20px !important;
        }
        
        /* 位置选择器响应式 */
        .location-selector-fixed {
            top: 10px !important;
            right: 10px !important;
            font-size: 12px !important;
        }
        
        /* 文本输入框响应式 */
        .stTextInput > div > div > input {
            font-size: 16px !important;
            padding: 12px !important;
            width: 100% !important;
        }
        
        /* 按钮响应式 */
        .stButton button {
            width: 100% !important;
            padding: 12px !important;
            font-size: 16px !important;
        }
        
        /* 列布局响应式 */
        [data-testid="column"] {
            padding: 5px !important;
        }
        
        /* 场地卡片响应式 */
        .venue-card {
            padding: 15px !important;
            margin-bottom: 15px !important;
            font-size: 14px !important;
        }
        
        /* icon调整 */
        .rotating-icon {
            font-size: 20px !important;
        }
        
        /* 标题响应式 */
        h1 {
            font-size: 1.5em !important;
        }
        
        h2 {
            font-size: 1.3em !important;
        }
        
        /* Selectbox响应式 */
        .stSelectbox > div > div {
            font-size: 14px !important;
        }
    }
    
    /* 平板设备 */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        .stApp {
            padding: 20px !important;
        }
        
        .weather-block {
            padding: 18px !important;
            font-size: 15px !important;
        }
        
        .search-block, .recommend-block {
            padding: 20px !important;
        }
        
        .stTextInput > div > div > input {
            font-size: 15px !important;
        }
        
        .stButton button {
            padding: 10px 15px !important;
            font-size: 15px !important;
        }
        
        h1 {
            font-size: 1.8em !important;
        }
    }
    
    /* 大屏幕设备 */
    @media only screen and (min-width: 1025px) {
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .weather-block {
            font-size: 16px;
        }
        
        .search-block, .recommend-block {
            padding: 25px;
        }
    }
    
    /* 超小屏幕设备优化 */
    @media only screen and (max-width: 480px) {
        .weather-block {
            padding: 10px !important;
            font-size: 12px !important;
        }
        
        .search-block, .recommend-block {
            padding: 12px !important;
        }
        
        .stSelectbox > div > div {
            font-size: 13px !important;
        }
        
        h1 {
            font-size: 1.3em !important;
        }
        
        h2 {
            font-size: 1.1em !important;
        }
        
        /* 启动动画响应式 */
        #appStartup .text-overlay {
            font-size: 1em !important;
            transform: translate(-50%, calc(-50% + 1.5cm)) !important;
            padding: 0 10px !important;
        }
    }
    
    /* 全局响应式设置 */
    * {
        box-sizing: border-box;
    }
    
    html, body {
        width: 100%;
        overflow-x: hidden;
    }
</style>
""", unsafe_allow_html=True)

# 確保 session state 已初始化
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

# 運動icon列表和動態更新
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

# 簡潔的標題區域 - 移除蓝色背景
st.markdown(f"""
<div style="padding: 20px 0; margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 2.5em;">{current_icon}</div>
            <div>
                <h1 style="margin: 0; font-size: 2em; color: #424242;">台北運動場地搜尋引擎</h1>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 1.1em;">找到最適合您的運動場地</p>
            </div>
        </div>
        <div style="min-width: 200px;">
            {st.session_state.selected_district}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 位置选择器（简化版，去除蓝色背景）
col1, col2, col3 = st.columns([2, 1, 1])
with col2:
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
        st.query_params["district"] = selected_district
        st.rerun()

with col3:
    if st.button("🎯 自動定位", help="使用GPS自動選擇最近的行政區"):
        st.info("請在瀏覽器中允許定位權限")

# ===== 天氣資訊區塊 =====
# 獲取選擇的區域
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

# ===== 天氣預報區塊 =====
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

# ===== 搜尋功能區塊 =====
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

if 'search_filters' not in st.session_state:
    st.session_state.search_filters = {
        'sport_type': [],
        'district': [],
        'price_range': [0, 5000],
        'facilities': [],
        'rating_min': 0.0
    }

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    # 運動類型篩選
    sport_types = ["全部", "籃球", "足球", "網球", "羽毛球", "游泳", "健身", "跑步", "桌球"]
    selected_sport = st.selectbox("🏃‍♂️ 運動類型", sport_types)

with filter_col2:
    # 地區篩選
    districts = ["全部", "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"]
    selected_district_filter = st.selectbox("📍 地區", districts)

with filter_col3:
    # 價格範圍
    price_range = st.selectbox("💰 價格範圍", ["全部", "免費", "NT$1-100", "NT$101-300", "NT$301-500", "NT$500以上"])

with filter_col4:
    # 評分篩選
    rating_filter = st.selectbox("⭐ 評分", ["全部", "4.5分以上", "4.0分以上", "3.5分以上", "3.0分以上"])

st.markdown('</div>', unsafe_allow_html=True)

# ===== 推薦場館區塊 =====
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

# ===== 原有搜索功能 =====
st.markdown("---")
st.title("🔍 進階搜尋")
st.markdown("使用詳細篩選條件找到最適合的運動場地")

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
                filtered_venues = filtered_venues.sort_values('rating', ascending=False, na_position='last')
            elif sort_option == "價格":
                filtered_venues = filtered_venues.sort_values('price_per_hour', ascending=True, na_position='last')
            elif sort_option == "名稱":
                filtered_venues = filtered_venues.sort_values('name', ascending=True, na_position='last')
            
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
                        button_col1, button_col2, button_col3 = st.columns(3)
                        
                        with button_col1:
                            if st.button(f"📋 詳情", key=f"detail_{idx}"):
                                # 設置選定的場地ID並導航到詳情頁面
                                venue_id = venue.get('id')
                                if venue_id:
                                    st.query_params.id = venue_id
                                    st.switch_page("pages/5_🏢_場地詳情.py")
                        
                        with button_col2:
                            if st.button(f"📍 地圖", key=f"map_{idx}"):
                                st.session_state.selected_venue = venue.to_dict()
                                st.switch_page("pages/2_🗺️_地圖檢視.py")
                        
                        with button_col3:
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
                            venue_id = venue.get('id')
                            if venue_id:
                                st.query_params.id = venue_id
                                st.switch_page("pages/5_🏢_場地詳情.py")
                    
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

# 假設 row 是每筆場地資料
if "favorites" not in st.session_state:
    st.session_state["favorites"] = {}

vid = str(row.get("id", row.get("name")))  # 有 id 就用 id，沒有就用 name
info = {
    "id": vid,
    "name": row.get("name"),
    "address": row.get("address"),
    "sport_type": row.get("sport_type"),
    "rating": row.get("rating"),
    "price_level": row.get("price_level"),
    "lat": row.get("lat") or row.get("latitude"),
    "lon": row.get("lon") or row.get("longitude"),
}

c1, c2 = st.columns([3,1])
with c1:
    st.markdown(f"**{info['name']}** 　{info['sport_type']}　⭐ {info['rating']}　💲{info['price_level']}")
    st.caption(info["address"])
with c2:
    already = vid in st.session_state["favorites"]
    label = "✓ 已收藏" if already else "加入收藏"
    if st.button(label, key=f"fav_{vid}", disabled=already):
        st.session_state["favorites"][vid] = info
        st.toast("已加入收藏", icon="✅")
