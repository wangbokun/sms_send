#!/usr/local/bin/python
#-*- coding: utf-8  -*-
import sys
import os
import json
import traceback
import logging as log
import uuid
import time


from bottle import Bottle, route, run, template, request, static_file

import sms_sender

'''
curl -X POST -d 'sms={"phone":"232323","content":"fwefefwefw"}' http://localhost:32040/smsapi/send



'''



in_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/in/'))
out_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/out/'))
def dealErrMsg(msg):
    return json.dumps({"status":"error",
                       "error_info":msg })
def dealSucMsg(msg):
    return json.dumps({"status":"ok",
                       "result":msg})
def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt
 
class SmsWeb(Bottle):


    def __init__(self):
        Bottle.__init__(self)
        self.init_route()

    def init_route(self):
        ''' GET 方法一定要配<path:path> '''
        self.route('/', callback=self.get_info)
        self.route('/send', method="POST", callback=self.add_sms)
        self.route('/status/<path:path>', callback=self.get_status)

    def get_status(self, path=""):
        #return waiting sended error
        sms_id = path
        filename = out_file_path +"/" + sms_id
        if os.path.exists(filename) == False:
            filename = in_file_path +"/"+ sms_id
            if os.path.exists(filename) == True:
                return dealSucMsg("waiting")
            else:
                return dealErrMsg("not sms_id {0}".format(sms_id))
        try:
            txt_file = open(filename)
            text = txt_file.read()
            info = json.loads(text)
            txt_file.close()
            return dealSucMsg(info.get("status") + " " + str(timestamp_datetime(info.get("timestamp"))))
        except :
            return dealErrMsg("sms_id {0} open error!".format(sms_id))

    def add_sms(self):
        #sms={"phone":"1860297****","content":"中午吃什么？"}
        #
        sms_str = request.forms.get("sms")
        print "recive:", sms_str
        try:
            sms_json = json.loads(sms_str)

        except:
            return dealErrMsg("sms format not json")
        if None == sms_str or len(sms_str) < 1:
            return dealErrMsg('sms element is not found')
        sms_id = str(uuid.uuid4())
        #保存到in目录中
        filename = in_file_path + "/" +sms_id
        txt_file = open(filename, 'w')
        t_str = sms_str
        save_txt = t_str
        txt_file.write(save_txt)
        txt_file.flush()
        txt_file.close()
        return dealSucMsg(sms_id)


    def get_info(self):
        return "it is working!"
