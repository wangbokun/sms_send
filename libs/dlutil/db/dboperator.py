# -*- coding: utf-8 -*-

import os, sys
py27k = sys.version_info >= (2,7,0)
_libs_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '../../..'))
print(_libs_file_path)
if py27k:
    sys.path.append(_libs_file_path)
else:
    sys.path.insert(0, _libs_file_path)


from mongooperator import *

#from cassandraoperator import *

from datetime import datetime

def get_now():

    now = str(datetime.today())
    s = now.replace('.','-')
    return s


def get_dao(table):
    ''' 获取表操作对象 '''
    return CommonDAO(table)

if __name__ == '__main__':
    #dao = get_dao("config_item")
    #dao.createDB()
    # dao.update('default-file-00010001',
     # { "target" : {"paths" : "/etc/yum.repos.d/CentOS-Base.repo"},
     # "source" : {"path" : "http://${serv_ip}$:${serv_port}$/staitc_file/CentOS-Base.zip"},
     # "owner" : {"group" : "dlmongo",
                # "user" : "dlmongo",
                # "rights" : "755"},
     # "config" : {},
     # "type" : {"status" : "keep",
                # "write-mode" : "over",
               # "file-type" : "txt"}})

    #d = dao.query(None, True, {"RowKey":{"$regex": u"002"}})
    #dao.remove('"default-file-00010002"', {})
    #d = dao.query('default-file-00010001')
    #print(d)

    # dao2 = get_dao("node_config")
    # dao2.update("cent_client2_172.16.40.146",
                # {"server_ver" : "0.0.1",
                 #"-app-001001":"",
                 #"-app-001002":"",
                 # "-file-001001":""})

    #dao2.remove('cent_client2_172.16.40.146', {})
    #print(dao2.query(key = u'cent_client2_172.16.40.146'))

    #db = CommonDAO("test_config")
    #print db.query(None, True, {"owner.group":"dlmongo"})
    #db = CommonDAO("posts")
    #import datetime
    #post = {"deta":datetime.datetime.utcnow()}
    #d = datetime.datetime.now() - datetime.timedelta(hours=10, minutes=60)
    #print d
    #db.update("8uyui", post)
    #print db.query(None, True,{"dd":{"$gte":d}})

    db = CommonDAO("res_jvm_pool")
    print db.query(None, True,{"node_ip":"172.16.40.203"})
    db = CommonDAO("res_user_res")
    print db.query(None, True, {"jvm":"c5148eab-61ea-4226-8a3e-27cc68b84bae"})
    
    db = CommonDAO("test")
    vm = {"jvm_uuid":"213123123","instance_id":["1111111111"],"count":1}
    db.update("213123123",vm)
    
    vm = {"jvm_uuid":"222222","instance_id":["2222222222"],"count":1}
    db.update("222222",vm)
    vm = {"jvm_uuid":"333333","instance_id":["2222222222","33333333333333"],"count":2}
    db.update("333333",vm)
    
    
    print db.query(None,True, {"instance_id":{"$all":["2222222222"]}})
    
    print db.query(None,True, {"count":{"$lt":2}})
    print db.query(None,True, {})
    
    
    
    db = CommonDAO("flume_log_conf")
    db.update("___flume_server_url",{"server_ip":"172.16.40.323"})
    print db.query("___flume_server_url")
    
    db = CommonDAO("testconf")
    db.update("2222",{"check_list":[{"fefe":"fefe","fefw":"333"}]})
    print db.query('2222')
    
    db = CommonDAO("nodestatus")
    print db.query(None, True, {"nId":{"$in":["172.16.40.207_xen207","172.16.40.203_xen203"]}})
    
    
