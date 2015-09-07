短信发送服务安装方法

当前服务兼容的发送设备是：
    HUAWEI E369 数据模块
已测试兼容的linux操作系统为：
    RHEL 6.5

在RHEL 6.5上安装设备步骤：
    
    1 启用usb转串口内核支持：
        cd /lib/modules/2.6.32-431.el6.x86_64/kernel/drivers/usb/serial/
        insmod option.ko
        insmod usbserial.ko

    2 下载安装usb-modeswitch：
        yum install kernel-devel libusb-devel libusb1-devel
        wget http://www.draisberghof.de/usb_modeswitch/usb-modeswitch-2.1.0.tar.bz2
        wget http://www.draisberghof.de/usb_modeswitch/usb-modeswitch-data-20140129.tar.bz2
        tar xjvf usb-modeswitch-2.1.0.tar.bz2
        cd usb-modeswitch-2.1.0
        make 
        make install
        cd ..

        tar xjvf usb-modeswitch-data-20140129.tar.bz2
        cd usb-modeswitch-data-20140129
        make 
        make install
        cd usb_modeswitch.d/
        cp * /etc/usb_modeswitch.d/
        cd ..
    
    3 配置usb-modeswitch
        vi /etc/usb_modeswitch.conf
        DefaultVendor= 0x12d1
        DefaultProduct= 0x1505
        TargetVendor= 0x12d1
        TargetProduct= 0x1505
        HuaweiMode=1
        DetachStorageOnly=1


    4 插上usb设备,等待蓝色灯闪烁后，执行：

        usb_modeswitch -c /etc/usb_modeswitch.d/12d1\:1505 -v 12d1 -p 1505

        modprobe option
        echo "12d1 1506" > /sys/bus/usb-serial/drivers/option1/new_id
        sleep 3
        chmod 777 /dev/ttyUSB*


    5 设备安装检查：
        查看是否存在/dev/ttyUSB0设备
    6 软件安装：
        解压安装包，即可使用
    

设备初始化：
    每次计算机重启，或者USB短信卡拔下 再插入后，
    需要用root用户，重新加载设备，执行步骤4


软件启动：
    cd sms
    python sms_main.py



测试命令：

发送

curl -X POST -d 'sms={"phone":"1860297****","content":"中文消息"}' http://172.16.15.26:32040/smsapi/send

查询
curl http://短信服务所在服务器的ip:32040/smsapi/status/dc5111d4-1e0c-41ad-868e-5d8c91770316

检查是否发送也可以通过目录下的文件来查看
sms/modules/sms/in是等待发送的短信文件
sms/modules/sms/out是已经发送短信文件


