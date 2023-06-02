'''
Created on 2023年2月10日

@author: Eric
'''
import ddddocr
import sys
import traceback

if __name__ == '__main__':
    
    try:
        
        if len(sys.argv) != 2:
            raise RuntimeError('No parameters.')
       
        with open(sys.argv[1], 'rb') as f:
            img_bytes = f.read()
            
        ocr = ddddocr.DdddOcr()
        print(ocr.classification(img_bytes))
        
    except:
        print("ERROR : {}".format(traceback.format_exc()))