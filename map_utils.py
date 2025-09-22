import pandas as pd
from typing import Dict, List, Optional
import math

class MapUtils:
    """地圖工具類別"""
    def __init__(self):
        # 台北市各區中心座標
        self.district_centers = {
            "台北市中心": [25.0330, 121.5654],
            "中正區": [25.0320, 121.5200],
            "大同區": [25.0632, 121.5138],
            "中山區": [25.0642, 121.5326],
            "松山區": [25.0497, 121.5746],
            "大安區": [25.0263, 121.5436],
            "萬華區": [25.0338, 121.5014],
            "信義區": [25.0308, 121.5645],
            "士林區": [25.0876, 121.5258],
            "北投區": [25.1174, 121.4985],
            "內湖區": [25.0695, 121.5945],
            "南港區": [25.0547, 121.6066],
            "文山區": [24.9887, 121.5706],
        }
        # Folium 支援的顏色
        self.sport_colors: Dict[str, str] = {
            "籃球": "blue",
            "足球": "green",
            "網球": "red",
            "羽毛球": "orange",
            "游泳": "lightblue",
            "健身房": "purple",
            "跑步": "gray",
            "桌球": "cadetblue",
            "排球": "darkpurple",
            "棒球": "darkgreen",
            "瑜伽": "lightgreen",
            "舞蹈": "pink",
            "其他": "black",
        }

    def get_district_center(self, district_name: str) -> List[float]:
        return self.district_centers.get(district_name, self.district_centers["台北市中心"])

    def get_sport_colors(self) -> Dict[str, str]:
        return self.sport_colors

    # --- 最近場地 ---
    def find_nearest_venue(self, df: pd.DataFrame, lat: float, lng: float) -> Optional[dict]:
        if df is None or df.empty:
            return None
        if "latitude" not in df.columns or "longitude" not in df.columns:
            return None

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
            return 2 * R * math.asin(math.sqrt(a))

        nearest_idx = None
        best_dist = float("inf")
        for idx, row in df.iterrows():
            try:
                rlat, rlng = float(row.get("latitude")), float(row.get("longitude"))
                if math.isnan(rlat) or math.isnan(rlng):
                    continue
                d = haversine(lat, lng, rlat, rlng)
                if d < best_dist:
                    best_dist = d
                    nearest_idx = idx
            except Exception:
                continue
        return None if nearest_idx is None else df.loc[nearest_idx].to_dict()
