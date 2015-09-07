# -*- coding: utf-8 -*- 

import sys, os 


from pycassa.system_manager import SystemManager,SIMPLE_STRATEGY, NETWORK_TOPOLOGY_STRATEGY,UTF8_TYPE,ASCII_TYPE
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.types import *


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
                              
def getConnectString():
    return ['172.16.40.147:9160','172.16.40.146:9160']

    
#update column family jobstatus with column_metadata=[{column_name:status, validation_class: UTF8Type, index_type: KEYS}];

def CreateCFByDefaultConn(keySpace,cfs,clist=None):
    CreateCF(getConnectString()[0], keySpace, cfs, clist)
    
def CreateCF(connStr, keySpace, cfs, columesTypeList = None):
    sysmgt = SystemManager(connStr)
    list = sysmgt.list_keyspaces()
    
    if keySpace in list:
        #print('pyagent is existed')
        pass
    else:
        sysmgt.create_keyspace(keySpace, SIMPLE_STRATEGY, {'replication_factor': '3'})
    cfDict = sysmgt.get_keyspace_column_families(keySpace)
    allCF = cfDict.keys()
    
    for i in range(len(cfs)):
        columnFamily = cfs[i]
        #print(columnFamily)
        if columesTypeList != None:
            columes = columesTypeList[i]
        else:
            columes = None
        if columnFamily in allCF:
            #print(columnFamily + ' is existed')
            pass
        else:
            #print(columnFamily + ' is creating')
            sysmgt.create_column_family(keySpace, columnFamily, super=False, 
                comparator_type=UTF8_TYPE,
                key_validation_class=ASCII_TYPE,
                default_validation_class=UTF8_TYPE,
                column_validation_classes=columes,
                gc_grace_seconds=1000)
    sysmgt.close()
    
def CreateCompositeCF(connStr, keySpace, cfs, columesTypeList, comparators):
    sysmgt = SystemManager(connStr)
    list = sysmgt.list_keyspaces()
    
    if keySpace in list:
        #print('pyagent is existed')
        pass
    else:
        sysmgt.create_keyspace(keySpace, SIMPLE_STRATEGY, {'replication_factor': '3'})
    cfDict = sysmgt.get_keyspace_column_families(keySpace)
    allCF = cfDict.keys()
    
    for i in range(len(cfs)):
        columnFamily = cfs[i]
        #print(columnFamily)
        
        if columesTypeList != None:
            columes = columesTypeList[i]
        else:
            columes = None
            
        if comparators != None:
            comparator = comparators[i]
        
        if columnFamily in allCF:
            #print(columnFamily + ' is existed')
            pass
        else:
            
            sysmgt.create_column_family(keySpace, columnFamily, super=False, 
                comparator_type=comparator,
                key_validation_class=ASCII_TYPE,
                default_validation_class=UTF8_TYPE,
                #column_validation_classes=columes,
                gc_grace_seconds=1000)
    sysmgt.close()
    
def GetValue(pool, columnFamily, key, *args, **kwargs):
    d = None
    try:
        col_fam = ColumnFamily(pool, columnFamily)
        d = col_fam.get(key, *args, **kwargs)
    except Exception,e:
        #print('empty column '+key)
        pass
    return d
def GetValueCount(pool, columnFamily, key, *args, **kwargs):
    d = None
    try:
        col_fam = ColumnFamily(pool, columnFamily)
        d = col_fam.get_count(key, *args, **kwargs)
    except Exception,e:
        #print('empty column '+key)
        pass
    return d
    
def Remove(pool, columnFamily, key, val,*args, **kwargs):
    col_fam = ColumnFamily(pool, columnFamily)
    d = col_fam.remove(key, columns=val,*args, **kwargs)
    
    
def UpdateValue(pool, columnFamily, key, value ):
    col_fam = ColumnFamily(pool, columnFamily)
    col_fam.insert(key, value)

def DealMapAndList(value):
    ret = {}
    for key in value.keys():
        val = value.get(key)
        ret[key] = str(val)
    return ret
    
def GetConnectPool(keySpace):
    return ConnectionPool(keySpace, getConnectString())
    
def GetComparatorWithTwo():
    return CompositeType(UTF8Type(), UTF8Type())

def GetComparatorUTF(count):
    l = []
    for i in range(count):
        l.append(UTF8Type())
    return CompositeType(*l)

class CommonDAO():
    cf = None
    def __init__(self,cfName):
        #self.__createDB(pyagentKS, cfName)
        self.cf = cfName
        
    def createDB(self):
        cfs = [self.cf]
        CreateCFByDefaultConn(pyagentKS,cfs)
        
    def createCompositeDB(self, ksName, cfName, count):
        comparator = GetComparatorUTF(count)
        CreateCompositeCF(getConnectString()[0],ksName,cfs,None,[comparator])
        
    def update(self,key,val):
        pool = GetConnectPool(pyagentKS)
        UpdateValue(pool, self.cf, key, val)
        pool.dispose()
    def query(self, key, *args, **kwargs):
        pool = GetConnectPool(pyagentKS)
        res = GetValue(pool, self.cf, key, *args, **kwargs)
        pool.dispose()
        return res
        
    def count(self, key, *args, **kwargs):
        pool = GetConnectPool(pyagentKS)
        res = GetValueCount(pool, self.cf, key, *args, **kwargs)
        pool.dispose()
        return res
    def remove(self, key, val):
        pool = GetConnectPool(pyagentKS)
        res = Remove(pool, self.cf, key, val)
        pool.dispose()
        
        
