import time

import pywifi
import requests
from pywifi import const

#判断wifi是否连接状态
def is_connected(wifi_inter):
    if wifi_inter.status() in [const.IFACE_CONNECTED, const.IFACE_INACTIVE]:
        return True
    else:
        return False

# 设置wifi
def set_profile(name,pwd):
    wifi_profile = pywifi.Profile()                 # 配置文件
    wifi_profile.ssid = name                        # wifi名称
    wifi_profile.auth = const.AUTH_ALG_OPEN         # 需要密码
    wifi_profile.akm.append(const.AKM_TYPE_WPA2PSK) # 加密类型
    wifi_profile.cipher = const.CIPHER_TYPE_CCMP    # 加密单元
    wifi_profile.key = pwd                          # wifi密码
    return wifi_profile                             # 返回wifi配置表

#获取网页数据
def get_webPage():
    url="https://www.baidu.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
    params = {"wd" : "中文"}
    try:
        #设定连接超时2秒
        response = requests.get(url=url, headers=headers ,params=params,timeout=2)
        return True
    except Exception as e:              #抛出异常是因为网络连接时间过长
        print("网页连接超时")
        return False


#连接wifi
def connet_wifi(wifi_inter, wifi_profile):
    #wifi_inter.remove_all_network_profiles()    # 删除其它配置文件
    tmp_profile = wifi_inter.add_network_profile(wifi_profile)  # 加载配置文件
    wifi_inter.connect(tmp_profile)
    time.sleep(2)
    if wifi_inter.status() == const.IFACE_CONNECTED:
        return True
    else:
        return False
