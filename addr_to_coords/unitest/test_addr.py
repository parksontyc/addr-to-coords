import requests
import json
import pandas as pd
import re
import csv


# 讀取Excel，支援csv及xlsx
# 取出要轉換的地址
def addresses_from_csv(path):
    addresses = []
    try:
        x = pd.read_excel(path)
        address = x['address'].tolist()
    except:
        x = pd.read_csv(path)
        address = x['address'].tolist()
    return address


# 輸出
def storage_excel(original_addresses, fix_addresses):  # , final_addresses
    try:
        print('---------------儲存檔案中--------------')
        storage = pd.DataFrame()  # postcode?
        storage['original_addresses'] = original_addresses
        storage['fix_addresses'] = fix_addresses
        # storage['final_addresses'] = final_addresses
        storage.to_csv('transformed_addr.csv', index=False, )
    except:
        print('於函數storage_excel中異常錯誤，請檢查')


# 全形轉半形，此處使用 : https://www.jianshu.com/p/a5d96457c4a4
def strQ2B(ustring):
    ss = []
    for s in str(ustring):
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)


# 處理地址資料中應該是中文但是是數字的錯誤格式(數字轉中文)。支援至兩位數
def num_to_ch(target_num):
    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ch = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if len(target_num) == 1:
        final = ch[num.index(target_num)]
        return final
    elif len(target_num) == 2:
        if target_num[-1] == '0':
            final = ch[num.index(target_num[0])] + '十'
            return final

        elif target_num[0] == '1':
            final = '十' + ch[num.index(target_num[-1])]
            return final

        elif target_num[-1] != '0':
            final = ch[num.index(target_num[0])] + '十' + ch[num.index(target_num[-1])]
            return final

    else:
        return target_num


# def ch_to_num(target_ch):  # 處理地址資料中應該是數字但是是中文字的錯誤格式(中文轉數字)。支援至三位數
#     ch = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
#     num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
#     if len(target_ch) == 1:
#         final = num[ch.index(target_ch)]
#         return final
#     elif len(target_ch) == 2:
#         if target_ch[0] == '十':
#             final = '1' + num[ch.index(target_ch[-1])]
#             return final
#         else:
#             final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[-1])]
#
#     # elif len(target_ch) == 3:
#     #     if target_ch.find('百') == True or target_ch.find('十') == True:
#     #         final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[-1])]
#     #         return final
#     #     else:
#     #         final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[1])] + num[ch.index(target_ch[2])]
#     #         return final
#
#     elif len(target_ch) == 3:
#         # 檢查是否包含 '百' 或 '十'
#         if '百' in target_ch:
#             # 處理如 '二百三' 的情況
#             if '零' in target_ch:
#                 # 處理如 '二百零三' 的情況
#                 final = num[ch.index(target_ch[0])] + '0' + num[ch.index(target_ch[-1])]
#             else:
#                 # 處理如 '二百三'，沒有 '零' 的情況
#                 final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[-1])] + '0'
#         elif '十' in target_ch:
#             # 處理如 '一十二' 的情況
#             if target_ch[0] == '十':
#                 # 處理 '十二' 這類情況，需要特別在前面加 '1'
#                 final = '1' + num[ch.index(target_ch[-1])]
#             else:
#                 # 處理如 '二十三'
#                 final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[-1])]
#         else:
#             # 如果沒有 '百' 或 '十'，但是長度為3，可能為錯誤輸入或需要特殊處理
#             final = ''.join([num[ch.index(c)] for c in target_ch if c in ch])
#         return final
#
#     elif len(target_ch) == 4:
#         if target_ch[0] == '兩' or target_ch[0] == '二':
#             final = '2' + num[ch.index(target_ch[2])] + '0'
#             return final
#         else:
#             final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[2])] + '0'
#             return final
#     elif len(target_ch) == 5:
#         if target_ch[0] == '兩' or target_ch[0] == '二':
#             final = '2' + num[ch.index(target_ch[2])] + num[ch.index(target_ch[-1])]
#             return final
#         else:
#             final = num[ch.index(target_ch[0])] + num[ch.index(target_ch[2])] + num[ch.index(target_ch[-1])]
#             return final
#     else:
#         return target_ch

