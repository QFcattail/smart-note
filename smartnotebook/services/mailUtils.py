import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup

from core import function

acc = os.environ.get("MAIL_ACCOUNT", "")
pwd = os.environ.get("MAIL_AUTH_CODE", "")
# 发送邮件函数
def send_email(note_current_num,html_contents):
    file_index=1
    file_amount=len(html_contents)
    for html_content in html_contents:
        send_email_item(note_current_num,html_content,file_index,file_amount)
        file_index+=1
def send_email_item(note_current_num,html_content,file_index,file_amount):
    # 发件人邮箱
    sender = acc
    # 发件人邮箱授权码
    password = pwd
    receiver = function.get_email_account()
    subject = function.get_title(note_current_num)+"-"+str(file_index)+"/"+str(file_amount)
    # 创建MIMEMultipart对象，用于存储邮件各个部分
    msg = MIMEMultipart()

    # 设置邮件主题、发件人和收件人
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到所有的img标签
    img_tags = soup.find_all('img')

    # 遍历所有的img标签
    for i, img_tag in enumerate(img_tags):
        # 获取图片的本地路径
        img_path = img_tag['src']

        # 打开图片文件
        with open(img_path, 'rb') as f:
            img_data = f.read()

        # 创建一个MIMEImage对象
        img = MIMEImage(img_data)

        # 添加一个唯一的Content-ID
        content_id = f'<image{i}>'
        img.add_header('Content-ID', content_id)

        # 将图片附件添加到邮件中
        msg.attach(img)

        # 更新HTML中的img标签
        img_tag['src'] = 'cid:' + content_id[1:-1]

    # 更新邮件的HTML正文
    msg.attach(MIMEText(str(soup), 'html', 'utf-8'))

    # 连接到SMTP服务器并发送邮件
    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()
