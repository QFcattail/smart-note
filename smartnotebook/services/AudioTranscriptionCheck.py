import requests
import json
import os

API_KEY = os.environ.get("BAIDU_TRANSCRIBE_API_KEY", "")
SECRET_KEY = os.environ.get("BAIDU_TRANSCRIBE_SECRET_KEY", "")
def format_milliseconds(ms):
    # 将毫秒转换为秒
    seconds = ms // 1000
    # 使用divmod函数将秒转换为分钟和秒
    minutes, seconds = divmod(seconds, 60)
    # 返回格式化的字符串
    return "{}分{}秒".format(minutes, seconds)

def main(task_id):
        
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/query?access_token=" + get_access_token()
    
    payload = json.dumps({
        "task_ids": [
            task_id
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response=response.json()
    task_info=response["tasks_info"][0]
    if task_info["task_status"]=="Running":
        return 0
    elif task_info["task_status"]!="Success":
        return "转写失败："+str(task_info.get("task_result",{}).get("err_msg",""))
    else:
        text=""
        for line in task_info["task_result"]["detailed_result"]:
            formatted_time = format_milliseconds(line["begin_time"])
            text+=formatted_time+" "+line["res"][0]+"\n"
        return text
    
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    print(main("656aaa10e097b50001cfde64"))
