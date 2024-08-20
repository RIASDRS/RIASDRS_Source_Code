import os
import requests
import email
import imaplib
import smtplib
from email.message import EmailMessage
from email.header import decode_header
from datetime import datetime
import time

import math
import requests
import json

import random

import serial
import pynmea2

from flask import Flask,render_template
import datetime

from threading import Thread
from time import sleep, ctime






# 设置常量

# 1.设置演示用树莓派的flask的地址和端口号
rsp_host = '192.168.31.247'
rsp_port = 5000

# 2.设置演示地址，在网络畅通的环境下可以获得百度地图的位置信息，经纬度。
# 当室内GPS信号弱时，用于演示
demo_address = ['东北育才浑南']

# 3.设置GPS模块所连接的爱芯派的通信端口号,用命令ls /dev/ttyUSB* 查询
# 例如"/dev/ttyUSB0"
comm_port = "COM3" #windows 电脑
#comm_port = "/dev/ttyUSB0" #爱芯派

# 4.设置发送邮箱和接收邮箱
imap_server = 'imap.163.com'
host, port = "smtp.163.com", 465
username = "15710562973@163.com"#发送和接收都使用此邮箱
password = "MMRRPDIYJRULLIRI"#授权码非邮箱密码
email_receiver ="15710562973@163.com"#接收报警信息的邮箱


# 5.发送图片的路径,测试用
file_path=r"./1.jpg"
# 6.下载的邮件附件存放文件夹
download_path=r"./alarm"





# flask的index.html存放路径,不用修改
templates_path=r".\templates"
pi = 3.141592653589793234  
r_pi = pi * 3000.0 / 180.0
la = 6378245.0  # 长半轴
ob = 0.00669342162296594323  # 扁率
ak='ijcTOFeNWi1YhtRbvSXPlXmQ34CC6UQt'#服务器ak
"""
ak='jFb9ExerFkGxSa6kLxiwS8hLWmiibVaR'#浏览器ak,百度地图js网页使用,此python不用
"""



app = Flask(__name__)



def demo_position(address):
      ser = serial.Serial(comm_port, 9600 )  
      gps_lng,gps_lat=gps_get(ser)
      print(gps_lng,gps_lat)
      if (not_in_china(gps_lng, gps_lat)):#经纬度不在中国范围内，说明GPS信号弱无法使用
          for add in address:
              add_url = list(getUrl(add))[0]#使用百度地图根据演示位置，计算经纬度，需要外网畅通
              try:
                  lat,lng = getPosition(add_url)
              except Exception as e:
                  print(e)
      else:#经纬度在中国范围内，说明GPS信号正常可以演示使用
          lng,lat=wgs84_bd09(gps_lng,gps_lat)
          
      print("演示位置:%s, 经度:%f,纬度:%f" %(add,lng,lat))    
      return lng,lat
            


"""      
使用百度地图API
"""
def getUrl(*address):

    if len(address) < 1:
        return None
    else:
        for add in address:   
            url = 'http://api.map.baidu.com/geocoding/v3/?address={inputAddress}&output=json&ak={myAk}'.format(inputAddress=add,myAk=ak)   
            yield url
            
"""      
百度地图经纬度
"""
def getPosition(url):
    '''返回经纬度信息'''
    res = requests.get(url)
    json_data = json.loads(res.text)
    
    if json_data['status'] == 0:
        lat = json_data['result']['location']['lat'] #纬度
        lng = json_data['result']['location']['lng'] #经度
    else:
        print("Error output!")
        return json_data['status']
    return lat,lng




def gps_get(ser):
    count = 0
    gps_lng=0
    gps_lat=0
    while(True):
        line = str(str(ser.readline())[2:])  # 将读取到的字节码转化成字符串（去掉前2位的无用字符    ‘
        # 寻找有地理坐标的那一行数据
        if line.startswith('$GNRMC'):
            line = line.replace('\\r\\n\'', '')  #  字符串结尾的无用换行符
            msg = pynmea2.parse(line)
            gps_lng=msg.longitude
            gps_lat=msg.latitude
            count = count + 1
            break
            
        else:
            count = count + 1
        if(count == 100):
            #print("GPS信号弱，无法定位")
            break
    
    return gps_lng,gps_lat
