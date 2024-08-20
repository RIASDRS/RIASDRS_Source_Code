import math
import requests
import json
import folium
import os
import webbrowser
# 设置常量
pi = 3.141592653589793234  # π
r_pi = pi * 3000.0 / 180.0
la = 6378245.0  # 长半轴
ob = 0.00669342162296594323  # 扁率
ak='ijcTOFeNWi1YhtRbvSXPlXmQ34CC6UQt'#服务器ak
#ak='jFb9ExerFkGxSa6kLxiwS8hLWmiibVaR'#浏览器ak

tiles="http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}"#高德




      
#使用百度地图API
def getUrl(*address):

    if len(address) < 1:
        return None
    else:
        for add in address:   
            url = 'http://api.map.baidu.com/geocoding/v3/?address={inputAddress}&output=json&ak={myAk}'.format(inputAddress=add,myAk=ak)   
            yield url
            
#格式为BD_09
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

#百度转高德
# bd09 -> gcj02
# lng为bd09的经度
# lat为bd09的纬度
# 返回值为转换后坐标的列表形式，[经度, 纬度]
def bd09_gcj02(lon_bd09, lat_bd09):
    m = lon_bd09 - 0.0065
    n = lat_bd09 - 0.006
    c = math.sqrt(m * m + n * n) - 0.00002 * math.sin(n * r_pi)
    o = math.atan2(n, m) - 0.000003 * math.cos(m * r_pi)
    lon_gcj02 = c * math.cos(o)
    lat_gcj02 = c * math.sin(o)
    return [lon_gcj02, lat_gcj02]


def bdToGaoDe(lon,lat):
    """
    百度坐标转高德坐标
    :param lon:
    :param lat:
    :return:
    """
    PI = 3.14159265358979324 * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PI)
    lon = z * math.cos(theta)
    lat = z * math.sin(theta)
    return lon,lat

def draw_gps(locations, output_path, file_name):
    """
    绘制gps轨迹图
    :param locations: list, 需要绘制轨迹的经纬度信息，格式为[[lat1, lon1], [lat2, lon2], ...]
    :param output_path: str, 轨迹图保存路径
    :param file_name: str, 轨迹图保存文件名
    :return: None
    """
    m = folium.Map(locations[0],
                   zoom_start=15,
                   tiles=tiles,
                   attr='default')  #中心区域的确定

    folium.PolyLine(    # polyline方法为将坐标用线段形式连接起来
        locations,    # 将坐标点连接起来
        weight=3,  # 线的大小为3
        color='blue',  # 线的颜色为橙色
        opacity=0.8    # 线的透明度
    ).add_to(m)    # 将这条线添加到刚才的区域m内
    
    # 起始点，结束点
    folium.Marker(locations[0], popup='<b>Starting Point</b>').add_to(m)
    folium.Marker(locations[-1], popup='<b>End Point</b>').add_to(m)
    
    m.save(os.path.join(output_path, file_name))  # 将结果以HTML形式保存到指定路径





            

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

if __name__ == "__main__":
    locations=[]
    address = ['东北育才浑南']
    for add in address:
        add_url = list(getUrl(add))[0]
        print(add_url)
        try:
            lat,lng = getPosition(add_url)
            print("{0}|经度:{1}|纬度:{2}.".format(add,lng,lat))
            lng,lat = bd09_gcj02(lng,lat)
            locations.append([lat,lng])
        except Exception as e:
            print(e)


    draw_gps(locations, 'D:\\work_dir\\ax','test.html')

    webbrowser.open("D:\\work_dir\\ax\\test.html")
