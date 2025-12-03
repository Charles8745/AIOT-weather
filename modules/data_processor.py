"""
資料處理模組 - 解析和處理天氣資料
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
import pandas as pd


class WeatherDataProcessor:
    """天氣資料處理器"""
    
    @staticmethod
    def parse_forecast_data(api_response: Dict[str, Any], location: str) -> Optional[Dict[str, Any]]:
        """
        解析一般天氣預報資料 (36小時預報)
        
        Args:
            api_response: API 回應的原始資料
            location: 縣市名稱
            
        Returns:
            解析後的天氣資料字典
        """
        try:
            if not api_response or 'records' not in api_response:
                return None
            
            locations = api_response['records']['location']
            
            # 找到指定縣市的資料
            location_data = None
            for loc in locations:
                if loc['locationName'] == location:
                    location_data = loc
                    break
            
            if not location_data:
                return None
            
            weather_elements = location_data['weatherElement']
            
            # 建立時間段對應的資料
            time_periods = []
            
            # 取得第一個元素的時間資訊作為基準
            if weather_elements and len(weather_elements[0]['time']) > 0:
                num_periods = len(weather_elements[0]['time'])
                
                for i in range(num_periods):
                    period_data = {
                        'start_time': None,
                        'end_time': None,
                        'weather': None,
                        'pop': None,  # 降雨機率
                        'min_temp': None,
                        'max_temp': None,
                        'comfort': None,  # 舒適度
                        'wind': None,  # 風向
                    }
                    
                    # 遍歷所有天氣元素
                    for element in weather_elements:
                        element_name = element['elementName']
                        time_data = element['time'][i] if i < len(element['time']) else None
                        
                        if not time_data:
                            continue
                        
                        # 記錄時間
                        if not period_data['start_time']:
                            period_data['start_time'] = time_data.get('startTime')
                            period_data['end_time'] = time_data.get('endTime')
                        
                        # 解析不同的天氣元素
                        if element_name == 'Wx':  # 天氣現象
                            period_data['weather'] = time_data['parameter']['parameterName']
                        elif element_name == 'PoP':  # 降雨機率
                            period_data['pop'] = int(time_data['parameter']['parameterName'])
                        elif element_name == 'MinT':  # 最低溫度
                            period_data['min_temp'] = float(time_data['parameter']['parameterName'])
                        elif element_name == 'MaxT':  # 最高溫度
                            period_data['max_temp'] = float(time_data['parameter']['parameterName'])
                        elif element_name == 'CI':  # 舒適度
                            period_data['comfort'] = time_data['parameter']['parameterName']
                        elif element_name == 'WD':  # 風向
                            period_data['wind'] = time_data['parameter']['parameterName']
                    
                    time_periods.append(period_data)
            
            return {
                'location': location,
                'update_time': api_response['records']['datasetDescription']['update_time'] if 'update_time' in api_response['records']['datasetDescription'] else datetime.now().isoformat(),
                'periods': time_periods
            }
            
        except Exception as e:
            print(f"解析天氣預報資料時發生錯誤: {e}")
            return None
    
    @staticmethod
    def get_current_weather(parsed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        取得當前時段的天氣資料
        
        Args:
            parsed_data: 已解析的天氣資料
            
        Returns:
            當前時段的天氣資料
        """
        if not parsed_data or 'periods' not in parsed_data or len(parsed_data['periods']) == 0:
            return None
        
        # 回傳第一個時段（最近的預報）
        current = parsed_data['periods'][0]
        return current
    
    @staticmethod
    def get_today_summary(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        取得今日天氣摘要
        
        Args:
            parsed_data: 已解析的天氣資料
            
        Returns:
            今日天氣摘要
        """
        if not parsed_data or 'periods' not in parsed_data:
            return {}
        
        periods = parsed_data['periods'][:3]  # 取前三個時段
        
        # 計算今日溫度範圍
        all_temps = []
        for period in periods:
            if period['min_temp'] is not None:
                all_temps.append(period['min_temp'])
            if period['max_temp'] is not None:
                all_temps.append(period['max_temp'])
        
        # 收集降雨機率
        rain_probs = [p['pop'] for p in periods if p['pop'] is not None]
        
        # 收集天氣描述
        weather_descriptions = [p['weather'] for p in periods if p['weather']]
        
        return {
            'location': parsed_data['location'],
            'min_temp': min(all_temps) if all_temps else None,
            'max_temp': max(all_temps) if all_temps else None,
            'avg_rain_prob': sum(rain_probs) / len(rain_probs) if rain_probs else 0,
            'max_rain_prob': max(rain_probs) if rain_probs else 0,
            'weather_summary': weather_descriptions[0] if weather_descriptions else '資料不可用',
            'periods': periods
        }
    
    @staticmethod
    def format_time_period(start_time: str, end_time: str) -> str:
        """
        格式化時間段顯示
        
        Args:
            start_time: 開始時間 ISO 格式
            end_time: 結束時間 ISO 格式
            
        Returns:
            格式化的時間段字串
        """
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # 判斷是今天、明天還是後天
            today = datetime.now().date()
            start_date = start.date()
            
            if start_date == today:
                day_label = "今天"
            elif (start_date - today).days == 1:
                day_label = "明天"
            elif (start_date - today).days == 2:
                day_label = "後天"
            else:
                day_label = start.strftime("%m/%d")
            
            # 判斷時段
            start_hour = start.hour
            if 6 <= start_hour < 12:
                time_label = "上午"
            elif 12 <= start_hour < 18:
                time_label = "下午"
            else:
                time_label = "晚上"
            
            return f"{day_label} {time_label}"
            
        except Exception as e:
            return f"{start_time} - {end_time}"
    
    @staticmethod
    def parse_observation_data(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析觀測站即時資料
        
        Args:
            api_response: API 回應的原始資料
            
        Returns:
            觀測站資料列表
        """
        try:
            if not api_response or 'records' not in api_response:
                return []
            
            stations = api_response['records']['Station']
            observations = []
            
            for station in stations:
                obs_data = {
                    'station_name': station.get('StationName', 'N/A'),
                    'obs_time': station.get('ObsTime', {}).get('DateTime', 'N/A'),
                    'temperature': None,
                    'humidity': None,
                    'pressure': None,
                    'wind_speed': None,
                    'wind_direction': None,
                }
                
                # 解析天氣元素
                weather_element = station.get('WeatherElement', {})
                
                if 'AirTemperature' in weather_element:
                    obs_data['temperature'] = weather_element['AirTemperature']
                if 'RelativeHumidity' in weather_element:
                    obs_data['humidity'] = weather_element['RelativeHumidity']
                if 'AirPressure' in weather_element:
                    obs_data['pressure'] = weather_element['AirPressure']
                if 'WindSpeed' in weather_element:
                    obs_data['wind_speed'] = weather_element['WindSpeed']
                if 'WindDirection' in weather_element:
                    obs_data['wind_direction'] = weather_element['WindDirection']
                
                observations.append(obs_data)
            
            return observations
            
        except Exception as e:
            print(f"解析觀測資料時發生錯誤: {e}")
            return []
    
    @staticmethod
    def create_forecast_dataframe(parsed_data: Dict[str, Any]) -> pd.DataFrame:
        """
        將解析後的預報資料轉換為 DataFrame
        
        Args:
            parsed_data: 已解析的天氣資料
            
        Returns:
            pandas DataFrame
        """
        if not parsed_data or 'periods' not in parsed_data:
            return pd.DataFrame()
        
        df_data = []
        for period in parsed_data['periods']:
            df_data.append({
                '時段': WeatherDataProcessor.format_time_period(
                    period['start_time'], 
                    period['end_time']
                ),
                '天氣': period['weather'],
                '降雨機率': f"{period['pop']}%" if period['pop'] is not None else 'N/A',
                '最低溫': f"{period['min_temp']}°C" if period['min_temp'] is not None else 'N/A',
                '最高溫': f"{period['max_temp']}°C" if period['max_temp'] is not None else 'N/A',
                '舒適度': period['comfort'],
            })
        
        return pd.DataFrame(df_data)


# 建立全域資料處理器實例
weather_processor = WeatherDataProcessor()
