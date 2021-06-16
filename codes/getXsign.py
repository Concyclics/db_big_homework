from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json


def getXsign():

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
                    return info['request']['headers']['x-sign']
                    
    browser.close()
        
if __name__=='__main__':
    print(getXsign())