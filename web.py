
import os
import sys
import json

from bottle import Bottle, route, run, template, request, static_file


from twisted.web import server,resource
from twisted.web.wsgi import WSGIResource
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor
from twisted.application import service, strports


STATIC_PATH = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/./static_file/'))
MODULES_PATH = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + "/./modules"))

from config import COMM_FILE_PATH, SAAS_GLOBAL_CFG
SOFT_PATH = COMM_FILE_PATH + "/"



class WebRoot(Bottle):

    def __init__(self):
        Bottle.__init__(self)
        self.init_route()

    def init_route(self):
        self.route('/static_file/<path:path>',callback=self.doStatic)
        self.route('/',callback=self.doRoot)
        self.route('/<name>',callback=self.doRoot)

    def doStatic(self, path=''):
        l = STATIC_PATH
        return static_file(path, root=l)

    def doRoot(self, name='all'):
        
        return 'Hello {0}'.format(name)

def getGlobalCFG():
    '''
        全局配置， 在整个web服务内共享
    '''
    cfg = SAAS_GLOBAL_CFG

    return cfg

def run(port):

    # Create and start a thread pool,
    wsgiThreadPool = ThreadPool()
    wsgiThreadPool.start()

    service_list = []

    b = WebRoot()
    global_cfg = getGlobalCFG()
    global_cfg["local_web_port"] = port
    def loadmodule(ob, packagename):
        '''
            载入扩展模块
        '''
        if hasattr(ob, "get_module_config"):
            config_dict = ob.get_module_config()
            web_define = config_dict.get("webmgt")
            if web_define != None:
                for (url_str,web_cls) in web_define.items():
                    print("loaded web: {0} ".format(url_str))
                    web_obj = web_cls()
                    web_obj.global_cfg = global_cfg
                    b.mount(url_str, web_obj)
            service_define = config_dict.get("service")
            if service_define != None:
                for (key, service_cls) in service_define.items():
                    print("loaded service: {0} ".format(str(service_cls)))
                    service_obj = service_cls()
                    service_obj.global_cfg = global_cfg
                    service_list.append(service_obj)

    ''' 扫描模块存放目录， 加载扩展模块 '''

    dir_list = os.listdir(MODULES_PATH)
    from dlutil import util_classutil as clsutil
    for directory in dir_list:
        path_tmp = "{0}/{1}".format(MODULES_PATH, directory)
        module_pack = MODULES_PATH.split('/')[-1] + "." + directory
        if os.path.isdir(path_tmp) and path_tmp[0:1] != ".":
            pack_name = clsutil.find_class_from_path(path_tmp,
                                                     loadmodule,
                                                     module_pack)



    wsgiAppAsResource = WSGIResource(reactor, wsgiThreadPool, b)
    site = server.Site(wsgiAppAsResource)
    reactor.listenTCP(port, site)
    reactor.run()

def stop():
    reactor.stop()

if __name__ == '__main__':
    run(8999)
