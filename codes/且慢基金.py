#by concyclics
import requests
import time
import json
import datetime

qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']

#x-sign记得每天更新
header={
'x-sign':'162208614727786A25459D7CF9AA74ECF7F4A32AEBF39'
}
#1621566508433」32A579E8505A7B5A7BB5CB69D6AA6BDD
#前13位为时间戳，后32位未知

#且慢的时间戳转日期
def qieman_to_date(s):
	s=int(s)
	s/=1000
	day=datetime.datetime.utcfromtimestamp(s).strftime('%Y-%m-%d')
	return day

def getfund(code):
	url='https://qieman.com/pmdj/v1/pomodels/'+code
	page=requests.get(url,headers=header).text
	
	items=json.loads(page)
	
	
	value=items.get("nav")
	date=items.get("navDate")
	name=items.get("poName")
	
	print("基金编号:",code,'\n基金名:',name,"\n日期:",date,"净值:",value)
	
	maxdown=items.get("maxDrawdown")
	volatility=items.get("volatility")
	sharpe=items.get("sharpe")
	
	print('最大回撤:',maxdown,'年化波动率:',volatility,'夏普率:',sharpe,'\n')
	
#获取历史净值
def gethistory(code,size=10):
	
	url='https://qieman.com/pmdj/v1/pomodels/'+code+'/nav-history'
	page=requests.get(url,headers=header).text
	
	
	items=json.loads(page)

	for item in items[-1:-size-1:-1]:
		print('日期:',qieman_to_date(item.get('navDate')),'净值:',item.get('nav'))
	print('\n')
	
if __name__=='__main__':
	for code in qieman:
		getfund(code)
		gethistory(code)
		