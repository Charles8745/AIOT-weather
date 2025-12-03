"""
測試天氣警特報功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from components.weather_warnings import (
    get_warnings_data, 
    process_warnings_data,
    get_warning_severity,
    get_warning_color,
    get_warning_icon
)
import traceback


def test_warnings_api():
    """測試警特報 API 連線"""
    print("=" * 60)
    print("測試 1: 天氣警特報 API 連線")
    print("=" * 60)
    
    try:
        data = get_warnings_data()
        
        if data is None:
            print("❌ 警特報 API 回傳 None")
            return False
        
        if not isinstance(data, dict):
            print(f"❌ 資料格式錯誤，預期 dict，實際 {type(data)}")
            return False
        
        print("✅ API 連線成功")
        
        # 檢查資料結構
        if 'records' not in data:
            print("❌ 資料缺少 'records' 鍵")
            return False
        
        records = data['records']
        
        if 'location' not in records:
            print("❌ records 缺少 'location' 鍵")
            return False
        
        locations = records['location']
        print(f"✅ 成功取得 {len(locations)} 個地點的警報資料")
        
        if len(locations) > 0:
            print("\n第一筆警報資料:")
            first_loc = locations[0]
            print(f"  縣市: {first_loc.get('locationName')}")
            
            hazards = first_loc.get('hazardConditions', {}).get('hazards', [])
            if hazards:
                first_hazard = hazards[0]
                info = first_hazard.get('info', {})
                print(f"  警報類型: {info.get('phenomena')}")
                print(f"  等級: {info.get('significance')}")
                
                valid_time = first_hazard.get('validTime', {})
                print(f"  有效時間: {valid_time.get('startTime')} ~ {valid_time.get('endTime')}")
        else:
            print("\n✅ 目前無警報資料（這是正常的）")
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def test_warnings_processing():
    """測試警特報資料處理"""
    print("\n" + "=" * 60)
    print("測試 2: 天氣警特報資料處理")
    print("=" * 60)
    
    try:
        # 取得資料
        data = get_warnings_data()
        
        if not data:
            print("❌ 無法取得警特報資料")
            return False
        
        print("✅ 成功取得 API 資料")
        
        # 處理資料
        df = process_warnings_data(data)
        
        if df.empty:
            print("✅ 目前無警報（DataFrame 為空是正常的）")
            return True
        
        print(f"✅ 成功處理 {len(df)} 筆警報資料")
        
        # 檢查 DataFrame 欄位
        expected_columns = ['縣市', '警報類型', '等級', '嚴重程度', '開始時間', '結束時間', '顏色']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ 缺少欄位: {missing_columns}")
            return False
        
        print("✅ 所有欄位都存在")
        
        # 統計資訊
        print(f"\n統計資訊:")
        print(f"  總警報數: {len(df)}")
        print(f"  影響縣市: {df['縣市'].nunique()} 個")
        print(f"  警報類型: {df['警報類型'].nunique()} 種")
        
        # 警報類型統計
        print(f"\n警報類型分布:")
        type_counts = df['警報類型'].value_counts()
        for warning_type, count in type_counts.items():
            print(f"  {warning_type}: {count} 個縣市")
        
        # 嚴重程度統計
        print(f"\n嚴重程度分布:")
        severity_counts = df['嚴重程度'].value_counts()
        for severity, count in severity_counts.items():
            print(f"  {severity}: {count} 個")
        
        # 顯示前 5 筆
        print(f"\n前 5 筆資料:")
        print(df.head().to_string())
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def test_helper_functions():
    """測試輔助函數"""
    print("\n" + "=" * 60)
    print("測試 3: 輔助函數")
    print("=" * 60)
    
    try:
        # 測試嚴重程度判斷
        test_cases = [
            ('陸上颱風警報', '警報', '危險'),
            ('豪雨特報', '特報', '警告'),
            ('大雨特報', '特報', '注意'),
            ('陸上強風', '特報', '注意'),
            ('低溫特報', '特報', '注意'),
        ]
        
        print("測試嚴重程度判斷:")
        all_passed = True
        for phenomena, significance, expected in test_cases:
            result = get_warning_severity(phenomena, significance)
            status = "✅" if result == expected else "❌"
            print(f"  {status} {phenomena} + {significance} → {result} (預期: {expected})")
            if result != expected:
                all_passed = False
        
        # 測試顏色取得
        print("\n測試顏色取得:")
        severities = ['危險', '警告', '注意', '特報']
        for severity in severities:
            color = get_warning_color(severity)
            print(f"  ✅ {severity}: {color}")
        
        # 測試圖示取得
        print("\n測試圖示取得:")
        phenomena_list = ['颱風', '豪雨', '強風', '低溫', '高溫', '雷雨', '其他']
        for phenomena in phenomena_list:
            icon = get_warning_icon(phenomena)
            print(f"  {icon} {phenomena}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        traceback.print_exc()
        return False


def main():
    """執行所有測試"""
    print("🧪 開始執行天氣警特報功能測試\n")
    
    results = {}
    
    results['警特報 API 連線'] = test_warnings_api()
    results['警特報資料處理'] = test_warnings_processing()
    results['輔助函數'] = test_helper_functions()
    
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
        print("⚠️ 部分測試失敗")
        return 1


if __name__ == '__main__':
    exit(main())
