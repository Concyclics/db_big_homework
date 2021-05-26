# coding=utf8
from selenium import webdriver  #需要安装selenium库
import time
import bs4  #需要安装bs4库
import re
from selenium.webdriver.common import desired_capabilities

qiemancode = ['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
qiemanURL = "https://qieman.com/portfolios/"

findname = re.compile(r'<div class="qm-header qm-header-1">(.*?)</div>')
finddata = re.compile(r'<span class="qm-amount qm-amount-std">(.*?)</span>')
findwithdrawal = re.compile(r'<span class="qm-percent qm-percent-std">(.*?)</span>')

def getfund(code):  #获取当日净值等信息
    try:
        code = str(code)
    except:
        print("wrong code!")
        return False
    datalist = []
    #需要在windows上安装PhantomJS,一个无头浏览器,path为exe文件路径
    #PhantomJS下载地址: https://phantomjs.org/download.html
    driver = webdriver.PhantomJS(executable_path=r"C:\Users\86178\Desktop\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    driver.get(qiemanURL+code)
    content = driver.page_source.encode("utf-8")
    soup = bs4.BeautifulSoup(content,"html.parser")
    for item in soup.find_all('div'):
        item = str(item)
        name = re.findall(findname,item)[0]#基金名称
        data = re.findall(finddata,item)[1]#净值
        sharp = re.findall(finddata,item)[2]#夏普率
        withdrawal = re.findall(findwithdrawal,item)[0]#最大回撤
        volatility = re.findall(findwithdrawal,item)[1]#年化波动率
        datalist.append(['基金编号',code])
        datalist.append(['基金名称',name])
        datalist.append(['当日净值',data])
        datalist.append(['夏普率',sharp])
        datalist.append(['最大回撤',withdrawal])
        datalist.append(['年化波动率',volatility])
        # print('基金名称:',name)
        # print('当日净值:',data)
        # print('夏普率:',sharp)
        # print('最大回撤: ',withdrawal,'%',sep='')
        # print('年化波动率: ',volatility,'%',sep='')
        break
    del driver,item,soup,content
    return datalist

for code in qiemancode:
    datalist = getfund(code)
    for data in datalist:
        print(data[0],': ',data[1],sep='')
    print('\n')
    time.sleep(2)