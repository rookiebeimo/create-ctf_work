import os
import base64

key = os.urandom(48) # 随机生成n个字节的字符串，一个字节是8位
print(key)
key_b = base64.b64encode(key) # base64是一种编码方式
print(key_b)
print(key_b.decode('utf-8'))  # 字节需要解码转换为字符串类型
