import m3axpi
from PIL import Image, ImageDraw, ImageFont
import time
import os
import shutil
import requests
from email.message import EmailMessage
import smtplib
import math
import json
import serial
import pynmea2
import sys, ftd2xx as ftd
import pynmea2


# 设置常量

# 1.设置演示用树莓派的flask的地址和端口号
rsp_host = '192.168.31.47'
rsp_port = 5000

# 2.设置演示地址，在网络畅通的环境下可以获得百度地图的位置信息，经纬度。
# 当室内GPS信号弱时，用于演示
demo_address = ['东北育才浑南']

# 3.设置GPS模块所连接的爱芯派的通信端口号,用命令ls /dev/ttyUSB* 查询
# 例如"/dev/ttyUSB0"
#comm_port = "COM3" #windows 电脑
comm_port = "/dev/ttyUSB0" #爱芯派

# 4.设置发送邮箱和接收邮箱
imap_server = 'imap.163.com'
host, port = "smtp.163.com", 465
username = "15710562973@163.com"#发送和接收都使用此邮箱
password = "MMRRPDIYJRULLIRI"#授权码非邮箱密码
email_receiver ="15710562973@163.com"#接收报警信息的邮箱

email_receiver ="lee_h_q1979@126.com"#接收报警信息的邮箱

send_folder ='./send/'




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

try:
    d = ftd.open(0) 
    usb_info = d.getDeviceInfo()
    uart_info= usb_info.get('description')
    d.setBaudRate(9600)#设置通信波特率
except Exception as e:
    print(e)
    uart_info=b'NO_USB_UART'
   

def demo_position(address):
      
    #ser = serial.Serial(comm_port, 9600 )  
    #gps_lng,gps_lat=gps_get(ser)
    if(uart_info==b'FT232R USB UART'):#USB-UART-GPS连接成功
        gps_time,gps_lng,gps_lat = get_gps_from_usb()      
        print('获取GPS时间%s' %gps_time)
        if (not_in_china(gps_lng, gps_lat)):#经纬度不在中国范围内，说明GPS信号弱无法使用
            print('由于卫星信号弱无法获取GPS经纬度，使用默认位置')
            for add in address:
                add_url = list(getUrl(add))[0]#使用百度地图根据演示位置，计算经纬度，需要外网畅通
                try:
                    lat,lng = getPosition(add_url)
                except Exception as e:
                    print(e)
        else:#经纬度在中国范围内，说明GPS信号正常可以演示使用
            lng,lat=wgs84_bd09(gps_lng,gps_lat)
    else:#USB-UART-GPS连接异常
        print('连接异常,使用默认位置')
        for add in address:
            add_url = list(getUrl(add))[0]#使用百度地图根据演示位置，计算经纬度，需要外网畅通
            try:
                lat,lng = getPosition(add_url)
            except Exception as e:
                print(e)

          
    print("位置 经度:%f,纬度:%f" %(lng,lat))    
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


def get_gps_from_usb():
    st=0
    while(True):
        s = d.read(1)
   
        if(st==0):
            if(s==b'$'):
                st=1
                text=b'$'
            else:
                st=0
        elif(st==1):
            if(s==b'\r'):
                st=2
            else:
                st=1   
                text=text+s
        elif(st==2):
            if(s==b'\n'):
                st=3
            else:
                st=2  
            
        else:
            st=0
            
            text=str(text,encoding = "utf-8")
            gps_time=text.split(',')[1]
            gps_time=str(int(gps_time[0:2])+8)+':'+gps_time[2:4]+':'+gps_time[4:6]
            msg = pynmea2.parse(text)
            gps_lng=msg.longitude
            gps_lat=msg.latitude

            return gps_time,gps_lng,gps_lat
    
   


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


        
        
        
        
        
#开始执行        
#m3axpi.load("/home/config/yolov5s.json")
m3axpi.load("/home/config/yolov5s.json")

shutil.rmtree(send_folder)
os.mkdir(send_folder)
demo_lng,demo_lat=demo_position(demo_address)       
        
       
        
        
lcd_width, lcd_height, lcd_channel = 854, 480, 4

fnt = ImageFont.truetype("/home/res/sans.ttf", 20)
img = Image.new('RGBA', (lcd_width, lcd_height), (0,128,0,200))
ui = ImageDraw.ImageDraw(img)
ui.rectangle((20, 20, lcd_width-20, lcd_height-20), fill=(0,0,0,0), outline=(0,255,0,100), width=20)

sw_logo = Image.open("sw_logo.png")
img.paste(sw_logo, box=(lcd_width-sw_logo.size[0], lcd_height-sw_logo.size[1]), mask=None)

detect_logo = Image.open("detect_logo.png")



while True:
    rgba = img.copy()

    tmp = m3axpi.capture()
    rgb = Image.frombuffer("RGB", (tmp[1], tmp[0]), tmp[3])


    res = m3axpi.forward()
    if 'nObjSize' in res:
        ui = ImageDraw.ImageDraw(rgba)

        for obj in res['mObjects']:
            x, y, w, h = int(obj['bbox'][0]*lcd_width), int(obj['bbox'][1]*lcd_height), int(obj['bbox'][2]*lcd_width), int(obj['bbox'][3]*lcd_height)
            objlabel = str(obj['objname'])
            objprob = float(obj['prob'])
            
            if(objprob>0.6):
                ui.rectangle((x,y,x+w,y+h), fill=(255,0,0,100), outline=(255,0,0,255))
                ui.text((x, y), "%s:%02f" % (obj['objname'], obj['prob']), font=fnt)
                rgba.paste(detect_logo, box=(x+w-detect_logo.size[1], y+h-detect_logo.size[1]), mask=None)
                
                
                

                #获取物种名称
                subject=objlabel
                #获取地点
                demo_lng,demo_lat=demo_position(demo_address)
                
                cam_lng=demo_lng
                cam_lat=demo_lat
                cam_location=str(cam_lng)+','+str(cam_lat)               
                body=cam_location
                #获取时间，用时间作为待发送的文件名
                t=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                t=t.replace(' ','').replace(':','').replace('-','')
                #准备待发送图片
                #picture_path=send_folder+objlabel+t+'.jpg'
                #rgb.save(picture_path)
                #发送邮件
                #send_attachment(username, password, email_receiver, subject, body,picture_path,host, port)
                #os.remove(picture_path)
                print(subject,body,objprob)
                #print('等待5秒，再次检测')
                #time.sleep(5)
            else:
                pass




    m3axpi.display([lcd_height, lcd_width, lcd_channel, rgba.tobytes()])
