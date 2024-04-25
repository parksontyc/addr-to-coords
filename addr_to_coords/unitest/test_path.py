import os
import requests
import time
import re
from addr_to_coords.configure import token
# from addr_to_coords.func.all_addr import addresses


def get_coordinates_from_address(address, token):
    url = f'https://tdx.transportdata.tw/api/advanced/V3/Map/GeoCode/Coordinate/Address/{address}?format=JSON'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data)  # 檢查數據結構
        try:
            match = re.search(r'POINT \(([-+]?\d*\.\d+) ([-+]?\d*\.\d+)\)', data[0]['Geometry'])
            if match:
                longitude = float(match.group(1))
                latitude = float(match.group(2))
                print("Longitude:", longitude)
                print("Latitude:", latitude)
                return latitude, longitude
            else:
                print("No match found.")
                return None, None
        except (IndexError, KeyError):
            print("Error parsing the geometry data.")
            return None, None
    else:
        print(f"Failed to fetch coordinates for address: {address}")
        return None, None


# 调用示例
addresses = [ "龍泉五街8號", "基臺中市沙鹿區大同街119之1號1樓"]  # 添加更多地址到這個列表中
token = token  # 替換為你的 Bearer token


requests_per_second = 50
with open('output.csv', 'w', encoding='utf-8') as f:
    f.write('address,lat,lon\n')
    for address in addresses:
        latitude, longitude = get_coordinates_from_address(address, token)
        if latitude is not None and longitude is not None:
            f.write(f'{address},{latitude},{longitude}\n')
            print(f"The coordinates for {address} are: Latitude {latitude}, Longitude {longitude}")
        else:
            f.write(f'{address},,\n')  # 紀錄無法獲取座標的地址
            print("Failed to fetch coordinates.")
        # 控制每秒請求次數
        time.sleep(1 / requests_per_second)


