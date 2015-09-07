#!/usr/local/bin/python
#-*- coding: utf-8  -*-
from pyDes import *

#convert string to hex
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)

    return reduce(lambda x,y:x+y, lst)

#convert hex repr to string
def toStr(s):
    return s and chr(int(s[:2], base=16)) + toStr(s[2:]) or ''

'''必须8个字符'''
default_key = 'dinglico'

def toDES(src):
    if isinstance(src,unicode):
        src = str(src)
    k = des(default_key, ECB, padmode=PAD_PKCS5)
    d = k.encrypt(src)
    new_s = toHex(d)
    return new_s
if __name__ == '__main__':
    s = u"http://www.baidu.com:3232/323/323?wefwe"
    new_s = toDES(s)
    print new_s



