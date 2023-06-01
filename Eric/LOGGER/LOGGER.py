'''
Created on 2022撟�6���10�

@author: Eric
'''
import logging.config
import time
import sys
from METHOD import METHOD



def Record(priority, message):
    
    try:
   
        log_yaml = METHOD.GetYaml(METHOD.PathJoin(METHOD.PathGetCurrent(), 'lOG.yaml'))
        
        date = time.strftime('%Y%m%d', time.localtime())
        filename = "Log\\{}_{}".format(date, METHOD.OrderedDict_Get("lOG.lOG", log_yaml, "handlers", "file", "filename"))
        METHOD.OrderedDict_Set(filename, log_yaml, "handlers", "file", "filename")
        path_new = METHOD.PathJoin(METHOD.PathGetCurrent(), "{}".format(filename))
        METHOD.DirectoryMake(path_new)
    
        logging.config.dictConfig(log_yaml)

    except:
        print('{} : {}'.format([s for s in str(sys.exc_info()[0]).split('\'')][1], sys.exc_info()[1]))
        raise

    else:
        logger = logging.getLogger('module')

        if priority == "INFO":
            logger.info("{}".format(Indent(message)))
        elif priority == "DEBUG":
            logger.debug("{}".format(Indent(message)))
        elif priority == "WARNING":
            logger.warning("{}".format(Indent(message)))
        elif priority == "ERROR":
            logger.error("{}".format(Indent(message)))
        elif priority == "CRITICAL":
            logger.critical("{}".format(Indent(message)))
            
        del logger
        
    pass
  
def Indent(message):

    data = ""
    for s in message.split("\n"):
        
        s.strip()
        if not s:
            data = "".join((data, "\n"))
        elif not data:
            data = "".join((s))
        else:
            data = "".join((data, "\n{:<31}".format(" "), s))

    # data = "".join((date, "\n"))
    data.strip()
    
    return data 

def RecordException(error):
    
    try:
   
        log_yaml = METHOD.GetYaml(METHOD.PathJoin(METHOD.PathGetCurrent(), 'lOG.yaml'))
        
        date = time.strftime('%Y%m%d', time.localtime())
        filename = "Log\\{}_{}".format(date, METHOD.OrderedDict_Get("lOG.lOG", log_yaml, "handlers", "file", "filename"))
        METHOD.OrderedDict_Set(filename, log_yaml, "handlers", "file", "filename")
        path_new = METHOD.PathJoin(METHOD.PathGetCurrent(), "{}".format(filename))
        METHOD.DirectoryMake(path_new)
    
        logging.config.dictConfig(log_yaml)

    except:
        print('{} : {}'.format([s for s in str(sys.exc_info()[0]).split('\'')][1], sys.exc_info()[1]))
        raise

    else:
        logger = logging.getLogger('module')
        
    logger.exception(error)
