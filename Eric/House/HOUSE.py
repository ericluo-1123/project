'''
Created on 2023年4月25日

@author: Eric
'''
import traceback
import sys
from selectolax.parser import HTMLParser  # @UnresolvedImport
import pandas
from io import StringIO
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import urllib
import os
import ssl
import re
import wx
from threading import Timer
import queue
from House import HOUSE_GUI
from METHOD import METHOD
from LOGGER import LOGGER


ssl._create_default_https_context = ssl._create_unverified_context
 
class RepeatingTimer(Timer): 
    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)
            
class MyHouse(HOUSE_GUI.MyFrameHouse):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        HOUSE_GUI.MyFrameHouse.__init__ ( self, params)
        self.queue = queue.Queue()
        self.timer = RepeatingTimer(0.5, self.show_msg)
        self.timer.start()
        
        # self.font_static = wx.Font(30, family = wx.FONTFAMILY_MODERN, style = 0, weight = 90,
        #               underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT)
        # self.m_staticText_url.SetFont(self.font_static)
        # self.font_text = wx.Font(10, family = wx.FONTFAMILY_MODERN, style = 0, weight = 90,
        #               underline = False, faceName ="", encoding = wx.FONTENCODING_DEFAULT)
        # self.m_textCtrl_status.SetFont(self.font_text)
        
    def show_msg(self):
        
        while not self.queue.empty():
            content = self.queue.get()
            self.m_textCtrl_status.AppendText('{}\n'.format(content))
            
        
    def send_msg(self, data):
        
        self.queue.put(data)
        
    def OK( self, event ):     
        
        try:
             
            self.m_textCtrl_status.Clear()
            url = self.m_textCtrl_url.GetValue().strip()
        
            if not url:
                self.send_msg('網址不可為空')
                raise
         
            self.send_msg('網址 = {}'.format(url))
            
            if re.match('^https?:/{2}\w.+$', url):
                self.m_button_ok.Disable()
                self.m_button_exit.Disable()
                self.m_textCtrl_url.Disable()
                
                house = Timer(1.0, self.OnOK, args=(url, ))
                house.start()
                
            else:
                self.send_msg('錯誤:網址不合法')
                raise 
        
        except:
            pass
          
        self.m_textCtrl_url.Clear()
        
    def EXIT( self, event ):
        
        self.timer.cancel()
        app.ExitMainLoop()
    
    def OnOK(self, url):
    
        try:
            self.GetInformation(url)     
        except:
            pass
        
        self.m_textCtrl_url.Clear()
        self.m_button_ok.Enable()
        self.m_button_exit.Enable()
        self.m_textCtrl_url.Enable()
        
    def GetCss(self, tree, selector):
        data = tree.css(selector)
        if len(data) == 0:
            return ''
        else:
            return data[0].child.html
        
    def GetCssList(self, tree, selector):
        list_css = []
        for node in tree.css(selector):
            if node.last_child == None: continue
            # elif node.child.tag != '-text':
            #     if node.last_child.tag == 'span': continue
            list_css.append(node.text().replace('(', '').replace(')', '').replace(',', ''))
        return list_css
    
    def Combine(self, source1, source2, destination):
        for s1 in source1:
            for s2 in source2:
                if s1 in s2:
                    if s1.find('總價') != -1:
                        destination['總價'] = s2.replace(s1, '')[:s2.find('萬')-1] 
                    else:
                        if s1 not in destination.keys() or s1.find('建坪') != -1:
                            destination[s1] = s2.replace(s1, '')
    
    def GetString(self, data, start, end, start_add=0, end_add=0):
        
        get = ''
        find = 0
        addr = 0
        
        while(find != -1):
            if not start: find = 0
            else: find = data.find(start, addr)
            if find == -1: continue
            addr = find + len(start)
            if not end: find = len(data)
            else: find = data.find(end, addr)
            if find == -1: continue
            get = data[addr+start_add:find+end_add]
            break
        
        return get.strip()
        
    def GetInformation(self, url):

        try:
            
            yaml = METHOD.GetYaml(METHOD.PathJoin(METHOD.PathGetCurrent(), 'config.yaml'), 'big5')  
            file_output = METHOD.OrderedDict_Get('output.csv', yaml, '輸出路徑')
            file_check = METHOD.OrderedDict_Get('看屋評分檢核表 .xlsx', yaml, '檢核表路徑')
            # r = requests.get('https://www.sinyi.com.tw/buy/house/74590T')
            # if r.status_code != 200:
            #     return r.text
            path_root = '{}'.format(METHOD.PathGetCurrent())
            path_jpg = '{}\\照片'.format(path_root)
            path_csv = '{}\\{}'.format(path_root, file_output)
            METHOD.DirectoryMake('{}'.format(path_csv))
                        # path_excel = '{}\\output.xls'.format(path_root)
            path_check = '{}\\{}'.format(path_root, file_check)
     
            # url = 'https://www.sinyi.com.tw/buy/house/0537YK'
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')  # 啟動Headless 無頭
            chrome_options.add_argument('--disable-gpu') #關閉GPU 避免某些系統或是網頁出錯
            driver = webdriver.Chrome(options=chrome_options)
            # handle = driver.current_window_handle
            # win32gui.SetForegroundWindow({handle: win32con.SW_MINIMIZE})
            # driver.minmize_window()
            driver.get(url)
            self.send_msg('啟動webdriver')
            
            if '頁面不存在' in driver.title:
                self.send_msg('錯誤:頁面不存在')
            else:
                # f=codecs.open('{}\\{}'.format(path_root, path), 'r', 'utf-8')
                # if METHOD.FileExtension(path) != '.html':
                #     continue
                # text = f.read()
                
                if 'sinyi.com' in url:
                    
                    WebDriverWait(driver, 10, 0.5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'buy-content-title-id')))
                    tree =  HTMLParser(driver.page_source)
                      
                    tmp = [node.attributes for node in tree.css("[src$=jpg]")]
                    jpg_list_tmp = [jpg['src'] for jpg in tmp]
                    jpg_list = []
                    for jpg in jpg_list_tmp:
                        if jpg in jpg_list or not re.match('^https?:/{2}\w.+$', jpg): continue
                        jpg_list.append(jpg)
                                                       
                    dictData = {}
                    dictData['資料來源'] = '信義房屋'
                    dictData['網址'] = url
                    dictData['物件編號'] = self.GetCssList(tree, 'span.buy-content-title-id')[0]
                    dictData['地址'] = self.GetCssList(tree, 'span.buy-content-title-address')[0].replace('地址', '')
                    dictData['單價'] = self.GetCssList(tree, 'span.buy-content-title-uni-price')[0]
                                
                    self.Combine(self.GetCssList(tree, 'div.buy-content-cell-title'), self.GetCssList(tree, 'div.buy-content-cell'), dictData)                    
                    self.Combine(self.GetCssList(tree, 'div.basic-title'), self.GetCssList(tree, 'div.buy-content-basic-cell'), dictData)
                    self.Combine(self.GetCssList(tree, 'div.obj-title'), self.GetCssList(tree, 'div.buy-content-obj-cell'), dictData)                                                 
                    self.Combine(self.GetCssList(tree, 'div.basic-title'), self.GetCssList(tree, 'div.buy-content-obj-cell'), dictData)
                    self.Combine(self.GetCssList(tree, 'div.obj-title'), self.GetCssList(tree, 'div.buy-content-obj-cell-full-width'), dictData)
                    
                    data_empty = ''
                    for d in dictData:
                        if not d: data_empty += d + '\n'
                    if data_empty:
                        self.send_msg('抓取資訊失敗\n')
                        self.send_msg(data_empty)
                        raise
                   
                    self.send_msg('信義房屋網址解析')
                elif 'yungching.com' in url:
                    
                    WebDriverWait(driver, 10, 0.5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'house-info-num')))
                    tree =  HTMLParser(driver.page_source)
                    
                    dictData = {}
                    dictData['物件編號'] = self.GetCssList(tree, 'div.house-info-num')[0]
                    dictData['總價'] = self.GetCssList(tree, 'span.price-num')[0] + '萬'
                    dictData['網址'] = url
                    dictData['資料來源'] = '永慶房屋'
                    dictData['地址'] = self.GetCssList(tree, 'div.house-info-addr')[0]
                    
                    tmp = [node.text() for node in tree.css('section')]
                    for d in tmp:
                        s_tmp = []
                        if d.find('其他資訊') != -1 and d.find('詳細資料') == -1:
                            for s in d.split('\n'):
                                s1 = s.replace(' ', '').strip()
                                if not s1: continue
                                s_tmp.append(s1)                                       
                            
                            for v in range(len(s_tmp)):
                                if v == 1:
                                    dictData['社區'] = s_tmp[v]
                                else:
                                    if s_tmp[v].find('樓') != -1:
                                        dictData['樓層'] = s_tmp[v]
                                    if s_tmp[v].find('年') != -1:
                                        dictData['屋齡'] = s_tmp[v][:s_tmp[v].find('年')+1]
                                        dictData['類型'] = s_tmp[v][s_tmp[v].find('年')+1:]
                                    if s_tmp[v].find('(') != -1 and s_tmp[v].find(')') != -1:
                                        dictData['建物結構'] = s_tmp[v]
                                    if s_tmp[v].find('朝') != -1:
                                        dictData['建物朝向'] = s_tmp[v]
                                    if s_tmp[v].find('保全公司') != -1:
                                        dictData['警衛管理'] = s_tmp[v]
                                    if s_tmp[v].find('建物管理費：') != -1:
                                        dictData['管理費'] = s_tmp[v][s_tmp[v].find('建物管理費：')+6:]
                                        
                                   
                        else:
                            v = ''.join(d.split('\n')).replace(' ', '')
                              
                            if v.find('土地坪數：') != -1 and v.find('建物坪數：') != -1: 
                                dictData['地坪'] = v[v.find('土地坪數：')+5:v.find('建物坪數：')]
                            if v.find('建物坪數：') != -1 and v.find('主建物小計：') != -1: 
                                dictData['建坪'] = v[v.find('建物坪數：')+5:v.find('主建物小計：')]
                            if v.find('主建物小計：') != -1 and v.find('共同使用小計：') != -1: 
                                dictData['主建物'] = v[v.find('主建物小計：')+6:v.find('共同使用小計：')]
                            if v.find('共同使用小計：') != -1 and v.find('附屬建物小計：') != -1: 
                                dictData['共有部份'] = v[v.find('共同使用小計：')+7:v.find('附屬建物小計：')]
                            if v.find('附屬建物小計：') != -1 and v.find('土地使用分區：') != -1: 
                                dictData['陽台'] = v[v.find('附屬建物小計：')+7:v.find('土地使用分區：')]
                            if v.find('登記用途：') != -1 and v.find('房間格局') != -1: 
                                dictData['使用分區'] = v[v.find('登記用途：')+5:v.find('房間格局')]
                            if v[0:4] == '房間格局': 
                                dictData['格局'] = v[v.find('房間格局')+4:]   
                            if v[0:2] == '車位': 
                                dictData['車位'] = v[v.find('車位')+2:]
                            if v.find('房貸試算') != -1 and v.find('附近實價登錄') != -1: 
                                dictData['單價'] = v[v.find('房貸試算')+4:v.find('附近實價登錄')] 
                         
                    jpg_list = []
                    img = [node.attributes['src'] for node in tree.css("img")]
                    for url_tmp in img:
                        if 'https' not in url_tmp:
                            url = 'https:{}'.format(url_tmp)
                        else:
                            url = url_tmp
                        if url == None or url in jpg_list or not re.match('^https?:/{2}\w.+$', url): continue
                        if 'v1/image' in url and 'height=0' not in url:
                            jpg_list.append(url)
                                                      
                        data_empty = ''
                        for d in dictData:
                            if not d: data_empty += d + '\n'
                        if data_empty:
                            self.send_msg('抓取資訊失敗\n')
                            self.send_msg(data_empty)
                            raise
                         
                    self.send_msg('永慶房屋網址解析')
                    
                elif 'hbhousing.com' in url:
     
                    WebDriverWait(driver, 10, 0.5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'item_num')))
                    tree =  HTMLParser(driver.page_source)
                    
                    dictData = {}
                    dictData['資料來源'] = '住商不動產'
                    dictData['網址'] = url
                    dictData['物件編號'] = self.GetCssList(tree, 'p.item_num')[0].replace('物件編號', '').replace('：', '')
                    dictData['地址'] = self.GetCssList(tree, 'p.item_add')[0]
                    dictData['總價'] = self.GetCssList(tree, 'div.item_price')[0]
                    dictData['總價'] = dictData['總價'][:dictData['總價'].find('萬')+1]
                    dictData['單價'] = self.GetCssList(tree, 'div.item_space')[0]
                    
                    text = [node.text() for node in tree.css('tbody')]
                    data = text[0].replace('謄本資料', '').replace('相似屋齡', '').replace('相似樓層', '').replace('同朝向', '')
                    
                    dictData['建坪'] = self.GetString(data, '登記面積', '坪', 0, 1)
                    if not dictData['建坪']:
                        dictData['建坪'] = self.GetString(data, '登記建坪', '坪', 0, 1)
                    dictData['主建物'] = self.GetString(data, '主建物', '坪', 0, 1)
                    dictData['陽台'] = self.GetString(data, '附屬建物', '坪', 0, 1)
                    dictData['共有部份'] = self.GetString(data, '公共設施', '坪', 0, 1)
                    dictData['地坪'] = self.GetString(data, '土地坪數', '坪', 0, 1)
                    dictData['屋齡'] = self.GetString(data, '屋齡', '年', 0, 1)
                    dictData['使用分區'] = self.GetString(data, '法定用途', '樓層')
                    dictData['樓層'] = self.GetString(data, '樓層', '朝向') + '樓'
                    dictData['建物朝向'] = self.GetString(data, '朝向', '外牆建材')
                    dictData['外牆建材'] = self.GetString(data, '外牆建材', '面臨路寬')
                    dictData['面臨路寬'] = self.GetString(data, '面臨路寬', '管理費')
                    dictData['管理費'] = self.GetString(data, '管理費', '車位')
                    dictData['車位'] = self.GetString(data, '車位', '社區')
                    dictData['社區'] = self.GetString(data, '社區', '')
                    
                    jpg_list = []
                    img_photo__pattern = [node.last_child.html for node in tree.css("div.photo__pattern")]
                    img_photo = img_photo__pattern[0][img_photo__pattern[0].rfind('/')+1:img_photo__pattern[0].find('jpg')-2]
                    img = [node.attributes['src'] for node in tree.css("img")]
                    for url_tmp in img:
                        url = 'https:{}'.format(url_tmp)
                        if url == None or url in jpg_list or not re.match('^https?:/{2}\w.+$', url): continue
                        if 'img.hbhousing.com.tw' in url and img_photo in url:
                            jpg_list.append(url)
                        
                    data_empty = ''
                    for d in dictData:
                        if not d: data_empty += d + '\n'
                    if data_empty:
                        self.send_msg('抓取資訊失敗\n')
                        self.send_msg(data_empty)
                        raise
                    
                    self.send_msg('住商不動產網址解析')
                elif '591.com' in url:
     
                    WebDriverWait(driver, 10, 0.5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'breadList-last')))
                    tree =  HTMLParser(driver.page_source)
                    
                    dictData = {}
                    dictData['資料來源'] = '591'
                    dictData['網址'] = url
                    dictData['物件編號'] = self.GetCssList(tree, 'span.breadList-last')[0].replace('（', '').replace('）', '').replace('當前房屋', '').strip()
                    dictData['總價'] = self.GetCssList(tree, 'span.info-price-num')[0] + '萬' 
                    
                    tmp = self.GetCssList(tree, 'div.info-addr-content')
                    for d in tmp:
                        v = ''.join(d.split('\n')).replace(' ', '')
                        if v.find('樓層') != -1: 
                            dictData['樓層'] = v.replace('樓層', '')
                        elif v.find('社區') != -1: 
                            dictData['社區'] = v.replace('社區', '')
                        elif v.find('地址') != -1: 
                            dictData['地址'] = v.replace('地址', '')               
                        
                    tmp = [node.text() for node in tree.css('#container > section.img-and-info.clearfix > div.info-box > div.info-box-price > div > div.info-price-right > div.info-price-per')]
                    for d in tmp:
                        v = ''.join(d.split('\n')).replace(' ', '').replace(':', '')
                        if v.find('單價') != -1: 
                            dictData['單價'] = v.replace('單價', '')
    
                    
                    tmp = self.GetCssList(tree, 'div.info-floor-left')
                    for d in tmp:
                        v = ''.join(d.split('\n')).replace(' ', '')
                        if v.find('屋齡') != -1: 
                            dictData['屋齡'] = v.replace('屋齡', '')
                        elif v.find('權狀坪數') != -1: 
                            dictData['建坪'] = v.replace('權狀坪數', '')
                        elif v.find('格局') != -1: 
                            dictData['格局'] = v.replace('格局', '')
                            
                    tmp = self.GetCssList(tree, 'div.detail-house-content')
                    for d in tmp:
                        v = ''.join(d.split('\n')).replace(' ', '').replace('：', '')
                        if '現況' not in dictData and v.find('現況') != -1 and v.find('型態') != -1:
                            s = v[v.find('現況')+2:v.find('型態')]
                            dictData['現況'] = s
                        if '型態' not in dictData and v.find('型態') != -1 and v.find('裝潢程度') != -1:
                            s = v[v.find('型態')+2:v.find('裝潢程度')]
                            dictData['類型'] = s
                        if '裝潢程度' not in dictData and v.find('裝潢程度') != -1 and v.find('管理費') != -1:
                            s = v[v.find('裝潢程度')+4:v.find('管理費')]
                            dictData['裝潢程度'] = s
                        if '管理費' not in dictData and v.find('管理費') != -1 and v.find('帶租約') != -1:
                            s = v[v.find('管理費')+3:v.find('帶租約')]
                            dictData['管理費'] = s
                        if '帶租約' not in dictData and v.find('帶租約') != -1 and v.find('法定用途') != -1:
                            s = v[v.find('帶租約')+3:v.find('法定用途')]
                            dictData['帶租約'] = s
                        if '使用分區' not in dictData and v.find('法定用途') != -1 and v.find('車位') != -1:
                            s = v[v.find('法定用途')+4:v.find('車位')]
                            dictData['使用分區'] = s
                        if '車位' not in dictData:
                            if v.find('車位') != -1 and v.find('公設比') != -1 :
                                s = v[v.find('車位')+2:v.find('公設比')]
                            else:
                                s = v[v.find('車位')+2:]
                            dictData['車位'] = s
                        if '公設比' not in dictData and v.find('公設比') != -1 :
                            s = v[v.find('公設比')+3:]
                            dictData['公設比'] = s
                        if '主建物' not in dictData and v.find('主建物') != -1 and v.find('共用部分') != -1:
                            s = v[v.find('主建物')+3:v.find('共用部分')]
                            dictData['主建物'] = s
                        if '共有部份' not in dictData and v.find('共用部分') != -1 and v.find('附屬建物') != -1:
                            s = v[v.find('共用部分')+4:v.find('附屬建物')]
                            dictData['共有部份'] = s
                        if '陽台' not in dictData and v.find('附屬建物') != -1 and v.find('土地坪數') != -1:
                            s = v[v.find('附屬建物')+4:v.find('土地坪數')]
                            dictData['陽台'] = s  
                        if '地坪' not in dictData and v.find('土地坪數') != -1:
                            s = v[v.find('土地坪數')+4:]
                            dictData['地坪'] = s  
                            
                    jpg_list = []
                    # img_photo__pattern = [node.last_child.html for node in tree.css("div.photo__pattern")]
                    # img_photo = img_photo__pattern[0][img_photo__pattern[0].rfind('/')+1:img_photo__pattern[0].find('jpg')-2]
                    img = [node.attributes['src'] for node in tree.css("img")]
                    for url_tmp in img:
                        if 'https' not in url_tmp:
                            url = 'https:{}'.format(url_tmp)
                        else:
                            url = url_tmp
                        if url == None or url in jpg_list or not re.match('^https?:/{2}\w.+$', url): continue
                        if 'img1.591.com.tw' in url or 'img2.591.com.tw' in url:
                            jpg_list.append(url)
                            
                    data_empty = ''
                    for d in dictData:
                        if not d: data_empty += d + '\n'
                    if data_empty:
                        self.send_msg('抓取資訊失敗\n')
                        self.send_msg(data_empty)
                        raise 
                    
                    self.send_msg('591網址解析')
                else:
                    self.send_msg('錯誤:非房屋網址')
                    raise
                
                house = {'地址' : '', 
                         '物件編號' : '', 
                         '記錄日期' : '',
                         '詳細地址' : '',
                         '社區' : '',
                         '總價' : '', 
                         '單價' : '', 
                         '屋齡' : '', 
                         '建坪' : '', 
                         '地坪' : '', 
                         '主+陽' : '', 
                         '共有部份' : '', 
                         '主建物' : '', 
                         '陽台' : '',
                         '車位' : '',
                         '公設比' : '',  
                         '樓層' : '', 
                         '格局' : '', 
                         '加蓋格局' : '', 
                         '類型' : '', 
                         '警衛管理' : '', 
                         '管理費' : '', 
                         '建物朝向' : '', 
                         '落地窗朝向' : '', 
                         '邊間/暗房' : '', 
                         '建物結構' : '', 
                         '外牆建材' : '', 
                         '每層戶數' : '', 
                         '謄本用途' : '', 
                         '使用分區' : '',
                         '面臨路寬' : '',
                         '裝潢程度' : '',
                         '帶租約' : '',
                         '注意事項' : '', 
                         '網址' : '',
                         '資料來源' : ''
                         }
                           
                for key, value in house.items():      # @UnusedVariable
                    if key in dictData: 
                        if not dictData[key]:
                            dictData[key] = '--'
                        house[key] = dictData[key].replace(',', '')
                    else:
                        house[key] = '--' 
                        
                if '記錄日期' in house:
                    date = METHOD.TimeGet('%Y/%m/%d')
                    house['記錄日期'] = date
                    
                keys = [key for key in house]
                values = [value for key, value in house.items()]
                      
                df = pandas.read_csv(StringIO(','.join(values)), sep=",", header=None, names=keys)
                # df.fillna('--')
                
                df_new = pandas.DataFrame()
                
                if METHOD.IsFileExist(path_csv):
                    exist_any = True
                    df_old = pandas.read_csv(path_csv, encoding='big5hkscs')
                    
                    exist_any &= df_old['地址'].eq(house['地址']).any()
                    exist_any &= df_old['屋齡'].eq(house['屋齡']).any()
                    exist_any &= df_old['建坪'].eq(house['建坪']).any()
                    exist_any &= df_old['主建物'].eq(house['主建物']).any()
                    exist_any &= df_old['樓層'].eq(house['樓層']).any()        
                
                    if exist_any == False:
                        df_new = pandas.concat([df_old, df], ignore_index=True)
                    else:
                        self.send_msg('重複物件:{}_{}'.format(df.at[0, '地址'], df.at[0, '物件編號']))
                else:
                    df_new = df
                    
                if not df_new.empty:
                                   
                    path = os.path.join(path_jpg, '{}_{}'.format(df.at[0, '地址'], df.at[0, '物件編號']))
                    METHOD.DirectoryMake('{}\\A.JPG'.format(path))
                    if 'sinyi.com' in house['網址']:
                        [urllib.request.urlretrieve(url, os.path.join(path , url.split('/')[-1])) for url in jpg_list]                 
                    elif 'yungching.com' in house['網址']:
                        count = 1
                        for url in jpg_list:                      
                            jpg = '{}.jpg'.format(count)
                            count += 1
                            urllib.request.urlretrieve(url, os.path.join(path , jpg))
                    elif 'hbhousing.com' in house['網址']:
                        count = 1
                        for url in jpg_list:
                            jpg = '{}.jpg'.format(count)
                            count += 1
                            urllib.request.urlretrieve(url, os.path.join(path , jpg))
                    elif '591.com' in house['網址']:
                        count = 1
                        for url in jpg_list:
                            jpg = '{}.jpg'.format(count)
                            count += 1
                            urllib.request.urlretrieve(url, os.path.join(path , jpg))
                            
                    df_new.to_csv(path_csv, index=False, encoding='big5hkscs')
                    # df_new.to_excel(path_excel, index=False, encoding='UTF-8')
                
                    path_check_new = '{}\\{}\\{}_{}.xlsx'.format(path_root, file_check.split('.')[0], df.at[0, '地址'], df.at[0, '物件編號'])
                    METHOD.DirectoryMake('{}'.format(path_check_new))
                    METHOD.FileCopy(path_check, path_check_new)
                    
                    self.send_msg('匯出檔案:{}_{}'.format(df.at[0, '地址'], df.at[0, '物件編號']))
        except:
            
            LOGGER.Record("ERROR", "{} : {}.".format([s for s in str(sys.exc_info()[0]).split('\'')][1], sys.exc_info()[1]))   
            traceback.print_tb(sys.exc_info()[2])
            self.send_msg('錯誤:'"{} : {}.".format([s for s in str(sys.exc_info()[0]).split('\'')][1], sys.exc_info()[1]))
    
        finally:
            driver.close()
            driver.quit()    
    
    
if __name__ == '__main__':

    app = wx.App()
    frm = MyHouse(None)
    frm.Show()
    app.MainLoop()

    
   
        