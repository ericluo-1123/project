'''
Created on 2022年12月11日

@author: Eric
'''
import requests
from METHOD import METHOD


def Notify(message):
    
    path = METHOD.PathJoin(METHOD.PathGetCurrent(), 'LINE.yaml')
    
    if METHOD.IsFileExist(path) == False:
        raise RuntimeError("LINE.yaml Not Exist.") 
              
    log_yaml = METHOD.YamlLoad(path)
    
    token = METHOD.OrderedDict_Get("", log_yaml, "token", "eric")
    # = 'UnWoOchaPDXxogIzmEvx6wNVlA5UN9Stpj7OZrX5bzN'

    # HTTP 標頭參數與資料
    headers = { "Authorization": "Bearer " + token }
    data = { 'message': message }
    
    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify",headers = headers, data = data)
    
    
    
    