"""
# 经纬度计算功能类
"""
def transformlat(lon, lat):
    r = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(math.fabs(lon))
    r += (20.0 * math.sin(6.0 * lon * pi) + 20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
    r += (20.0 * math.sin(lat * pi) + 40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    r += (160.0 * math.sin(lat / 12.0 * pi) + 320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return r

def transformlng(lon, lat):
    r = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(math.fabs(lon))
    r += (20.0 * math.sin(6.0 * lon * pi) + 20.0 * math.sin(2.0 * lon * pi)) * 2.0 / 3.0
    r += (20.0 * math.sin(lon * pi) + 40.0 * math.sin(lon / 3.0 * pi)) * 2.0 / 3.0
    r += (150.0 * math.sin(lon / 12.0 * pi) + 300.0 * math.sin(lon / 30.0 * pi)) * 2.0 / 3.0
    return r

"""
简单判断坐标点是否在中国
不在的话返回True
在的话返回False
"""
def not_in_china(lon, lat):
    if lon < 70 or lon > 140:
        return True
    if lat < 0 or lat > 55:
        return True
    return False
     


"""
GPS转高德
"""
def wgs84_gcj02(lon_wgs84, lat_wgs84):
    if not_in_china(lon_wgs84, lat_wgs84):  # 判断是否在国内
        return [lon_wgs84, lat_wgs84]
    tlat = transformlat(lon_wgs84 - 105.0, lat_wgs84 - 35.0)
    tlng = transformlng(lon_wgs84 - 105.0, lat_wgs84 - 35.0)
    rlat = lat_wgs84 / 180.0 * pi
    m = math.sin(rlat)
    m = 1 - ob * m * m
    sm = math.sqrt(m)
    tlat = (tlat * 180.0) / ((la * (1 - ob)) / (m * sm) * pi)
    tlng = (tlng * 180.0) / (la / sm * math.cos(rlat) * pi)
    lat_gcj02 = lat_wgs84 + tlat
    lon_gcj02 = lon_wgs84 + tlng
    return [lon_gcj02, lat_gcj02]

"""
高德转百度
"""
def gcj02_bd09(lon_gcj02, lat_gcj02):
    b = math.sqrt(lon_gcj02 * lon_gcj02 + lat_gcj02 * lat_gcj02) + 0.00002 * math.sin(lat_gcj02 * r_pi)
    o = math.atan2(lat_gcj02, lon_gcj02) + 0.000003 * math.cos(lon_gcj02 * r_pi)
    lon_bd09 = b * math.cos(o) + 0.0065
    lat_bd09 = b * math.sin(o) + 0.006
    return [lon_bd09, lat_bd09]

"""
GPS转百度
"""
def wgs84_bd09(lon_wgs84, lat_wgs84):
    tmpList_gcj02 = wgs84_gcj02(lon_wgs84, lat_wgs84)
    return gcj02_bd09(tmpList_gcj02[0], tmpList_gcj02[1])




"""
邮件主题中是一般是可以获取到邮件编码的，但也有获取不准的时候，这时就会报错。这需要做编码兼容性处理。
#decode_data()函数优先采用邮件内容获取的编码，如果解析不成功，就依次用UTF-8，GBK，GB2312编码来解析。
"""
def decode_data(bytes, added_encode=None):
    """
    字节解码
    :param bytes:
    :return:
    """
    def _decode(bytes, encoding):
        try:
            return str(bytes, encoding=encoding)
        except Exception as e:
            return None

    encodes = ['UTF-8', 'GBK', 'GB2312']
    if added_encode:
        encodes = [added_encode] + encodes
    for encoding in encodes:
        str_data = _decode(bytes, encoding)
        if str_data is not None:
            return str_data
    return None

"""
# 解析邮件内容
"""      
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None,decode=True)




      
def send_attachment(username, password, email_receiver, subject, body, file_path,host, port):
    # 创建邮件对象
    em = EmailMessage()
    em['From'] = username
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # 打开附件
    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name
    #获取文件名，否则发送的附件名称是文件路径
    file_name = os.path.basename(file_name)

    # 将附件写入邮件
    em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    # 输入stmp的host和port并发送邮件
    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(username, password)
        smtp.send_message(em)






def open_mailbox(username,password,imap_server):
    #建立接受邮件对象
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, password)

    # 添加缺失的命令
    imaplib.Commands['ID'] = ('AUTH')
    # 上传客户端身份信息
    args = ("name","ax","contact","ax","version","1.0.0","vendor","ax")
    typ, dat = imap._simple_command('ID', '("' + '" "'.join(args) + '")')
    
    #选择收件箱
    status, msgs = imap.select('INBOX')



    resp, mails = imap.search(None, "ALL") 

    mails_list = mails[0].split()
    mails_list = list(reversed(mails_list))#按最新时间倒序

    return imap, mails_list
      

def open_one_mail(imap, mails_list,download_path,num):
      status, data = imap.fetch(num, '(RFC822)')
      msg = email.message_from_bytes(data[0][1])
 
      mail_title = decode_header(msg.get("Subject"))[0][0]#识别到的外来入侵物种
      mail_body = decode_data(get_body(msg))#识别到的外来入侵物种的经纬度坐标
      mail_body=mail_body.replace('\n', '').replace('\r', '')#去掉结尾的\r\n
      mail_datetime = msg.get("date")#识别到的外来入侵物种的时间
      for part in msg.walk():
       
          if part.get_content_maintype() == 'multipart':
              continue
          if part.get('Content-Disposition') is None:
              continue


          filename = part.get_filename()
          if bool(filename):
              #print('Downloading attachment:', filename)
              attach_data = part.get_payload(decode=True)
              #注意：文件用双反斜杠链接
              file_path=download_path + '\\' + filename
              with open(file_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))  # 将附件解码并写入文件

              # 修改邮件的标志位为已读
              #imap.store(num, '+FLAGS', '\\Seen')
              imap.store(num, '+FLAGS', '\\Deleted')
      return mail_title,mail_body,mail_datetime
      #return mail_title,mail_body






