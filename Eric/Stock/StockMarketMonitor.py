'''
Created on 2022年12月20日

@author: Eric
'''

from threading import Timer
import traceback
from win32api import Sleep
import threading
import time
from MYSQL80 import MYSQL80
from TWSE import TWSE
from METHOD import METHOD
from LOGGER import LOGGER

def OnTest(data):
    Sleep(1000)
    return ""

def OnStart(code, odict):

    try:
        TWSE.InstantStockPrice(code, odict)
        OnTimer(code, odict)    
    except:
        raise 
    
def OnTimer(code, odict):
    
    try:
        stock = Timer(1.0, OnStart, args=(code, odict, ))
        stock.start()
    except:
        raise 

def aa():
    lock.acquire()         # 鎖定
    i = 0
    while i<5:
        i = i + 1
        time.sleep(0.5)
        print('A:', i)
        if i==2:
            lock.release()  # i 等於 2 時解除鎖定

def bb():
    lock.acquire()          # 鎖定
    i = 0
    while i<50:
        i = i + 10
        time.sleep(0.5)
        print('B:', i)
    lock.release()
    
def Run(code):
    print(1)
    
if __name__ == '__main__':
    pass
          
    try:
              

        syntax = []
        db = MYSQL80.GetConnector({
            "host": 'localhost',
            "port": 3306,
            "database": 'sys',
            "user": 'root',
            "password": '1234',
            "charset": 'utf8',
            "use_unicode": True,
            "get_warnings": True,
        })
        
        config = TWSE.GetConfig(db)
        
        db.close()

            
        code = 1
        df = TWSE.DailyClosingQuotes('{}'.format(METHOD.TimeGet('%Y%m%d')))
        TWSE.CreateField(df)

        print(df)
        lock = threading.Lock()         # 建立 Lock
        
        a = threading.Thread(target=aa, args=(code))
        b = threading.Thread(target=bb)
        
        a.start()
        b.start()
        
        # yaml = METHOD.GetYaml(METHOD.PathJoin(METHOD.PathGetCurrent(), 'StockMarketMonitor.yaml'), "big5")  
        # table = METHOD.OrderedDict_Get("", yaml, "table").split(",")
        # if len(table) == 0:
        #     raise RuntimeError("table is empty.")
        #
        # executor = ThreadPoolExecutor()         # 建立非同步的多執行緒的啟動器
        # with ThreadPoolExecutor(max_workers=5) as executor:
        #
        #     future_all = {executor.submit(OnTest, code) for code in table}
        #
        #         # data = OrderedDict()
        #         # METHOD.OrderedDict_Set(code, data, "股票代碼")
        #         # METHOD.OrderedDict_Set(METHOD.OrderedDict_Get("", yaml, "{}".format(code), "停損點"), data, "停損點")
        #         # METHOD.OrderedDict_Set(METHOD.OrderedDict_Get("", yaml, "{}".format(code), "停利點"), data, "停利點")
        #
        #
        #         # sleep(1)
        #     for future in concurrent.futures.as_completed(future_all):
        #         # data = future_all[future]
        #         try:
        #             result = future.result()
        #         except:
        #             raise
        #         finally:
        #             print(result)
        #
        #     future_all = {executor.submit(OnTimer, code, yaml) for code in table}
        #
        #         # data = OrderedDict()
        #         # METHOD.OrderedDict_Set(code, data, "股票代碼")
        #         # METHOD.OrderedDict_Set(METHOD.OrderedDict_Get("", yaml, "{}".format(code), "停損點"), data, "停損點")
        #         # METHOD.OrderedDict_Set(METHOD.OrderedDict_Get("", yaml, "{}".format(code), "停利點"), data, "停利點")
        #
        #
        #         # sleep(1)
        #     for future in concurrent.futures.as_completed(future_all):
        #         data = future_all[future]
        #         try:
        #             result = data.result()
        #         except:
        #             raise
        #         finally:
        #             print(data)
        #         # except Execption as exc:
        #         #     print('%r generated an exception: %s' % (url, exc))
        #         # else:
        #         #     print('%r page length is %d' % (url, len(data)))
        #
        # start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:00', '%Y-%m-%d%H:%M')
        # end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')         
        # while(True):
        #
        #
        #     now_time = datetime.datetime.now()
        #     # 判断当前时间是否在范围时间内
        #     # if now_time > start_time and now_time < end_time:
        #     if now_time >= end_time:
        #         break
        #     sleep(10)
            
    except:
        LOGGER.Record("ERROR", "{}".format(traceback.format_exc()))

       
