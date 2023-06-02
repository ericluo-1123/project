'''
Created on 2022年12月9日

@author: Eric
'''

import pandas
import requests
import time
from io import StringIO
import json
import datetime
import numpy
from concurrent.futures.thread import ThreadPoolExecutor
import concurrent.futures
from MYSQL80 import MYSQL80
from METHOD import METHOD
from LOGGER import LOGGER
from LINE import LINE


def DailyClosingQuotes(date = ""):#取每日收盤行情
    
    try :
          
        pandas.set_option("display.max_rows", None) #顯示所有行
        pandas.set_option("display.max_columns", None) #显示所有列
        pandas.set_option("max_colwidth", None) #顯示列中單獨元素最大長度
        pandas.set_option("expand_frame_repr",True)#True表示列可以换行显示。设置成False的时候不允许换行显示；
        pandas.set_option("display.width", 80)#横向最多显示多少个字符；
        
        # POST請求夾帶資料
        form_data = {'date': '{}'.format(date), 'type': 'MS'}
        r = requests.post('https://www.twse.com.tw/zh/exchangeReport/MI_INDEX', data=form_data)

        if r.status_code != 200 or '很抱歉，沒有符合條件的資料!' in r.text:
            return r.text
    
        if not date :
            date = time.strftime('%Y%m%d', time.localtime())
            
        r = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALLBUT0999'.format(date))
        if r.status_code != 200:
            return r.text
        
        s = ''    
        for v in r.text.split('\n'):
            if len(v.split('",')) == 17:
                s += '\n'.join([v.translate({ord(c): None for c in ' '})]).replace('=', '')
          
        si = StringIO(s)
        df = pandas.read_csv(si)
        si.close()
        df = df.fillna(0)
        # df = df.drop(["本益比", "最後揭示賣量", "最後揭示賣價", "最後揭示買量", "最後揭示買價", "漲跌價差", "成交金額", "成交筆數", "漲跌(+/-)", "Unnamed: 16"], axis=1)
        df.insert(df.shape[1], column="日期", value=[date for i in range(0, df.shape[0])])  # @UnusedVariable
        return df;
    
    except:
        raise



def GetConfig(db):
    
    data = MYSQL80.Database_Show(db)
    
    # if 'config' in data:
    #     print('config')
    # else:
        
    data = MYSQL80.Database_Create(db, 'config')
    data = MYSQL80.Database_Use(db, 'config')
    data = MYSQL80.Table_Create(db, 'config', 'config')
    data = MYSQL80.Table_Show(db)
    
    data = MYSQL80.Database_Drop(db, 'config')
        
        
    return data

def CreateField(df):
    
    print(df.columns)
    print(df.values)
    
        
