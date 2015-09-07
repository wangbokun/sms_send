#! /usr/bin/python
#-*- coding: utf-8 -*-

#SaaS config section
SAAS_GLOBAL_CFG = {"config":"saas",
       "app_web_file_path" : "/dinglicom/modules/webapp/",
       "nmgr_http_url":"http://localhost:32020/",
       "jstack_plg_port":"10041",
       "res_jstack_order_log_table":"jstack_msg",
       "res_instance_info_table":"res_instance_info",
       "balance_host":"172.16.40.208:8080",
       "website_url":"dinglicom.com",
       "imgr_main_url" : "http://localhost:31020/"}

MONGO_DB_IP = '172.16.40.149'
COMM_FILE_PATH = '/home/rudy/svnroot/soft/'
ZMQ_ROUTE_IP_PORT='172.16.40.24:32021'
MGT_WEB_IP_PORT='localhost:32030'
NMGR_MASTER_IP='172.16.40.19'
DL_INSTALL_PATH = '/dinglicom/modules'

#log config define
import os
import logging
import logging.config
path = os.path.realpath(__file__)
config_file_path = path.split("/")[:-1]
config_file_path = "/".join(config_file_path)
print config_file_path
logging.config.fileConfig(config_file_path + "/log.conf")