def ch_to_num(target_ch):
    # 對應中文數字到阿拉伯數字的映射
    ch = ['０', '一', '二', '三', '四', '五', '六', '七', '八', '九',]
    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ]

    final = ''
    i = 0
    while i < len(target_ch):
        if target_ch[i].isdigit():
            # 直接添加阿拉伯數字
            final += target_ch[i]
        elif target_ch[i] in ch:
            # 添加映射的阿拉伯數字
            final += num[ch.index(target_ch[i])]
        elif target_ch[i] == '十':
            if i == 0 or not target_ch[i - 1] in ch:
                # 如果 '十' 是第一個字符或前一個字符不是中文數字
                if i + 1 < len(target_ch) and target_ch[i + 1] in ch:
                    # 如果 '十' 後面跟著一個中文數字
                    final += '1'
                else:
                    # 如果 '十' 是單獨的
                    final += '10'
            else:
                # 如果 '十' 前面是一個中文數字
                if i + 1 == len(target_ch) or not target_ch[i + 1] in ch:
                    # 如果 '十' 是最後一個字符或後一個字符不是中文數字
                    final += '0'
        elif target_ch[i] == '百':
            final += '00' if i + 1 == len(target_ch) or not target_ch[i + 1] in ch else '0'
        elif target_ch[i] == '千':
            final += '000' if i + 1 == len(target_ch) or not target_ch[i + 1] in ch else '00'
        i += 1

    return final






