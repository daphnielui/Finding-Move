from pathlib import Path
import pandas as pd
import streamlit as st
import random
from typing import List, Dict, Any, Optional

@st.cache_data(show_spinner=False)
def load_venues_data() -> pd.DataFrame:
    """讀取場地資料並做欄位映射與補強。"""
    # 搜尋幾個常見路徑
    candidates = [
        Path('attached_assets') / 'finding move 2.csv',
        Path('data') / 'finding_move_2.csv',
        Path('finding move 2.csv'),
    ]
    csv_path = None
    for p in candidates:
        if p.exists():
            csv_path = p
            break

    if csv_path is None:
        # 回傳空表，避免整個app崩潰
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    except Exception:
        df = pd.read_csv(csv_path)  # 再試一次

    # 欄位映射
    col_map = {
        "名稱": "name", "場地名稱": "name",
        "行政區": "district", "地區": "district",
        "運動類型": "sport_type", "運動": "sport_type",
        "地址": "address",
        "設施": "facilities",
        "價格": "price_per_hour", "價位": "price_per_hour", "收費": "price_per_hour",
        "開放時間": "opening_hours",
        "電話": "contact_phone", "聯絡電話": "contact_phone",
        "網站": "website",
        "描述": "description", "其他": "description",
        "相片": "photos",
        "經度": "longitude",
        "緯度": "latitude",
    }
    df = df.rename(columns={c: col_map.get(c, c) for c in df.columns})

    # 產生必要欄位
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)
    if "rating" not in df.columns:
        df["rating"] = [round(random.uniform(3.6, 4.9), 1) for _ in range(len(df))]

    # 型別清理
    for col in ["price_per_hour", "latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

class DataManager:
    """資料管理類別：封裝常用查詢與操作。"""

    def __init__(self):
        self.venues_data = load_venues_data()

    # ---- 資料基本取得 ----
    def get_all_venues(self) -> pd.DataFrame:
        return self.venues_data

    def get_venue_by_id(self, venue_id: int) -> Optional[Dict[str, Any]]:
        if self.venues_data is None or self.venues_data.empty:
            return None
        m = self.venues_data[self.venues_data["id"] == int(venue_id)]
        return None if m.empty else m.iloc[0].to_dict()

    # ---- 列表選項 ----
    def get_sport_types(self) -> List[str]:
        if "sport_type" not in self.venues_data.columns:
            return []
        vals = sorted(v for v in self.venues_data["sport_type"].dropna().astype(str).unique())
        return vals

    def get_districts(self) -> List[str]:
        if "district" not in self.venues_data.columns:
            return []
        vals = sorted(v for v in self.venues_data["district"].dropna().astype(str).unique())
        return vals

    def get_facilities(self) -> List[str]:
        facs = set()
        if "facilities" in self.venues_data.columns:
            for v in self.venues_data["facilities"].dropna().astype(str):
                for part in str(v).replace("、", ",").split(","):
                    p = part.strip()
                    if p:
                        facs.add(p)
        return sorted(facs)

    def get_popular_searches(self) -> List[str]:
        # 簡單回傳常見搜尋詞或熱門運動
        base = ["籃球", "羽毛球", "游泳", "健身", "網球", "足球"]
        # 加入幾個常見地區
        for d in ["信義區", "大安區", "中山區"]:
            if d in self.get_districts():
                base.append(d)
        return base

    # ---- 搜尋與篩選 ----
    def search_venues(self, query: str) -> pd.DataFrame:
        if self.venues_data is None or self.venues_data.empty or not query:
            return pd.DataFrame()
        q = str(query).strip().lower()
        mask = pd.Series(False, index=self.venues_data.index)
        for col in ["name", "district", "sport_type", "address", "facilities", "description"]:
            if col in self.venues_data.columns:
                mask |= self.venues_data[col].astype(str).str.lower().str.contains(q, na=False)
        res = self.venues_data[mask]
        return res if not res.empty else pd.DataFrame()

    def get_filtered_venues(self,
                            sport_types: Optional[List[str]] = None,
                            districts: Optional[List[str]] = None,
                            price_range: Optional[List[float]] = None,
                            facilities: Optional[List[str]] = None,
                            min_rating: float = 0.0,
                            search_query: Optional[str] = None) -> pd.DataFrame:
        if self.venues_data is None or self.venues_data.empty:
            return pd.DataFrame()
        df = self.venues_data.copy()

        if search_query:
            df = self.search_venues(search_query) if not df.empty else df

        if sport_types:
            df = df[df["sport_type"].isin(sport_types)] if "sport_type" in df.columns else df
        if districts:
            df = df[df["district"].isin(districts)] if "district" in df.columns else df
        if price_range and "price_per_hour" in df.columns:
            lo, hi = price_range
            df = df[(df["price_per_hour"] >= lo) & (df["price_per_hour"] <= hi)]
        if facilities and "facilities" in df.columns:
            for f in facilities:
                df = df[df["facilities"].astype(str).str.contains(f, na=False)]
        if min_rating and "rating" in df.columns:
            df = df[df["rating"] >= float(min_rating)]
        return df if not df.empty else pd.DataFrame()

    # ---- 預訂流程（簡化示範） ----
    def _init_bookings(self):
        if "bookings" not in st.session_state:
            st.session_state["bookings"] = []  # list of dict

    def check_availability(self, venue_id: int, date: str, start: str, end: str) -> bool:
        """簡化的可用性檢查：若該時段已存在同場地預訂，視為不可用。"""
        self._init_bookings()
        for bk in st.session_state["bookings"]:
            if bk["venue_id"] == int(venue_id) and bk["date"] == date:
                # 粗略的時間重疊判定
                if not (end <= bk["start"] or start >= bk["end"]):
                    return False
        return True

    def create_booking(self,
                       venue_id: int,
                       user_name: str,
                       user_email: str,
                       user_phone: str,
                       date: str,
                       start: str,
                       end: str,
                       special_requests: str = "") -> Optional[str]:
        self._init_bookings()
        booking_id = f"BK-{int(random.random()*1e6):06d}"
        st.session_state["bookings"].append({
            "id": booking_id,
            "venue_id": int(venue_id),
            "user_name": user_name,
            "user_email": user_email,
            "user_phone": user_phone,
            "date": date,
            "start": start,
            "end": end,
            "special_requests": special_requests
        })
        return booking_id
