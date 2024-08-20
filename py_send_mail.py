import os
from email.message import EmailMessage
import smtplib
import py_get_address

def send_mail(subject):
    res=0,0
    # 创建邮件对象
    username = "15710562973@163.com"#发送和接收都使用此邮箱
    password = "MMRRPDIYJRULLIRI"#授权码非邮箱密码
    email_receiver ="15710562973@163.com"#接收报警信息的邮箱
    host, port = "smtp.163.com", 465
    cam_lon,cam_lag=py_get_address.info_from_gps(0)
    cam_location=str(cam_lon)+','+str(cam_lag)    
    body = cam_location
    file_path='/root/send/send.jpg'
    

    em = EmailMessage()
    em['From'] = username
    em['To'] = email_receiver
    em['Subject'] = str(subject)
    em.set_content(body)

    # 打开附件
    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name
        res=1,1
        
    #获取文件名，否则发送的附件名称是文件路径
    file_name = os.path.basename(file_name)

    # 将附件写入邮件
    em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)


    # 输入stmp的host和port并发送邮件
    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(username, password)
        smtp.send_message(em)
        res=2,2
 
    return res