def DailyClosingQuotesA(date = ""):#取每日收盤行情
    
    try :
          
        pandas.set_option("display.max_rows", None) #顯示所有行
        pandas.set_option("display.max_columns", None) #显示所有列
        pandas.set_option("max_colwidth", None) #顯示列中單獨元素最大長度
        pandas.set_option("expand_frame_repr",True)#True表示列可以换行显示。设置成False的时候不允许换行显示；
        pandas.set_option("display.width", 80)#横向最多显示多少个字符；
        
        # POST請求夾帶資料
        form_data = {'date': '{}'.format(date), 'type': 'MS'}
        r = requests.post('https://www.twse.com.tw/zh/exchangeReport/MI_INDEX', data=form_data)

        if r.status_code != 200 or '很抱歉，沒有符合條件的資料!' in r.text:
            return r.text
    
        if not date :
            date = time.strftime('%Y%m%d', time.localtime())
            
        r = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALLBUT0999'.format(date))
        if r.status_code != 200:
            return r.text
        
        s = ''    
        for v in r.text.split('\n'):
            if len(v.split('",')) == 17:
                s += '\n'.join([v.translate({ord(c): None for c in ' '})]).replace('=', '')
        
                
        si = StringIO(s)
        df = pandas.read_csv(si)
        si.close()
        df = df.fillna(0)
        # df = df.drop(["本益比", "最後揭示賣量", "最後揭示賣價", "最後揭示買量", "最後揭示買價", "漲跌價差", "成交金額", "成交筆數", "漲跌(+/-)", "Unnamed: 16"], axis=1)
        df.insert(df.shape[1], column="日期", value=[date for i in range(0, df.shape[0])])
        
        #to csv
        # path = METHOD.PathJoin(METHOD.PathGetCurrent(), 'temp', 'test1.csv')
        # METHOD.DirectoryMake(path)
        # df.to_csv(path, index = None, encoding='utf-16')
              
        #yaml
        path = METHOD.PathJoin(METHOD.PathGetCurrent(), 'MYSQL80.yaml')
        if METHOD.IsFileExist(path) == False:
            raise RuntimeError("MYSQL80.yaml Not Exist.")     
        yaml_load = METHOD.YamlLoad(path)     
        METHOD.OrderedDict_Set(None, yaml_load, "execute", "database_create")
        METHOD.OrderedDict_Set(None, yaml_load, "execute", "table_create")
        METHOD.OrderedDict_Set(None, yaml_load, "execute", "table_create_type")      
        METHOD.YamlDump(path, yaml_load)
        yaml_load = METHOD.YamlLoad(path)
        
        database_create = "".join(("`twse_", time.strftime("%Y", time.localtime()), "`"))
        METHOD.OrderedDict_Set(database_create, yaml_load, "execute", "database_create")
        
        code = ",".join(df["證券代號"]).split(",")
        # name = ",".join(df["證券名稱"]).split(",")
        table_create = ""
        for i in range(0, df.shape[0]):
            # if i >= 5: break
            table_create = ",".join((table_create, "`{}`".format(code[i])))
                 
        table_create = table_create[1:]
        METHOD.OrderedDict_Set(table_create, yaml_load, "execute", "table_create")
        
        INSERT_INDEX = []
  
        TYPE_DATE = ["日期"]
        TYPE_INT = ["成交股數"]
        TYPE_SMALLINT = []
        TYPE_VARCHAR = ["證券代號", "證券名稱"]
        TYPE_DECIMAL = ["開盤價","最高價","最低價","收盤價"]
        #primary key 主鍵
        #foreign key 外來鍵
        #unique 不允許重複值
        #check 需節合條件
        #not null
        DEFAULT = [""]
        NOT_NULL = [""]
        AUTO_INCREMENT = [""]
        UNIQUE = ["日期"]
        PRIMARY_KEY = ["日期"]
        FOREIGN_KEY = [""]
        CHECK = [""]   
        DEFAULT_VALUE = {"":""}
              
        # table_create_type = "".join("`日期` date unique primary key")
        table_create_type = ""
        for columns in df.columns:
          
            if columns in TYPE_DATE:
                table_create_type = ",".join((table_create_type, "`{}` date".format(columns)))
            elif columns in TYPE_INT:
                table_create_type = ",".join((table_create_type, "`{}` int(20)".format(columns)))
            elif columns in TYPE_SMALLINT:
                table_create_type = ",".join((table_create_type, "`{}` smallint(4)".format(columns)))
            elif columns in TYPE_VARCHAR:
                table_create_type = ",".join((table_create_type, "`{}` varchar(255)".format(columns)))
            elif columns in TYPE_DECIMAL:
                table_create_type = ",".join((table_create_type, "`{}` DECIMAL(5,2)".format(columns)))
            else:
                continue
            
            if columns in DEFAULT:
                table_create_type = " ".join((table_create_type, "default '{}'".format(DEFAULT_VALUE[columns])))
            if columns in NOT_NULL:
                table_create_type = " ".join((table_create_type, "not null"))
            if columns in AUTO_INCREMENT:
                table_create_type = " ".join((table_create_type, "auto_increment"))
            if columns in UNIQUE:
                table_create_type = " ".join((table_create_type, "unique"))
            if columns in PRIMARY_KEY:
                table_create_type = " ".join((table_create_type, "primary key"))
            if columns in FOREIGN_KEY:
                table_create_type = " ".join((table_create_type, "foreign key"))
            if columns in CHECK:
                table_create_type = " ".join((table_create_type, "check"))
        
            INSERT_INDEX.append(columns)
                
        table_create_type = table_create_type[1:]
        METHOD.OrderedDict_Set(table_create_type, yaml_load, "execute", "table_create_type")     
        METHOD.YamlDump(path, yaml_load)
        MYSQL80.ExecuteFromYaml()
        
        host = METHOD.OrderedDict_Get("localhost", yaml_load, "execute", "host")
        port = METHOD.OrderedDict_Get(3306, yaml_load, "execute", "port")
        database = METHOD.OrderedDict_Get("sys", yaml_load, "execute", "database")
        user = METHOD.OrderedDict_Get("root", yaml_load, "execute", "user")
        password = METHOD.OrderedDict_Get("1234", yaml_load, "execute", "password")
        charset = METHOD.OrderedDict_Get("utf8", yaml_load, "execute", "charset")
        use_unicode = METHOD.OrderedDict_Get(True, yaml_load, "execute", "use_unicode")
        get_warnings = METHOD.OrderedDict_Get(True, yaml_load, "execute", "get_warnings")
        
        database = database_create.replace("`", "")
        user = "admin"
        password = "1234"
        
        config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "charset": charset,
            "use_unicode": use_unicode,
            "get_warnings": get_warnings,
        }
        
        
        syntax = []
        
        #inser
        syntax.clear()
        num = 0   
        item = ""
        table = ""
        value = ""
        # df.set_index("證券代號" , inplace=True)
        for index in df.index:
            item = ""
            table = ""
            for columns in df.columns:
                value = df.loc[index][columns]
                if columns == "證券代號": table = value            
                if columns not in INSERT_INDEX: continue           
                if columns == "成交股數":
                    value = value.replace(",","")
                item = ",".join((item, "=".join(("`{}`".format(columns), "'{}'".format(value)))))
     
            if item:
                item = item[1:]
                syntax.append("insert ignore `{}`.`{}` SET {};".format(database, table, item))           
            
            # num += 1
            # if num >= 5:
            #     break;
            
        syntax.append("commit;")
        syntax.append("select version();")
        MYSQL80.Request(config, syntax)
      
        if 1 == 0 :
            #add
            syntax.clear()
            ADD_INDEX = ["成交筆數", "成交金額"]
            num = 0
            item = ""
            table = ""
            value = ""
            for index in df.index:
                item = ""
                table = ""
                for columns in df.columns:
                    value = df.loc[index][columns]
                    if columns == "證券代號": table = value              
                    if columns not in ADD_INDEX: continue           
                    if columns == "成交筆數": 
                        item = ",".join((item, " ".join(("`{}`".format(columns), "int(20)"))))
                    if columns == "成交金額": 
                        item = ",".join((item, " ".join(("`{}`".format(columns), "int(20)"))))
      
                if item:
                    item = item[1:]
                    syntax.append("alter table `{}`.`{}` add column ({});".format(database, table, item))           
                
                # num += 1
                # if num >= 5:
                #     break;
                
            syntax.append("commit;")
            syntax.append("select version();")
            MYSQL80.Request(config, syntax)
          
            #update
            syntax.clear()
            UPDATE_INDEX = ["成交筆數", "成交金額"]
            num = 0
            item = ""
            table = ""
            value = ""
            for index in df.index:
                item = ""
                table = ""
                for columns in df.columns:
                    value = df.loc[index][columns]
                    if columns == "證券代號": table = value              
                    if columns not in UPDATE_INDEX: continue           
                    if columns == "成交筆數":
                        value = value.replace(",","")
                        item = ",".join((item, "=".join(("`{}`".format(columns), "'{}'".format(value)))))
                    if columns == "成交金額":
                        value = value.replace(",","")
                        item = ",".join((item, "=".join(("`{}`".format(columns), "'{}'".format(value)))))
                        
                if item:
                    item = item[1:]
                    syntax.append("update `{}`.`{}` set {} where `日期` like date({});".format(database, table, item, date))           
                #
                # num += 1
                # if num >= 5:
                #     break;
            
            syntax.append("commit;")
            syntax.append("select version();")
            MYSQL80.Request(config, syntax)
            
            
            #drop
            syntax.clear()
            DRIP_INDEX = ["成交筆數", "成交金額"]
            num = 0
            item = ""
            table = ""
            value = ""
            for index in df.index:
                item = ""
                table = ""
                for columns in df.columns:
                    value = df.loc[index][columns]
                    if columns == "證券代號": table = value              
                    if columns not in DRIP_INDEX: continue           
                    if columns == "成交筆數":
                        value = value.replace(",","")
                        item = ",".join((item, "".join(("drop column `{}`".format(columns)))))
                    if columns == "成交金額":
                        value = value.replace(",","")
                        item = ",".join((item, "".join(("drop column `{}`".format(columns)))))
                        
                if item:
                    item = item[1:]
                    syntax.append("alter table `{}`.`{}` {};".format(database, table, item, date))           
                
                # num += 1
                # if num >= 5:
                #     break;
             
            syntax.append("commit;")   
            syntax.append("select version();")
            MYSQL80.Request(config, syntax)
            
            
            #select
            syntax.clear()
            sql = "select *from `twse_2022`.`0050`"
            syntax.append("show columns from `twse_2022`.`0050`;")
            syntax.append(sql)
            output = MYSQL80.Request(config, syntax)
            print(len(output))
            print(output[0])
            
    except:
        raise
        
    else:
        LOGGER.Record("INFO", "TWSE >> DailyClosingQuotes({})".format(date))
        
    
    pass

