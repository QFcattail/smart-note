#utf-8
import os
import requests
import json

import aiohttp
import asyncio
from pyee.asyncio import AsyncIOEventEmitter

ee = AsyncIOEventEmitter()
def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
        
    client_id = os.environ.get("BAIDU_WENXIN_API_KEY", "")
    client_secret = os.environ.get("BAIDU_WENXIN_SECRET_KEY", "")
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + client_id + "&client_secret=" + client_secret
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


async def mainreque(prompt):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
         "stream": True
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            async for line in response.content:
                line=line.decode('utf-8')
                line=line[6:]
                try:
                    line=json.loads(line)
                    ee.emit('new_result', line["result"])
                    #print(line["result"])
                except Exception as e :
                    #print("wx error", e)
                    pass

def main(prompt):
    #print("wxfl")
    asyncio.run(mainreque(prompt))
    
if __name__== "__main__":
    def update_answer(new_result):
        print(new_result)
    ee.on('new_result', update_answer)
    
    main("用一句话介绍故宫")

