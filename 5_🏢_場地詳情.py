import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from datetime import date, time

st.set_page_config(page_title="場地詳情 - 台北運動場地搜尋引擎", page_icon="🏢", layout="wide")

if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

dm: DataManager = st.session_state.data_manager

st.title("🏢 場地詳細資訊")

venue_id = st.query_params.get("id", None)
if venue_id is None:
    all_venues = dm.get_all_venues()
    if all_venues is not None and not all_venues.empty:
        st.subheader("請選擇要查看的場地")
        options = {f"{r['name']} - {r['district']}": int(r['id']) for _, r in all_venues.iterrows()}
        label = st.selectbox("選擇場地", list(options.keys()))
        venue_id = options[label] if label else None
    else:
        st.error("沒有可用的場地資料")
        st.stop()

if venue_id is not None:
    try:
        venue_id = int(venue_id)
        info = dm.get_venue_by_id(venue_id)
        if not info:
            st.error("找不到指定的場地")
            st.stop()

        col1, col2 = st.columns([2,1])
        with col1:
            st.header(info.get('name','場地'))
            st.write(f"**地址:** {info.get('address','—')}")
            st.write(f"**地區:** {info.get('district','—')}")
            st.write(f"**運動類型:** {info.get('sport_type','—')}")
            if info.get('description'):
                st.markdown("**場地介紹:**")
                st.write(info.get('description'))
        with col2:
            if info.get('price_per_hour'):
                st.metric("時租價格", f"NT${int(info.get('price_per_hour'))}/小時")
            if info.get('rating'):
                st.metric("平均評分", f"{float(info.get('rating')):.1f}/5.0")

        if info.get('facilities'):
            st.subheader("🏃‍♂️ 設施資訊")
            facs = info.get('facilities')
            if isinstance(facs, str):
                facs = [p.strip().strip('"') for p in facs.replace('、', ',').split(',') if p.strip()]
            cols = st.columns(min(4, len(facs)))
            for i, f in enumerate(facs):
                with cols[i % 4]:
                    st.info(f"✓ {f}")

        st.subheader("📞 聯絡資訊")
        c1, c2 = st.columns(2)
        with c1:
            if info.get('contact_phone'): st.write(f"**電話:** {info.get('contact_phone')}")
            if info.get('opening_hours'): st.write(f"**營業時間:** {info.get('opening_hours')}")
        with c2:
            if info.get('website'): st.write(f"**網站:** {info.get('website')}")
            if info.get('latitude') and info.get('longitude'):
                st.write(f"**座標:** {float(info.get('latitude')):.4f}, {float(info.get('longitude')):.4f}")

        tab1, tab2, tab3 = st.tabs(["💬 用戶評論", "📅 立即預訂", "📍 地圖位置"])
        with tab1:
            st.info("評論功能尚未接入資料庫，這裡先顯示示範內容。")
            st.write("✨ 乾淨寬敞，器材齊全。")
            st.write("👍 交通方便，價格合理。")
        with tab2:
            st.subheader("場地預訂")
            with st.form("booking_form"):
                c1, c2 = st.columns(2)
                with c1:
                    user_name = st.text_input("預訂人姓名", placeholder="請輸入您的姓名")
                    user_email = st.text_input("電子郵件", placeholder="用於確認預訂")
                    user_phone = st.text_input("聯絡電話", placeholder="緊急聯絡用")
                with c2:
                    booking_date = st.date_input("預訂日期", min_value=date.today())
                    t1, t2 = st.columns(2)
                    with t1:
                        start_time = st.time_input("開始時間", value=time(9, 0))
                    with t2:
                        end_time = st.time_input("結束時間", value=time(10, 0))
                special = st.text_area("特殊需求", placeholder="其他需要說明的事項…")
                if st.form_submit_button("檢查可用性並預訂"):
                    if not (user_name and user_email and user_phone):
                        st.error("請填寫所有必填欄位。")
                    elif start_time >= end_time:
                        st.error("結束時間必須晚於開始時間！")
                    else:
                        ok = dm.check_availability(venue_id, str(booking_date), str(start_time), str(end_time))
                        if ok:
                            bid = dm.create_booking(venue_id, user_name, user_email, user_phone,
                                                    str(booking_date), str(start_time), str(end_time), special)
                            st.success(f"預訂成功！編號：{bid}")
                            st.info("我們將透過電子郵件確認您的預訂詳情。")
                        else:
                            st.warning("該時段已被預訂，請選擇其他時間。")
        with tab3:
            st.subheader("地圖位置")
            if info.get('latitude') and info.get('longitude'):
                df = pd.DataFrame({'lat':[float(info['latitude'])], 'lon':[float(info['longitude'])]})
                st.map(df, zoom=14)
                url = f"https://www.google.com/maps?q={float(info['latitude'])},{float(info['longitude'])}"
                st.markdown(f"[在 Google 地圖中開啟]({url})")
    except Exception as e:
        st.error(f"讀取場地詳情時發生錯誤：{e}")
