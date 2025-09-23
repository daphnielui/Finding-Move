# app.py
import streamlit as st
import time, base64
from pathlib import Path

st.set_page_config(
    page_title="Finding Move 尋地寳",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def show_startup_overlay(seconds: float = 2.3):
    """顯示啟動畫面（純 CSS，自動播放 + 自動淡出）"""
    logo_b64 = ""
    logo_file = Path("attached_assets/FM logo_1757941352267.jpg")  # 沒有也沒關係，會自動隱藏
    if logo_file.exists():
        logo_b64 = base64.b64encode(logo_file.read_bytes()).decode()

    st.markdown(f"""
    <style>
    .app-startup-overlay {{
      position: fixed; inset: 0; z-index: 9999;
      display: flex; align-items: center; justify-content: center; gap: 12px;
      background: rgba(255,255,255,.96);
      animation: startupFade 2.2s ease-out forwards;  /* 播完自動隱藏 */
    }}
    @keyframes startupFade {{
      0% {{ opacity: 0; }}
      10% {{ opacity: 1; }}
      85% {{ opacity: 1; }}
      100% {{ opacity: 0; visibility: hidden; }}
    }}
    .startup-logo {{
      height: 72px; width: 72px; object-fit: cover;
      border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,.12);
    }}
    .startup-title-compact {{
      font-size: 18px; font-weight: 700; letter-spacing: .1em; color: #222;
      display: inline-block; white-space: nowrap;
    }}
    .bounce-char {{ display: inline-block; animation: bounce .8s ease-in-out infinite alternate; }}
    .bounce-char:nth-child(2n) {{ animation-delay: .08s; }}
    .bounce-char:nth-child(3n) {{ animation-delay: .16s; }}
    .bounce-char:nth-child(4n) {{ animation-delay: .24s; }}
    @keyframes bounce {{ 0% {{ transform: translateY(0); }} 100% {{ transform: translateY(-6px); }} }}
    </style>

    <div class="app-startup-overlay">
      {('<img src="data:image/jpeg;base64,' + logo_b64 + '" class="startup-logo" alt="FM logo">') if logo_b64 else ''}
      <div class="startup-title-compact">
        <span class="bounce-char">尋</span><span class="bounce-char">地</span><span class="bounce-char">寳</span>
        <span class="bounce-char">-</span>
        <span class="bounce-char">根</span><span class="bounce-char">據</span><span class="bounce-char">您</span>
        <span class="bounce-char">的</span><span class="bounce-char">節</span><span class="bounce-char">奏</span>
        <span class="bounce-char">找</span><span class="bounce-char">到</span><span class="bounce-char">最</span>
        <span class="bounce-char">適</span><span class="bounce-char">合</span><span class="bounce-char">的</span>
        <span class="bounce-char">運</span><span class="bounce-char">動</span><span class="bounce-char">場</span>
        <span class="bounce-char">所</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 讓 overlay 有時間播放（與 CSS 2.2s 對齊）
    time.sleep(seconds)

# 只在第一次載入 app 時播放一次
if "has_played_intro" not in st.session_state:
    show_startup_overlay(2.3)
    st.session_state["has_played_intro"] = True

# 播完導向首頁（如果你的首頁檔名不同，改這行路徑）
st.switch_page("pages/1_🔍_場地搜尋.py")
