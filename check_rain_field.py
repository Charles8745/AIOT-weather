"""
檢查降雨機率的確切欄位結構
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('CWA_API_KEY')
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

params = {
    'Authorization': api_key,
    'locationName': '臺北市'
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

# 找到臺北市的資料
locations = data['records']['Locations'][0]['Location']
taipei = None
for loc in locations:
    if loc['LocationName'] == '臺北市':
        taipei = loc
        break

if taipei:
    print("臺北市的 WeatherElement:")
    for element in taipei['WeatherElement']:
        element_name = element['ElementName']
        print(f"\n元素名稱: {element_name}")
        
        if '降' in element_name or 'rain' in element_name.lower() or 'pop' in element_name.lower():
            print("  ⭐ 這可能是降雨機率！")
            time_list = element.get('Time', [])
            if time_list:
                first_time = time_list[0]
                print(f"  第一筆時間資料:")
                print(f"    StartTime: {first_time.get('StartTime')}")
                print(f"    EndTime: {first_time.get('EndTime')}")
                element_values = first_time.get('ElementValue', [])
                print(f"    ElementValue 數量: {len(element_values)}")
                for ev in element_values:
                    print(f"      - {ev}")