def MainDailyClosingQuotes(date_start, date_end):

    # executor = ThreadPoolExecutor()         # 建立非同步的多執行緒的啟動器
    with ThreadPoolExecutor(max_workers=5) as executor:
        
        date_list = []
        for day in range(0, (date_end - date_start).days):
            date_day = datetime.datetime.strftime(date_start + datetime.timedelta(days=day), '%Y%m%d')
            
            date_list.append(date_day)
            if len(date_list) != 10:
                continue
            
            future_all = {executor.submit(DailyClosingQuotes, date) for date in date_list}
                
            for future in concurrent.futures.as_completed(future_all):
                result = future.result()
                print(result)

            date_list.clear()
            
def InstantStockPrice(code, odict):#條件監測即時股價

    try:
        
        condition = METHOD.OrderedDict_Get(0, odict, '{}'.format(code), 'condition')
        time_notify = METHOD.OrderedDict_Get(1, odict, '{}'.format(code), 'time_notify') 
        time_old = METHOD.OrderedDict_Get('', odict, '{}'.format(code), '時間')
        
        if not code:
            raise RuntimeError("股票代碼不可為空.")
        
        pandas.set_option("display.max_rows", None) #顯示所有行
        pandas.set_option("display.max_columns", None) #显示所有列
        pandas.set_option("max_colwidth", None) #顯示列中單獨元素最大長度
        pandas.set_option("expand_frame_repr",True)#True表示列可以换行显示。设置成False的时候不允许换行显示；
        pandas.set_option("display.width", 120)#横向最多显示多少个字符；
        
        data = ""
        response = requests.get("https://tw.stock.yahoo.com/quote/{}".format(code))
        start = response.text.find('\"quote\":{\"data\":')
        end =  response.text.find(',"isFailed":', start)
        data = "".join((data, response.text[start:end])).replace("\"quote\":{\"data\":", "")
        data = json.loads(data)
        # response = requests.get("https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{}.tw".format(code))
        # data = response.json()
        # # 過濾出有用到的欄位
        # columns = ['c','n','z','tv','v','o','h','l','y']
        # df = pandas.DataFrame(data['msgArray'], columns=columns)
        columns = ['symbol', 'symbolName', 'price', 'volume',\
                   'regularMarketOpen', 'regularMarketDayHigh', 'regularMarketDayLow','regularMarketPreviousClose',\
                   'change', 'changePercent', 'avgPrice', 'previousVolume',\
                   'limitDownPrice', 'limitUpPrice', 'holdingType']
        df = pandas.DataFrame(data, columns=columns, index=[0])
        df.columns = ['股票代號','股票名稱','成交價','成交量',\
                      '開盤價','最高價','最低價','昨收價',\
                      '漲跌', '漲跌百分比', '均價', '昨收成交量',\
                      '跌停價', '漲停價', '股票類型']
        # 新增市場時間欄位
        time_now = METHOD.TimeGet('%Y-%m-%d %H:%M:%S')
        df.insert(df.shape[1], "市場時間", "{}".format(time_now))
         
        df = df.drop(['跌停價', '漲停價', '股票類型', '均價', '昨收成交量'], axis=1)
        #資料與類型處理
        for x in range(df.shape[0]):
            # if not df.loc[x, '成交量'].isdecimal(): 
            #     df.loc[x, '成交量']  = "0"
            df.loc[x, '股票代號'] = df.loc[x, '股票代號'].replace('.TW', '')
            df.loc[x, '漲跌百分比'] = df.loc[x, '漲跌百分比'].replace('%', '')
            # df.loc[x, '市場時間'] = df.loc[x, '市場時間'].replace('%', '')
            df.loc[x, '成交量'] = df.loc[x, '成交量'][:len(df.loc[x, '成交量'])-3]
            # if df.loc[x, '成交價'] != '-':
            # df.loc[x:,['成交價', '成交量', '開盤價','最高價','最低價', '昨收價','漲跌','漲跌百分比']] = df.loc[x:,['成交價', '成交量', '開盤價','最高價','最低價', '昨收價','漲跌','漲跌百分比']].astype(float).dtypes
            
            # df.iloc[x, [2,3,4,5,6,7,8]] = df.iloc[x, [2,3,4,5,6,7,8]].astype(float)
            # df.loc[x, '漲跌百分比'] = format((df.loc[x, '成交價'] - df.loc[x, '昨收價'])/df.loc[x, '昨收價'] * 100, ".2f")                   
            
        df = df.astype({'成交價': numpy.float64, '成交量': numpy.float64,\
                        '開盤價': numpy.float64, '最高價': numpy.float64,\
                        '最低價': numpy.float64, '昨收價': numpy.float64,\
                        '漲跌': numpy.float64, '漲跌百分比': numpy.float64,\
                        })
        # print(df.dtypes)
        
        notify = False
        if not time_old:
            time_old = time_now
            METHOD.OrderedDict_Set(time_now, odict, '{}'.format(code), '時間')
            notify = True
            
        date_now = datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S')
        date_old = datetime.datetime.strptime(time_old, '%Y-%m-%d %H:%M:%S')
        
        date = (date_now - date_old).seconds
        if date >= time_notify:
            METHOD.OrderedDict_Set(time_now, odict, '{}'.format(code), '時間')
            print('{}'.format(time_now))
            notify = True
            
        if notify == True:
            for l in condition.split(';'):
                for i in l.split(','):
                    c = i.split('=')
                    if len(c) != 2: continue
                    key = c[0]
                    if key == 'stop_loss' :
                        value = float(c[1])
                        if value != 0 and df.loc[0, '成交價'] <= value:                       
                            LINE.Notify("\n股票代號:{} 成交價({})\n- 已達停損價({})".format(df.loc[0, "股票代號"], df.loc[0, "成交價"], value))
                    if key == 'stop_profit':           
                        value = float(c[1])
                        if value != 0 and df.loc[0, '成交價'] >= value:
                            LINE.Notify("\n股票代號:{} 成交價({})\n- 已達停利價({})".format(df.loc[0, "股票代號"], df.loc[0, "成交價"], value))
               
        print("{}\n".format(df))
               
    except:
        raise
    








