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
import sys


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
    
    data = Execute(db, 'create table `{}`.`{}`(id bigint unsigned auto_increment primary key)'.format(database, table))
    
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
        output.append("{}\n".format(syntax))
        cursor = db.cursor()  
        cursor.execute(syntax)
        rows = cursor.fetchall()
        warnings = cursor.fetchwarnings()
        
        if warnings != None:
            for wars in warnings:
                output.append("Warning {} ({}): {}".format(wars[0], wars[1], wars[2]))
        else:
            
            if 'show columns' in syntax:
                for row in rows:
                    message.append(repr(row).split(',')[0].replace("'", "").replace("(", ""))
            else:
                for row in rows:
                    message.append("".join(repr(row)).replace("'", "").replace(",", "").replace("(", "").replace(")", ""))
          
            message[0] = 'True'
            output.append(','.join(message))        
       
    except:
        # output.append("{}".format(traceback.format_exc()))
        # output.append("{} : {}".format([s for s in str(sys.exc_info()[0]).split('\'')][1], sys.exc_info()[1]))
        output.append("Error Code {}\n".format(sys.exc_info()[1]))
        
        
    finally:
        cursor.close()
        end = time.time()
        output.append("{} row(s) affected {:.2f} sec".format(len(rows), (end - start)))
        LOGGER.Record("DEBUG", "\n".join(output))
        
    return message
     
def ReadProfile(db, key, default):
    
    data = []
    for i in range(1):
        
        data = Execute(db, 'use `profile`;')
        if data[0] == False: continue
        data = Execute(db, 'select `{}` from `profile`.`config`;'.format(key))
        if data[0] == False: continue
        
    if len(data) == 1:
        data.append(default)
        
    return data

def WriteProfile(db, key, value):
      
    data = Execute(db, 'show databases;')
    if 'profile' in data:
        
        for i in range(1):
            data = Execute(db, 'use `profile`;')
            if data[0] == False: continue
                             
            data = Execute(db, 'show tables;')
            if 'config' not in data:
                data = Execute(db, 'create table if not exists `profile`.`config`(id bigint unsigned not null auto_increment primary key);')
                if data[0] == False: continue
            
            data = Execute(db, 'show columns from `profile`.`config`;')
            if key in data:      
                data = Execute(db, 'insert into `profile`.`config`(`{}`) values("{}");'.format(key, value))
                if data[0] == False: continue
            else:
                data = Execute(db, 'alter table `profile`.`config` add column {} VARCHAR(30);'.format(key, value))
                if data[0] == False: continue  
    else:
    
        for i in range(1):
            
            data = Execute(db, 'create database if not exists `profile`;')
            if data[0] == False: continue              
       
            data = Execute(db, 'use `profile`;')
            if data[0] == False: continue              
            
            data = Execute(db, 'create table if not exists `profile`.`config`(id bigint unsigned not null auto_increment primary key);')
            if data[0] == False: continue          
            
            data = Execute(db, 'show tables;')
            if data[0] == False: continue          
            
            data = Execute(db, 'alter table `profile`.`config` add column {} VARCHAR(30);'.format(key, value))
            if data[0] == False: continue
                       
        
    return data

