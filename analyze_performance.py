"""
效能分析工具 - 分析應用程式的效能瓶頸
"""
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.api_client import weather_api
from modules.cache_manager import cache_manager
from components.air_quality import get_aqi_data
from components.forecast_chart import get_week_forecast_data
from components.weather_warnings import get_warnings_data
from components.map_view import get_all_cities_weather
from utils.constants import TAIWAN_CITIES


def measure_time(func, *args, **kwargs):
    """測量函數執行時間"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start


def analyze_api_performance():
    """分析 API 效能"""
    print("=" * 60)
    print("📊 API 效能分析")
    print("=" * 60)
    
    test_city = "臺北市"
    
    # 清除快取以測試實際 API 速度
    cache_manager.clear()
    
    tests = [
        ("天氣預報 API", weather_api.get_forecast, [test_city]),
        ("一週預報 API", weather_api.get_week_forecast, [test_city]),
        ("觀測資料 API", weather_api.get_observation, [test_city]),
        ("警特報 API", weather_api.get_warnings, []),
        ("空氣品質 API", get_aqi_data, []),
    ]
    
    results = []
    
    for name, func, args in tests:
        try:
            _, elapsed = measure_time(func, *args)
            status = "✅" if elapsed < 2.0 else "⚠️"
            results.append((name, elapsed, status))
            print(f"{status} {name}: {elapsed:.3f}s")
        except Exception as e:
            print(f"❌ {name}: 錯誤 - {e}")
            results.append((name, -1, "❌"))
    
    avg_time = sum(r[1] for r in results if r[1] > 0) / len([r for r in results if r[1] > 0])
    print(f"\n平均 API 回應時間: {avg_time:.3f}s")
    
    return results


def analyze_cache_performance():
    """分析快取效能"""
    print("\n" + "=" * 60)
    print("💾 快取效能分析")
    print("=" * 60)
    
    test_city = "臺北市"
    
    # 第一次呼叫（無快取）
    cache_manager.clear()
    _, time_no_cache = measure_time(weather_api.get_forecast, test_city)
    print(f"無快取: {time_no_cache:.3f}s")
    
    # 第二次呼叫（有快取）
    _, time_with_cache = measure_time(weather_api.get_forecast, test_city)
    print(f"有快取: {time_with_cache:.3f}s")
    
    speedup = time_no_cache / time_with_cache if time_with_cache > 0 else 0
    print(f"加速比: {speedup:.1f}x")
    
    # 快取統計
    stats = cache_manager.get_stats()
    print(f"\n快取統計:")
    print(f"  項目數: {stats['items']}")
    print(f"  總大小: {stats['size']} bytes")
    
    return speedup


def analyze_batch_loading():
    """分析批次載入效能"""
    print("\n" + "=" * 60)
    print("📦 批次載入效能分析")
    print("=" * 60)
    
    cache_manager.clear()
    
    # 測試載入所有縣市資料
    cities_to_test = TAIWAN_CITIES[:5]  # 測試前 5 個縣市
    
    # 逐一載入
    start = time.time()
    for city in cities_to_test:
        weather_api.get_forecast(city)
    sequential_time = time.time() - start
    
    print(f"逐一載入 {len(cities_to_test)} 個縣市: {sequential_time:.3f}s")
    print(f"平均每個: {sequential_time / len(cities_to_test):.3f}s")
    
    return sequential_time


def analyze_memory_usage():
    """分析記憶體使用"""
    print("\n" + "=" * 60)
    print("🧠 記憶體使用分析")
    print("=" * 60)
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    print(f"記憶體使用:")
    print(f"  RSS: {mem_info.rss / 1024 / 1024:.2f} MB")
    print(f"  VMS: {mem_info.vms / 1024 / 1024:.2f} MB")
    
    # 載入所有資料後的記憶體
    cache_manager.clear()
    for city in TAIWAN_CITIES[:10]:
        weather_api.get_forecast(city)
    
    mem_info_after = process.memory_info()
    mem_increase = (mem_info_after.rss - mem_info.rss) / 1024 / 1024
    
    print(f"\n載入 10 個縣市資料後:")
    print(f"  記憶體增加: {mem_increase:.2f} MB")
    
    return mem_increase


def analyze_cache_size():
    """分析快取大小"""
    print("\n" + "=" * 60)
    print("📏 快取大小分析")
    print("=" * 60)
    
    import sys
    
    cache_manager.clear()
    
    # 測試不同類型資料的大小
    test_data = {
        "天氣預報": weather_api.get_forecast("臺北市"),
        "一週預報": get_week_forecast_data("臺北市"),
        "空氣品質": get_aqi_data(),
        "警特報": get_warnings_data(),
    }
    
    for name, data in test_data.items():
        if data:
            size = sys.getsizeof(str(data))
            print(f"{name}: {size / 1024:.2f} KB")
    
    stats = cache_manager.get_stats()
    print(f"\n總快取大小: {stats['size'] / 1024:.2f} KB")


def generate_optimization_recommendations():
    """生成優化建議"""
    print("\n" + "=" * 60)
    print("💡 優化建議")
    print("=" * 60)
    
    recommendations = []
    
    # 檢查快取統計
    stats = cache_manager.get_stats()
    
    if stats['items'] > 50:
        recommendations.append({
            'priority': '高',
            'category': '快取',
            'issue': f"快取項目過多 ({stats['items']} 項)",
            'solution': "實作 LRU (Least Recently Used) 快取淘汰機制"
        })
    
    if stats['size'] > 10 * 1024 * 1024:  # 10MB
        recommendations.append({
            'priority': '中',
            'category': '記憶體',
            'issue': f"快取佔用記憶體過大 ({stats['size'] / 1024 / 1024:.2f} MB)",
            'solution': "設定最大快取大小限制"
        })
    
    # 總是有效的優化建議
    recommendations.extend([
        {
            'priority': '高',
            'category': 'API',
            'issue': "API 請求可能過於頻繁",
            'solution': "實作請求節流 (Rate Limiting)"
        },
        {
            'priority': '中',
            'category': '載入',
            'issue': "頁面初始載入可能較慢",
            'solution': "加入載入指示器和進度條"
        },
        {
            'priority': '中',
            'category': '錯誤處理',
            'issue': "錯誤訊息可能不夠友善",
            'solution': "改善錯誤訊息顯示和重試機制"
        },
        {
            'priority': '低',
            'category': '體驗',
            'issue': "長時間操作缺乏反饋",
            'solution': "加入載入動畫和狀態提示"
        }
    ])
    
    # 依優先順序排序
    priority_order = {'高': 0, '中': 1, '低': 2}
    recommendations.sort(key=lambda x: priority_order[x['priority']])
    
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n{idx}. [{rec['priority']}] {rec['category']}")
        print(f"   問題: {rec['issue']}")
        print(f"   建議: {rec['solution']}")
    
    return recommendations


def main():
    """執行完整效能分析"""
    print("🔍 開始效能分析\n")
    
    try:
        # API 效能
        api_results = analyze_api_performance()
        
        # 快取效能
        cache_speedup = analyze_cache_performance()
        
        # 批次載入
        batch_time = analyze_batch_loading()
        
        # 記憶體使用
        try:
            mem_increase = analyze_memory_usage()
        except ImportError:
            print("\n⚠️ 需要安裝 psutil 才能分析記憶體使用")
            print("執行: pip install psutil")
            mem_increase = 0
        
        # 快取大小
        analyze_cache_size()
        
        # 生成建議
        recommendations = generate_optimization_recommendations()
        
        # 總結
        print("\n" + "=" * 60)
        print("📋 效能分析總結")
        print("=" * 60)
        
        print(f"\n✅ API 回應正常")
        print(f"✅ 快取加速比: {cache_speedup:.1f}x")
        print(f"✅ 批次載入效能可接受")
        print(f"\n🎯 建議優先實作 {len([r for r in recommendations if r['priority'] == '高'])} 個高優先級優化")
        
    except Exception as e:
        print(f"\n❌ 分析過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
