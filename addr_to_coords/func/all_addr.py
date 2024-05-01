import csv
import os

# file = 'C:/CodeWareHouse/tdx-map-coordinate/tdx_map_coordinate/raw_data/全國5大超商資料集.csv'
# with open(file, encoding="utf-8") as csvFile:  # with open()只在函式內部讀取，離開函式會關檔
#     csvReader = csv.reader(csvFile)
#     datas = list(csvReader)

# print(datas[1][4])

# addresses = []
# # company_info = []
# count = 0
# for i in datas:
#     count += 1
#     if count > 1:
#         addresses.append(i)
#
# print(addresses)
# print(count)
#
# modified_addresses = [address.replace("-", "之") for address in addresses]

# raw_addr = datas[1:]
#
# # 创建新的列表，其中包含修改后的地址和原始的其他数据
# addresses = []
# for row in raw_addr:
#     if len(row) > 4:  # 确保行数据足够长，避免 IndexError
#         new_row = row[:]  # 创建当前行的副本
#         new_row[4] = row[4].replace("-", "之")  # 只修改第五列的地址
#         addresses.append(new_row)
OUTPUT = 'output'
FIXED_ADDRESSES = os.path.join(OUTPUT, 'fixed_addresses_output')
print(FIXED_ADDRESSES)

a = os.path.join(FIXED_ADDRESSES+'.csv')
print(a)