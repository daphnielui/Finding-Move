# utils/data_manager.py
from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import streamlit as st
import random

# ---------- 穩健路徑 ----------
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "attached_assets"
DEFAULT_CSV = ASSETS / "attached_assets/finding move 2.csv"   # 👈 新資料請上傳/覆蓋到這個檔名

# ---------- 欄位別名（自動對應） ----------
COLUMN_ALIASES = {
    "name":        ["name", "名稱", "場地名稱", "地點"],
    "district":    ["district", "行政區", "區"],
    "address":     ["address", "地址", "地點地址"],
    "sport_type":  ["sport_type", "sport", "運動", "運動類型"],
    "price_range": ["price_range", "價格區間", "價格範圍", "價位"],
    "price_per_hour": ["price_per_hour", "每小時價格", "價格"],
    "opening_hours":["opening_hours", "營業時間", "開放時間"],
    "facilities":  ["facilities", "設施"],
    "venue_scale": ["venue_scale", "場地規模"],
    "courses":     ["courses", "課程"],
    "other":       ["other", "其他"],
    "website":     ["website", "官網", "網站"],
    "contact_phone":["contact_phone", "電話", "聯絡電話"],
    "photos":      ["photos", "圖片", "相片"],
    "latitude":    ["latitude", "lat", "緯度"],
    "longitude":   ["longitude", "lon", "經度"],
    "rating":      ["rating", "評分", "stars"],
    "id":          ["id", "場地ID", "場館ID"],
}

# 台北各行政區中心點（缺緯經時使用）
DISTRICT_COORDS = {
    '士林區': (25.0881, 121.5256), '大安區': (25.0266, 121.5484),
    '中山區': (25.0633, 121.5267), '大同區': (25.0633, 121.5154),
    '中正區': (25.0364, 121.5161), '信義區': (25.0336, 121.5751),
    '萬華區': (25.0327, 121.5060), '文山區': (24.9906, 121.5420),
    '松山區': (25.0501, 121.5776), '內湖區': (25.0838, 121.5948),
    '南港區': (25.0415, 121.6073), '北投區': (25.1372, 121.5018)
}
DEFAULT_TAIPEI = (25.0478, 121.5319)

def _rename_by_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """把中英/別名欄位對應到標準欄位名。"""
    mapping = {}
    lower_map = {c.lower(): c for c in df.columns}
    for std, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a in df.columns:
                mapping[a] = std
                break
            if a.lower() in lower_map:
                mapping[lower_map[a.lower()]] = std
                break
    return df.rename(columns=mapping)

def _detect_header_row(csv_path: Path) -> int:
    """
    嘗試偵測 header 在第幾列（回傳需跳過的列數）。
    規則：掃前 10 行，找到包含關鍵欄（如 地址/address/名稱/name）的那一行。
    """
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            lines = [next(f) for _ in range(10)]
    except Exception:
        return 0

    keywords = ["地址", "address", "名稱", "name", "運動", "sport"]
    for i, line in enumerate(lines):
        normalized = line.strip().lower()
        if any(k in normalized for k in [k.lower() for k in keywords]):
            return i  # 跳過 i 行 → 第 i 行當 header
    return 0

def _normalize_sport_type(sport_type):
    if pd.isna(sport_type) or str(sport_type).strip() == "":
        return "綜合運動"
    s = str(sport_type).strip()
    mapping = {
        '羽球': '羽毛球', '羽毛球': '羽毛球', '游泳': '游泳', '健身': '健身',
        '重訓': '健身', '有氧': '有氧運動', '瑜珈': '瑜伽', '瑜伽': '瑜伽',
        '球類': '球類運動', '籃球': '籃球', '足球': '足球', '網球': '網球',
        '桌球': '桌球', '撞球': '撞球', '排球': '排球', '戶外運動': '戶外運動'
    }
    for k, v in mapping.items():
        if k in s:
            return v
    # 多個以 / 分隔時取第一個能對應的
    if "/" in s:
        for t in [x.strip() for x in s.split("/")]:
            for k, v in mapping.items():
                if k in t:
                    return v
    return s

def _extract_price(price_range):
    if pd.isna(price_range) or str(price_range).strip() == "":
        return random.randint(100, 500)
    s = str(price_range).strip()
    if "0-200" in s:
        return 150
    if "200-500" in s:
        return 350
    if "500以上" in s or "500+" in s:
        return 700
    # 若原本就有數字欄位 price_per_hour，就不覆蓋
    try:
        # e.g. "300", "NT$300"
        digits = "".join(ch for ch in s if ch.isdigit())
        if digits:
            return int(digits)
    except Exception:
        pass
    return random.randint(200, 400)