# 運用正則表達式搜索錯誤格式的地址，並且運用上方轉換工具轉換成正確格式
def deal_address(address, error_code):
    print('---------------修正地址，第', error_code, '回合開始---------------')
    after_deal = []
    for i in address:
        i = strQ2B(i)
        i = i.replace(' ', '')
        i = i.replace("-", "之")
        i = i.replace("－", "之")
        i = i.replace("○", "0")
        i = i.replace(".", "、")

        regex0 = re.compile(r'\d')
        regex0_0 = re.compile(r'[\u4e00-\u9fa5]')
        regex1 = re.compile(r'\d+村')
        regex1_2 = re.compile(r'\d+[\u4E00-\u9FFF]+村')
        regex2 = re.compile(r'\d+里')
        regex2_2 = re.compile(r'\d+[\u4E00-\u9FFF]+里')
        regex3 = re.compile(r'\d+路')
        regex4 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+鄰')
        regex5 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+弄')
        regex6 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+號')
        regex7 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+樓')
        # regex7 = re.compile(r'(?<!地|下)([\u4e00-\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+)樓')

        regex8 = re.compile(r'\d+段')
        regex9 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+、')
        regex10 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+之')
        regex11 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+巷')
        regex12 = re.compile(r'([\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+)(\d+)')
        regex13 = re.compile(r'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+–')
        # regex9 = re.compile(r'([\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+)\d')

        try:
            # address中的前三個字中是否有位一個為中阿拉伯數字而沒有任一中文字，如果有就移除
            if regex0.search(i[0:3]) != None and error_code == 0 and regex0_0.search(i[0:3]) == None:
                print('修正地址 :', i, '| 修正部位:', i[0:3])
                after_deal.append(i.replace(i[0:3], ''))

            # address中的前五個字符中是否有位一字符為阿拉伯數字且沒有位一中文字符，如果有就移除
            elif regex0.search(i[0:5]) != None and error_code == 1 and regex0_0.search(i[0:5]) == None:
                print('修正地址 :', i, '| 修正部位:', i[0:5])
                after_deal.append(i.replace(i[0:5], ''))

            elif regex0_0.search(i[0:5]) != None and error_code == 2 and regex0_0.search(i[0:5]) == None:
                print('修正地址 :', i, '| 修正部位:', i[0:5])
                after_deal.append(i.replace(i[0:5], ''))

            # 檢查addr中是否有村，如果有村字，則處理
            elif regex1.search(i) != None and error_code == 3:
                after_deal.append(re.sub(regex1.search(i).group()[:-1], num_to_ch(regex1.search(i).group()[:-1]), i))
                print('修正地址 :', i, '| 修正部位:', regex1.search(i).group())

            elif regex1_2.search(i) != None and error_code == 4:
                print('修正地址 :', i, '| 修正部位:', re.search('\d', regex1_2.search(i).group()).group())
                after_deal.append(re.sub(re.search('\d', regex1_2.search(i).group()).group(),
                                         num_to_ch(re.search('\d', regex1_2.search(i).group()).group()), i))

            elif regex2.search(i) != None and error_code == 5:
                print('修正地址 :', i, '| 修正部位:', regex2.search(i).group())
                after_deal.append(re.sub(regex2.search(i).group()[:-1], num_to_ch(regex2.search(i).group()[:-1]), i))

            elif regex2_2.search(i) != None and error_code == 6:
                print('修正地址 :', i, '| 修正部位:', re.search('\d', regex2_2.search(i).group()).group())
                after_deal.append(re.sub(re.search('\d', regex2_2.search(i).group()).group(),
                                         num_to_ch(re.search('\d', regex2_2.search(i).group()).group()), i))

            elif regex3.search(i) != None and error_code == 7:
                print('修正地址 :', i, '| 修正部位:', regex3.search(i).group())
                after_deal.append(re.sub(regex3.search(i).group()[:-1], num_to_ch(regex3.search(i).group()[:-1]), i))

            elif regex4.search(i) != None and error_code == 8:
                print('修正地址 :', i, '| 修正部位:', regex4.search(i).group())
                after_deal.append(re.sub(regex4.search(i).group()[:-1], ch_to_num(regex4.search(i).group()[:-1]), i))

            elif regex5.search(i) != None and error_code == 9:
                print('修正地址 :', i, '| 修正部位:', regex5.search(i).group())
                after_deal.append(re.sub(regex5.search(i).group()[:-1], ch_to_num(regex5.search(i).group()[:-1]), i))

            elif regex6.search(i) != None and error_code == 10:
                print('修正地址 :', i, '| 修正部位:', regex6.search(i).group())
                after_deal.append(re.sub(regex6.search(i).group()[:-1], ch_to_num(regex6.search(i).group()[:-1]), i))

            elif regex7.search(i) != None and error_code == 11:
                print('修正地址 :', i, '| 修正部位:', regex7.search(i).group())
                after_deal.append(re.sub(regex7.search(i).group()[:-1], ch_to_num(regex7.search(i).group()[:-1]), i))

            elif regex8.search(i) != None and error_code == 12:
                after_deal.append(re.sub(regex8.search(i).group()[:-1], num_to_ch(regex8.search(i).group()[:-1]), i, 1))

                print('修正地址 :', i, '| 修正部位:', regex8.search(i).group())

            elif regex9.search(i) != None and error_code == 13:
                after_deal.append(re.sub(regex9.search(i).group()[:-1], ch_to_num(regex9.search(i).group()[:-1]), i, 1))

                print('修正地址 :', i, '| 修正部位:', regex9.search(i).group())

            elif regex10.search(i) != None and error_code == 14:
                after_deal.append(re.sub(regex10.search(i).group()[:-1], ch_to_num(regex10.search(i).group()[:-1]), i, 1))

                print('修正地址 :', i, '| 修正部位:', regex10.search(i).group())

            elif regex11.search(i) != None and error_code == 15:
                after_deal.append(re.sub(regex11.search(i).group()[:-1], ch_to_num(regex11.search(i).group()[:-1]), i, 1))

                print('修正地址 :', i, '| 修正部位:', regex11.search(i).group())

            elif regex12.search(i) != None and error_code == 16:
                after_deal.append(re.sub(regex12, ch_to_num(regex12.search(i).group()), i, ))

                print('修正地址 :', i, '| 修正部位:', regex12.search(i).group())

            elif regex13.search(i) != None and error_code == 17:
                after_deal.append(re.sub(regex13.search(i).group()[:-1], ch_to_num(regex13.search(i).group()[:-1]), i, 1))

                print('修正地址 :', i, '| 修正部位:', regex13.search(i).group())

            else:
                after_deal.append(i)
                continue

        except TypeError:
            print('修正地址 :', i, '邏輯有誤，未修正')
            after_deal.append(i)
            continue
    error_code += 1
    return after_deal, error_code


