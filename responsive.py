"""統一響應式設計系統"""
import streamlit as st
from pathlib import Path

def apply_responsive_design():
    """注入 CSS。優先使用 .streamlit/responsive.css，其次使用根目錄 responsive.css，否則使用內建後備樣式。"""
    tried_paths = [
        Path('.streamlit') / 'responsive.css',
        Path('responsive.css'),
    ]
    css_text = None
    for p in tried_paths:
        try:
            if p.exists():
                css_text = p.read_text(encoding='utf-8')
                break
        except Exception:
            pass

    if css_text is None:
        css_text = """
        * { box-sizing: border-box; }
        html, body { width: 100%; overflow-x: hidden; }
        .stApp { max-width: 1200px; margin: 0 auto; padding: 20px; }
        @media (max-width: 768px) {
            .stApp { padding: 10px !important; }
            h1 { font-size: 1.5rem !important; }
            .stButton > button { width: 100% !important; padding: 12px !important; }
        }
        """

    st.markdown(f"""<style>{css_text}</style>""", unsafe_allow_html=True)
