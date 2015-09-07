# -*- coding: utf-8 -*- 


import os
import sys
import re
import config as cf

try:
    from pymongo import Connection
except:
    _libs_file_path = os.path.abspath('libs')
    sys.path.append(_libs_file_path)
    from pymongo import Connection


ROWKEY_NAME = "RowKey"
COLS_SPLIT = ','
# Main keyspace name
pyagentKS = 'pyagent'

# Node's column family name
nodeCfgCf = 'nodecfg'
nodeSoftCF = 'nodesoft'
nodeStatusCf = 'nodestatus'

# Job's column family name
jobLogCf = 'joblog'
jobInfoCf = 'jobinfo'
jobStatusCf = 'jobstatus' #key=(wait, run, finish, waitforanalysis, analysised, analysiserror) 
                          #column = {jobid, time}
                          #
WAIT_FOR_ANALYSIS = 'waitforanalysis' # JobAnalysis waiting queue
ANALYSISED = 'analysised'
ANALYSIS_ERROR = 'analysiserror'


serviceNodeCf = 'servicenode' #key = (analysis)
                              #column = {uuid, time}

                              
#install log
installLogCf = 'installjoblog'
installJobCf = 'installjob'
installcommCF = 'installcomlog'
                              
def getConnectString():
    MONGO_DB_IP = [cf.MONGO_DB_IP]
    #print '-'*77, MONGO_DB_IP
    #return ['172.16.40.149']
    return MONGO_DB_IP

# def dealKey(key):
    # if isinstance(key,str):
        # return k

def createConn(connStr):
    return Connection(host=connStr)
    

def CreateCFByDefaultConn(keySpace,cfs,clist=None):
    CreateCF(getConnectString()[0], keySpace, cfs, clist)
    
def CreateCF(connStr, keySpace, cfs, columesTypeList = None):
    conn = Connection(host=connStr)
    db = conn[pyagentKS]
    list = db.collection_names()
    
    conn.disconnect()
    
    
def CreateCompositeCF(connStr, keySpace, cfs, columesTypeList, comparators):
    conn = Connection(host=connStr)
    db = conn[pyagentKS]
    list = db.collection_names()
    
    conn.disconnect()
    
def GetValue(pool, columnFamily, *args, **kwargs):
    table = pool[columnFamily]
    #print(args)
    #print(kwargs)
    p = table.find( *args, **kwargs)
    if p.count() < 1:
        return None
    return p
    
def GetAllValue(pool, cf, *args, **kwargs):
    table = pool[cf]
    #print(args)
    #print(kwargs)
    p = table.find(*args, **kwargs)
    if p.count() < 1:
        return None
    return p
    
def GetValueCount(pool, columnFamily, key, *args, **kwargs):
    table = pool[columnFamily]
    p = table.find(key).count()
    return p
    
def Remove(pool, columnFamily, key, val,*args, **kwargs):
    table = pool[columnFamily]
    d = table.remove(key)
    
def UpdateValue(pool, columnFamily, key, value ):
    table = pool[columnFamily]
    #print(key,value)
    p = table.find_one(key)
    if p == None:
        print("create one")
        k=dict(key, **value)
        table.insert(k)
    else:
        #print("update one")
        post = {"$set":value}
        table.update({"_id":p["_id"]}, post)

def DealMapAndList(value):
    ret = {}
    for key in value.keys():
        val = value.get(key)
        ret[key] = str(val)
    return ret
    
def GetConnectPool(keySpace):
    conn = Connection(getConnectString()[0])
    db = conn[keySpace]
    return db
    
def GetComparatorWithTwo():
    return []

def GetComparatorUTF(count):
    return []

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
        
            
    def query(self, key=None, isAll=False, *args, **kwargs):
        pool = GetConnectPool(pyagentKS)
        tkey = list(args)
        #print("---",tkey)
        #print(kwargs)
        if key != None:
            tkey = tkey + [{ROWKEY_NAME:self.dealKey(key)}]
        #print(tkey)
        res = None
        if isAll:
            res = GetAllValue(pool, self.cf, *tkey, **kwargs)
        else:
            res = GetValue(pool, self.cf, *tkey, **kwargs)
        
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
                elif k != '_id':
                    if isAll:
                        val[k] = v
                    elif k.find(ROWKEY_NAME) == -1:
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
    c = CommonDAO('alert_data')
    c.createDB()
    # print(c.count("uuuu"))
    # c.update("uuuu",{"fff":'23333'})
    # d = c.query("uuuu")
    d = c.query(isAll=True)
    print(d)
    # c.remove("uuuu",{})

    

