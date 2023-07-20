'''
Created on 2021年12月24日

@author: Eric
'''

import shutil
import os
import datetime
import ruamel.yaml  # @UnresolvedImport


def TimeGet(formatter = '%Y-%m-%d %H:%M:%S'):

    return datetime.datetime.now().strftime(formatter)

def TimeGetByNow(formatter = '%Y-%m-%d %H:%M:%S'):

    return datetime.datetime.strptime(datetime.datetime.now().strftime(formatter), formatter)

def TimeGetByDate(date, formatter = 'Y-%m-%d %H:%M:%S'):
    
    return datetime.datetime.strptime(date, formatter)
 
def TimeToString(date, formatter = 'Y-%m-%d %H:%M:%S'):
       
    return date.strftime(formatter)

def FileCopy(src, dst):
    
    if IsFileExist(src):
        DirectoryMake(dst)
        shutil.copyfile(src, dst)
    
def FileExtension(path):
   
    root, extension = os.path.splitext(path)
    return  extension

def FileList(path):
    
    return os.listdir(path)
    
def FileCreate(path):
    
    open(path, mode='w', encoding='utf-8')
    
def FileDelete(path):
    
    if IsFileExist(path) == True : os.remove(path)
    
def PathGetCurrent():
    
    return os.path.abspath(os.getcwd())

def PathJoin(path, *paths):
           
    return os.path.join(path, *paths)
    
def DirectoryDelete(path):

    try:
        shutil.rmtree(path)
    except :
        raise RuntimeError("DirectoryDelete Fail.\n{}".format(path))

def DirectoryMake(path):

    if IsDirExist(path) == True: return
    
    path_split = os.path.split(path)
    if IsDirExist(path_split[0]) == True: return
    
    path_drive = os.path.splitdrive(path_split[0])
    string_split = path_drive[1].split('\\')
    path_new = path_drive[0]
    
    for s in string_split :
        
        s.strip()      
        if not s: continue    
        path_new = "".join((path_new, '\\', s))  
        if IsDirExist(path_new) ==  False: os.mkdir(path_new)

def IsFileExist(path):
    
    return os.path.isfile(path)
        
def IsLinkExist(path):
    
    return os.path.islink(path)

def IsDirExist(path):
    
    return os.path.isdir(path)

def IsPathExist(path):
    
    return os.path.exists(path)

def YamlLoad(path, encode="utf-8"):
          
    try:                            
        with open(path, 'r', encoding=encode) as stream:
            return ruamel.yaml.load(stream, Loader=ruamel.yaml.RoundTripLoader)      
    except:       
        raise RuntimeError("YamlLoad Fail.\n{}".format(path))
             

    
def YamlDump(path, config, encode="utf-8"):
          
    try:                             
        with open(path, 'w', encoding=encode) as stream:
            ruamel.yaml.dump(config, stream, Dumper=ruamel.yaml.RoundTripDumper)                  
    except:       
        raise RuntimeError("YamlDump Fail.\n{}".format(path))

def GetYaml(path, encode="utf-8"):
    
    if IsFileExist(path) == False: 
        raise RuntimeError("Yaml file Not Exist.\n{}".format(path))
    
    return YamlLoad(path, encode)

def OrderedDict_Get(default, odict, *key):

    try:
        value = default
        if len(key) == 1:
            value = odict[key[0]]
        elif len(key) == 2:
            value = odict[key[0]][key[1]]
        elif len(key) == 3:
            value = odict[key[0]][key[1]][key[2]]
        elif len(key) == 4:
            value = odict[key[0]][key[1]][key[2]][key[3]]
        elif len(key) == 5:
            value = odict[key[0]][key[1]][key[2]][key[3]][key[4]]
    except:
        pass
    
    finally:
        
        if isinstance(value, str):
            value.strip()
            
        if (value == None or not value) and (value != default):
            value = default
            
        

        return value
        
def OrderedDict_Set(value, odict, *key):

    try:
        if len(key) == 1:
            odict[key[0]] = value
        elif len(key) == 2:
            odict[key[0]][key[1]] = value
        elif len(key) == 3:
            odict[key[0]][key[1]][key[2]] = value
        elif len(key) == 4:
            odict[key[0]][key[1]][key[2]][key[3]] = value
        elif len(key) == 5:
            odict[key[0]][key[1]][key[2]][key[3]][key[4]] = value
    except:
        if len(key) == 1:
            odict[key[0]] = value
        elif len(key) == 2:
            odict[key[0]] = {key[1]:value}
        elif len(key) == 3:
            odict[key[0]] = {key[1]:{key[2]:value}}
        elif len(key) == 4:
            odict[key[0]] = {key[1]:{key[2]:{key[3]:value}}}
        elif len(key) == 5:
            odict[key[0]] = {key[1]:{key[2]:{key[3]:{key[4]:value}}}}
   
         
        
    