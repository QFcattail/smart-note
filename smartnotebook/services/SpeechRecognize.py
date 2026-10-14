import base64
import urllib
import requests
import json
import os

API_KEY = os.environ.get("BAIDU_ASR_API_KEY", "")
SECRET_KEY = os.environ.get("BAIDU_ASR_SECRET_KEY", "")

def main(FilePath):
        
    url = "https://vop.baidu.com/server_api"
    
    # speech 可以通过 get_file_content_as_base64("C:\fakepath\test.wav",False) 方法获取
    payload = json.dumps({
        "format": "wav",
        "rate": 8000,
        "channel": 1,
        "cuid": "2tOvxmIitXze4NZRv4zymJjv9L77S6Jj",
        "token": get_access_token(),
        "speech":get_file_content_as_base64(FilePath),
        "len": os.path.getsize(FilePath)
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    try:
        return (response.json()["result"][0])
    except:
        return ""
    

def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def get_access_token():
   
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    main("test.wav")
    
    