file = 'C:/CodeWareHouse/tdx-map-coordinate/tdx_map_coordinate/raw_data/全國5大超商資料集.csv'
with open(file, encoding="utf-8") as csvFile:  # with open()只在函式內部讀取，離開函式會關檔
    csvReader = csv.reader(csvFile)
    datas = list(csvReader)

raw_datas = datas[1:]

address = []
for row in raw_datas:
    address.append(row[4])

c = 0
error_code = 0
for i in range(0, 18):
    if c == 0:
        fixed_addresses, error_code = deal_address(address, error_code)
        c += 1
    elif c != 0 and error_code != 0:
        fixed_addresses, error_code = deal_address(fixed_addresses, error_code)
        c += 1
    else:
        break

# print(addresses)
# storage_excel(address, fixed_addresses)  # , transformed


# def split_address(address_list):
#     fixed_address_list = []
#     for address in address_list:
#         # 检查地址中是否包含需要分割的模式
#         if '、' in address and re.search(r'\d+之?\d*\w*、', address):  #\d+之?\d*號
#             # 分割保留“之”和“號”的部分
#             parts = re.split(r'(\d+之?\d*\w*、)', address)  # \d+之?\d*號
#             if len(parts) > 2:  # 确保有足够的部分来解包
#                 base_address = parts[0]
#                 numbers_floor = parts[1] + parts[2]
#             else:
#                 # 处理未找到预期模式的情况
#                 fixed_address_list.append({"address1": address})
#                 continue
#
#             # 搜索数字和楼层
#             match = re.search(r'(\d+之?\d*、\d+之?\d*號)(\d+樓)?', numbers_floor)
#             if match:
#                 numbers, floor = match.groups()
#                 floor = floor if floor else ''
#                 individual_numbers = numbers.split('、')
#                 address_dict = {
#                     "address1": f'{base_address}{individual_numbers[0]}號{floor}',
#                     "address2": f'{base_address}{individual_numbers[1]}{floor}'
#                 }
#                 fixed_address_list.append(address_dict)
#             else:
#                 # 处理预期模式未找到的情况
#                 fixed_address_list.append({"address1": address})
#         else:
#             # 地址不需要分割
#             fixed_address_list.append({"address1": address})
#     return fixed_address_list

def split_address(address_list):
    fixed_address_list = []
    for address in address_list:
        # 直接查找第一个“、”之前的地址部分
        match = re.search(r'^([^、]+)', address)
        if match:
            first_part = match.group(1)
            # 检查整个部分中是否包含“号”
            if '號' not in first_part:
                first_part += '號'
            fixed_address_list.append({"address1": first_part})
        else:
            # 如果没有找到“、”，则使用原始地址
            first_part = address
            # 检查整个地址中是否包含“号”
            if '號' not in first_part:
                first_part += '號'
            fixed_address_list.append({"address1": first_part})
    return fixed_address_list

def add_fixed_addresses(raw_datas, fixed_addresses):
    column_names = [
        "公司统一编号", "公司名称", "分公司统一编号", "分公司名称",
        "原分公司地址", "修正后的地址1", "分公司状态", "分公司核准设立日期", "分公司最后核准变更日期"
    ]

    # 检查并处理每行数据，确保添加新地址后的列数匹配
    for index, row in enumerate(raw_datas):
        if index < len(fixed_addresses):
            addresses_to_add = fixed_addresses[index].get("address1", ""), fixed_addresses[index].get("address2", "")
            # 根据原始数据的列数调整插入的位置，确保不会出错
            insert_position = 5 if len(row) > 4 else len(row)
            row.insert(insert_position, addresses_to_add[0])
            if addresses_to_add[1]:
                # 如果第二个地址存在，插入到下一个位置
                row.insert(insert_position + 1, addresses_to_add[1])

        # 如果数据行的列数少于列名数，添加空字符串直到匹配
        while len(row) < len(column_names):
            row.append('')

    # 转换为 DataFrame
    df = pd.DataFrame(raw_datas, columns=column_names)

    # 保存到 CSV 文件
    file_name = 'updated_data5.csv'
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")

    return raw_datas




