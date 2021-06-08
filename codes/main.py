#by concyclics
import databaseOP
import creeper
import fundation
from alive_progress import alive_bar
import datetime
import time
import chart1
import os
import sys
import platform

danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
qieman.sort() 

            

if __name__=='__main__':
    
    DB=databaseOP.DBconnect(password='19260817')
    if DB==False:
        print('MySQL数据库链接失败！尝试打开数据库')
        
        if platform.system()=='Darwin':
            os.system('/usr/local/MySQL/support-files/mysql.server start')
        elif platform.system()=='Windows':
            os.system('net start mysql')
        elif platform.system()=='Linux':
            os.system('service mysql start')
            
        DB=databaseOP.DBconnect(password='19260817')
        if DB==False:
            raise ConnectionError('MySQL数据库链接失败！')

    if databaseOP.DBexist(DB)==False:
        databaseOP.DBinit(DB)
        print("数据库不存在，正重新创建")
    
    databaseOP.update(DB)
                
    win = chart1.Window()
    win.main()
                