def send_mails(name):
      while(True):
          subject='test'
          cam_lng=demo_lng+random.uniform(0, 0.002)
          cam_lat=demo_lat+random.uniform(0, 0.002)
          cam_location=str(cam_lng)+','+str(cam_lat)
          body=cam_location
          send_attachment(username, password, email_receiver, subject, body,file_path,host, port)
          sleep(10)
            
def receive_mails(name):
      while(True):
             imap, mails_list=open_mailbox(username,password,imap_server)
             for num in mails_list:              
                   mail_title,mail_body,mail_datetime=open_one_mail(imap, mails_list,download_path,num)
                   if(len(mail_body.split(','))!=2):
                         break
                   
                   lng = float(mail_body.split(',')[0])
                   lat = float(mail_body.split(',')[1])
                   #将获取的邮件内容，提取出来，并发送至templates文件夹下的index.html中
                   data.append({"lat":lat,"lng":lng,"address":mail_title})
                   print('外来入侵物种事件详细信息:')
                   print('入侵物种种类: %s' %mail_title)
                   print('地点经纬度: %f,%f' %(lng,lat))
                   print('采集时间: %s\n' %mail_datetime)
             imap.expunge()
             imap.close()
             imap.logout()



"""
向页面传递变量
"""
@app.route('/')
def index():
    return render_template("index.html",data=data)



"""
flask的ip地址和端口号
"""
def app_run(name):
    app.run(host=rsp_host,port=rsp_port)



#开始运行

demo_lng,demo_lat=demo_position(demo_address);

#用data保存待发送至templates文件夹下的index.html中的内容
data=[]

t0 = Thread(target=send_mails, args=('send_mails',))
t1 = Thread(target=receive_mails, args=('receive_mails',))
t2 = Thread(target=app_run, args=('app_run',))

t0.start()
t1.start()
t2.start()

t0.join()
t1.join()
t2.join()


#app.run()

