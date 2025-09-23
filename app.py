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

def show_startup_overlay(seconds: float = 2.3,
                         photo_path: str = "attached_assets/FM logo_1757941352267.jpg",
                         title: str = "Finding Move 尋地寳"):
    """啟動畫面：全螢幕背景大圖（自動播放與淡出）"""
    img_b64 = ""
    p = Path(photo_path)
    if p.exists():
        img_b64 = base64.b64encode(p.read_bytes()).decode()

    # 背景樣式（存在圖片就用全螢幕覆蓋，否則用淡色底）
    bg_style = (
        f"background: url('data:image/jpeg;base64,{img_b64}') center/cover no-repeat fixed;"
        if img_b64
        else "background:#e9eef6;"
    )

    st.markdown(f"""
    <style>
      .fm-start-overlay {{
        position: fixed; inset: 0; z-index: 99999;
        {bg_style}
        display: grid; place-items: center;
        animation: fmFade 2.2s ease-out forwards; /* 2.2s 後自動隱藏 */
      }}
      @keyframes fmFade {{
        0% {{ opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; visibility: hidden; }}
      }}
      .fm-title-badge {{
        padding: 14px 20px;
        border-radius: 14px;
        background: rgba(255,255,255,.86);
        box-shadow: 0 8px 24px rgba(0,0,0,.14);
        font-size: 18px; font-weight: 700; color: #222;
        letter-spacing: .04em;
      }}
      @media (max-width: 520px) {{
        .fm-title-badge {{ font-size: 16px; padding: 10px 14px; border-radius: 12px; }}
      }}
    </style>

    <div class="fm-start-overlay">
      <div class="fm-title-badge">{title}</div>
    </div>
    """, unsafe_allow_html=True)

    # 給動畫時間播放（與 CSS 2.2s 對齊，稍微多 0.1s 保險）
    time.sleep(seconds)

# 僅第一次載入播放
if "has_played_intro" not in st.session_state:
    show_startup_overlay(2.3)
    st.session_state["has_played_intro"] = True

# 播完導向首頁（若你的首頁檔名不同，改這行）
st.switch_page("pages/1_🔍_場地搜尋.py")
