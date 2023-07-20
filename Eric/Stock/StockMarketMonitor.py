'''
Created on 2022年12月20日

@author: Eric
'''

import traceback
import threading
from MYSQL80 import MYSQL80
from TWSE import TWSE
from METHOD import METHOD
from LOGGER import LOGGER
import datetime
from _collections import OrderedDict
import time
import random
from sqlalchemy.sql.expression import false

  
def Run(date, user, password, df):
    
    print('Run : {}'.format(date))
    MYSQL80.CreateField(user, password, df)
    
if __name__ == '__main__':
    pass
          
    try:
           
        # yaml = OrderedDict()  
        # METHOD.OrderedDict_Set('', yaml, '通用', '開始日期') 
        # METHOD.OrderedDict_Set('', yaml, '通用', '結束日期')
        # METHOD.YamlDump('{}//stock.yaml'.format(METHOD.PathGetCurrent()), yaml, 'big5')      
        yaml = METHOD.GetYaml(METHOD.PathJoin(METHOD.PathGetCurrent(), 'stock.yaml'), 'big5')
        date_now = METHOD.TimeGet('%Y%m%d')
        date_start = METHOD.OrderedDict_Get(date_now, yaml, '通用', '開始時間')
        date_start = METHOD.TimeGetByDate(date_start, '%Y%m%d')      
        date_end = METHOD.OrderedDict_Get(date_now, yaml, '通用', '結束時間')
        date_end = METHOD.TimeGetByDate(date_end, '%Y%m%d')

        # data = MYSQL80.Execute(db, 'SELECT * FROM twse_2023.`0050`;')
        # data = MYSQL80.WriteProfile(db, 'Item', 'test')
        # data = MYSQL80.ReadProfile(db, 'Item', '123')
              
        user = ''
        password = '1234'
        is_max_threading = 0
        is_create_table = False
        # 建立 Lock
        threadings = []
        lock = threading.Lock()
        
        while(True):
            for i in range(1):
                df = TWSE.DailyClosingQuotes('{}'.format(METHOD.TimeToString(date_start, '%Y%m%d')))
                time.sleep(random.randint(5, 7))
                if df.empty: continue
                
                user = 'user{}'.format(len(threadings)+1)
                if is_create_table == False:
                    MYSQL80.CreateTable(user, password, df)
                    is_create_table = True
                
                
                t = threading.Thread(target=Run, args=(date_start, user, password, df))
                threadings.append(t)
                is_max_threading += 1
                
                if len(threadings) == 3:
                    is_max_threading = 0
                    
                    for t in threadings:
                        t.start()
                      
                    for t in threadings:
                        t.join()       
            
            if date_start >= date_end:
                break;
            date_start += datetime.timedelta(days=1)
                  
                 
            
    except:
        LOGGER.Record("ERROR", "{}".format(traceback.format_exc()))

       
