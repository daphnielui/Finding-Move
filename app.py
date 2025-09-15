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
    
    /* 應用啟動動畫覆蓋層 */
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
        color: white;
        font-family: 'Arial', sans-serif;
    }
    
    .startup-logo-container {
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .app-startup-overlay.hidden {
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.8s ease-out, visibility 0.8s ease-out;
    }
    
    /* 啟動logo動畫 */
    .startup-logo {
        max-width: 90vw;
        max-height: 90vh;
        width: auto;
        height: auto;
        animation: logoFadeIn 1.5s ease-out;
        position: relative;
    }
    
    @keyframes logoFadeIn {
        0% {
            opacity: 0;
            transform: scale(0.8) translateY(20px);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    
    
    /* 啟動標題 - 放置在頁面 2/3 位置 */
    .startup-title-compact {
        position: fixed;
        top: calc(66.67vh - 1.5cm);
        left: 50%;
        transform: translateX(-50%);
        font-size: 1em;
        font-weight: normal;
        text-align: center;
        opacity: 0.9;
        white-space: nowrap;
        font-family: 'uoqmunthenkhung', 'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', 'Heiti TC', sans-serif;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* 字符弹跳动画 - 单个字符依次跳动 */
    .bounce-char {
        display: inline-block;
        animation: charBounceOnce 0.6s ease-in-out;
        animation-fill-mode: both;
    }
    
    @keyframes charBounceOnce {
        0% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-0.2cm);
        }
        100% {
            transform: translateY(0);
        }
    }
    
    /* 为每个字符设置不同的动画延迟 - 依次跳动 */
    .bounce-char:nth-child(1) { animation-delay: 0s; }
    .bounce-char:nth-child(2) { animation-delay: 0.6s; }
    .bounce-char:nth-child(3) { animation-delay: 1.2s; }
    .bounce-char:nth-child(4) { animation-delay: 1.8s; }
    .bounce-char:nth-child(5) { animation-delay: 2.4s; }
    .bounce-char:nth-child(6) { animation-delay: 3.0s; }
    .bounce-char:nth-child(7) { animation-delay: 3.6s; }
    .bounce-char:nth-child(8) { animation-delay: 4.2s; }
    .bounce-char:nth-child(9) { animation-delay: 4.8s; }
    .bounce-char:nth-child(10) { animation-delay: 5.4s; }
    .bounce-char:nth-child(11) { animation-delay: 6.0s; }
    .bounce-char:nth-child(12) { animation-delay: 6.6s; }
    .bounce-char:nth-child(13) { animation-delay: 7.2s; }
    .bounce-char:nth-child(14) { animation-delay: 7.8s; }
    .bounce-char:nth-child(15) { animation-delay: 8.4s; }
    .bounce-char:nth-child(16) { animation-delay: 9.0s; }
    .bounce-char:nth-child(17) { animation-delay: 9.6s; }
    .bounce-char:nth-child(18) { animation-delay: 10.2s; }
    .bounce-char:nth-child(19) { animation-delay: 10.8s; }
    .bounce-char:nth-child(20) { animation-delay: 11.4s; }
    .bounce-char:nth-child(21) { animation-delay: 12.0s; }
    .bounce-char:nth-child(22) { animation-delay: 12.6s; }
    .bounce-char:nth-child(23) { animation-delay: 13.2s; }
    .bounce-char:nth-child(24) { animation-delay: 13.8s; }
    
    @keyframes titleSlideUp {
        0% {
            opacity: 0;
            transform: translateY(30px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 載入進度動畫 */
    .startup-loading {
        display: flex;
        align-items: center;
        gap: 15px;
        animation: loadingFadeIn 2.2s ease-out 0.9s both;
    }
    
    .loading-text {
        font-size: 1.1em;
        margin-right: 10px;
    }
    
    .loading-dots {
        display: flex;
        gap: 5px;
    }
    
    .loading-dot {
        width: 8px;
        height: 8px;
        background-color: white;
        border-radius: 50%;
        animation: dotPulse 1.4s ease-in-out infinite;
    }
    
    .loading-dot:nth-child(1) { animation-delay: 0s; }
    .loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .loading-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes dotPulse {
        0%, 60%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
        }
        30% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes loadingFadeIn {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
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
    
    /* 隱藏 Streamlit 頂部導航元素當啟動動畫顯示時 */
    #appStartup:not(.hidden) {
        display: flex !important;
    }
    
    /* 全域隱藏頂部元素於啟動動畫期間 */
    [data-testid="stHeader"],
    [data-testid="stToolbar"], 
    [data-testid="stDeployButton"],
    [data-testid="stMainMenu"],
    [data-testid="stManageApp"] {
        display: none !important;
    }
    
    /* 當啟動動畫完成後重新顯示頂部元素 */
    .app-startup-overlay.hidden ~ * [data-testid="stHeader"],
    .app-startup-overlay.hidden ~ * [data-testid="stToolbar"],
    .app-startup-overlay.hidden ~ * [data-testid="stDeployButton"],
    .app-startup-overlay.hidden ~ * [data-testid="stMainMenu"],
    .app-startup-overlay.hidden ~ * [data-testid="stManageApp"] {
        display: block !important;
    }
</style>

<!-- 應用啟動動畫HTML -->
<div id="appStartup" class="app-startup-overlay">
    <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAgAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAIcA8ADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDu6KKK9Q4QooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiisrWdYXTo9keGuHHyjso9TVJNuyJlJRV2W73UbbT03TyYJ6IOWP4Vzl14ouZCRbRrEvqfmb/AArEmmknlaWVy7t1JpldMaSW5yTrSe2hck1W/lOWu5v+Atj+VQ/bLrOftM2f981EAWIABJPYVaj0u/l+7aTY9SuP51fuozvJjotW1CE5S7lPsx3D9a17LxSwIW8iBH9+Pr+VZL6NqKDJtJPwGf5VUkikibbJGyN6MMVLjCRSlOJ6JBcRXUQlhkV0PcVJXn1jqE+nzeZC3B+8p6N9a7XTtSg1GDfEcOPvoeqmsJ03E6qdVT06lyiiisjUKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAgvLpLK0kuH6IOB6nsK4C4nkup3mlbLuck1u+KbzdLFaKeFG9/r2/z71z6I0jqiKWZjgAdzXVSjZXOOvO8rCKrOwVFLMTgADJNdDp/hhnAkvWKD/nmvX8T2rU0fR49PiEkgDXLDlv7vsK1aidXpEunQW8iC2sra0XbBCie4HJ/Gp6KKx3OhK2wU140kXa6KynswyKdRQMyrnw/YXAJWMwt6xnH6dKxpdI1DSJhdWreaq91HOPcelddRVqpJGcqUXrsU9N1CPUbUSpww4dP7pq5We+nmC+F5aAKzcTRdA49R6GtCpduhUb21CiiipKCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoopkrbIXYdlJpgcBqE/wBp1CebOQznH06D9K3/AA1pgVPt0q/M3EQPYdzXO2lubq8igHV2A+g711HijWE8OeHZJ4gBLgQ269txHH5AE/hXRVlZcqOSjG7cmNl1ddQ8Trols2Ut0M1249sbY/zIJ9hj1rfrzX4WK011q93KxaQiMFmOSSSxP8hXpVc51J3VwoorgvE3xFj0+4ey0mOOeZDteZ+UU9wAOp9+n1oBux3tFeIt4+8SmTf/AGlj/ZEKY/8AQa6bw98SzLOltrUaIGOBcxjAH+8P6j8qLCU0ekVHNOlum+TITOC3Zfc+1PVgyhlIIIyCO9DKGUqwBBGCD3oGKCCMg5BorCt7s6TqR064Y/Z35gcn7oPY+3at2nJWFGVwoooqSgooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKjuBm2lHqh/lUlIRkEHoaYjj/AAxD5mqGQjiNCR9Tx/U1zfxS1Ay6raWCn5IIvMYf7TH/AAA/Ouy8LReW15u+8rKn5ZrzDxxObjxjqLZ4V1Qf8BUD+laVHeZhTVqZ1vwox9m1T13x/wAmr0WvK/hXdrHqt9aE4M0KuPcqf/sq9UrNm0djmvHWsPpHhqVoW2z3DCFGB5XIOT+QNeI16r8VI3Oj2MgzsW4IP1KnH8jXlVNET3Ciiigk9e+GusPf6JJZTMWks2CqSedhzgfhgj6Yrta8x+FEbm51OTnYEjU/XJ/wr06kzWOxy/iwDzrU99rf0q/4e1E3loYZTmWHAyf4l7GsnxRMH1JIwf8AVxjP1PP+FUtGujaapC+cKx2N9D/nNdHLemc3Py1Wd5RRRXMdYUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAGbYQfZ9T1BcYV2SQfjnP6g14l4kYt4n1Ut1+1yj/x8179gZzgZ6Zrwrxlbm28X6khGN0vmf8AfQDf1qr3ZnJWRR0XU5NG1i1v4wSYXyyj+JTwR+IJr6At54rq2iuIXDxSqHRh3BGRXzhXp3w18Rh4Tody+HTL2xJ6jqV/Dr+fpQwg+h2PiLR013RLixYhXcbo2P8AC45B/wA9jXg13aT2F3Ja3MTRTRttZW7Gvo2sjW/DOl6+g+2wfvVGFmjO11H17j2OaRUo3PA6dHG80qxRIzyOQqqoySfQCvT2+FNp5mV1ScR/3TECfzz/AErpND8IaToDebbRNJcYx58x3MPp2H4U7kKDG+DtAPh/QkhlA+1SnzJsdiei/gP1zW87rGjOxwqjJPoKdWF4lv8AybUWiH95Ly3sv/1/8aIrmdipNRjc5i8uTd3ks5/jYkD0Hb9KgoortWhwN31PSIWLwRuerKCfyp9MhG2CNfRQP0p9cJ6KCiiikMKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvJ/ijYGHWra+UfLcRbSf9pT/AIEflXrFcz480k6r4YmMa5mtj56epA+8Pyz+QpomSujxKpIJ5baeOeF2jljYMjKeQR0NR0UzI9y8JeJ4vEenZYql7EAJox3/ANoex/Suhr540vVLrR9QivbOTZLGfwYdwfUGvcfD/iC08Q6etzbsFkGBLCT80bf4ehpM0jK5rUUVFcXEVrA00zBUUZJoKI769isLVp5TwOAvdj6Vwd1cyXly88pyzH8varGqalJqVyXbKxrwieg/xqjXVThyrXc4qtTmdlsFTWsJuLuGEfxuF/Woa3PDFoZr9rgj5IV4P+0f/rZq5OyuRCPNJI6+iiiuE9EKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoIBBBGQe1FFAHhHi3RDoWvz26qRbufMgP+we34cj8Kw6908W+HI/EWkmNQBdw5eBz691Psf8K8OlikgmeKVGSRGKsrDBBHUVRjJWYyrulaje6ZqEVxp8jpcA4AUZ3/AOyR3B9Khs7O41C7jtbWJpZpDhUXvXq+h+G7DwfZi9vtlxqTDgjop9E/qaN9BLudQNQEGlw3d8vkSNGrPFnJDEcqPXmuQ1PVZtSmy3yxKfkjB6e596ivr+fUJzLM3H8Kjoo9qq1006fLq9zGpVctFsFFFFamI6ON5ZFjRSzscADua73TLFdPsUhGC/3nPq1ZugaP9mQXdwv75h8in+Af41vVy1Z30R2UafKuZhRRRWJuFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFcR408ENrUy3+miNLw4WVGOBIOxz6j9R9K7eqmoX8WnWxllOT0VB1Y00m3oTK1tTnNE0Wy8FaWZZis2oSjDOO/8Asr6KPXv+QrJvLya+uGmmbLHoOwHoKLy8mvrhppmyx6DsB6CoK64Q5fU46lTm0WwUUU+KJ5pFjjQu7HAUDrVmQyun0PQipW7vF56pGe3uf8KW106z0O0bUdUljUxjOWPyp9PU/wCRWno+t2Ou2hubCXeittYEYZT7iuepVvpE6qVG2sjQooorA6QooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAjnmS3geaRsIgyTXB6jfyajdNM/C9EX+6K2PFF+WkWyQ8L80nuew/rXOV1UoWV2cded3yoKKK0tK0ebUn3HKQA/M/r7CtW0ldmKTk7IrWVhPfzeXAuf7zHoo9619Q1XSPBdmfMYT3zrxGp+dv/iV/zzXS21rDZwCGBAqD9fc1454w8K6lpF5LfSyPd2srk/aDywJ7P6fXp/KuWdRy06HXGnyK/Uytc8Q6h4guvOvJfkU/u4V4RB7D+tXPB3iFvD+tLJIx+yTYjnHoOzfh/LNc9RUBfW59JKyuoZSCpGQQeCKWuJ+HGunUNIbTp3zPZ4C56tGen5dPyrtqRsncKKKKQwooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACkZgiM7HCqMk+1LWdrkxh0e4IPLAIPxOP5ZppXdhSdlc4u6nN1dyzt1di30qGitPRtKbUbjc+Rbofnb19hXa2oo89JydkS6LorX7iaYFbZT+Ln0HtXYoiRRqiKFRRgADgUIixoqIoVVGAB2FOrknNyZ206aggpksMc8LwzIskbgqyMMgj0NPoqDQ8d8Z+C30ORr6xVn05zyOphJ7H29D+B9+Or6QlijnieKVFeNwVZWGQQexrxjxn4Tfw9e+fbhm0+Zv3bdfLP8AdP8AT/61UjKUbaoz/C2rnRPENrdlsRFvLm/3Dwfy6/hXvQORkdK+bK928HagdS8K2EzNmRU8p/qvy/yAP40mOD6G7RRRSNAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACsPxS2NMRf70o/ka3KwPFf/AB4Q/wDXX+hq6fxIzq/Azm7K0kvrtII+rHk+g7mu9tbaK0t0giXCKPz96x/DFkIrRrph88pwvso/+v8Ayreq6sruxFGFlcKKKKxNwooooAKrahYW+qWE1ldJvhlXDDuPQj3FWaKAPnzW9Jn0TVp7Cfkxn5W7Op6H8q9K+Fspbw/dRE8Jckj8VX/Co/ifo4uNMh1WNf3ls3lyH1Rjx+R/9CNHwrUjRb5uxuMf+Oj/ABpmaVpHe0UUUjQKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigArG8TRGTSdw/wCWcgY/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gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP//Z" alt="Finding Move Logo" class="startup-logo">
        <div class="startup-title-compact">
            <span class="bounce-char">尋</span><span class="bounce-char">地</span><span class="bounce-char">寳</span><span class="bounce-char"> </span><span class="bounce-char">-</span><span class="bounce-char"> </span><span class="bounce-char">根</span><span class="bounce-char">據</span><span class="bounce-char">您</span><span class="bounce-char">的</span><span class="bounce-char">節</span><span class="bounce-char">奏</span><span class="bounce-char">，</span><span class="bounce-char">找</span><span class="bounce-char">到</span><span class="bounce-char">最</span><span class="bounce-char">適</span><span class="bounce-char">合</span><span class="bounce-char">您</span><span class="bounce-char">的</span><span class="bounce-char">運</span><span class="bounce-char">動</span><span class="bounce-char">場</span><span class="bounce-char">所</span>
        </div>
</div>

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

// 應用啟動動畫控制
(function() {
    const startupOverlay = document.getElementById('appStartup');
    
    // 確保啟動動畫在頁面載入時顯示
    if (startupOverlay) {
        // 檢查是否是第一次載入或從其他頁面返回
        const isFirstLoad = !sessionStorage.getItem('appLoaded');
        
        if (isFirstLoad) {
            // 第一次載入，顯示完整啟動動畫
            startupOverlay.style.display = 'flex';
            
            // 3秒後隱藏啟動動畫
            setTimeout(function() {
                startupOverlay.classList.add('hidden');
                // 動畫結束後設置已載入標記
                setTimeout(function() {
                    sessionStorage.setItem('appLoaded', 'true');
                }, 800); // 等待fade out動畫完成
            }, 3000);
        } else {
            // 非第一次載入，立即隱藏啟動動畫
            startupOverlay.style.display = 'none';
        }
    }
    
    // 監聽頁面重新載入事件
    window.addEventListener('beforeunload', function() {
        // 如果是完全重新載入頁面，清除已載入標記
        if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
            sessionStorage.removeItem('appLoaded');
        }
    });
})();

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
