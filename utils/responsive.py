"""
統一響應式設計系統
"""
import streamlit as st

def apply_responsive_design():
    """應用統一的響應式設計到當前頁面"""
    
    # 讀取響應式CSS
    try:
        with open('.streamlit/responsive.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        st.markdown(f"""
        <style>
        {css_content}
        </style>
        """, unsafe_allow_html=True)
    except:
        # 後備CSS
        st.markdown("""
        <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; overflow-x: hidden; }
        .stApp { max-width: 1200px; margin: 0 auto; padding: 20px; }
        @media screen and (max-width: 768px) {
            .stApp { padding: 10px !important; }
            h1 { font-size: 1.5rem !important; }
            .stButton > button { width: 100% !important; padding: 12px !important; }
        }
        </style>
        """, unsafe_allow_html=True)