if __name__ == '__main__':
    ks = 'pyagent'
    testcf = ['testcf_33']
    #nodeCfg = {'ip': '172.16.40.147','hostname':'centos123','user':'cloudil','passwd':'1','desc':u'没有表述'}
    nodeinfo1 = {'software':'apache2','ver':'2.0.1','docbase':'/var/www'}
    nodeinfo2 = {'software':'cassandra','ver':'1.0.12','seeds':'172.16.40.145'}
    cols = [{'software':UTF8_TYPE,'ver':UTF8_TYPE}]
    #CreateCFByDefaultConn(ks,testcf,cols)
    #ip_name:
    #   apache:ver
    #   apache:docbase
    #   cassandra:ver
    #   cassandra:seeds
    #comparator = CompositeType(UTF8Type(), UTF8Type(),UTF8Type())
    #cols = [{"param":comparator}]
    
    #CreateCompositeCF(getConnectString()[0],ks,testcf,None,[comparator])
    
    pool = ConnectionPool(ks, getConnectString())
    #print(pool)
    # key = '172.16.40.145:cent_client1:'+nodeinfo1.get('software')
    # print(key)
    #UpdateValue(pool,testcf[0],'172.16.40.147',{('172.16.40.147','centos123','tomcat','7.0','port'):'8080'})
    #key = '172.16.40.145:cent_client1:'+nodeinfo2.get('software')
    #print(key)
    #UpdateValue(pool,testcf[0],key,nodeinfo2)
    
    #s = GetValue(pool,'testcf','172.16.40.145')
    #print(s)
    # update column family testcf with column_metadata=[{column_name:docbase, validation_class: UTF8Type, index_type: KEYS}]
    
    '''
    CREATE TABLE testcf (
      key ascii,
      software text,
      param text,
      value text,
      PRIMARY KEY (key, software, param)
    ) WITH COMPACT STORAGE AND
      comment='' AND
      caching='KEYS_ONLY' AND
      read_repair_chance=0.100000 AND
      dclocal_read_repair_chance=0.000000 AND
      gc_grace_seconds=1000 AND
      replicate_on_write='true' AND
      compression={'sstable_compression': 'SnappyCompressor'};
    
    
    '''
    #UpdateValue(pool,testcf[0],'172.16.40.147',{('apache','port'):'8080',('apache','docbase'):'/var/www',('cassandra','ver'):'1.2.0'})
    # UpdateValue(pool,testcf[0],'172.16.40.147',{('apache','port'):'8080'})
    # UpdateValue(pool,testcf[0],'172.16.40.145',{('apache','port'):'8080'})
    # UpdateValue(pool,testcf[0],'172.16.40.146',{('apache','port'):'8080'})
    # UpdateValue(pool,testcf[0],'172.16.40.147',{('apache','docbase'):'/var/www'})
    # UpdateValue(pool,testcf[0],'172.16.40.145',{('apache','docbase'):'/var/www'})
    # UpdateValue(pool,testcf[0],'172.16.40.146',{('apache','docbase'):'/var/www'})
    # UpdateValue(pool,testcf[0],'172.16.40.145',{('cassandra','ver'):'1.2.0'})
    # UpdateValue(pool,testcf[0],'172.16.40.146',{('cassandra','ver'):'1.2.0'})
    # UpdateValue(pool,testcf[0],'172.16.40.145',{('cassandra','seeds'):'172.16.40.145,172.16.40.147'})
    # UpdateValue(pool,testcf[0],'172.16.40.146',{('cassandra','seeds'):'172.16.40.145,172.16.40.147'})
    # UpdateValue(pool,testcf[0],'172.16.40.145',{('apache333','zzz'):'empty'})
    # s = GetValue(pool,testcf[0],('172.16.40.145'), column_start = ('apache','ver'), column_finish = ('cassandra',))
    #s = GetValue(pool,'jobstatus',('wait'), column_start = ('GANGLIA_CHECK_20130104133051_1',''), column_finish = ('GANGLIA_CHECK_20130104133051_1',))
    s = GetValue(pool,'nodesoft', ('172.16.40.149_cent_yum'), column_start = ('ganglia',''), column_finish = ('ganglia',))
    
    #s = Remove(pool,'jobstatus',('analysised'),[('GANGLIA_CHECK_20121231175157_1','2013-01-04 09:27:58.996000'),])
    #s = Remove(pool,'jobstatus',('analysised'),None)
    
    print(s)
    pool.dispose()


    

