#by concyclics
import databaseOP
import creeper
import fundation
from alive_progress import alive_bar
import datetime
import time
import os
import sys
import platform
import Tips
import chart1
import getXsign

danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
qieman.sort()

            

if __name__=='__main__':
    
    if Tips.welcomeWindow()==False:
        sys.exit(0)
    #Tips.welcomeWindow()
    #Tips.failWindow()
    
    DB=databaseOP.DBconnect(password='19260817')
    if DB==False:
        if Tips.ensureWindow('数据库链接失败！','MySQL数据库链接失败！是否尝试打开数据库？')==False:
            sys.exit(0)
        
        if platform.system()=='Darwin':
            os.system('/usr/local/MySQL/support-files/mysql.server start')
        elif platform.system()=='Windows':
            os.system('net start mysql')
        elif platform.system()=='Linux':
            os.system('service mysql start')
        
        time.sleep(0.5)
        DB=databaseOP.DBconnect(password='19260817')
        if DB==False:
            raise ConnectionError('MySQL数据库链接失败！')

    if databaseOP.DBexist(DB)==False:
        databaseOP.DBinit(DB)
        if Tips.ensureWindow('数据库不存在！',"数据库不存在，是否重新创建？")==False:
            sys.exit(0)
        xsign = getXsign.getXsign()
        if xsign != False:
            creeper.header_for_qieman['x-sign'] = xsign
        with alive_bar(len(qieman+danjuan)) as bar:
            for code in qieman+danjuan:
                databaseOP.updateFundInfo(DB,code)
                bar()
    else:
        xsign = getXsign.getXsign()
        if xsign != False:
            creeper.header_for_qieman['x-sign'] = xsign
            if Tips.ensureWindow('更新数据','是否更新数据？')==True:
                databaseOP.update_mult(DB)
                Tips.TipsWindow('数据更新完毕!')
        else:
            if Tips.ensureWindow('无法连接网络',"无法连接网络，是否进入离线模式？")==False:
                sys.exit(0)

    
    DB.close()
                
    win = chart1.Window()
    win.main()
                