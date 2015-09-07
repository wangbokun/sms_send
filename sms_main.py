
import os
import sys

py27k = sys.version_info >= (2,7,0)
_libs_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/libs/'))
if py27k:
    sys.path.append(_libs_file_path)
else:
    sys.path.insert(0, _libs_file_path)


import logging

import time

import re
import socket
import SocketServer
import collections

import traceback
import signal
import random

from multiprocessing import Process,Pipe

import web

WEB_PORT = 32040

'''
########### utility class part ###############
'''
global is_stop
def sig_handler (sig, frame):
    """ Hanle ctrl c signal"""
    print "Close "+__file__
    try:
        web.stop()
    except:
        pass

    sys.exit()

'''
############### main method part #########
'''
if __name__=='__main__':

    #scanning ctrl-c
    signal.signal(signal.SIGINT,sig_handler)
    signal.signal(signal.SIGTERM,sig_handler)

    # start Web server
    p2 = Process(target=web.run, args=(WEB_PORT,))
    p2.daemon = True
    p2.start()

    print('service living,  web: ' + str(WEB_PORT))

    while True:
        time.sleep(10)



