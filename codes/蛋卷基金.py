#by concyclics
import requests
import time
import json


header={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

#获取当天信息
def getfund(code):
    url='https://danjuanapp.com/djapi/plan/'+code
    page=requests.get(url,headers=header).text
    
    items=json.loads(page)
    items=items.get("data")
    
    value=items.get('plan_derived').get("unit_nav")
    date=items.get('plan_derived').get("end_date")
    name=items.get('plan_name')
    
    print("基金编号:",code,'\n基金名:',name,"\n日期:",date,"净值:",value)
    
def getdetail(code):
    url='https://danjuanapp.com/djapi/plan/nav/indicator?plan_code='+code
    page=requests.get(url,headers=header).text
    
    items=json.loads(page)
    items=items.get("data")
    
    maxdown=items.get('max_drawdown')
    volatility=items.get('volatility')
    sharpe=items.get('sharpe')
    
    print('最大回撤:',maxdown,'年化波动率:',volatility,'夏普率:',sharpe,'\n')
    

#获取历史净值
def gethistory(code, size):
    
    try: int(size)
    except ValueError:
        print("输入整数")
        return 
    size=int(size)
    if size<=0:
        print("输入正数")
        return
    
    url='https://danjuanapp.com/djapi/plan/nav/history/'+code+'?size='+str(size)+'&page=1'
    page=requests.get(url,headers=header).text
    
    items=json.loads(page)
    items=items.get("data").get("items")
    
    for item in items:
        print('日期:',item.get('date'),'净值:',item.get('value'))
    print('\n')

if __name__=='__main__':
    for code in danjuan:
        getfund(code)
        getdetail(code)
        gethistory(code,10)
        
        