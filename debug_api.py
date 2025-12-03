"""
Debug API 回應
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("測試空氣品質 API")
print("=" * 60)

# 測試空氣品質 API
aqi_url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
params = {
    'limit': 10,
    'api_key': '9be7b239-557b-4c10-9775-78cadfc555e9'
}

print(f"URL: {aqi_url}")
print(f"參數: {params}")

try:
    response = requests.get(aqi_url, params=params, timeout=10)
    print(f"\n狀態碼: {response.status_code}")
    print(f"回應頭: {dict(response.headers)}")
    print(f"\n回應內容 (前 500 字元):")
    print(response.text[:500])
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\nJSON 結構:")
            print(f"  類型: {type(data)}")
            print(f"  鍵值: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            if isinstance(data, dict) and 'records' in data:
                records = data['records']
                print(f"  records 長度: {len(records)}")
                if records:
                    print(f"  第一筆資料: {records[0]}")
        except json.JSONDecodeError as e:
            print(f"\nJSON 解析錯誤: {e}")
            
except Exception as e:
    print(f"\n錯誤: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("測試一週預報 API")
print("=" * 60)

# 測試一週預報 API
api_key = os.getenv('CWA_API_KEY')
week_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

params = {
    'Authorization': api_key,
    'locationName': '臺北市',
    'elementName': 'MinT,MaxT,Wx,PoP,CI'
}

print(f"URL: {week_url}")
print(f"API Key: {api_key[:20]}..." if api_key else "None")

try:
    response = requests.get(week_url, params=params, timeout=10)
    print(f"\n狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nJSON 結構:")
        print(f"  成功: {data.get('success')}")
        
        if 'records' in data:
            records = data['records']
            print(f"  records 鍵值: {list(records.keys())}")
            
            # 檢查 Locations 還是 location
            if 'Locations' in records:
                print(f"  使用 'Locations' (大寫)")
                locations = records['Locations']
                print(f"  類型: {type(locations)}")
                
                if isinstance(locations, list):
                    print(f"  長度: {len(locations)}")
                    if locations:
                        print(f"  第一個 location: {list(locations[0].keys())}")
                elif isinstance(locations, dict):
                    print(f"  Locations 是字典，鍵值: {list(locations.keys())}")
                    if 'location' in locations:
                        print(f"  location 長度: {len(locations['location'])}")
                        
            elif 'location' in records:
                print(f"  使用 'location' (小寫)")
                
    else:
        print(f"\n錯誤回應: {response.text[:500]}")
        
except Exception as e:
    print(f"\n錯誤: {e}")
    import traceback
    traceback.print_exc()
