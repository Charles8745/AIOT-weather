"""
測試地圖功能
"""
from components.map_view import WeatherMap, get_all_cities_weather
from utils.constants import CITY_COORDINATES, TAIWAN_CITIES

def test_map_creation():
    """測試地圖建立"""
    print("=" * 60)
    print("測試: 地圖元件建立")
    print("=" * 60)
    
    try:
        weather_map = WeatherMap()
        print(f"✅ 地圖物件建立成功")
        print(f"✅ 台灣中心座標: {weather_map.taiwan_center}")
        print(f"✅ 預設縮放等級: {weather_map.default_zoom}")
        return True
    except Exception as e:
        print(f"❌ 地圖建立錯誤: {e}")
        return False

def test_city_coordinates():
    """測試縣市座標"""
    print("\n" + "=" * 60)
    print("測試: 縣市座標")
    print("=" * 60)
    
    print(f"✅ 座標資料筆數: {len(CITY_COORDINATES)}")
    print(f"✅ 縣市列表筆數: {len(TAIWAN_CITIES)}")
    
    # 檢查所有縣市都有座標
    missing_coords = []
    for city in TAIWAN_CITIES:
        if city not in CITY_COORDINATES:
            missing_coords.append(city)
    
    if missing_coords:
        print(f"❌ 缺少座標的縣市: {missing_coords}")
        return False
    else:
        print(f"✅ 所有縣市都有座標資料")
        
        # 顯示幾個範例
        print("\n📍 座標範例:")
        for city in list(TAIWAN_CITIES)[:5]:
            coords = CITY_COORDINATES[city]
            print(f"   {city}: {coords}")
        
        return True

def test_all_cities_weather_data():
    """測試取得所有縣市天氣資料"""
    print("\n" + "=" * 60)
    print("測試: 取得所有縣市天氣資料")
    print("=" * 60)
    print("⚠️  這個測試會請求所有縣市的 API 資料，可能需要一些時間...")
    
    try:
        # 取得部分縣市資料進行測試（避免太多 API 請求）
        test_cities = ["臺北市", "臺中市", "高雄市"]
        from modules.api_client import weather_api
        from modules.data_processor import weather_processor
        
        success_count = 0
        for city in test_cities:
            print(f"\n📍 測試 {city}...")
            forecast_data = weather_api.get_forecast(city)
            
            if forecast_data:
                parsed_data = weather_processor.parse_forecast_data(forecast_data, city)
                if parsed_data and parsed_data.get('periods'):
                    period = parsed_data['periods'][0]
                    print(f"   ✅ 天氣: {period.get('weather')}")
                    print(f"   ✅ 溫度: {period.get('min_temp')}°C ~ {period.get('max_temp')}°C")
                    success_count += 1
                else:
                    print(f"   ❌ 資料解析失敗")
            else:
                print(f"   ❌ API 請求失敗")
        
        success_rate = (success_count / len(test_cities)) * 100
        print(f"\n✅ 測試成功率: {success_rate:.0f}% ({success_count}/{len(test_cities)})")
        
        return success_count == len(test_cities)
        
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_map_marker_creation():
    """測試地圖標記建立"""
    print("\n" + "=" * 60)
    print("測試: 地圖標記建立")
    print("=" * 60)
    
    try:
        import folium
        from modules.api_client import weather_api
        from modules.data_processor import weather_processor
        
        # 建立測試地圖
        test_map = folium.Map(
            location=[23.5, 121.0],
            zoom_start=7
        )
        
        # 取得測試資料
        city = "臺北市"
        forecast_data = weather_api.get_forecast(city)
        
        if forecast_data:
            parsed_data = weather_processor.parse_forecast_data(forecast_data, city)
            
            if parsed_data:
                # 建立地圖物件並測試標記
                weather_map = WeatherMap()
                coords = CITY_COORDINATES[city]
                
                weather_map._add_city_marker(
                    test_map, 
                    city, 
                    coords, 
                    parsed_data
                )
                
                print(f"✅ 成功為 {city} 建立地圖標記")
                print(f"✅ 座標: {coords}")
                return True
            else:
                print("❌ 資料解析失敗")
                return False
        else:
            print("❌ API 請求失敗")
            return False
            
    except Exception as e:
        print(f"❌ 標記建立錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_map_tests():
    """執行所有地圖測試"""
    print("\n" + "🗺️" * 30)
    print("開始地圖功能測試")
    print("🗺️" * 30 + "\n")
    
    test_results = []
    
    # 測試 1: 地圖元件建立
    result = test_map_creation()
    test_results.append(("地圖元件建立", result))
    
    # 測試 2: 縣市座標
    result = test_city_coordinates()
    test_results.append(("縣市座標", result))
    
    # 測試 3: 地圖標記建立
    result = test_map_marker_creation()
    test_results.append(("地圖標記建立", result))
    
    # 測試 4: 取得所有縣市天氣（可選）
    result = test_all_cities_weather_data()
    test_results.append(("天氣資料獲取", result))
    
    # 顯示測試結果摘要
    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:20s} {status}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    success_rate = passed_tests / total_tests * 100
    
    print("\n" + "=" * 60)
    print(f"總測試數: {total_tests}")
    print(f"通過: {passed_tests}")
    print(f"失敗: {total_tests - passed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    print("=" * 60)
    
    if success_rate == 100:
        print("\n🎉 所有地圖功能測試通過！")
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    run_map_tests()
