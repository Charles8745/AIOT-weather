"""
測試天氣警特報 API
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('CWA_API_KEY')
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-001"

params = {
    'Authorization': api_key
}

print("=" * 60)
print("測試天氣警特報 API")
print("=" * 60)

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        
        # 檢查資料結構
        if 'records' in data:
            records = data['records']
            print(f"\nrecords 鍵值: {list(records.keys())}")
            
            # 檢查警報資料
            if 'record' in records:
                record_list = records['record']
                print(f"警報筆數: {len(record_list)}")
                
                if len(record_list) > 0:
                    print("\n有警報資料！")
                    for idx, record in enumerate(record_list[:3]):  # 只顯示前 3 筆
                        print(f"\n警報 {idx + 1}:")
                        print(f"  鍵值: {list(record.keys())}")
                        print(f"  資料: {json.dumps(record, ensure_ascii=False, indent=2)}")
                else:
                    print("\n目前無警報資料")
                    print("這是正常的，表示目前沒有發布天氣警特報")
            
            # 完整 JSON 結構
            print("\n" + "=" * 60)
            print("完整 JSON 結構 (前 2000 字元):")
            print("=" * 60)
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
    else:
        print(f"錯誤: {response.text}")
        
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
