#!/usr/bin/env python
#coding=utf-8

import os
import socket
import sys
import time
from subprocess import Popen, PIPE

#DLLIBPATH=os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/../../../libs/'))
#print(__file__, DLLIBPATH)
#sys.path.append(DLLIBPATH)

from outpututil import echo_dict, put_dict_to_db, query_dict_in_db, printfgx

py3k = sys.version_info >= (3,0,0)


def get_dict(mydict):
    pass

   
    

class HostInfo():
    ''' 获取与主机相关的软硬件信息 '''
    def __init__(self):
        self._ginfo = {}
        #self.get_err = ''


    def get_hostname(self):
        ''' 主机名 '''
        import socket
        _tmp = socket.gethostname()
        _ret = {'hostname':_tmp}
        self._ginfo.update(_ret)
        return _ret

    def run(self):
        _tmp=dir(self)
        #print(_tmp)
        for i in _tmp:
            j = getattr(self,i)
            # 希望判断是否为方法#
            # print type(j), '====', i, j.__class__
            if not i.startswith('get_'):
                continue
            try:
                j()
            except Exception as x:
                print('call %-10r: %r' % (i, x))
                pass

    def __str__(self):
        return str(self._ginfo)
        
    __repr__ = __str__
    
    def ret_me(self):
        return self._ginfo

    def put_all(self, first='hostname'):
        echo_dict(self._ginfo, first)
        
    def update_to_db(self):
        self.run()
        _myrk=self.row_key_for_db()
        put_dict_to_db(self._ginfo, _myrk)
        
    def row_key_for_db(self):
        _tmp=self.get_hostname()
        _ret=_tmp['hostname']
        try:
            _tmp=self.get_ifconfig()
            _ret += '_' + _tmp['NET iplist'][0]
        except Exception as x:
            print(x)
            pass
        # print(_ret)
        return _ret #['hostname']
        
    def check_from_db(self):
        _myrk=self.row_key_for_db()
        tmpdict = query_dict_in_db(_myrk)
        echo_dict(tmpdict)

    def get_uname(self):
        ''' 获取与os、内核版本、发行版、硬件相关的信息，只适用于*nix '''
        try:
            _tmps=os.uname()
        except Exception as x:
            print(x)
            return

        # print(_tmps, type(_tmps))
        _ret = {'sysname':_tmps[0], 'release':_tmps[2],\
            'version':_tmps[3], 'machine':_tmps[4]}
        self._ginfo.update(_ret)
        return _ret
        

    def get_mem(self):
        ''' 获取与内存相关的信息，只适用于*nix '''
        try:
            f = open("/proc/meminfo")
        except Exception as x:
            print(x)
            return
        lines = f.readlines()
        f.close()
        mem = {}
        for line in lines:
            if len(line) < 2: continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = int(var) * 1024.0
            
        mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
        _ret ={ 'MEM MemUsed':round(mem['MemUsed'] / 1024.0 /1024.0, 2),\
            'MEM MemTotal':round(mem['MemTotal']/ 1024.0 /1024.0, 2),\
            'MEM MemFree':round(mem['MemFree'] / 1024.0 /1024.0, 2),\
            'MEM Buffers':round(mem['Buffers'] / 1024.0 /1024.0, 2),\
            'MEM Cached':round(mem['Cached']  / 1024.0 /1024.0, 2)}

        self._ginfo.update(_ret)
        return _ret

    def get_user(self):
        ''' 获取与用户名相关的信息，只适用于*nix '''
        try:
            f = open("/etc/passwd")
        except Exception as x:
            print(x)
            return
        lines = f.readlines()
        f.close()
        _tmp=[]
        for line in lines:
            i = line.split(':')
            if ( 500 <= int(i[2]) < 65534)  and ( i[1] == 'x') :
                _tmp.append(i[0])
        _ret={'users':_tmp}
        self._ginfo.update(_ret)
        return _ret

    def get_cpu(self):
        ''' 获取与用户名相关的信息，只适用于*nix '''
        try:
            f = open("/proc/cpuinfo")
        except Exception as x:
            print(x)
            return
        _cpu_keys=['cpu cores','model name','cpu MHz']
        _ret={}
        for line in f:
            j = line.split(':')
            i = j[0].strip()
            if i in _cpu_keys :
                #_cpu_keys.pop(i)
                _ret['CPU '+i]=j[1].strip()
            #_cpu_keys.
        self._ginfo.update(_ret)
        f.close()
        return _ret

    def get_ifconfig(self):
        try:
            p1 = Popen(["/sbin/ifconfig"], stdout=PIPE)
        except Exception as x:
            print(x)
            return
        output = p1.communicate()[0]
        p1.stdout.close()
        #print(output)
        wordone=lambda x: x.split()[0]
        
        _ret={}
        _iplist=[]
        if py3k:
            output = str( output, encoding='utf8' )
        for i in output.split('\n'):
            if len(i) == 0:
                continue
            if not i.startswith(' '): 
                ifname=i.split()[0]
                if ifname=='lo':
                    ifname = ''
                    continue
                _ret['NET '+ifname] = {'hwaddress':i.split()[-1]}

            if len(ifname) == 0:
                continue
            j=i.strip()
            if j.startswith('inet '):
                _tmp={'ipaddress':wordone(j.split(':')[1]), \
                    'broadcast':wordone(j.split(':')[3])}
                _ret['NET '+ifname].update(_tmp)
                _iplist.append(_tmp['ipaddress'])
                ifname = ''
                
        if _iplist:
            _ret.update({'NET iplist':_iplist})
        self._ginfo.update(_ret)
        return _ret


    def get_diskinfo(self):
        try:
            p1 = Popen(["df", '-Th'], stdout=PIPE, stderr=PIPE)
        except Exception as x:
            print(x)
            return
        output = p1.communicate()[0]
        p1.stdout.close()
        p1.stderr.close()
        
        _ret={}
        strcache=''
        if py3k:
            output = str( output, encoding='utf8' )
        lines=output.split('\n')
        lines.pop(0)
        for i in lines:
            
            if len(i.split()) <= 1:
                strcache=i
                continue
            if len(strcache)>1:
                i="%s %s" % (strcache,i)
                strcache=''
            j=i.split()
            if j[1] in ('tmpfs', 'iso9660', 'devtmpfs'):
                continue
            _ret['DISK '+j[0]] = {'Type':j[1], 'Size':j[2], \
                    'Used':j[3], 'Avail':j[4], 'Use%':j[5], 'MountAt':j[6] }
            
        self._ginfo.update(_ret)     
        return _ret
        
    def get_python_version(self):
        self._ginfo['Python ver']=str(sys.version_info)
    
    def get_uptime(self):
        _tmp = {}
        f = open("/proc/uptime")
        con = f.read().split()
        f.close()
        all_sec = float(con[0])
        MINUTE,HOUR,DAY = 60,3600,86400
        _tmp['day'] = int(all_sec / DAY )
        _tmp['hour'] = int((all_sec % DAY) / HOUR)
        _tmp['minute'] = int((all_sec % HOUR) / MINUTE)
        _tmp['second'] = int(all_sec % MINUTE)
        _tmp['Free rate'] = round(float(con[1]) / float(con[0]), 3)
        _tmp['all second'] = int(all_sec)
        
        def d2ymd(nDay):
            year,month = 365,30
            nYear,nDay = divmod(nDay,year)
            strYear = (str(nYear)+' years ') if nYear else ''
            nMonth,nDay = divmod(nDay,month)
            strMonth = (str(nMonth)+' months ') if nMonth else ''
            strDay = (str(nDay)+' days') if nDay else ''
            return ("%s%s%s" % (strYear,strMonth,strDay))
        
        strDay = '{0} days({1}) '.format(_tmp['day'],d2ymd(_tmp['day']))
        strDay = strDay if _tmp['day'] else ""
        strUptime="{0}{1} hours {2} minutes {3} seconds".format(\
                    strDay, _tmp['hour'],_tmp['minute'],_tmp['second'])
        
        _ret = {}
        _ret['uptime dict'] = _tmp
        _ret['uptime str'] =  strUptime
        self._ginfo.update(_ret)     
        return _ret
