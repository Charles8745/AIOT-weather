"""
測試腳本 - 測試天氣資料 API 和資料處理功能
"""
import sys
from modules.api_client import weather_api
from modules.data_processor import weather_processor
from utils.constants import TAIWAN_CITIES
from utils.helpers import get_weather_icon, format_temperature, format_probability

def test_api_connection():
    """測試 API 連線"""
    print("=" * 60)
    print("測試 1: API 連線測試")
    print("=" * 60)
    
    test_city = "臺北市"
    print(f"📍 測試城市: {test_city}")
    
    try:
        forecast_data = weather_api.get_forecast(test_city)
        
        if forecast_data:
            print("✅ API 連線成功")
            print(f"✅ 資料結構正確: {bool(forecast_data.get('records'))}")
            return True, forecast_data
        else:
            print("❌ API 連線失敗")
            return False, None
    except Exception as e:
        print(f"❌ API 連線錯誤: {e}")
        return False, None

def test_data_parsing(forecast_data, test_city):
    """測試資料解析"""
    print("\n" + "=" * 60)
    print("測試 2: 資料解析測試")
    print("=" * 60)
    
    try:
        parsed_data = weather_processor.parse_forecast_data(forecast_data, test_city)
        
        if parsed_data:
            print("✅ 資料解析成功")
            print(f"✅ 縣市: {parsed_data.get('location')}")
            print(f"✅ 更新時間: {parsed_data.get('update_time')}")
            print(f"✅ 時段數量: {len(parsed_data.get('periods', []))}")
            
            # 顯示第一個時段的資料
            if parsed_data.get('periods'):
                first_period = parsed_data['periods'][0]
                print(f"\n📅 第一個時段資料:")
                print(f"   - 開始時間: {first_period.get('start_time')}")
                print(f"   - 結束時間: {first_period.get('end_time')}")
                print(f"   - 天氣: {first_period.get('weather')}")
                print(f"   - 降雨機率: {first_period.get('pop')}%")
                print(f"   - 最低溫: {first_period.get('min_temp')}°C")
                print(f"   - 最高溫: {first_period.get('max_temp')}°C")
                print(f"   - 舒適度: {first_period.get('comfort')}")
            
            return True, parsed_data
        else:
            print("❌ 資料解析失敗")
            return False, None
    except Exception as e:
        print(f"❌ 資料解析錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_today_summary(parsed_data):
    """測試今日摘要生成"""
    print("\n" + "=" * 60)
    print("測試 3: 今日摘要生成測試")
    print("=" * 60)
    
    try:
        summary = weather_processor.get_today_summary(parsed_data)
        
        if summary:
            print("✅ 今日摘要生成成功")
            print(f"✅ 縣市: {summary.get('location')}")
            print(f"✅ 最低溫: {summary.get('min_temp')}°C")
            print(f"✅ 最高溫: {summary.get('max_temp')}°C")
            print(f"✅ 平均降雨機率: {summary.get('avg_rain_prob'):.1f}%")
            print(f"✅ 最高降雨機率: {summary.get('max_rain_prob')}%")
            print(f"✅ 天氣摘要: {summary.get('weather_summary')}")
            print(f"✅ 天氣圖示: {get_weather_icon(summary.get('weather_summary'))}")
            return True
        else:
            print("❌ 今日摘要生成失敗")
            return False
    except Exception as e:
        print(f"❌ 今日摘要錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_time_formatting(parsed_data):
    """測試時間格式化"""
    print("\n" + "=" * 60)
    print("測試 4: 時間格式化測試")
    print("=" * 60)
    
    try:
        if parsed_data.get('periods') and len(parsed_data['periods']) >= 3:
            for i, period in enumerate(parsed_data['periods'][:3]):
                formatted_time = weather_processor.format_time_period(
                    period['start_time'],
                    period['end_time']
                )
                print(f"✅ 時段 {i+1}: {formatted_time}")
            return True
        else:
            print("❌ 沒有足夠的時段資料")
            return False
    except Exception as e:
        print(f"❌ 時間格式化錯誤: {e}")
        return False

def test_dataframe_creation(parsed_data):
    """測試 DataFrame 建立"""
    print("\n" + "=" * 60)
    print("測試 5: DataFrame 建立測試")
    print("=" * 60)
    
    try:
        df = weather_processor.create_forecast_dataframe(parsed_data)
        
        if not df.empty:
            print("✅ DataFrame 建立成功")
            print(f"✅ 資料筆數: {len(df)}")
            print(f"✅ 欄位: {list(df.columns)}")
            print("\n📊 資料預覽:")
            print(df.to_string())
            return True
        else:
            print("❌ DataFrame 是空的")
            return False
    except Exception as e:
        print(f"❌ DataFrame 建立錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_cities():
    """測試多個城市"""
    print("\n" + "=" * 60)
    print("測試 6: 多城市測試")
    print("=" * 60)
    
    test_cities = ["臺北市", "臺中市", "高雄市"]
    results = []
    
    for city in test_cities:
        try:
            print(f"\n📍 測試 {city}...")
            forecast_data = weather_api.get_forecast(city)
            
            if forecast_data:
                parsed_data = weather_processor.parse_forecast_data(forecast_data, city)
                if parsed_data and parsed_data.get('periods'):
                    summary = weather_processor.get_today_summary(parsed_data)
                    print(f"   ✅ {city}: {summary['weather_summary']}, "
                          f"{summary['min_temp']}°C~{summary['max_temp']}°C, "
                          f"降雨機率 {summary['max_rain_prob']}%")
                    results.append(True)
                else:
                    print(f"   ❌ {city}: 資料解析失敗")
                    results.append(False)
            else:
                print(f"   ❌ {city}: API 連線失敗")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {city}: 錯誤 - {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n✅ 成功率: {success_rate:.0f}% ({sum(results)}/{len(results)})")
    return all(results)

def test_helper_functions():
    """測試輔助函數"""
    print("\n" + "=" * 60)
    print("測試 7: 輔助函數測試")
    print("=" * 60)
    
    try:
        # 測試天氣圖示
        weather_types = ["晴天", "多雲", "陰天", "雨天", "雷雨"]
        print("天氣圖示測試:")
        for weather in weather_types:
            icon = get_weather_icon(weather)
            print(f"   {weather}: {icon}")
        
        # 測試溫度格式化
        print("\n溫度格式化測試:")
        print(f"   25.5°C: {format_temperature(25.5)}")
        print(f"   None: {format_temperature(None)}")
        
        # 測試機率格式化
        print("\n機率格式化測試:")
        print(f"   80%: {format_probability(80)}")
        print(f"   None: {format_probability(None)}")
        
        print("\n✅ 所有輔助函數測試通過")
        return True
    except Exception as e:
        print(f"❌ 輔助函數錯誤: {e}")
        return False

def run_all_tests():
    """執行所有測試"""
    print("\n" + "🧪" * 30)
    print("開始執行完整測試套件")
    print("🧪" * 30 + "\n")
    
    test_results = []
    test_city = "臺北市"
    
    # 測試 1: API 連線
    success, forecast_data = test_api_connection()
    test_results.append(("API 連線", success))
    
    if not success:
        print("\n❌ API 連線失敗，無法繼續測試")
        return
    
    # 測試 2: 資料解析
    success, parsed_data = test_data_parsing(forecast_data, test_city)
    test_results.append(("資料解析", success))
    
    if not success:
        print("\n❌ 資料解析失敗，無法繼續測試")
        return
    
    # 測試 3: 今日摘要
    success = test_today_summary(parsed_data)
    test_results.append(("今日摘要", success))
    
    # 測試 4: 時間格式化
    success = test_time_formatting(parsed_data)
    test_results.append(("時間格式化", success))
    
    # 測試 5: DataFrame 建立
    success = test_dataframe_creation(parsed_data)
    test_results.append(("DataFrame 建立", success))
    
    # 測試 6: 多城市測試
    success = test_multiple_cities()
    test_results.append(("多城市測試", success))
    
    # 測試 7: 輔助函數
    success = test_helper_functions()
    test_results.append(("輔助函數", success))
    
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
        print("\n🎉 所有測試通過！系統運作正常！")
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    run_all_tests()
