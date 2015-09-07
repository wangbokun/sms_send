# -*- encoding=utf-8 -*-

from util_http import http_request

host = "172.16.40.17"  #"localhost"
app_id = "b638183d-81fb-4f7a-93ff-0ec7b2cdc35c"
res_list = "d8ae105b-662d-4c80-b106-a29ff2b4e807" #,937d620f-fea4-4caa-bf4e-4c3ca363a583"
instance_id = "510c09f5-6320-4b32-8229-1009dcf6135b"

#host = 'localhost'
##app_id = "844c9138-9dd0-44e4-8c71-b9cd57d636ff"
#instance_id = "f37f74a0-75f6-4c75-ba6d-c189a0149484"
#res_list = "5f2a01cc-a829-457e-9200-3a6121629085"

def start_inst(runmode):
    url = "http://"+ host +":32040/instance/controlparam/admin/"+instance_id
    data = {"run_mode":runmode,"log_mode":"log_mode"}
    return url, data

def jstack_dp():
    url = "http://"+host+":32020/jstack/deploy/"+instance_id
    data = {'from': 'http://'+host+':32040/appapi/down/'+app_id,
    'order_type': 'app_deploy',
    'node_jstack_plg_port': '10041',
    'order_id': u'app_deploy_db0b85b2-d959-4bb0-982b-d12f9b6fc31b',
    'node_ip': u'172.16.40.164',
    'to': u'/opt/modules/webapp/app.war'}
    return url, data

def create_inst():
    data = {#"instance_id" : "d4efa683-7b35-4d12-ad8d-752d8721d6b8",
            "username":"rudy",
            "instance_type":"app",
            "app_id":app_id,
            "res_amount":"3",
            "res_list":res_list,
            "config_items":"configidx333"}
    url = "http://"+ host +":32040/instance/deploy"
    return url, data
def req_user_res():
    data = None
    url = "http://"+ host +":32040/res/requserres/rudy/jvm/3"
    return url, data


<<<<<<< .mine
#url, data = jstack_dp()
#url, data = start_inst("start")
#url, data = start_inst("stop")
url, data = create_inst()
#url, data = req_user_res()
if data == None:
    print http_request(url)
else:
    print http_request(url, data)
=======
if __name__ == '__main__':
    import sys
    arg=sys.argv[1]

    if arg == '1':
        url, data = req_user_res() 
    #上传应用#
    if arg == '2':
         pass#web : http://ip:32040/appapi/uploadpage
>>>>>>> .r3867

    if arg == '3':
        url, data = create_inst()

    if arg == '4':
        url, data = start_inst("start")

    if arg == '5':
        url, data = start_inst("stop")

    if data == None:
        print http_request(url)
    else:
        print http_request(url, data)








