"""
進階功能測試 - 測試空氣品質和一週預報
"""
import sys
import os

# 加入專案路徑
sys.path.insert(0, os.path.dirname(__file__))

from components.air_quality import get_aqi_data, process_aqi_data
from components.forecast_chart import get_week_forecast_data, parse_week_forecast
from modules.api_client import weather_api
import traceback


def test_aqi_api():
    """測試空氣品質 API 連線"""
    print("=" * 60)
    print("測試 1: 空氣品質 API 連線")
    print("=" * 60)
    
    try:
        data = get_aqi_data()
        
        if data is None:
            print("❌ 空氣品質 API 回傳 None")
            return False
        
        if not isinstance(data, list):
            print(f"❌ 空氣品質資料格式錯誤，預期 list，實際 {type(data)}")
            return False
        
        if len(data) == 0:
            print("❌ 空氣品質資料為空")
            return False
        
        print(f"✅ 成功取得 {len(data)} 筆空氣品質資料")
        
        # 檢查第一筆資料結構
        first_record = data[0]
        print("\n第一筆資料結構:")
        print(f"  資料鍵值: {list(first_record.keys())}")
        
        required_fields = ['sitename', 'county', 'aqi', 'pm2.5', 'pm10', 'publishtime']
        missing_fields = [field for field in required_fields if field not in first_record]
        
        if missing_fields:
            print(f"⚠️ 缺少欄位: {missing_fields}")
        else:
            print("✅ 所有必要欄位都存在")
        
        # 顯示範例資料
        print("\n範例資料:")
        print(f"  測站: {first_record.get('sitename', 'N/A')}")
        print(f"  縣市: {first_record.get('county', 'N/A')}")
        print(f"  AQI: {first_record.get('aqi', 'N/A')}")
        print(f"  PM2.5: {first_record.get('pm2.5', 'N/A')}")
        print(f"  PM10: {first_record.get('pm10', 'N/A')}")
        print(f"  發布時間: {first_record.get('publishtime', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def test_aqi_processing():
    """測試空氣品質資料處理"""
    print("\n" + "=" * 60)
    print("測試 2: 空氣品質資料處理")
    print("=" * 60)
    
    try:
        # 取得資料
        data = get_aqi_data()
        
        if not data:
            print("❌ 無法取得空氣品質資料")
            return False
        
        # 處理資料
        df = process_aqi_data(data)
        
        if df.empty:
            print("❌ 處理後的 DataFrame 為空")
            return False
        
        print(f"✅ 成功處理 {len(df)} 筆資料")
        
        # 檢查 DataFrame 欄位
        expected_columns = ['測站', '縣市', 'AQI', '狀態', 'PM2.5', 'PM10', '發布時間', '顏色']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ 缺少欄位: {missing_columns}")
            return False
        
        print("✅ 所有欄位都存在")
        
        # 統計資訊
        print(f"\n統計資訊:")
        print(f"  總測站數: {len(df)}")
        print(f"  縣市數: {df['縣市'].nunique()}")
        print(f"  平均 AQI: {df['AQI'].mean():.1f}")
        print(f"  最高 AQI: {df['AQI'].max()} ({df.loc[df['AQI'].idxmax(), '測站']})")
        print(f"  最低 AQI: {df['AQI'].min()} ({df.loc[df['AQI'].idxmin(), '測站']})")
        
        # 顯示各狀態數量
        print(f"\n各空氣品質狀態統計:")
        status_counts = df['狀態'].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}: {count} 站")
        
        # 顯示前 5 筆
        print(f"\n前 5 筆資料:")
        print(df.head().to_string())
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def test_week_forecast_api():
    """測試一週預報 API 連線"""
    print("\n" + "=" * 60)
    print("測試 3: 一週預報 API 連線")
    print("=" * 60)
    
    test_city = "臺北市"
    
    try:
        print(f"測試縣市: {test_city}")
        
        # 直接測試 API
        data = weather_api.get_week_forecast(test_city)
        
        if data is None:
            print("❌ 一週預報 API 回傳 None")
            return False
        
        if not isinstance(data, dict):
            print(f"❌ 一週預報資料格式錯誤，預期 dict，實際 {type(data)}")
            return False
        
        print("✅ API 連線成功")
        
        # 檢查資料結構
        if 'records' not in data:
            print("❌ 資料缺少 'records' 鍵")
            print(f"可用的鍵: {list(data.keys())}")
            return False
        
        records = data['records']
        print(f"\nrecords 結構: {list(records.keys())}")
        
        # 新版 API 使用 Locations (大寫)
        if 'Locations' not in records and 'location' not in records:
            print("❌ records 缺少 'Locations' 或 'location' 鍵")
            return False
        
        print("✅ 資料結構正確")
        
        # 處理新舊版 API 結構
        if 'Locations' in records:
            # 新版 API
            locations_list = records['Locations']
            if isinstance(locations_list, list) and len(locations_list) > 0:
                locations = locations_list[0].get('Location', [])
            else:
                locations = []
        else:
            # 舊版 API
            locations = records.get('location', [])
        
        print(f"✅ 成功取得 {len(locations)} 個地點的資料")
        
        # 檢查是否包含測試縣市
        city_found = False
        for loc in locations:
            # 新版使用 LocationName，舊版使用 locationName
            loc_name = loc.get('LocationName') or loc.get('locationName')
            
            if loc_name == test_city:
                city_found = True
                print(f"✅ 找到 {test_city} 的資料")
                
                # 檢查資料元素
                weather_elements = loc.get('WeatherElement', []) or loc.get('weatherElement', [])
                print(f"  天氣元素數量: {len(weather_elements)}")
                
                element_names = [elem.get('ElementName') or elem.get('elementName') for elem in weather_elements]
                print(f"  元素名稱前5個: {element_names[:5]}")
                
                # 檢查時間資料
                if weather_elements:
                    first_element = weather_elements[0]
                    time_data = first_element.get('Time', []) or first_element.get('time', [])
                    print(f"  時間筆數: {len(time_data)}")
                    
                    if time_data:
                        first_time = time_data[0]
                        start_time = first_time.get('StartTime') or first_time.get('startTime')
                        end_time = first_time.get('EndTime') or first_time.get('endTime')
                        print(f"  第一筆時間: {start_time} ~ {end_time}")
                
                break
        
        if not city_found:
            print(f"❌ 找不到 {test_city} 的資料")
            print(f"可用的地點: {[loc.get('locationName') for loc in locations[:5]]}...")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def test_week_forecast_parsing():
    """測試一週預報資料解析"""
    print("\n" + "=" * 60)
    print("測試 4: 一週預報資料解析")
    print("=" * 60)
    
    test_city = "臺北市"
    
    try:
        # 取得資料
        api_data = get_week_forecast_data(test_city)
        
        if not api_data:
            print("❌ 無法取得一週預報資料")
            return False
        
        print("✅ 成功取得 API 資料")
        
        # 解析資料
        df = parse_week_forecast(api_data, test_city)
        
        if df is None:
            print("❌ 解析結果為 None")
            return False
        
        if df.empty:
            print("❌ 解析後的 DataFrame 為空")
            return False
        
        print(f"✅ 成功解析 {len(df)} 筆資料")
        
        # 檢查欄位
        expected_columns = ['start_time', 'end_time', 'min_temp', 'max_temp', 'weather', 'pop', 'date', 'date_str', 'weekday']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ 缺少欄位: {missing_columns}")
            print(f"實際欄位: {list(df.columns)}")
            return False
        
        print("✅ 所有欄位都存在")
        
        # 檢查資料完整性
        print(f"\n資料完整性檢查:")
        for col in ['min_temp', 'max_temp', 'weather', 'pop']:
            null_count = df[col].isnull().sum()
            print(f"  {col}: {len(df) - null_count}/{len(df)} 筆有資料")
        
        # 統計資訊
        print(f"\n溫度統計:")
        print(f"  最低溫範圍: {df['min_temp'].min():.1f}°C ~ {df['min_temp'].max():.1f}°C")
        print(f"  最高溫範圍: {df['max_temp'].min():.1f}°C ~ {df['max_temp'].max():.1f}°C")
        
        print(f"\n降雨機率:")
        print(f"  平均: {df['pop'].mean():.1f}%")
        print(f"  最高: {df['pop'].max()}%")
        
        # 按日期分組統計
        daily_data = df.groupby('date_str').agg({
            'min_temp': 'min',
            'max_temp': 'max',
            'pop': 'max',
            'weather': 'first'
        })
        
        print(f"\n每日摘要 (共 {len(daily_data)} 天):")
        print(daily_data.to_string())
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def test_multiple_cities_week_forecast():
    """測試多個縣市的一週預報"""
    print("\n" + "=" * 60)
    print("測試 5: 多個縣市一週預報")
    print("=" * 60)
    
    test_cities = ["臺北市", "新北市", "臺中市", "高雄市"]
    results = {}
    
    for city in test_cities:
        print(f"\n測試 {city}...")
        
        try:
            api_data = get_week_forecast_data(city)
            
            if not api_data:
                print(f"  ❌ 無法取得資料")
                results[city] = False
                continue
            
            df = parse_week_forecast(api_data, city)
            
            if df is None or df.empty:
                print(f"  ❌ 解析失敗")
                results[city] = False
                continue
            
            print(f"  ✅ 成功 ({len(df)} 筆資料)")
            results[city] = True
            
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            results[city] = False
    
    # 總結
    print(f"\n測試結果總結:")
    success_count = sum(results.values())
    total_count = len(results)
    
    for city, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {city}")
    
    print(f"\n成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count


def main():
    """執行所有測試"""
    print("🧪 開始執行進階功能測試\n")
    
    results = {}
    
    # 空氣品質測試
    results['AQI API 連線'] = test_aqi_api()
    results['AQI 資料處理'] = test_aqi_processing()
    
    # 一週預報測試
    results['一週預報 API 連線'] = test_week_forecast_api()
    results['一週預報資料解析'] = test_week_forecast_parsing()
    results['多縣市一週預報'] = test_multiple_cities_week_forecast()
    
    # 輸出測試結果總表
    print("\n" + "=" * 60)
    print("📊 測試結果總表")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{status} - {test_name}")
    
    # 統計
    passed_count = sum(results.values())
    total_count = len(results)
    success_rate = (passed_count / total_count) * 100
    
    print(f"\n總計: {passed_count}/{total_count} 通過 ({success_rate:.1f}%)")
    
    if passed_count == total_count:
        print("✅ 所有測試通過！")
        return 0
    else:
        print("⚠️ 部分測試失敗，請檢查錯誤訊息")
        return 1


if __name__ == '__main__':
    exit(main())