def _test():
    ''' 此处展示如何使用本类 '''
    printfgx('%s._test() start' % __file__)
    hi=HostInfo()
    # 执行run()来获取当前主机的一些信息，存到一个dict中 
    hi.run()
    # 以较为易读的方式输出这个dict 
    hi.put_all()    
    # 将这个dict的内容存入db中，以下两个方法目前对python3支持不是太好
    hi.update_to_db()
    # 从db中读取存入的dict，并以易读的方式输出到终端
    hi.check_from_db()
    printfgx('%s._test() stop ' % __file__)
    
if __name__ == '__main__':
    _test()
    
   
    MAP_TEST  =   {
        'a' : 'aa' ,
        'c' : '123' ,
        'b' : 324.8 ,
        123 : 323 ,
        'daaaaaaaaaaa' : ["172.16.40.109","172.16.40.177"] ,
        423.4 : 3223873 ,
        'e' : {'eth0':"172.16.40.109",'eth0:0':"172.16.40.177"} ,
    }
    #echo_dict(MAP_TEST, 423.4)

    #echo_dict(memory_stat())

    hi=HostInfo()
    hi.get_xx=""
    hi.run()
    hi.put_all()
    printfgx()
    
    #echo_dict(hi.get_mem(),'MemTotal')
    #echo_dict( hi.get_diskinfo())
    printfgx()
    hi.update_to_db()
    printfgx()
    hi.check_from_db()
    

#### NameError("global name 'long' is not defined",)
#### TypeError("Type str doesn't support the buffer API",)
#### except Exception, x: ^ SyntaxError: invalid syntax
#### 'dict_keys' object has no attribute 'sort'
