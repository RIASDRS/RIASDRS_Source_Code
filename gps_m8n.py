import serial
import pynmea2
import time
 
def gps_get():
    print("开始测试：")
        
    #创建gps串口的句柄
    ser = serial.Serial("COM3", 9600 )  
 
    print("获取句柄成功，进入循环：")
    count = 0
    while(True):
        #读取一行gps信息
        #line = ser.readline()
        line = str(str(ser.readline())[2:])  # 将读取到的字节码转化成字符串（去掉前2位的无用字符）
        print(line)
            
        # 寻找有地理坐标的那一行数据
        if line.startswith('$GPRMC'):
            print("*********************")
            line = line.replace('\\r\\n\'', '')  #  字符串结尾的无用换行符
            print(line)
            rmc = pynmea2.parse(line)
            print("当前坐标：")
            print("北纬(度分秒)：", float(rmc.lat)/100 , "度")
            print("东经(度分秒)：", float(rmc.lon)/100 , "度")
            print("************")
            print("北纬(十进制)：", rmc.latitude , "度")
            print("东经(十进制)：",  rmc.longitude, "度")
            
            print("***************")
        count = count + 1
        if(count == 100):
            break
 
if __name__ == "__main__":
 
    gps_get()
