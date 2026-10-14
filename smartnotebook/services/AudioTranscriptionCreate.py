import requests
import json
import os

API_KEY = os.environ.get("BAIDU_TRANSCRIBE_API_KEY", "")
SECRET_KEY = os.environ.get("BAIDU_TRANSCRIBE_SECRET_KEY", "")

def main(vedio_url):
        
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/create?access_token=" + get_access_token()
    
    payload = json.dumps({
        "speech_url": vedio_url,
        "format": "m4a",
        "pid": 80001,
        "rate": 16000
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response=response.json()
    return response["task_id"]
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    vedio_url="https://basic.beijing.smartedu.cn/fs/feedf2f6-187a-4377-9844-892179ee1685.mp4"
    main(vedio_url)
