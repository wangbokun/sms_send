# -*- coding: UTF-8 -*- 
#  通过数据卡发送短信
#  注意：需要用root权限执行, python 2.6 2.7下运行
#  依赖： usb_modeswitch 
#      http://www.draisberghof.de/usb_modeswitch/usb-modeswitch-2.1.0.tar.bz2
#      http://www.draisberghof.de/usb_modeswitch/usb-modeswitch-data-20140129.tar.bz2
#   
#  已知问题： 1 一次发送不成功，则后面一次会失败，第三次会正常。可能是串口关闭的问题。也可以拔下重插一下。
#
#
import time
import signal
import os

import serial
from messaging.sms import SmsSubmit
from messaging.sms.deliver import SmsDeliver


serial_device = '/dev/ttyUSB0'
dev_id = "12d1 1506"
#检查/dev/ttyUSB0是否存在
def checkUSB():
    def check():
        return os.path.exists(serial_device)
    def check_module():
        return os.path.exists("/sys/bus/usb-serial/drivers/option1/new_id")
    if check() == False:
        #尝试加载设备
	if check_module() == False:
            command = "modprobe option"
            print os.popen(command).readlines()
            command = r'echo "{0} {1}" > /sys/bus/usb-serial/drivers/option1/new_id'.format(dev_id)
            print os.popen(command).readlines()
            
        command = r"usb_modeswitch -c /etc/usb_modeswitch.d/12d1\:1505 -v 12d1 -p 1505"
        print os.popen(command).readlines()
        time.sleep(10)
        if check() == False:
            print("not device be loaded")
            exit(999)
checkUSB()
ser = serial.Serial(serial_device, 115200, timeout=1)

def sigint_handler(signum, frame):
    ser.close()
    print "closing serial port"
    exit()

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

order_list = ["AT S7=45 S0=0 L1 V1 X4 &c1 E1 Q0",
              "AT+CSQ",
	      "AT+CNUM",
	      "AT+CMEE=1",
              'AT+CMGF=0']
def read_result(ser_port, isDebug=False):
    stm = ""
    line = []
    #return ser_port.readlines()
    while True:
        c = ser_port.read()
        stm = stm + c
        if isDebug:
            print c, stm
        if c == "\n":
            line.append(stm)
            if stm == "OK\r\n":
                print("Line: {0}".format(stm))
                break
            stm = ""
    return "".join(line)


def out_at_order(ser_port, order):
    ser_port.write(order)
    ser_port.write("\r")
    stm = ""
    line = []
    #return ser_port.readlines()
    return read_result(ser_port) 

def send_sms(ser_port, phone_num, content):
    phone = "+86{0}".format(phone_num)
    pdu = SmsSubmit(phone, content).to_pdu()[0]

    ser_port.write('AT+CMGS=%d\r' % pdu.length)
    print ser_port.readlines() #注意：必须读取，但返回没有ok
    ser_port.write('%s\x1a' % pdu.pdu)
    return read_result(ser_port)

#初始化端口
for order in order_list:
    print out_at_order(ser, order)

print send_sms(ser, "18602973632", u"吃饭了没有?")

#print send_sms(ser, "18602973632", u"吃了")

#print send_sms(ser, "18602973632", u"吃了再吃点？")

ser.close()

