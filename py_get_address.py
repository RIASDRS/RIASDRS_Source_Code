import math
import ftd2xx as ftd
import pynmea2

from email.message import EmailMessage
import smtplib



pi = 3.141592653589793234  
pi = 3.141592653589793234  
r_pi = pi * 3000.0 / 180.0
la = 6378245.0  # 长半轴
ob = 0.00669342162296594323  # 扁率


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



def open_uart():
    try:
        d = ftd.open(0) 
        d.setBaudRate(9600)#设置通信波特率
        return d
    except Exception as e:
        #print(e)
        return b'NO_USB_UART'


def get_gps_from_usb(d):
    st=0
    gps_lng,gps_lat=0,0
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
   
            msg = pynmea2.parse(text)
            gps_lng=msg.longitude
            gps_lat=msg.latitude
            return gps_lng,gps_lat
    
def info_from_gps(a):
    d=open_uart()
    if(d!=b'NO_USB_UART'): 
        usb_info = d.getDeviceInfo()
        uart_info= usb_info.get('description')
        gps_lon,gps_lag=get_gps_from_usb(d)
        if (not_in_china(gps_lon, gps_lag)):#经纬度不在中国范围内，说明GPS信号弱无法使用
            print('由于卫星信号弱无法获取GPS经纬度，使用默认位置(东北育才学校)')
            #lon,lag = 123.442772,41.715834
            lon,lag = 123.442974,41.767282
        else:#经纬度在中国范围内，说明GPS信号正常可以演示使用
            lon,lag=wgs84_bd09(gps_lon,gps_lag)
        d.close()     
        return lon,lag
        
        
    else:#东北育才学校
        #print('NO_USB_UART')
        #lon,lag = 123.442772,41.715834
        #沈阳科学宫
        lon,lag = 123.442974,41.767282
        return lon,lag
    

