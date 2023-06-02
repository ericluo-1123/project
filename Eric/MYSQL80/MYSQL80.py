'''
Created on 2022年12月7日

@author: Eric
'''

import mysql.connector
import time
from sqlalchemy.engine.create import create_engine
import traceback
from PROCESS import PROCESS
from METHOD import METHOD
from LOGGER import LOGGER


_SQL = {
        "select_all_table":"select *from [table];",
        "select from_table":"select [column] from {column};",
        "show_columns_from_table":"show columns from [table];",
    }

def Check_Service():
    
    result = False
    while(True):
        output = PROCESS.Execute("net start MySQL80")
        if output.find('已經啟動要使用的服務') == -1:
            output = PROCESS.Execute("netstat -ano | findstr 0.0:3306")
            find = 'LISTENING'
            addr = output.rfind(find)
            if addr != -1:
                port = output[addr+len(find):output.rfind("\n")].strip()
                output = PROCESS.Execute("taskkill /F /IM {}".format(port))
                
            output = PROCESS.Execute("net start MySQL80")
            if output.find('服務已經啟動成功') != -1 or output.find('已經啟動要使用的服務') != -1:
                result = True

        else:
            result = True
        
        break
    
    return result
    
def Database_Show(db):
    
    data = Execute(db, 'show databases')
    
    return data

def Database_Create(db, database):
    
    data = Execute(db, 'create database `{}`;'.format(database))
    
    return data

def Database_Use(db, database):
    
    data = Execute(db, 'use `{}`;'.format(database))
    
    return data

def Database_Drop(db, database):
    
    data = Execute(db, 'drop database `{}`;'.format(database))
    
    return data

def Table_Show(db):
    
    data = Execute(db, 'show tables;')
    
    return data

def Table_Create(db, database, table):
    
    data = Execute(db, 'create table `{}`.`{}`()'.format(database, table))
    
    return data
    
def GetYaml():
    '''
    Constructor
    '''

    path = METHOD.PathJoin(METHOD.PathGetCurrent(), 'MYSQL80.yaml')
    
    if METHOD.IsFileExist(path) == False:
        raise RuntimeError("MYSQL80.yaml Not Exist.") 
              
    log_yaml = METHOD.YamlLoad(path)
    
    return log_yaml
         
def GetConnector(config):

    try:
        
        result = False
        while(True):
            output = PROCESS.Execute("net start MySQL80")
            if output.find('已經啟動要使用的服務') == -1:
                output = PROCESS.Execute("netstat -ano | findstr 0.0:3306")
                find = 'LISTENING'
                addr = output.rfind(find)
                if addr != -1:
                    port = output[addr+len(find):output.rfind("\n")].strip()
                    output = PROCESS.Execute("taskkill /F /IM {}".format(port))
                    
                output = PROCESS.Execute("net start MySQL80")
                if output.find('服務已經啟動成功') != -1 or output.find('已經啟動要使用的服務') != -1:
                    result = True
    
            else:
                result = True
            
            break
        
        
        if result == False:
            return None

        db = mysql.connector.Connect(**config)
        return db
        # with mysql.connector.Connect(**config) as db:        
        #     return db
            
    except:
        raise
    
def Execute(db, syntax):
    
    try:
           
        message = ['False']
        output = []
        rows = []
        start = time.time()
        cursor = db.cursor()
        
        cursor.execute(syntax)
        rows = cursor.fetchall()
        warnings = cursor.fetchwarnings()  
        output.append("cursor.execute >> {}\n".format(syntax))
        
        if warnings != None:
            for wars in warnings:
                output.append("mysql.connector.warning.ProgrammingWarnings : {} ({}): {}".format(wars[0], wars[1], wars[2]))
        else:

            for row in rows:
                message.append("".join(repr(row)).replace("'", "").replace(",", "").replace("(", "").replace(")", ""))
          
            message[0] = 'True'
            output.append(','.join(message))
            
       
    except:
        output.append("{}".format(traceback.format_exc()))
        # output.append("{} : {}".format([s for s in str(sys.exc_info()[0]).split('\'')][1], sys.exc_info()[1]))

        
    finally:
        cursor.close()
        end = time.time()
        output.append("{} row(s) affected {:.2f} sec".format(len(rows), (end - start)))
        LOGGER.Record("DEBUG", "\n".join(output))
        
    return message
        
