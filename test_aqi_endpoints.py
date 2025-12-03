"""
測試不同的空氣品質 API 端點
"""
import requests

print("測試不同的環保署 API 端點\n")

# 測試端點 1: 無 API key
print("=" * 60)
print("測試 1: 不帶 API key")
print("=" * 60)
try:
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
    params = {'limit': 5, 'format': 'json'}
    response = requests.get(url, params=params, timeout=10)
    print(f"狀態碼: {response.status_code}")
    print(f"回應 (前 200 字元): {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"JSON 類型: {type(data)}")
        if isinstance(data, dict):
            print(f"鍵值: {list(data.keys())}")
except Exception as e:
    print(f"錯誤: {e}")

# 測試端點 2: 舊版 API
print("\n" + "=" * 60)
print("測試 2: 舊版 API")
print("=" * 60)
try:
    url = "https://data.epa.gov.tw/api/v2/aqx_p_432"
    params = {'limit': 5, 'format': 'json'}
    response = requests.get(url, params=params, timeout=10)
    print(f"狀態碼: {response.status_code}")
    print(f"回應 (前 200 字元): {response.text[:200]}")
except Exception as e:
    print(f"錯誤: {e}")

# 測試端點 3: 中央氣象署的觀測資料
print("\n" + "=" * 60)
print("測試 3: 使用中央氣象署觀測資料")
print("=" * 60)
try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    api_key = os.getenv('CWA_API_KEY')
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"
    params = {'Authorization': api_key}
    
    response = requests.get(url, params=params, timeout=10)
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        if 'records' in data:
            print(f"records 鍵值: {list(data['records'].keys())}")
            locations = data['records'].get('Station', [])
            print(f"測站數量: {len(locations)}")
            if locations:
                first = locations[0]
                print(f"第一筆資料鍵值: {list(first.keys())}")
except Exception as e:
    print(f"錯誤: {e}")

# 測試端點 4: 政府開放資料平台
print("\n" + "=" * 60)
print("測試 4: 政府開放資料平台")
print("=" * 60)
try:
    url = "https://data.gov.tw/api/v2/rest/datastore/355000000I-000259"
    params = {'limit': 5}
    response = requests.get(url, params=params, timeout=10)
    print(f"狀態碼: {response.status_code}")
    print(f"回應 (前 500 字元): {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nJSON 類型: {type(data)}")
        if isinstance(data, dict):
            print(f"鍵值: {list(data.keys())}")
            if 'result' in data:
                result = data['result']
                print(f"result 類型: {type(result)}")
                if isinstance(result, dict):
                    print(f"result 鍵值: {list(result.keys())}")
                    if 'records' in result:
                        records = result['records']
                        print(f"records 數量: {len(records)}")
                        if records:
                            print(f"第一筆資料: {records[0]}")
except Exception as e:
    print(f"錯誤: {e}")
