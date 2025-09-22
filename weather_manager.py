import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

class WeatherManager:
    """台北市天氣資料管理。優先讀取本地 JSON（離線備援），可擴充支援 API。"""
    def __init__(self, fallback_json_paths: Optional[list] = None):
        self.data = None
        self.by_district: Dict[str, dict] = {}
        self.fallback_json_paths = fallback_json_paths or [
            'response_1758531461872.json',  # 使用者提供
            os.path.join('attached_assets', 'response_1758531461872.json'),
        ]
        self._load()

    def _load(self):
        # 嘗試讀取本地 JSON
        for p in self.fallback_json_paths:
            if os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        self.data = json.load(f)
                    break
                except Exception:
                    continue
        # 解析
        if self.data:
            self._parse()

    def _parse(self):
        try:
            records = self.data.get('records', {})
            groups = records.get('Locations', [])
            for g in groups:
                if g.get('LocationsName') in ('臺北市', '台北市'):
                    for loc in g.get('Location', []):
                        name = loc.get('LocationName')
                        # 整理各元素
                        elements = {}
                        for e in loc.get('WeatherElement', []):
                            elements[e.get('ElementName')] = e.get('Time', [])
                        self.by_district[name] = {
                            'lat': loc.get('Latitude'),
                            'lon': loc.get('Longitude'),
                            'elements': elements,
                        }
        except Exception:
            self.by_district = {}

    def _nearest_time_value(self, items, key: str, now_dt: Optional[datetime] = None):
        """在多個時間片段中找擇最近的一筆，回傳 ElementValue 的 dict。"""
        if not items:
            return None
        now_dt = now_dt or datetime.now()
        best = None
        best_diff = float('inf')
        for it in items:
            # 支援兩種格式：有 StartTime/EndTime 或 DataTime
            tstr = it.get('DataTime') or it.get('StartTime')
            try:
                t = datetime.fromisoformat(tstr.replace('+08:00', ''))
            except Exception:
                continue
            diff = abs((now_dt - t).total_seconds())
            if diff < best_diff:
                best = it
                best_diff = diff
        if not best:
            return None
        ev = best.get('ElementValue') or []
        if ev and isinstance(ev, list):
            # 可能是 [{Weather: "晴", WeatherCode: "01"}] 或 {Value: "30"}
            return ev[0]
        return None

    def get_current_weather(self, district: str) -> Dict[str, Any]:
        """回傳統一結構的即時天氣資訊。若資料不足，以安全預設填補。"""
        d = self.by_district.get(district) or {}
        elements = d.get('elements', {})

        def val_of(name, subkey='Value', default=None):
            v = self._nearest_time_value(elements.get(name, []), name)
            if isinstance(v, dict):
                return v.get(subkey) or v.get('Weather') or default
            return v or default

        desc = val_of('WeatherDescription', 'Weather') or val_of('Wx', 'Value') or '晴'
        temp = float(val_of('T', 'Value', 28) or 28)
        rh = float(val_of('RH', 'Value', 70) or 70)
        wind = val_of('Wind', 'Value') or ''
        pop = float(val_of('PoP6h', 'Value', 10) or 10)
        app = float(val_of('AT', 'Value', temp) or temp)

        wind_dir = ''
        wind_speed = ''
        if isinstance(wind, str):
            # 可能格式 like "東北風 3 級"
            parts = wind.replace('　', ' ').split()
            if parts:
                wind_dir = parts[0]
            if len(parts) >= 2:
                wind_speed = parts[1]

        comfort = self._comfort_index(temp, rh, pop)

        return {
            "district": district,
            "weather_description": str(desc),
            "temperature": round(temp, 1),
            "humidity": int(round(rh)),
            "wind_direction": wind_dir or '—',
            "wind_speed": wind_speed or '—',
            "precipitation_probability": int(round(pop)),
            "apparent_temperature": round(app, 1),
            "comfort_index": comfort,
            "update_time": datetime.now().strftime('%Y-%m-%d %H:%M')
        }

    def _comfort_index(self, t: float, rh: float, pop: float) -> str:
        score = 10.0 - (max(0, t - 26) * 0.2 + max(0, rh - 60) * 0.05 + pop * 0.02)
        if score >= 8.5: return "舒適"
        if score >= 7.0: return "尚可"
        if score >= 5.5: return "悶熱"
        return "不舒適"

    @staticmethod
    def get_weather_icon(desc: str, temperature: float) -> str:
        d = (desc or '').lower()
        if '雨' in d: return '🌧️'
        if '雷' in d: return '⛈️'
        if '雲' in d or '陰' in d: return '⛅'
        if temperature >= 32: return '🥵'
        if temperature <= 15: return '🥶'
        return '☀️'
