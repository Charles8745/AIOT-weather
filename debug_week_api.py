"""
詳細檢查一週預報 API 結構
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
    'locationName': '臺北市',
    'elementName': 'MinT,MaxT,Wx,PoP,CI'
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

print("完整 JSON 結構:")
print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])

print("\n" + "=" * 60)
print("records 結構:")
records = data['records']
print(f"records 類型: {type(records)}")
print(f"records 鍵值: {list(records.keys())}")

print("\n" + "=" * 60)
print("Locations 結構:")
locations_list = records['Locations']
print(f"Locations 類型: {type(locations_list)}")
print(f"Locations 長度: {len(locations_list)}")

print("\n" + "=" * 60)
print("第一個 Locations 元素:")
first_locations = locations_list[0]
print(f"類型: {type(first_locations)}")
print(f"鍵值: {list(first_locations.keys())}")

print("\n" + "=" * 60)
print("Location 列表:")
location_list = first_locations['Location']
print(f"類型: {type(location_list)}")
print(f"長度: {len(location_list)}")

print("\n" + "=" * 60)
print("第一個 Location:")
first_location = location_list[0]
print(f"LocationName: {first_location.get('LocationName')}")
print(f"locationName: {first_location.get('locationName')}")
print(f"鍵值: {list(first_location.keys())}")

print("\n" + "=" * 60)
print("WeatherElement:")
weather_elements = first_location.get('WeatherElement', [])
print(f"元素數量: {len(weather_elements)}")

for element in weather_elements[:2]:
    print(f"\n元素名稱: {element.get('ElementName')}")
    print(f"  elementName: {element.get('elementName')}")
    time_list = element.get('Time', [])
    print(f"  時間筆數: {len(time_list)}")
    if time_list:
        first_time = time_list[0]
        print(f"  第一筆時間: {first_time.get('StartTime')} ~ {first_time.get('EndTime')}")
        print(f"  startTime: {first_time.get('startTime')}")
        print(f"  Parameter: {first_time.get('Parameter')}")
        print(f"  parameter: {first_time.get('parameter')}")
