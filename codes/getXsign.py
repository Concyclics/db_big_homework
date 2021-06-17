from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time
import datetime
import creeper


def getX_sign():

    url = 'https://qieman.com'
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'performance': 'ALL'}

    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    browser = webdriver.Chrome(options=option)


    browser.get(url)


    info = browser.get_log('performance')
    #print(info)

    for i in info:
        dic_info = json.loads(i["message"]) 
        info = dic_info["message"]['params'] 
        if 'request' in info:  
            #print(info['request'])
            if 'headers' in info['request']:
                #print(info['request']['headers'])
                if 'x-sign' in info['request']['headers']:
                    # print(info['request']['headers']['x-sign'])
                    return info['request']['headers']['x-sign']
    
    browser.close()
    return False


def getXsign():
    
    
    t=int(creeper.header_for_qieman['x-sign'][0:13])//1000
    
    last=time.localtime(t)
    last=datetime.datetime(last[0],last[1],last[2])
    
    
    today=time.localtime(time.time())
    today=datetime.datetime(today[0],today[1],today[2])
    diff=(today-last).days
    
    #print(t,last,today,diff)
    
    if diff==0:
        return creeper.header_for_qieman['x-sign']
    
    try:
        getX_sign()
    except Exception:
        return False
    
    return getX_sign()

if __name__=='__main__':
    print(getXsign())