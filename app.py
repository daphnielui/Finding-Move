import sys, os
sys.path.insert(0, os.path.dirname(__file__))
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

# 統一響應式設計 - 簡潔高效
st.markdown("""
<style>
    /* 統一響應式設計系統 */
    * { box-sizing: border-box; }
    html, body { width: 100%; overflow-x: hidden; margin: 0; padding: 0; }
    
    .stApp { 
        max-width: 1200px; 
        margin: 0 auto; 
        padding: 20px; 
    }
    
    /* 手機響應 */
    @media screen and (max-width: 768px) {
        .stApp { padding: 10px !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        .stButton > button { 
            width: 100% !important; 
            padding: 12px !important; 
            font-size: 16px !important; 
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div { 
            font-size: 16px !important; 
            padding: 12px !important; 
        }
        [data-testid="column"] { padding: 5px !important; }
        iframe { width: 100% !important; height: 400px !important; }
        .js-plotly-plot { width: 100% !important; }
    }
    
    @media screen and (max-width: 480px) {
        .stApp { padding: 5px !important; }
        h1 { font-size: 1.3rem !important; }
        iframe { height: 350px !important; }
    }
    
    /* 啟動動畫響應式 */
    .startup-title-compact {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, calc(-50% + 4.5cm));
        font-size: clamp(0.6rem, 1.8vw, 0.9rem);
        color: white;
        white-space: nowrap;
        width: 95vw;
        text-align: center;
        font-family: 'Microsoft JhengHei', sans-serif;
    }
    
    @media screen and (max-width: 768px) {
        .startup-title-compact {
            font-size: clamp(0.5rem, 2.2vw, 0.8rem) !important;
            width: 98vw !important;
        }
    }
    
    .app-startup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #a6bee2;
        z-index: 99999;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    
    .startup-logo {
        max-width: 100vw;
        max-height: 100vh;
        width: auto;
        height: auto;
    }
    
    .app-startup-overlay.hidden {
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.8s ease-out, visibility 0.8s ease-out;
    }
    
    .bounce-char {
        display: inline-block;
        animation: charBounce 0.6s ease-in-out;
    }
    
    @keyframes charBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-0.2cm); }
    }
    
    /* 隐藏顶部白色条 */
    header[data-testid="stHeader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ===== 启动页面逻辑 =====

# 读取logo文件
with open('attached_assets/FM logo_1757941352267.jpg', 'rb') as f:
    logo_data = f.read()

# 编码为base64
import base64
logo_base64 = base64.b64encode(logo_data).decode()

# 完整的启动页面HTML
startup_html = f'''
<div id="appStartup" class="app-startup-overlay" style="display: flex !important;">
    <img src="data:image/jpeg;base64,{logo_base64}" class="startup-logo" alt="Finding Move Logo">
    <div class="startup-title-compact">
        <span class="bounce-char">尋</span><span class="bounce-char">地</span><span class="bounce-char">寳</span><span class="bounce-char"> </span><span class="bounce-char">-</span><span class="bounce-char"> </span><span class="bounce-char">根</span><span class="bounce-char">據</span><span class="bounce-char">您</span><span class="bounce-char">的</span><span class="bounce-char">節</span><span class="bounce-char">奏</span><span class="bounce-char">，</span><span class="bounce-char">找</span><span class="bounce-char">到</span><span class="bounce-char">最</span><span class="bounce-char">適</span><span class="bounce-char">合</span><span class="bounce-char">您</span><span class="bounce-char">的</span><span class="bounce-char">運</span><span class="bounce-char">動</span><span class="bounce-char">場</span><span class="bounce-char">所</span>
    </div>
</div>

<script>
setTimeout(function() {{
    var overlay = document.getElementById('appStartup');
    if (overlay) {{
        overlay.classList.add('hidden');
    }}
}}, 3000);
</script>
'''

# 显示启动页面
st.markdown(startup_html, unsafe_allow_html=True)

# 等待3.5秒显示启动动画
time.sleep(3.5)

# 初始化session state
if 'current_sport_icon' not in st.session_state:
    st.session_state.current_sport_icon = 0
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = '中正區'
if 'user_location' not in st.session_state:
    st.session_state.user_location = None

# 设置启动完成标志
st.session_state.startup_done = True

# 自动跳转到主页面
st.switch_page("pages/1_🔍_場地搜尋.py")
