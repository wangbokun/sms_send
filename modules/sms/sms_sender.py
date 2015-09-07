# -*- coding: UTF-8 -*- 
#  通过数据卡发送短信
#  注意：需要用root权限执行, python 2.6 2.7下运行
#       非root用户，需要将/dev/ttyUSB0的权限修改为777
#
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
import json
import threading


if __name__ == "__main__":
    import sys
    py27k = sys.version_info >= (2,7,0)
    _libs_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '../../../libs/'))
    print _libs_file_path
    if py27k:
        sys.path.append(_libs_file_path)
    else:
        sys.path.insert(0, _libs_file_path)
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
            command = r'echo "{0}" > /sys/bus/usb-serial/drivers/option1/new_id'.format(dev_id)
            print os.popen(command).readlines()
            
        command = r"usb_modeswitch -c /etc/usb_modeswitch.d/12d1\:1505 -v 12d1 -p 1505"
        print os.popen(command).readlines()
        time.sleep(10)
        if check() == False:
            print("not device be loaded")
            exit(999)
        else:
            command = "chmod 777 {0}".format(serial_device)
            print os.popen(command).readlines()

def sigint_handler(signum, frame):
    ser.close()
    print "closing serial port"
    exit()


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


def cut_str_len(src, cut_len):
    return [src[i:i+cut_len] for i in range(0, len(src), cut_len)]

def is_chinese(src):
    def check_chinese(uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'/u4e00' and uchar<=u'/u9fa5':
            return True
        else:
            return False
    for cchar in src:
        if check_chinese(cchar):
            return True
    return False

def send_sms(ser_port, phone_num, content):
    phone = "+86{0}".format(phone_num)
    ctns = []
    if is_chinese(content):
        if len(content) > 60:
            ctns = cut_str_len(content, 60)
        else:
            ctns.append(content)
    else:
        if len(content) > 128:
            ctns = cut_str_len(content, 128)
        else:
            ctns.append(content)
    
    #sending
    results = []
    for ctn in ctns:
        pdu = SmsSubmit(phone, ctn).to_pdu()[0]
        ser_port.write('AT+CMGS=%d\r' % pdu.length)
        print ser_port.readlines() #注意：必须读取，但返回没有ok
        ser_port.write('%s\x1a' % pdu.pdu)
        results.append(read_result(ser_port))

    return results


def init():

    checkUSB()
    ser = serial.Serial(serial_device, 115200, timeout=1)


    order_list = ["AT S7=45 S0=0 L1 V1 X4 &c1 E1 Q0",
              "AT+CSQ",
	      "AT+CNUM",
	      "AT+CMEE=1",
              'AT+CMGF=0']

    #初始化端口
    for order in order_list:
        print out_at_order(ser, order)
    return ser

def main():

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)
    ser = init()
    print send_sms(ser, "18602973632", u"吃饭了没有?")

    #print send_sms(ser, "18602973632", u"吃了")

    #print send_sms(ser, "18602973632", u"吃了再吃点？")

    ser.close()



class SmsSender():

    def __init__(self):
        self.ser = None
        thread_obj = threading.Thread(target=self.send_txt_file, args=())
        thread_obj.daemon = True
        thread_obj.start()
        
    def send_txt_file(self):
        
        in_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/in/'))
        out_file_path = os.path.abspath((os.path.abspath(os.path.dirname(__file__)) + '/out/'))
        
        ser_wait_time = 60

        def get_file():
            in_path = os.listdir(in_file_path)

            in_path = filter(lambda f: f[0:1] != '.', in_path)
            return in_path

        def read_in_file(filename):
            fname = in_file_path +"/"+ filename
            
            try:
                txt_file = open(fname)
                text = txt_file.read().decode('utf-8')
                print text
                info = json.loads(text)
                txt_file.close()
                os.remove(fname)
                return info
            except :
                print "read file error"
                return {}


        def is_valid_phone(phone):
            return phone and len(phone) == 11 and phone[0:1] == "1"

        def get_sender():
            self.ser = init()
            return self.ser

        def ret_sender():
            if None == self.ser:
                return 
            self.ser.close()
            self.ser = None

        def put_out(filename, sms_info):
            fname = out_file_path + "/" +filename
            txt_file = open(fname, 'w')
            t_str = json.dumps(sms_info)
            save_txt = t_str.decode('utf-8')
            txt_file.write(save_txt)
            txt_file.flush()
            txt_file.close()

        def remove_in(filename):
            print "remove",filename
            if filename and filename[0:1] != "." :
                fname = in_file_path + "/" +filename
                if os.path.exists(fname):
                    print "remove", fname       
                    os.remove(fname)
          
        while 1:
            filenames = get_file()
            if filenames != None and len(filenames) > 0:
                sender = get_sender()
                for filename in filenames:
                    if filename == None or filename[0:1] == ".":
                        continue
                    sms = read_in_file(filename)
                    print(">>>>>>>>>>>>>>>",sms)
                    phone = sms.get("phone")
                    phone_list = []
                    if phone and phone.find(",") > 0:
                        #多个号码
                        phone_list = phone.split(",")
                    elif phone:
                        #单个号码
                        phone_list.append(phone)
                    else:
                        #错误号码
                        print "error no"
                        remove_in(filename)
                        if sms == None:
                            sms = {}
                        sms["status"] = "error, phone error"
                        sms["timestamp"] = time.time()
                        put_out(filename, sms)
                        continue


                    content = sms.get("content")
                    
                    
                    for p_num in phone_list:
                        p_num = p_num.strip()
                        if is_valid_phone(p_num):
                            
                            send_sms(sender, p_num, content)
                            
                        else:
                            sms["error"] = "phone number error:{0}".format(p_num)
                            
                    sms["status"] = "sended"
                    remove_in(filename)
                    sms["timestamp"] = time.time()
                    put_out(filename, sms)
                    
                    
            ret_sender()
            time.sleep(3)

if __name__ == "__main__":

    main()

