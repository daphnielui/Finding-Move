# utils/data_manager.py
from pathlib import Path
import pandas as pd
import streamlit as st
import random
import os

@st.cache_data
def load_venues_data():
    """
    從 CSV 載入場地資料，並做欄位映射
    """
    # 指定你的新檔案
    csv_path = Path(__file__).resolve().parents[1] / "attached_assets" / "finding move 2.csv"

    if not csv_path.exists():
        print(f"❌ 找不到 CSV：{csv_path}")
        return pd.DataFrame()

    try:
        # 嘗試以 utf-8-sig 讀檔（避免中文亂碼）
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

        # 欄位名稱對應表（可再依實際 CSV 欄名調整）
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
            "相片": "photos"
        }

        # 統一欄位名稱
        df = df.rename(columns={c: col_map.get(c, c) for c in df.columns})

        # 補充必要欄位
        if "id" not in df.columns:
            df["id"] = range(1, len(df)+1)
        if "rating" not in df.columns:
            df["rating"] = [round(random.uniform(3.5, 5.0), 1) for _ in range(len(df))]

        print(f"✅ 成功載入 {len(df)} 筆場地資料")
        return df

    except Exception as e:
        print(f"❌ 載入 CSV 發生錯誤: {e}")
        return pd.DataFrame()

class DataManager:
    """ 資料管理類別 """

    def __init__(self):
        self.venues_data = load_venues_data()

    def get_all_venues(self):
        return self.venues_data

    def search_venues(self, query: str):
        """ 根據關鍵字搜尋場地 """
        if self.venues_data.empty or not query:
            return pd.DataFrame()

        q = str(query).lower()
        mask = pd.Series(False, index=self.venues_data.index)
        for col in ["name","district","sport_type","address","facilities","description"]:
            if col in self.venues_data.columns:
                mask |= self.venues_data[col].astype(str).str.lower().str.contains(q)

        results = self.venues_data[mask]
        return results if not results.empty else pd.DataFrame()

    def get_filtered_venues(self, sport_types=None, districts=None, price_range=None, facilities=None, min_rating=0.0, search_query=None):
        """ 多條件篩選場地 """
        if self.venues_data.empty:
            return pd.DataFrame()

        filtered = self.venues_data.copy()

        # 搜尋
        if search_query:
            filtered = self.search_venues(search_query)

        # 運動類型
        if sport_types and "sport_type" in filtered.columns:
            filtered = filtered[filtered["sport_type"].isin(sport_types)]

        # 行政區
        if districts and "district" in filtered.columns:
            filtered = filtered[filtered["district"].isin(districts)]

        # 價格
        if price_range and "price_per_hour" in filtered.columns:
            min_p, max_p = price_range
            filtered = filtered[
                (filtered["price_per_hour"] >= min_p) & (filtered["price_per_hour"] <= max_p)
            ]

        # 設施
        if facilities and "facilities" in filtered.columns:
            for f in facilities:
                filtered = filtered[filtered["facilities"].astype(str).str.contains(f, na=False)]

        # 評分
        if min_rating > 0 and "rating" in filtered.columns:
            filtered = filtered[filtered["rating"] >= min_rating]

        return filtered if not filtered.empty else pd.DataFrame()
