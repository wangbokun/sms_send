
import os
import urllib
import urllib2 as ul

def http_request(url, data=None, header=None):
    #ul.socket.setdefaulttimeout(10)
    try:
        param = [url]
        if data != None:
            data = urllib.urlencode(data)
            param.append(data)
        if header != None:
            param.append(header)
            #print(param)
        req = ul.Request(*param)
        r = ul.urlopen(req, timeout=15)
        return r.read()
    except Exception as e:
        return ""


def http_request_json(*args, **kwargs):
    return json.loads(http_request(*args, **kwargs))

def http_down(url, localFileName):
    try:
        sub_dir = "/".join(localFileName.split("/")[:-1])
        os.makedirs(sub_dir)
    except Exception as e:
        print e
    try:
        req = ul.Request(url)
        r = ul.urlopen(req)
        f = open(localFileName, 'wb')
        f.write(r.read())
        f.close()
        return "ok"
    except Exception as e:
        return str(e)





if __name__ == '__main__':
    #http_request('http://www.apache.org')
    #http_request('http://172.16.40.210:9091/rest/jvminfo/listjvm')
    #j = {"aa" : {"34234":"3333"},"e33":['234','23432']}
    #import json
    #data = {"json_value" : json.dumps(j), "username" : "aaa",
    #        "service_id":"123123213",
    #        "config_type":"fefefe"}

    #print http_request('http://localhost:32040/instanceconfig/', data)
    #    print http_down("http://localhost:32030/static_file/plugin/shell.py","/tmp/shell.py")
    print http_down("http://localhost:32040/appapi/down/50e061f8-17e0-4b37-8429-af46b6e7b245", "/tmp/ffff/fff/ee/a.tar.gz")
