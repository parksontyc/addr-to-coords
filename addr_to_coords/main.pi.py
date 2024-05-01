import time

from addr_to_coords.configure import token
from addr_to_coords.func.get_coordination import get_coordinates_from_address
from addr_to_coords.func.fixed_addresses import addresses


if __name__ == '__main__':
    token = token
    requests_per_second = 50
    with open('C:/CodeWareHouse/addr-to-coords/addr_to_coords/output/get_coords/coords_output.csv', 'w',
              encoding='utf-8') as f:
        f.write('id, company_name, company_subname, raw_address, fixed_address, coords_address, company_statement, '
                'founding_date, change_date, lat, lon\n')
        count = 0
        for address in addresses:
            count += 1
            print(count)
            # print(address)
            coords_address, latitude, longitude = get_coordinates_from_address(address[5], token)
            if latitude is not None and longitude is not None:
                f.write(f'{address[0]}, {address[1]}, {address[3]}, {address[4]}, {address[5]}, {coords_address}, '
                        f'{address[6]}, '
                        f'{address[7]}, {address[8]}, {latitude}, {longitude}\n')
                print(f"The coordinates for {address[5]} to {coords_address} are: Latitude {latitude}, "
                      f"Longitude {longitude}")
            else:
                f.write(f'{address[4]},,\n')  # 紀錄無法獲取座標的地址
                print("Failed to fetch coordinates.")
            # 控制每秒請求次數
            time.sleep(1 / requests_per_second)