def _normalize_facilities(facilities):
    if pd.isna(facilities) or str(facilities).strip() == "":
        return "基本設施"
    s = str(facilities).strip()
    mapping = {
        '淋浴間': '淋浴間', '置物櫃': '置物櫃', '停車場': '停車場',
        'Wi-Fi': 'Wi-Fi', 'WiFi': 'Wi-Fi', '無障礙設施': '無障礙設施',
        '性別友善設施': '性別友善設施', '寵物友善': '寵物友善', '女性專用': '女性專用'
    }
    norm = [v for k, v in mapping.items() if k in s]
    return "/".join(norm) if norm else s

def _coords_from_district(district: str) -> tuple[float, float]:
    return DISTRICT_COORDS.get(str(district).strip(), DEFAULT_TAIPEI)

@st.cache_data(show_spinner=False)
def load_venues_data(csv_path: str | Path | None = None) -> pd.DataFrame:
    """
    讀取 CSV → 欄位對應 → 數值轉型 → 填補座標/價格/評分
    將新 CSV 放在 attached_assets/venues.csv 後，這裡會自動讀取。
    """
    p = Path(csv_path) if csv_path else DEFAULT_CSV
    if not p.exists():
        print(f"CSV 檔案不存在：{p}")
        return pd.DataFrame()

    # 自動偵測 header 列；優先用 UTF-8-SIG
    skiprows = _detect_header_row(p)
    try:
        df = pd.read_csv(p, encoding="utf-8-sig", skiprows=skiprows)
    except UnicodeDecodeError:
        df = pd.read_csv(p, encoding="utf-8", skiprows=skiprows)

    # 先對應欄位名（把中文/英文/別名統一成標準名）
    df = _rename_by_aliases(df)

    # 若你的舊檔有固定 13 欄（你之前手動命名過），可在找不到標準名時補上對應
    fallback_cols = [
        'name','district','price_range','sport_type','opening_hours','facilities',
        'venue_scale','courses','other','website','address','contact_phone','photos'
    ]
    if set(fallback_cols).issubset(set(df.columns)) is False and len(df.columns) == 13:
        df.columns = fallback_cols

    # 建立標準欄位
    if "name" not in df.columns:
        # 沒名字就沒辦法呈現，直接返回空資料
        return pd.DataFrame()

    # 基本清理
    df = df.dropna(subset=["name"])
    df = df[df["name"].astype(str).str.strip() != ""]

    # sport_type 正規化
    if "sport_type" in df.columns:
        df["sport_type"] = df["sport_type"].apply(_normalize_sport_type)
    else:
        df["sport_type"] = "綜合運動"

    # price_per_hour 優先使用現有欄位，否則由 price_range 推估
    if "price_per_hour" not in df.columns:
        df["price_per_hour"] = df.get("price_range", pd.Series([np.nan]*len(df))).apply(_extract_price)
    df["price_per_hour"] = pd.to_numeric(df["price_per_hour"], errors="coerce")

    # 評分欄位：若沒有就模擬 3.5~5.0
    if "rating" not in df.columns:
        df["rating"] = [round(random.uniform(3.5, 5.0), 1) for _ in range(len(df))]

    # 設施正規化
    if "facilities" in df.columns:
        df["facilities"] = df["facilities"].apply(_normalize_facilities)
    else:
        df["facilities"] = "基本設施"

    # 取得座標：若無緯經度，則用行政區中心；若有空值也補上
    lat_exists = "latitude" in df.columns
    lon_exists = "longitude" in df.columns
    if not lat_exists or not lon_exists:
        coords = df["district"].apply(_coords_from_district) if "district" in df.columns else [DEFAULT_TAIPEI]*len(df)
        df["latitude"]  = [c[0] for c in coords]
        df["longitude"] = [c[1] for c in coords]
    else:
        df["latitude"]  = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
        need_fill = df["latitude"].isna() | df["longitude"].isna()
        if "district" in df.columns and need_fill.any():
            coords = df.loc[need_fill, "district"].apply(_coords_from_district)
            df.loc[need_fill, "latitude"]  = [c[0] for c in coords]
            df.loc[need_fill, "longitude"] = [c[1] for c in coords]

    # 建立 id 欄（若沒有）
    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df)+1))

    # 常用欄位確保存在
    for col in ["opening_hours","venue_scale","courses","other","website","contact_phone","photos","address","district"]:
        if col not in df.columns:
            df[col] = ""

    # 欄位順序（可依需求調整）
    preferred_order = [
        "id","name","address","district","sport_type","price_per_hour","rating",
        "facilities","description","opening_hours","website","contact_phone",
        "venue_scale","courses","photos","latitude","longitude"
    ]
    if "description" not in df.columns and "other" in df.columns:
        df = df.rename(columns={"other":"description"})
    for c in preferred_order:
        if c not in df.columns:
            df[c] = np.nan
    df = df[preferred_order]

    print(f"✅ 成功載入 {len(df)} 筆場地資料：{p}")
    return df

