import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from datetime import date, time

st.set_page_config(page_title="場地詳情 - 台北運動場地搜尋引擎", page_icon="🏢", layout="wide")

# ---- 初始化 DataManager ----
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()
dm: DataManager = st.session_state.data_manager

st.title("🏢 場地詳細資訊")

# 方便在 fallback 時使用
_df_cache = None

def _load_all_venues() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = dm.get_all_venues()
        if _df_cache is None:
            _df_cache = pd.DataFrame()
    return _df_cache

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """把常見的中文欄位名對應到統一欄位：name / district / id"""
    rename_map = {}
    if "name" not in df.columns:
        for alt in ["場地名稱", "名稱", "Name"]:
            if alt in df.columns:
                rename_map[alt] = "name"
                break
    if "district" not in df.columns:
        for alt in ["行政區", "地區", "區"]:
            if alt in df.columns:
                rename_map[alt] = "district"
                break
    if rename_map:
        df = df.rename(columns=rename_map)
    if "id" not in df.columns:
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1
    return df

def _safe_float(v):
    try:
        return float(v)
    except Exception:
        return None

def _get_query_id():
    """同時相容 st.query_params 與舊版 experimental_get_query_params。"""
    # 1) 新版
    try:
        qp = st.query_params
        v = qp.get("id", None)
        if isinstance(v, (list, tuple)):
            v = v[0]
        if v is not None:
            return v
    except Exception:
        pass
    # 2) 舊版
    try:
        qp = st.experimental_get_query_params()
        v = qp.get("id", [None])[0]
        return v
    except Exception:
        return None

# ---- 取得 current venue_id ----
venue_id = _get_query_id()

# ---- 若沒有 id：提供下拉選擇（耐撞版） ----
if venue_id is None:
    all_venues = _load_all_venues()
    if all_venues is None or all_venues.empty:
        st.error("沒有可用的場地資料")
        st.stop()

    all_venues = _normalize_columns(all_venues)

    # 組安全的下拉標籤
    def make_label(row: pd.Series) -> str:
        n = row.get("name") or row.get("場地名稱") or row.get("名稱") or "場地"
        d = row.get("district") or row.get("行政區") or row.get("地區") or "—"
        return f"{str(n)} - {str(d)}"

    all_venues["__label"] = all_venues.apply(make_label, axis=1)
    # 避免重名，後綴 #id
    all_venues["__label_id"] = all_venues["__label"] + "  #" + all_venues["id"].astype(int).astype(str)

    label = st.selectbox("選擇場地", all_venues["__label_id"].tolist())
    venue_id = int(all_venues.loc[all_venues["__label_id"] == label, "id"].iloc[0]) if label else None

# ---- 顯示場地資訊 ----
if venue_id is not None:
    try:
        venue_id = int(venue_id)
        info = dm.get_venue_by_id(venue_id)

        # 後備：若 DataManager 沒回來，直接從全表找
        if not info:
            df_all = _normalize_columns(_load_all_venues())
            m = df_all[df_all["id"] == int(venue_id)]
            info = m.iloc[0].to_dict() if not m.empty else None

        if not info:
            st.error("找不到指定的場地")
            st.stop()

        # Header 區
        col1, col2 = st.columns([2, 1])
        with col1:
            title_txt = str(info.get("name") or info.get("場地名稱") or info.get("名稱") or "場地")
            st.header(title_txt)
            st.write(f"**地址:** {info.get('address','—')}")
            st.write(f"**地區:** {info.get('district') or info.get('行政區') or info.get('地區') or '—'}")
            st.write(f"**運動類型:** {info.get('sport_type') or info.get('運動類型') or '—'}")
            if info.get("description"):
                st.markdown("**場地介紹:**")
                st.write(info.get("description"))
        with col2:
            price = _safe_float(info.get("price_per_hour"))
            rating = _safe_float(info.get("rating"))
            if price is not None:
                st.metric("時租價格", f"NT${int(price)}/小時")
            if rating is not None:
                st.metric("平均評分", f"{rating:.1f}/5.0")

        # 設施
        facs = info.get("facilities")
        if facs:
            st.subheader("🏃‍♂️ 設施資訊")
            if isinstance(facs, str):
                fac_list = [p.strip().strip('"') for p in facs.replace("、", ",").split(",") if p.strip()]
            elif isinstance(facs, (list, tuple)):
                fac_list = [str(p).strip() for p in facs if str(p).strip()]
            else:
                fac_list = []
            if fac_list:
                cols = st.columns(min(4, len(fac_list)))
                for i, f in enumerate(fac_list):
                    with cols[i % 4]:
                        st.info(f"✓ {f}")

        # 聯絡資訊
        st.subheader("📞 聯絡資訊")
        c1, c2 = st.columns(2)
        with c1:
            if info.get("contact_phone"):
                st.write(f"**電話:** {info.get('contact_phone')}")
            if info.get("opening_hours"):
                st.write(f"**營業時間:** {info.get('opening_hours')}")
        with c2:
            if info.get("website"):
                st.write(f"**網站:** {info.get('website')}")
            lat = _safe_float(info.get("latitude"))
            lon = _safe_float(info.get("longitude"))
            if lat is not None and lon is not None:
                st.write(f"**座標:** {lat:.4f}, {lon:.4f}")

        # Tabs
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
            lat = _safe_float(info.get("latitude"))
            lon = _safe_float(info.get("longitude"))
            if lat is not None and lon is not None:
                df = pd.DataFrame({"lat":[lat], "lon":[lon]})
                st.map(df, zoom=14)
                url = f"https://www.google.com/maps?q={lat},{lon}"
                st.markdown(f"[在 Google 地圖中開啟]({url})")
    except Exception as e:
        st.error(f"讀取場地詳情時發生錯誤：{e}")
