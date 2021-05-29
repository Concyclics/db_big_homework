#by concyclics
import requests
import time
import json
import fundation
import datetime

#获取失败返回ValueError

#蛋卷基金爬虫
header_for_danjuan={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']

#x-sign记得每天更新
header_for_qieman={
'x-sign':'1622257424529E36D03062A5903D91302F2E81F164D94'
}

#获取当天信息
def getfund_danjuan(code):
    url='https://danjuanapp.com/djapi/plan/'+code
    page=requests.get(url,headers=header_for_danjuan).text
    
    items=json.loads(page)
    if items.get('result_code')==91003:
        raise ValueError('请检查code')
        
    items=items.get("data")
    
    value=items.get('plan_derived').get("unit_nav")
    date=items.get('plan_derived').get("end_date")
    name=items.get('plan_name')
    found=items.get('found_date')
    
#    print("基金编号:",code,'\n基金名:',name,"\n日期:",date,"净值:",value)
    
    url='https://danjuanapp.com/djapi/plan/nav/indicator?plan_code='+code
    page=requests.get(url,headers=header_for_danjuan).text
    
    items=json.loads(page)
    items=items.get("data")
    
    maxdown=items.get('max_drawdown')
    maxdown=float(maxdown)
    volatility=items.get('volatility')
    volatility=float(volatility)
    sharpe=items.get('sharpe')
    sharpe=float(sharpe)
    
#    print('最大回撤:',maxdown,'年化波动率:',volatility,'夏普率:',sharpe,'\n')   
    
    return fundation.fund(code=code,name=name,found_date=found,sharp_rate=sharpe,max_down=maxdown,volatility=volatility)
    
    
    
#获取历史净值
def gethistory_danjuan(code, size=10000):
    
    try: int(size)
    except ValueError:
        print("输入整数")
        return 
    size=int(size)
    if size<=0:
        print("输入正数")
        return
    
    url='https://danjuanapp.com/djapi/plan/nav/history/'+code+'?size='+str(size)+'&page=1'
    page=requests.get(url,headers=header_for_danjuan).text
    
    items=json.loads(page)
    if items.get('result_code')==91003:
        raise ValueError('请检查code')
        
    items=items.get("data").get("items")
    
    list=[]
    
    for item in items:
        day=item.get('date')
        value=item.get('value')
        value=float(value)
        
        list.append(fundation.history(code=code,day=day,value=value))
    
    return list


#且慢的时间戳转日期
def qieman_to_date(s):
    s=int(s)
    s/=1000
    day=datetime.datetime.utcfromtimestamp(s).strftime('%Y-%m-%d')
    return day

def getfund_qieman(code):
    url='https://qieman.com/pmdj/v1/pomodels/'+code
    page=requests.get(url,headers=header_for_qieman).text
    
    if(page==''):
        raise ValueError('请设置x-sign或检查code')
    
    items=json.loads(page)
    
    value=items.get("nav")
    date=items.get("navDate")
    name=items.get("poName")
    found=items.get('establishedOn')
    
    
    maxdown=items.get("maxDrawdown")
    maxdown=float(maxdown)
    volatility=items.get("volatility")
    volatility=float(volatility)
    sharpe=items.get("sharpe")
    sharpe=float(sharpe)
    
    return fundation.fund(code=code,name=name,found_date=found,sharp_rate=sharpe,max_down=maxdown,volatility=volatility)
    
#获取历史净值
def gethistory_qieman(code,size=10000):
    
    url='https://qieman.com/pmdj/v1/pomodels/'+code+'/nav-history'
    page=requests.get(url,headers=header_for_qieman).text
    
    if(page==''):
        raise ValueError('请设置x-sign或检查code')
    
    items=json.loads(page)
    
    list=[]
    
    for item in items[-1:-size-1:-1]:
        day=qieman_to_date(item.get('navDate'))
        value=item.get('nav')
        value=float(value)
    
        list.append(fundation.history(code=code,day=day,value=value))
        
    return list
    
if __name__=='__main__':
    for code in danjuan:
        fund=getfund_danjuan(code)
        fund.display()
        historys=gethistory_danjuan(code,10)
        for i in historys:
            i.display()
        
    for code in qieman:
        fund=getfund_qieman(code)
        fund.display()
        historys=gethistory_qieman(code,10)
        for i in historys:
            i.display()