

def find_class_from_path(file_path, deal_func, path=None):
    '''
        载入指定路径下的py文件, 并用dealfunc处理
        dealfunc的传入参数是 ob(对象) 和 package名
    '''
    import os
    local_plug = {}

    list = os.listdir(file_path)
    def getobject(package, imp_list):
            return __import__(package, globals(), locals(),imp_list, -1)

    for el in list:
        if el[-3:] == '.py':
            ob = None
            package_header = el[:-3]
            if path != None:
                package_header = path + '.' + package_header
            try:
                ob = getobject(package_header, ['*'])
                deal_func(ob, package_header)
            except Exception as ex:
                print(ex)
                if ob != None:
                    del ob
                continue

    return local_plug

def create_class_by_name(pkg, name, *oargs):

    class Dynload():
        def __init__(self, package, imp_list):
            self.package=package
            self.imp=imp_list

        def getobject(self):
            return __import__(self.package, globals(), locals(), self.imp, -1)
        def getClassInstance(self,classstr,*args):
            return getattr(self.getobject(),classstr)(*args)
        def execfunc(self,method,*args):
            return getattr(self.getobject(),method)(*args)
        def execMethod(self,instance,method,*args):
            return getattr(instance,method)(*args)
    try:

        ''' import '''
        dyn=Dynload(pkg, name)
        ''' __init__ '''
        task = dyn.getClassInstance(name, *oargs)

    except Exception as e:
        print(e)
        return None


    return task

if __name__ == '__main__':
    day = create_class_by_name("datetime","datetime", 2012,12,12)
    print(day)
