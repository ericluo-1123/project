'''
Created on 2022年12月19日

@author: Eric
'''
import subprocess
from subprocess import check_output

def Execute(command):
    
    try:      
        output = check_output("{}".format(command), shell=True, stderr=subprocess.STDOUT)
        data = "".join(output.decode("big5").replace("\r", ""))      
    except subprocess.CalledProcessError as e:
        data = "".join(e.output.decode("big5").replace("\r", ""))
    finally:
        return data