def ExecuteFromYaml():
    
    try:    
        
        log_yaml = METHOD.GetYaml(METHOD.PathJoin(METHOD.PathGetCurrent(), 'MYSQL80.yaml'))
        
        #init
        database_create = METHOD.OrderedDict_Get("", log_yaml, "execute", "database_create").split(",")
        database_create = [x.strip("`") for x in database_create]
        
        table_create = METHOD.OrderedDict_Get("", log_yaml, "execute", "table_create").split(",")
        table_create = [x.strip("`") for x in table_create]
    
        table_drop = METHOD.OrderedDict_Get("", log_yaml, "execute", "table_drop").split(",")
        table_drop = [x.strip() for x in table_drop]
        
        table_create_type = METHOD.OrderedDict_Get("", log_yaml, "execute", "table_create_type").split(",")
        table_create_type = [x.strip("") for x in table_create_type]
        
        table_add_column = METHOD.OrderedDict_Get("", log_yaml, "execute", "table_add_column").split(",")
        table_add_column = [x.strip() for x in table_add_column]
        
        table_change_column = METHOD.OrderedDict_Get("", log_yaml, "execute", "table_change_column").split(",")
        table_change_column = [x.strip() for x in table_change_column]
        
        table_drop_column = METHOD.OrderedDict_Get("", log_yaml, "execute", "table_drop_column").split(",")
        table_drop_column = [x.strip() for x in table_drop_column]
        
        database_drop = METHOD.OrderedDict_Get("", log_yaml, "execute", "database_drop").split(",")
        database_drop = [x.strip() for x in database_drop]
            
        #connect config 
        host = METHOD.OrderedDict_Get("localhost", log_yaml, "execute", "host")
        port = METHOD.OrderedDict_Get(3306, log_yaml, "execute", "port")
        database = METHOD.OrderedDict_Get("sys", log_yaml, "execute", "database")
        user = METHOD.OrderedDict_Get("root", log_yaml, "execute", "user")
        password = METHOD.OrderedDict_Get("1234", log_yaml, "execute", "password")
        charset = METHOD.OrderedDict_Get("utf8", log_yaml, "execute", "charset")
        use_unicode = METHOD.OrderedDict_Get(True, log_yaml, "execute", "use_unicode")
        get_warnings = METHOD.OrderedDict_Get(True, log_yaml, "execute", "get_warnings")
        
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
            
        output = []
        tables = []
        escribes = []
            
        with mysql.connector.Connect(**config) as sql_db:
              
            cursor = sql_db.cursor()
            
            Execute(cursor, "select version();")                                             
            for db in database_create: 
                if db:
                    databases = Execute(cursor, "show databases;")                 
                    if db not in databases[0].split(","):
                        output = Execute(cursor, "create database if not exists {};".format("".join(("`", db, "`"))))                       
                        databases = Execute(cursor, "show databases;")
                    
                    if db in databases[0].split(","):         
                        for tb in table_create:
                            if tb:
                                output = Execute(cursor, "use {};".format("".join(("`", db, "`"))))
                                tables = Execute(cursor, "show tables;")
                                if tb not in tables[0].split(","): 
                                    output = Execute(cursor, "create table if not exists {}.{}({});".format("".join(("`", db, "`")), "".join(("`", tb, "`")), ",".join(table_create_type)))
                                    tables = Execute(cursor, "show tables;")                       
                        
                            if tb in tables[0].split(","):                                
                                escribes = Execute(cursor, "describe {}.{};".format("".join(("`", db, "`")), "".join(("`", tb, "`"))))                                
                                for column in table_add_column:
                                    if (column) and (column.split(" ")[0].strip("`") not in escribes[0].split(",")): 
                                        output = Execute(cursor, "alter table {}.{} add column {};".format("".join(("`", db, "`")), "".join(("`", tb, "`")), column))
                                
                                for column in table_change_column:
                                    if (column) and (column.split(" ")[0].strip("`") in escribes[0].split(",")):
                                        output = Execute(cursor, "alter table {}.{} change column {};".format("".join(("`", db, "`")), "".join(("`", tb, "`")), column))                               
                                
                                for column in table_drop_column: 
                                    if (column) and (column.split(" ")[0].strip("`") in escribes[0].split(",")):
                                        output = Execute(cursor, "alter table {}.{} drop column {};".format("".join(("`", db, "`")), "".join(("`", tb, "`")), column))
                        
                        
                        for tb in table_drop: 
                            if tb:
                                tables = Execute(cursor, "show tables;")
                                if tb in tables[0].split(","): 
                                    output = Execute(cursor, "drop table {}.{};".format("".join(("`", db, "`")), "".join(("`", tb, "`"))))
                                              
            for db in database_drop: 
                if (db):
                    databases = Execute(cursor, "show databases;") 
                    if db in databases: 
                        output = Execute(cursor, "drop database {};".format("".join(("`", db, "`"))))          
               
            for db in database_create:
                if db:
                    databases = Execute(cursor, "show databases;")
                    if db in databases:
                        output = Execute(cursor, "use {};".format("".join(("`", db, "`"))))
                        tables = Execute(cursor, "show tables;")
                         
            cursor.close()
            output.clear()
            output.append("MYSQL80 >> ExecuteFromYaml Finish.")
            return output
        
    except:
        raise

def ToSQL(config, df):
    
    engine = create_engine("mysql+pymysql://admin:1234@localhost/twse_2022?charset=utf8")
    # df = pandas.DataFrame({"日期":["20221111"], "證券代號":["0050"]})
    df.to_sql("0050", engine, index= False, if_exists='append')
    
    # with mysql.connector.Connect(**config) as db:
        
        
            # output = []        
            # cursor = db.cursor()
            # output = Execute(cursor, syntax)          
            # cursor.close()
            # db.close()    
            # return output
    
def Request(config, syntax):
    
    try:
        
        output = []
        data = []
        with mysql.connector.Connect(**config) as db:
            output = []        
            cursor = db.cursor()
            for sql in syntax:
                data = Execute(cursor, sql)
                if len(data) == 0: continue
                output.append("".join(data))       
            cursor.close()
            db.close()
            return output
            
    except:
        raise
    
    
    
    
        
        
 
        
    