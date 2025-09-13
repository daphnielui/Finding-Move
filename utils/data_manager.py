import pandas as pd
import numpy as np
import os
from typing import List, Optional, Dict, Any
import json
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class DataManager:
    """
    資料管理類別，負責處理場地資料的載入、篩選和搜尋功能
    """
    
    def __init__(self):
        self.venues_data = None
        self.sport_types = []
        self.districts = []
        self.facilities = []
        self._load_data()
    
    def _load_data(self):
        """
        從PostgreSQL資料庫載入場地資料
        """
        try:
            # 建立資料庫連接
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL environment variable not found")
            
            self.engine = create_engine(database_url)
            
            # 載入所有場地資料
            query = """
            SELECT id, name, address, district, sport_type, price_per_hour, 
                   rating, facilities, description, contact_phone, opening_hours, 
                   website, latitude, longitude, photos, created_at, updated_at
            FROM venues
            ORDER BY name
            """
            
            self.venues_data = pd.read_sql(query, self.engine)
            
            # 更新可用選項
            self._update_available_options()
            
            print(f"成功載入 {len(self.venues_data)} 筆場地資料")
            
        except Exception as e:
            print(f"載入資料庫資料時發生錯誤: {e}")
            # 建立空的資料結構作為後備
            column_names = [
                'id', 'name', 'address', 'district', 'sport_type',
                'price_per_hour', 'rating', 'facilities', 'description',
                'contact_phone', 'opening_hours', 'website',
                'latitude', 'longitude', 'photos', 'created_at', 'updated_at'
            ]
            self.venues_data = pd.DataFrame(columns=column_names)
            self.engine = None
            self._update_available_options()
    
    def _update_available_options(self):
        """更新可用的運動類型、地區和設施列表"""
        if self.venues_data is not None and not self.venues_data.empty:
            # 運動類型
            if 'sport_type' in self.venues_data.columns:
                self.sport_types = self.venues_data['sport_type'].dropna().unique().tolist()
            
            # 地區
            if 'district' in self.venues_data.columns:
                self.districts = self.venues_data['district'].dropna().unique().tolist()
            
            # 設施
            if 'facilities' in self.venues_data.columns:
                all_facilities = []
                for facilities in self.venues_data['facilities'].dropna():
                    if isinstance(facilities, str):
                        all_facilities.extend([f.strip() for f in facilities.split(',')])
                    elif isinstance(facilities, list):
                        all_facilities.extend(facilities)
                
                self.facilities = list(set(all_facilities))
        else:
            # 如果沒有資料，提供一些預設選項供篩選器使用
            self.sport_types = [
                "籃球", "足球", "網球", "羽毛球", "游泳", "健身房", 
                "跑步", "桌球", "排球", "棒球", "瑜伽", "舞蹈"
            ]
            self.districts = [
                "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區",
                "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"
            ]
            self.facilities = [
                "停車場", "淋浴間", "更衣室", "冷氣", "音響設備", "器材租借",
                "飲水機", "休息區", "無障礙設施", "Wi-Fi", "置物櫃", "觀眾席"
            ]
    
    def get_all_venues(self) -> Optional[pd.DataFrame]:
        """獲取所有場地資料"""
        return self.venues_data.copy() if self.venues_data is not None else None
    
    def get_sport_types(self) -> List[str]:
        """獲取所有可用的運動類型"""
        return self.sport_types.copy()
    
    def get_districts(self) -> List[str]:
        """獲取所有可用的地區"""
        return self.districts.copy()
    
    def get_facilities(self) -> List[str]:
        """獲取所有可用的設施"""
        return self.facilities.copy()
    
    def get_venue_stats(self) -> Dict[str, Any]:
        """獲取場地統計資訊"""
        if self.venues_data is None or self.venues_data.empty:
            return {
                'total_venues': 0,
                'sport_types': 0,
                'districts': 0,
                'avg_price': 0
            }
        
        stats = {
            'total_venues': len(self.venues_data),
            'sport_types': len(self.sport_types),
            'districts': len(self.districts),
            'avg_price': self.venues_data['price_per_hour'].mean() if 'price_per_hour' in self.venues_data.columns else 0
        }
        
        return stats
    
    def search_venues(self, query: str) -> Optional[pd.DataFrame]:
        """
        根據關鍵字搜尋場地
        
        Args:
            query: 搜尋關鍵字
            
        Returns:
            符合搜尋條件的場地資料
        """
        if self.venues_data is None or self.venues_data.empty or not query:
            return None
        
        query = query.lower().strip()
        
        # 在多個欄位中搜尋
        search_columns = ['name', 'address', 'district', 'sport_type', 'facilities', 'description']
        
        mask = pd.Series([False] * len(self.venues_data))
        
        for col in search_columns:
            if col in self.venues_data.columns:
                mask |= self.venues_data[col].astype(str).str.lower().str.contains(query, na=False)
        
        results = self.venues_data[mask].copy()
        
        return results if not results.empty else None
    
    def get_filtered_venues(self, 
                          sport_types: Optional[List[str]] = None,
                          districts: Optional[List[str]] = None,
                          price_range: Optional[List[float]] = None,
                          facilities: Optional[List[str]] = None,
                          min_rating: float = 0.0,
                          search_query: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        根據多個條件篩選場地
        
        Args:
            sport_types: 運動類型列表
            districts: 地區列表
            price_range: 價格範圍 [最低價, 最高價]
            facilities: 設施需求列表
            min_rating: 最低評分要求
            search_query: 搜尋關鍵字
            
        Returns:
            符合篩選條件的場地資料
        """
        if self.venues_data is None or self.venues_data.empty:
            return None
        
        filtered_data = self.venues_data.copy()
        
        # 關鍵字搜尋
        if search_query:
            search_results = self.search_venues(search_query)
            if search_results is not None:
                filtered_data = search_results
            else:
                return None
        
        # 運動類型篩選
        if sport_types and 'sport_type' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['sport_type'].isin(sport_types)]
        
        # 地區篩選
        if districts and 'district' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['district'].isin(districts)]
        
        # 價格範圍篩選
        if price_range and 'price_per_hour' in filtered_data.columns:
            min_price, max_price = price_range
            filtered_data = filtered_data[
                (filtered_data['price_per_hour'] >= min_price) &
                (filtered_data['price_per_hour'] <= max_price)
            ]
        
        # 設施篩選
        if facilities and 'facilities' in filtered_data.columns:
            for facility in facilities:
                filtered_data = filtered_data[
                    filtered_data['facilities'].astype(str).str.contains(facility, na=False, case=False)
                ]
        
        # 評分篩選
        if min_rating > 0 and 'rating' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
        
        return filtered_data if not filtered_data.empty else None
    
    def get_venues_by_ids(self, venue_ids: List[Any]) -> Optional[pd.DataFrame]:
        """
        根據場地ID列表獲取場地資料
        
        Args:
            venue_ids: 場地ID列表
            
        Returns:
            對應的場地資料
        """
        if self.venues_data is None or self.venues_data.empty or not venue_ids:
            return None
        
        # 如果沒有ID欄位，使用name或index作為ID
        if 'id' in self.venues_data.columns:
            filtered_data = self.venues_data[self.venues_data['id'].isin(venue_ids)]
        elif 'name' in self.venues_data.columns:
            filtered_data = self.venues_data[self.venues_data['name'].isin(venue_ids)]
        else:
            # 使用index
            filtered_data = self.venues_data[self.venues_data.index.isin(venue_ids)]
        
        return filtered_data if not filtered_data.empty else None
    
    def get_popular_searches(self) -> List[str]:
        """
        獲取熱門搜尋關鍵字
        
        Returns:
            熱門搜尋關鍵字列表
        """
        # 這裡可以從實際的搜尋記錄中統計
        # 暫時返回一些常見的搜尋關鍵字
        popular_searches = []
        
        # 添加運動類型作為熱門搜尋
        if self.sport_types:
            popular_searches.extend(self.sport_types[:5])
        
        # 添加地區作為熱門搜尋
        if self.districts:
            popular_searches.extend(self.districts[:3])
        
        # 添加一些常見搜尋詞
        common_searches = ["室內", "戶外", "便宜", "高評分", "停車場", "24小時"]
        popular_searches.extend(common_searches)
        
        return popular_searches[:10]  # 返回前10個熱門搜尋
    
    def add_venue(self, venue_data: Dict[str, Any]) -> bool:
        """
        新增場地資料
        
        Args:
            venue_data: 場地資料字典
            
        Returns:
            是否新增成功
        """
        try:
            if self.venues_data is None:
                self._load_data()
            
            # 生成新的ID
            if 'id' not in venue_data:
                venue_data['id'] = len(self.venues_data) + 1
            
            # 將新資料轉換為DataFrame並合併
            new_venue_df = pd.DataFrame([venue_data])
            self.venues_data = pd.concat([self.venues_data, new_venue_df], ignore_index=True)
            
            # 更新可用選項
            self._update_available_options()
            
            return True
            
        except Exception as e:
            print(f"新增場地時發生錯誤: {e}")
            return False
    
    def update_venue(self, venue_id: Any, venue_data: Dict[str, Any]) -> bool:
        """
        更新場地資料
        
        Args:
            venue_id: 場地ID
            venue_data: 更新的場地資料
            
        Returns:
            是否更新成功
        """
        try:
            if self.venues_data is None or self.venues_data.empty:
                return False
            
            # 尋找對應的場地
            if 'id' in self.venues_data.columns:
                mask = self.venues_data['id'] == venue_id
            else:
                return False
            
            if mask.any():
                # 更新資料
                for key, value in venue_data.items():
                    if key in self.venues_data.columns:
                        self.venues_data.loc[mask, key] = value
                
                # 更新可用選項
                self._update_available_options()
                
                return True
            
            return False
            
        except Exception as e:
            print(f"更新場地時發生錯誤: {e}")
            return False
    
    def delete_venue(self, venue_id: Any) -> bool:
        """
        刪除場地資料
        
        Args:
            venue_id: 場地ID
            
        Returns:
            是否刪除成功
        """
        try:
            if self.venues_data is None or self.venues_data.empty:
                return False
            
            # 尋找對應的場地
            if 'id' in self.venues_data.columns:
                mask = self.venues_data['id'] == venue_id
            else:
                return False
            
            if mask.any():
                # 刪除資料
                self.venues_data = self.venues_data[~mask].reset_index(drop=True)
                
                # 更新可用選項
                self._update_available_options()
                
                return True
            
            return False
            
        except Exception as e:
            print(f"刪除場地時發生錯誤: {e}")
            return False
    
    def get_venue_by_id(self, venue_id: int) -> Optional[Dict[str, Any]]:
        """根據ID獲取場地詳細資訊"""
        try:
            if self.engine is None:
                return None
            
            query = """
            SELECT v.*, 
                   COALESCE(AVG(r.rating), v.rating) as avg_rating,
                   COUNT(r.id) as review_count
            FROM venues v
            LEFT JOIN reviews r ON v.id = r.venue_id AND r.status = 'approved'
            WHERE v.id = %s
            GROUP BY v.id
            """
            
            result = pd.read_sql(query, self.engine, params=[venue_id])
            
            if result.empty:
                return None
                
            return result.iloc[0].to_dict()
            
        except Exception as e:
            print(f"獲取場地詳細資訊時發生錯誤: {e}")
            return None
    
    def get_venue_reviews(self, venue_id: int, status: str = 'approved') -> List[Dict[str, Any]]:
        """獲取場地的評論"""
        try:
            if self.engine is None:
                return []
            
            query = """
            SELECT user_name, rating, comment, created_at
            FROM reviews
            WHERE venue_id = %s AND status = %s
            ORDER BY created_at DESC
            """
            
            result = pd.read_sql(query, self.engine, params=[venue_id, status])
            return result.to_dict('records')
            
        except Exception as e:
            print(f"獲取場地評論時發生錯誤: {e}")
            return []
    
    def add_review(self, venue_id: int, user_name: str, rating: int, comment: str) -> bool:
        """添加場地評論"""
        try:
            if self.engine is None:
                return False
            
            with self.engine.connect() as conn:
                query = text("""
                INSERT INTO reviews (venue_id, user_name, rating, comment, status)
                VALUES (:venue_id, :user_name, :rating, :comment, 'pending')
                """)
                
                conn.execute(query, {
                    'venue_id': venue_id,
                    'user_name': user_name,
                    'rating': rating,
                    'comment': comment
                })
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"添加評論時發生錯誤: {e}")
            return False
    
    def check_availability(self, venue_id: int, booking_date: str, start_time: str, end_time: str) -> bool:
        """檢查場地可用性"""
        try:
            if self.engine is None:
                return False
            
            query = """
            SELECT COUNT(*) as booking_count
            FROM bookings
            WHERE venue_id = %s 
              AND booking_date = %s
              AND status IN ('pending', 'confirmed')
              AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s) OR
                (start_time >= %s AND end_time <= %s)
              )
            """
            
            result = pd.read_sql(query, self.engine, params=[
                venue_id, booking_date, start_time, start_time,
                end_time, end_time, start_time, end_time
            ])
            
            return result.iloc[0]['booking_count'] == 0
            
        except Exception as e:
            print(f"檢查場地可用性時發生錯誤: {e}")
            return False
    
    def create_booking(self, venue_id: int, user_name: str, user_email: str, user_phone: str,
                      booking_date: str, start_time: str, end_time: str, 
                      special_requests: str = None) -> Optional[int]:
        """創建場地預訂"""
        try:
            if self.engine is None:
                return None
            
            # 首先檢查可用性
            if not self.check_availability(venue_id, booking_date, start_time, end_time):
                return None
            
            # 計算總價格
            venue_info = self.get_venue_by_id(venue_id)
            if not venue_info:
                return None
            
            # 簡單計算小時數和總價
            from datetime import datetime
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            hours = (end - start).seconds / 3600
            total_price = hours * float(venue_info['price_per_hour'])
            
            with self.engine.connect() as conn:
                query = text("""
                INSERT INTO bookings (venue_id, user_name, user_email, user_phone,
                                    booking_date, start_time, end_time, total_price, special_requests)
                VALUES (:venue_id, :user_name, :user_email, :user_phone,
                        :booking_date, :start_time, :end_time, :total_price, :special_requests)
                RETURNING id
                """)
                
                result = conn.execute(query, {
                    'venue_id': venue_id,
                    'user_name': user_name,
                    'user_email': user_email,
                    'user_phone': user_phone,
                    'booking_date': booking_date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_price': total_price,
                    'special_requests': special_requests
                })
                conn.commit()
                
                booking_id = result.fetchone()[0]
                return booking_id
                
        except Exception as e:
            print(f"創建預訂時發生錯誤: {e}")
            return None
