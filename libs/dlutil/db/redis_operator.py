#!/usr/local/bin/python
#-*- coding: utf-8  -*-
'''
Created on 2013-03-12

@author: rudy
'''
import redis
import time

def test():
    pool = redis.ConnectionPool(host='172.16.40.149', db=0)
    r = redis.Redis(connection_pool=pool)
    s = r.get('fewf')
    print(s)
    script1 = '''
    local i=0
    local b=0
    local res
    local limit = tonumber(KEYS[1])
    while (i <= limit) do
        res = redis.call('set', i, b)
        i = i+1
        b = b+i
    end
    return {KEYS[1]}'''
    #start = time.time()
    #print r.eval(script, 1, 20000)
    #print time.time() - start

    script2 = '''
    local list=redis.call('keys', '*')
    for x in pairs(list) do
        redis.call('del', x)
    end
    return {1}
    '''
    print r.eval(script2, 0)



class CommonDAO():
    
    cf = None
    def __init__(self,cfName):
        #self.__createDB(pyagentKS, cfName)
        self.cf = cfName
        
    def createDB(self):
        cfs = [self.cf]
        CreateCFByDefaultConn(pyagentKS,cfs)
    def dealKey(self,key):
        tkey = key
        if isinstance(key,str) != True or isinstance(key,unicode)!= True:
            tkey = str(key)
        #print("dealkey",tkey, key)
        return tkey
    def dealMuliCol(self,val):
        dt = {}
        if isinstance(val, dict):
            for (k,v) in val.items():
                if isinstance(k,str) == True or isinstance(k,unicode) == True:
                    dt[k] = v
                else:
                    #print(type(k))
                    ks = COLS_SPLIT.join(k)
                    dt[ks] = v
                    #print("dealCol",ks, v)
        else:
            dt = val
        
        return dt
    def createCompositeDB(self, ksName, cfName, count):
        comparator = GetComparatorUTF(count)
        CreateCompositeCF(getConnectString()[0],ksName,[cfName],None,[comparator])
        
    def update(self,key,val):
        pool = GetConnectPool(pyagentKS)
        tkey = self.dealKey(key)
        tval = self.dealMuliCol(val)
        UpdateValue(pool, self.cf, {ROWKEY_NAME:tkey}, tval)
            
    def query(self, key, *args, **kwargs):
        pool = GetConnectPool(pyagentKS)
        tkey = self.dealKey(key)
        res = GetValue(pool, self.cf, {ROWKEY_NAME:tkey}, *args, **kwargs)
        
        if res == None:
            return None
        #print(res)
        def dealItem(item):
            val = {}
            
            for k,v in item.items():
                if k.find(',') > -1:
                    for i in k.split(','):
                        val[i] = ''
                    val[v] = ''
                elif k.find(ROWKEY_NAME) == -1 and k.find("_id") == -1:
                    val[k] = v
            #print("dealitem",item,val)
            return val
            
        t = [dealItem(i) for i in res]
        if len(t) == 0:
            return None
        return t
        
    def count(self, key, *args, **kwargs):
        pool = GetConnectPool(pyagentKS)
        tkey = self.dealKey(key)
        res = GetValueCount(pool, self.cf, {ROWKEY_NAME:tkey}, *args, **kwargs)
        
        return res
    def remove(self, key, val):
        pool = GetConnectPool(pyagentKS)
        tkey = self.dealKey(key)
        res = Remove(pool, self.cf, {ROWKEY_NAME:tkey}, val)
        
        
        
if __name__ == '__main__':
    c = CommonDAO('testinfo')
    c.createDB()
    print(c.count("uuuu"))
    c.update("uuuu",{"fff":'23333'})
    d = c.query("uuuu")
    print(d)
    c.remove("uuuu",{})