# def add_fixed_addresses(raw_datas, fixed_addresses):
#     # 確保每行數據都添加新地址
#     for index, row in enumerate(raw_datas):
#         if index < len(fixed_addresses):  # 防止索引超出範圍
#             # 取得要添加的地址列表，並檢查是否有足夠的元素
#             addresses_to_add = fixed_addresses[index].get("address1", ""), fixed_addresses[index].get("address2", "")
#             # 在原始地址（索引4）之後插入修正後的地址
#             row.insert(5, addresses_to_add[0])  # 插入第一個地址
#             if addresses_to_add[1]:  # 只有當第二個地址存在時才插入
#                 row.insert(6, addresses_to_add[1])
#     return raw_datas

# def add_fixed_addresses(raw_datas, fixed_addresses):
#     # 确保每行数据都添加新地址
#     for index, row in enumerate(raw_datas):
#         if index < len(fixed_addresses):  # 防止索引超出范围
#             # 这里处理可能有多个地址的情况
#             addresses_to_add = [fixed_addresses[index].get("address1", ""),
#                                 fixed_addresses[index].get("address2", "")]
#             row.insert(5, addresses_to_add)  # 在原始地址（索引4）之后插入修正后的地址

# def add_fixed_addresses(raw_datas, fixed_addresses):
#     # 确保每行数据都添加新地址
#     for index, row in enumerate(raw_datas):
#         if index < len(fixed_addresses):  # 防止索引超出范围
#             row.insert(5, fixed_addresses[index])  # 在原始地址（索引4）之后插入修正后的地址


# def save_to_csv(raw_datas, file_name='updated_data.csv'):
#     # 根据您的列信息更新列名列表
#     column_names = [
#         "公司统一编号", "公司名称", "分公司统一编号", "分公司名称",
#         "原分公司地址", "修正后的地址", "修正后的地址2", "分公司状态", "分公司核准设立日期", "分公司最后核准变更日期"
#     ]
#     # 将数据转换为 DataFrame
#     df = pd.DataFrame(raw_datas,  columns=column_names)  #,
#     df.to_csv(file_name, index=False)
#     # print(f"Data saved to {file_name}")


# def save_to_csv(raw_datas, file_name='updated_data4.csv'):
#     # 根据您的列信息更新列名列表
#     column_names = [
#         "公司统一编号", "公司名称", "分公司统一编号", "分公司名称",
#         "原分公司地址", "修正后的地址1", "修正后的地址2", "分公司状态", "分公司核准设立日期", "分公司最后核准变更日期"
#     ]
#
#     # 檢查每個子列表的長度，確保其符合列名數量
#     max_columns = len(column_names)
#     for i in range(len(raw_datas)):
#         while len(raw_datas[i]) < max_columns:
#             raw_datas[i].append('')  # 如果數據列數少於列名數量，添加空字符串以匹配
#
#     # 将数据转换为 DataFrame
#     df = pd.DataFrame(raw_datas, columns=column_names)
#
#     # 保存 DataFrame 到 CSV 文件
#     df.to_csv(file_name, index=False)
#
#     # 打印信息确认文件保存
#     print(f"Data saved to {file_name}")


fixed_address_list = split_address(fixed_addresses)
# print(fixed_addresses)
# raw_datas 已经被加载
# fixed_addresses 是修正后的地址列表
add_fixed_addresses(raw_datas, fixed_address_list)

# save_to_csv(a)
# #
addresses = raw_datas
print(addresses)
#
# # print(fixed_addresses)
# print(addresses)

# with open('C:/CodeWareHouse/addr-to-coords/addr_to_coords/unitest/test_addr_output.csv', 'w', encoding='utf-8') as f:
#     # f.write('address, fixed_address\n')
# test = []
# for d in raw_datas:
#     test.append(d[4])
#     for j in addresses:
#         test.append(j)
#
# print(test)




