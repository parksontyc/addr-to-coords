import requests
import re


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
            coords_address = data[0]['Address']
            if match:
                longitude = float(match.group(1))
                latitude = float(match.group(2))
                print("Longitude:", longitude)
                print("Latitude:", latitude)
                return coords_address, latitude, longitude
            else:
                print("No match found.")
                return None, None, None
        except (IndexError, KeyError):
            print("Error parsing the geometry data.")
            return None, None, None
    else:
        print(f"Failed to fetch coordinates for address: {address}")
        return None, \
            None, None