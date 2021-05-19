#by concyclics
import requests
import time
import json


header={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

def getfund(code):
    url='https://danjuanapp.com/djapi/plan/'+code
    page=requests.get(url,headers=header).text
    
    items=json.loads(page)
    items=items.get("data")
    
    value=items.get('plan_derived').get("unit_nav")
    date=items.get('plan_derived').get("end_date")
    
    print("基金编号:",code,"\n日期:",date,"净值",value,"\n")

for id in danjuan:
    getfund(id)
    