# ---------------- DataManager 類別（保留你的 API）----------------
class DataManager:
    """資料管理類別：對外介面維持相容。"""

    def __init__(self):
        self.venues_data = load_venues_data()  # 直接用上面的函式
        self.sport_types: List[str] = []
        self.districts: List[str] = []
        self.facilities: List[str] = []
        self._extract_metadata()

    def _extract_metadata(self):
        df = self.venues_data
        if df is None or df.empty:
            self.sport_types = [
                "籃球","足球","網球","羽毛球","游泳","健身","跑步","桌球","排球","棒球","瑜伽","舞蹈"
            ]
            self.districts = list(DISTRICT_COORDS.keys())
            self.facilities = [
                "停車場","淋浴間","更衣室","冷氣","器材租借","飲水機","休息區","無障礙設施","Wi-Fi","置物櫃","觀眾席"
            ]
            return

        if "sport_type" in df.columns:
            self.sport_types = sorted(df["sport_type"].dropna().unique().tolist())
        if "district" in df.columns:
            self.districts = sorted(df["district"].dropna().unique().tolist())
        if "facilities" in df.columns:
            all_f = []
            for x in df["facilities"].dropna():
                s = str(x)
                all_f.extend([t.strip() for t in s.split("/") if t.strip()])
            self.facilities = sorted(list(set(all_f)))

    # 其餘你的方法基本保留（僅微調用 self.venues_data）：
    def get_all_venues(self) -> Optional[pd.DataFrame]:
        return self.venues_data.copy() if self.venues_data is not None else None

    def get_sport_types(self) -> List[str]:
        return self.sport_types.copy()

    def get_districts(self) -> List[str]:
        return self.districts.copy()

    def get_facilities(self) -> List[str]:
        return self.facilities.copy()

    def get_venue_stats(self) -> Dict[str, Any]:
        df = self.venues_data
        if df is None or df.empty:
            return {'total_venues': 0,'sport_types': 0,'districts': 0,'avg_price': 0}
        return {
            'total_venues': len(df),
            'sport_types': len(self.sport_types),
            'districts': len(self.districts),
            'avg_price': df['price_per_hour'].mean() if 'price_per_hour' in df.columns else 0
        }

    def search_venues(self, query: str) -> Optional[pd.DataFrame]:
        df = self.venues_data
        if df is None or df.empty or not query:
            return None
        q = str(query).lower().strip()
        cols = ['name','address','district','sport_type','facilities','description']
        mask = pd.Series([False]*len(df))
        for c in cols:
            if c in df.columns:
                mask |= df[c].astype(str).str.lower().str.contains(q, na=False)
        res = df[mask].copy()
        return res if not res.empty else None

    def get_filtered_venues(
        self,
        sport_types: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        price_range: Optional[List[float]] = None,
        facilities: Optional[List[str]] = None,
        min_rating: float = 0.0,
        search_query: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        df = self.venues_data
        if df is None or df.empty:
            return None
        data = df.copy()
        if search_query:
            sr = self.search_venues(search_query)
            if sr is None or sr.empty:
                return None
            data = sr
        if sport_types and "sport_type" in data.columns:
            data = data[data["sport_type"].isin(sport_types)]
        if districts and "district" in data.columns:
            data = data[data["district"].isin(districts)]
        if price_range and "price_per_hour" in data.columns:
            lo, hi = price_range
            data = data[(data["price_per_hour"] >= lo) & (data["price_per_hour"] <= hi)]
        if facilities and "facilities" in data.columns:
            for f in facilities:
                data = data[data["facilities"].astype(str).str.contains(f, na=False, case=False)]
        if min_rating > 0 and "rating" in data.columns:
            data = data[data["rating"] >= min_rating]
        return data if not data.empty else None

    def get_venues_by_ids(self, venue_ids: List[Any]) -> Optional[pd.DataFrame]:
        df = self.venues_data
        if df is None or df.empty or not venue_ids:
            return None
        if "id" in df.columns:
            res = df[df["id"].isin(venue_ids)]
            return res if not res.empty else None
        return None

    def get_venue_by_id(self, venue_id: int) -> Optional[Dict[str, Any]]:
        df = self.venues_data
        if df is None or df.empty:
            return None
        hit = df[df["id"] == venue_id]
        return None if hit.empty else hit.iloc[0].to_dict()

    def get_popular_searches(self) -> List[str]:
        items: List[str] = []
        if self.sport_types:
            items.extend(self.sport_types[:5])
        if self.districts:
            items.extend(self.districts[:3])
        items.extend(["室內", "戶外", "便宜", "高評分", "停車場", "24小時"])
        return items[:10]