def CreateTable(user, password, df):
    
    try:
        syntax = []
        db = GetConnector({
            "host": 'localhost',
            "port": 3306,
            "database": 'sys',
            "user": '{}'.format(user),
            "password": '{}'.format(password),
            "charset": 'utf8',
            "use_unicode": True,
            "get_warnings": True,
        })
            
        items = ''
        items_insert = ''  
        for col in df.columns:
            if col == '證券代號' or col == '證券名稱': continue
            
            if items:
                items += ', `{}` VARCHAR(30)'.format(col)
            else:
                items += '`{}` VARCHAR(30)'.format(col)
                
            if items_insert:
                items_insert += ', `{}`'.format(col)
            else :
                items_insert += '`{}`'.format(col)
                    
        database_name = 'twse_{}'.format(METHOD.TimeGet('%Y'))
    
        for i in range(1):
            
            data = Execute(db, 'show databases;')
            if data[0] == False: continue
            
            if database_name not in data:
                data = Execute(db, 'create database if not exists `{}`;'.format(database_name))
                if data[0] == False: continue
                     
            data = Execute(db, 'use `{}`;'.format(database_name))
            if data[0] == False: continue                 
                    
            tables = Execute(db, 'show tables;')
            if data[0] == False: continue
     
            for j in range(df.shape[0]):
                code = df.at[j, '證券代號']
                name = df.at[j, '證券名稱']
                table_name = '{} {}'.format(code.lower(), name.lower())
                if table_name in tables: continue
                data = Execute(db, 'create table if not exists `{}`.`{}`({});'.format(database_name, table_name, items))
                if data[0] == False: continue
            
    except:
        raise
    finally:
        db.close()
        
    
def CreateField(user, password, df):
    
    try:
        syntax = []
        db = GetConnector({
            "host": 'localhost',
            "port": 3306,
            "database": 'sys',
            "user": '{}'.format(user),
            "password": '{}'.format(password),
            "charset": 'utf8',
            "use_unicode": True,
            "get_warnings": True,
        })
            
        items = ''
        items_insert = ''  
        for col in df.columns:
            if col == '證券代號' or col == '證券名稱': continue
            
            if items:
                items += ', `{}` VARCHAR(30)'.format(col)
            else:
                items += '`{}` VARCHAR(30)'.format(col)
                
            if items_insert:
                items_insert += ', `{}`'.format(col)
            else :
                items_insert += '`{}`'.format(col)
                    
        database_name = 'twse_{}'.format(METHOD.TimeGet('%Y'))
    
        for i in range(1):
            
            data = Execute(db, 'show databases;')
            if data[0] == False: continue
            
            # if database_name not in data:
            #     data = Execute(db, 'create database if not exists `{}`;'.format(database_name))
            #     if data[0] == False: continue
                     
            data = Execute(db, 'use `{}`;'.format(database_name))
            if data[0] == False: continue                 
                    
            # tables = Execute(db, 'show tables;')
            # if data[0] == False: continue
            #
            # for j in range(df.shape[0]):
            #     code = df.at[j, '證券代號']
            #     name = df.at[j, '證券名稱']
            #     table_name = '{} {}'.format(code.lower(), name.lower())
            #     if table_name in tables: continue
            #     data = Execute(db, 'create table if not exists `{}`.`{}`({});'.format(database_name, table_name, items))
            #     if data[0] == False: continue
        
            for j in range(df.shape[0]):
                code = df.at[j, '證券代號']
                name = df.at[j, '證券名稱']
                table_name = '{} {}'.format(code.lower(), name.lower())    
                # index = df[df['證券代號'] == code].index.tolist()
    
                checks = ''
                values = ''
                for col in df.columns:
                    if col == '證券代號' or col == '證券名稱': continue
                    
                    if values:
                        values += ', "{}"'.format(df.at[j, col])
                    else:
                        values += '"{}"'.format(df.at[j, col])
                        
                    if checks:
                        checks += ' and `{}` = "{}"'.format(col, df.at[j, col])
                    else:
                        checks += '`{}` = "{}"'.format(col, df.at[j, col])
                        
                # data = Execute(db, 'insert into `{}`.`{}`({}) values({});'.format(database_name, table_name, items_insert, values, df.at[j, '日期']))
                data = Execute(db, 'insert into `{}`.`{}`({}) select {} from dual where not exists(select {} from `{}`.`{}` where {});'.format(database_name, table_name, items_insert, values, items_insert, database_name, table_name, checks))
                if data[0] == False: continue
    
    
            data = Execute(db, 'commit')
            if data[0] == False: continue
            
    except:
        raise
    finally:
        db.close()
    
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
    
    
    
    
        
        
 
        
    