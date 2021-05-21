#by concyclics
import requests


qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']

url='https://qieman.com/pmdj/v1/pomodels/ZH043108/nav-history'



head={
'Accept':'application/json',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
'Connection':'keep-alive',
'Host':'qieman.com',
'Referer':'https://qieman.com/portfolios/ZH043108',
'sec-ch-ua':'\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Microsoft Edge\";v=\"90\"',
'sec-ch-ua-mobile':'?0',
'Sec-Fetch-Dest':'empty',
'Sec-Fetch-Mode':'cors',
'Sec-Fetch-Site':'same-origin',
'sensors-anonymous-id':'179846e5cc3f9e-0829c76cb06d02-79670e5f-1764000-179846e5cc4e6a',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62',
'x-aid':'A.89E6C0E01F626WKBNDHW8K17N48X508J6',
'x-request-id':'albus.840A00E6BEAC0A65A48B',
'x-sign':'162156650843332A579E8505A7B5A7BB5CB69D6AA6BDD'
}
#1621566508433」32A579E8505A7B5A7BB5CB69D6AA6BDD
#前13位为时间戳，后32位未知
print(requests.get(url,headers=head).text)

