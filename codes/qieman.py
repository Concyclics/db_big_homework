# coding=gbk
from selenium import webdriver
import time
import bs4  #��Ҫ��װ��bs4��
import re
from selenium.webdriver.common import desired_capabilities

qiemancode = ['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
qiemanURL = "https://qieman.com/portfolios/"

findname = re.compile(r'<div class="qm-header qm-header-1">(.*?)</div>')
finddata = re.compile(r'<span class="qm-amount qm-amount-std">(.*?)</span>')
findwithdrawal = re.compile(r'<span class="qm-percent qm-percent-std">(.*?)</span>')

def getfund(code):  #��ȡ���վ�ֵ����Ϣ
    try:
        code = str(code)
    except:
        print("wrong code!")
        return False
    datalist = []
    #��Ҫ��windows�ϰ�װPhantomJS,һ����ͷ�����,pathΪexe�ļ�·��
    driver = webdriver.PhantomJS(executable_path=r"C:\Users\86178\Desktop\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    driver.get(qiemanURL+code)
    content = driver.page_source.encode("utf-8")
    soup = bs4.BeautifulSoup(content,"html.parser")
    for item in soup.find_all('div'):
        item = str(item)
        name = re.findall(findname,item)[0]#��������
        data = re.findall(finddata,item)[1]#��ֵ
        sharp = re.findall(finddata,item)[2]#������
        withdrawal = re.findall(findwithdrawal,item)[0]#���س�
        volatility = re.findall(findwithdrawal,item)[1]#�껯������
        datalist.append(['������',code])
        datalist.append(['��������',name])
        datalist.append(['���վ�ֵ',data])
        datalist.append(['������',sharp])
        datalist.append(['���س�',withdrawal])
        datalist.append(['�껯������',volatility])
        # print('��������:',name)
        # print('���վ�ֵ:',data)
        # print('������:',sharp)
        # print('���س�: ',withdrawal,'%',sep='')
        # print('�껯������: ',volatility,'%',sep='')
        break
    del driver,item,soup,content
    return datalist

for code in qiemancode:
    datalist = getfund(code)
    for data in datalist:
        print(data[0],': ',data[1],sep='')
    print('\n')
    time.sleep(2)