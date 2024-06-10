import hashlib
import base64
from Crypto.Cipher import AES
import random
import string
import struct
import socket
import time

from tools.config import *

def check_signature(token, timestamp, nonce, echostr, msg_signature):
    """
    验证签名
    """
    try:
        sorted_list = [token, timestamp, nonce, echostr]
        sorted_list.sort()
        sha = hashlib.sha1()
        sha.update("".join(sorted_list).encode())
        hashcode = sha.hexdigest()
        return hashcode == msg_signature
    except Exception as e:
        return False

def decrypt_echostr(encoding_aes_key, echostr):
    """
    解密echostr
    """
    aes_key = base64.b64decode(encoding_aes_key + "=")
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_key[:16])
    decrypted = cipher.decrypt(base64.b64decode(echostr))
    pad = decrypted[-1]
    if pad < 1 or pad > 32:
        pad = 0
    decrypted = decrypted[:-pad]
    decrypted = decrypted[16:]  # 去除16位随机字符串
    content_length = int.from_bytes(decrypted[:4], byteorder='big')
    content = decrypted[4: 4 + content_length].decode('utf-8')
    return content

def generate_signature(token, timestamp, nonce, encrypted_msg):
    # 根据企业微信的要求生成消息签名
    try:
        sorted_list = [token, timestamp, nonce, encrypted_msg]
        sorted_list.sort()
        sha = hashlib.sha1()
        sha.update("".join(sorted_list).encode())
        return sha.hexdigest()
    except Exception as e:
        print(e)
        return None
    
    
def get_random_str():
    """生成16位随机字符串"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

# def encode_padding(s):
#     """对需要加密的明文进行填充补位"""
#     block_size = AES.block_size
#     amount_to_pad = block_size - (len(s) % block_size)
#     if amount_to_pad == 0:
#         amount_to_pad = block_size
#     pad = chr(amount_to_pad)
#     return s + pad * amount_to_pad

# def encrypt_message(msg):
#     """
#     加密消息
#     """
#     random_str = get_random_str()
#     msg_length = len(msg.encode('utf-8'))
#     msg = encode_padding(random_str + msg_length.to_bytes(4, byteorder='big').decode('iso-8859-1') + msg + CORPID)
    
#     aes_key = base64.b64decode(ENCODING_AES_KEY + '=')
#     cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
#     encrypted = cipher.encrypt(msg.encode('iso-8859-1'))
    
#     return base64.b64encode(encrypted).decode('utf-8')

def encrypt_message(reply_msg, encoding_aes_key=ENCODING_AES_KEY, receive_id=CORPID):
    """
    加密回复消息
    """
    # 生成16位随机字符串
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    msg_len = len(reply_msg.encode('utf-8'))
    msg_len_bytes = msg_len.to_bytes(4, byteorder='big')
    # 拼接需要加密的字符串
    msg = random_str.encode('utf-8') + msg_len_bytes + reply_msg.encode('utf-8') + receive_id.encode('utf-8')
    # 补位
    pad_len = 32 - len(msg) % 32
    pad = chr(pad_len).encode('utf-8')
    msg += pad * pad_len
    # 加密
    aes_key = base64.b64decode(encoding_aes_key + "=")
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_key[:16])
    encrypted_msg = cipher.encrypt(msg)
    return base64.b64encode(encrypted_msg).decode('utf-8')

