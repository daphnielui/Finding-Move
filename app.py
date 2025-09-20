# --- app.py (clean & fixed header + custom icons + startup overlay) ---
import sys, os
from pathlib import Path
import base64
import time
import streamlit as st
import pandas as pd  # 你原本有 import，先保留以免後面用到

# 確保可以匯入 utils/*
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_manager import DataManager
from utils.recommendation_engine import RecommendationEngine
from utils.weather_manager import WeatherManager

# ========= 基本設定（只呼叫一次） =========
st.set_page_config(
    page_title="Finding Move 尋地寶",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========= 載入全域 CSS =========
css_path = Path(".streamlit/responsive.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
else:
    st.warning("⚠️ 找不到 .streamlit/responsive.css")

# ========= 自訂 Icon（取代左上角側邊欄與右上角「更多」的圖示；保留原功能）=========
ICON_FILE = Path("attached_assets/Untitled design - 1.png")  # ← 換成你的實際檔名/路徑
if ICON_FILE.exists():
    icon_b64 = base64.b64encode(ICON_FILE.read_bytes()).decode()
    icon_mime = "image/svg+xml" if ICON_FILE.suffix.lower() == ".svg" else "image/png"

    st.markdown(f"""
    <style>
    /* 左上角：側邊欄切換按鈕（隱藏原 SVG，用你的圖示） */
    header [data-testid="baseButton-headerNoPadding"] svg,
    header [data-testid="stHeader"] button[kind="header"] svg,
    header [data-testid="collapsedControl"] button svg {{
      display: none !important;
    }}
    header [data-testid="baseButton-headerNoPadding"],
    header [data-testid="stHeader"] button[kind="header"],
    header [data-testid="collapsedControl"] button {{
      background-image: url("data:{icon_mime};base64,{icon_b64}");
      background-repeat: no-repeat;
      background-position: center;
      background-size: 22px 22px;
      width: 36px; height: 36px; border-radius: 8px;
    }}
    header [data-testid="baseButton-headerNoPadding"]:hover,
    header [data-testid="stHeader"] button[kind="header"]:hover,
    header [data-testid="collapsedControl"] button:hover {{
      background-color: rgba(0,0,0,0.06);
    }}

    /* 右上角：更多（三點）按鈕（同樣保留功能） */
    [data-testid="stToolbar"] button[kind="header"] svg {{
      display: none !important;
    }}
    [data-testid="stToolbar"] button[kind="header"] {{
      background-image: url("data:{icon_mime};base64,{icon_b64}");
      background-repeat: no-repeat;
      background-position: center;
      background-size: 20px 20px;
      width: 36px; height: 36px; border-radius: 8px;
    }}
    [data-testid="stToolbar"] button[kind="header"]:hover {{
      background-color: rgba(0,0,0,0.06);
    }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ 找不到自訂 icon 檔（attached_assets/Untitled design - 1.png）")

# ========= 啟動畫面（startup overlay）=========
# 小心：不要把整個 header 隱藏，不然你自訂 icon 看不到
# 讀取 Logo（穩健寫法，找不到就不擋啟動）
logo_b64 = ""
logo_file = Path("attached_assets/FM logo_1757941352267.jpg")
if logo_file.exists():
    try:
        logo_b64 = base64.b64encode(logo_file.read_bytes()).decode()
    except Exception as e:
        st.warning(f"讀取啟動 Logo 失敗：{e}")

startup_html = f"""
<div id="appStartup" class="app-startup-overlay" style="display: flex !important;">
    {'<img src="data:image/jpeg;base64,' + logo_b64 + '" class="startup-logo" alt="Finding Move Logo">' if logo_b64 else ''}
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
}}, 2200);
</script>
"""
st.markdown(startup_html, unsafe_allow_html=True)

# 讓 overlay 有機會顯示一下（避免卡太久）
time.sleep(2.4)

# ========= Session State 初始化 =========
st.session_state.setdefault("current_sport_icon", 0)
st.session_state.setdefault("selected_district", "中正區")
st.session_state.setdefault("user_location", None)
st.session_state["startup_done"] = True

# ========= 導向主功能頁 =========
st.switch_page("pages/1_🔍_場地搜尋.py")
# --- end of header section ---
