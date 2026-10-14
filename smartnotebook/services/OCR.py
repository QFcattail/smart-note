import requests
import os
import urllib.parse
API_KEY = os.environ.get("BAIDU_OCR_API_KEY", "")
SECRET_KEY = os.environ.get("BAIDU_OCR_SECRET_KEY", "")

def main(payload):
    payload=urllib.parse.quote(payload)    
    payload='image='+payload
    
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token=" + get_access_token()
    

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    response=response.json()
    Output=''
    for word in response ["words_result"]:
      Output+=word["words"]
    return Output
   

  #  ["words_result"][0]["words"]
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


