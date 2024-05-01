import re
import csv
import pandas as pd
import cn2an


# 全形轉半形
# 此處使用 : https://www.jianshu.com/p/a5d96457c4a4
# note：ss = []是包在def中，每重新啟動一次strQ2B時ss = []會被清空；rstring = ''也是同理
def strQ2B(ustring):
    ss = []
    for s in str(ustring):
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)  # 取得字串unicode編號
            if inside_code == 12288:  # 全形空格
                inside_code = 32  # 半形空格
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字串的unicode編碼範圍
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)  # 把清單的單一字符合併成完整字串


# 處理地址資料中應該是中文但是是數字的錯誤格式(數字轉中文)。支援至兩位數
# 在處理地址的過程中，數字轉中文數字多數會出現在"段"前，基本上兩位數是可以覆蓋多數情況，但如果是在"巷"、"弄"前的中文數字就有可能會到三位
# 改寫為可以處理到三位數以上
def num_to_ch(target_num):
    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ch = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if len(target_num) == 1:
        # 傳入的tar_num如果僅有一個時，則先傳入num.index找出位置，再傳入ch列表找出對應值
        # 用字典改寫
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


# 中文數字轉阿拉伯數字
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


# 拆分多個地址
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


# 修正後地址合併至原始資料中
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
    file_name = 'C:/CodeWareHouse/addr-to-coords/addr_to_coords/output/fixed_addr/fixed_addr_output.csv'
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")

    return raw_datas


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


fixed_address_list = split_address(fixed_addresses)
add_fixed_addresses(raw_datas, fixed_address_list)
addresses = raw_datas
