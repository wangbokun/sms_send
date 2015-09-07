#!/usr/bin/env python
# -*- encoding=utf-8 -*-


import os
import socket
import sys
import time
from subprocess import Popen, PIPE

DLLIBPATH=os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/../../libs/'))
#print(__file__, DLLIBPATH)
sys.path.append(DLLIBPATH)
     
py3k = sys.version_info >= (3,0,0)



def echo_dict(mydict, first=''):
    '''    输出dict类型数据，以repr()输出，汉字不支持
    keys等宽输出（<17字符宽），value为float时处理 '''
    if not isinstance(mydict, dict):
        return
    _kl=mydict.keys()
    _n=max([len(str(i)) for i in _kl])+2

    _nmin=10
    _nmax=16
    _n = _n if _n > _nmin else _nmin
    _n = _n if _n < _nmax else _nmax
    fmt='    %-{0}r : %r'.format(_n)
    # print(fmt)
    
    delfloat=lambda x: str(x) if isinstance(x, float) else x
    
    #_kl.sort()
    _kl=sorted(_kl)
    _i1 = str(first)
    # if isinstance(first, (int, float)): _i1 = first
    if _i1 in mydict:
        print(fmt % (_i1, delfloat(mydict[_i1])))
    for  i in _kl:
        if i == str(_i1):
            continue
        print(fmt % (i, delfloat(mydict[i])))

def put_dict_to_db(aDict, rowKey='hostname', collectionName='hostinfo'):
    ad = dict(aDict)
    try:
        import mongooperator as DBo
        rk = str(ad['hostname'])
    except Exception as x:
        print(x)
        return
    
    rk = rowKey if str(rowKey) != 'hostname' else rk
    cn=str(collectionName)
    c = DBo.CommonDAO(cn)
    c.createDB()
    c.update(rk,ad)
    _ltime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    
    c.update(rk,{'updatetime':_ltime})


def query_dict_in_db(rowKey, collectionName='hostinfo'):
    try:
        import mongooperator as DBo
        rk = str(rowKey)
    except Exception as x:
        print(x)
        return
    
    cn=str(collectionName)
    c = DBo.CommonDAO(cn)
    c.createDB()
    d = c.query(rk)

    return d[0]
    

def printfgx(*arg):
    _somex = '-'*22
    strarg = ' '
    for i in arg:
        strarg += ('%s ' % str(i))
    if not arg:
        _ltime = time.strftime(" %Y-%m-%d %H:%M:%S ", time.gmtime())
        strarg = _ltime
    print('%s%-16s%s' % (_somex, strarg,  _somex))


def listtostr(a):
    ''' 主要用于将list转换为str，包含空格的项用引号括起来 '''
    if not isinstance(a, list):
        return ''
        
    ret=''
    for i in a:
        if ' ' in i:
            ret += ' %r' % i
        else:
            ret += ' %s' % i
    return ret.strip()


if __name__ == '__main__':
    _test()
    pass
    





