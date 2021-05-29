#by concyclics
import databaseOP
import creeper
import fundation
from alive_progress import alive_bar


danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
qieman.sort() 

if __name__=='__main__':
    with databaseOP.DBconnect(password='root') as DB, alive_bar(len(danjuan+qieman)) as bar:
        #databaseOP.DBinit(DB)
        for code in danjuan+qieman:
            databaseOP.addFund(DB,creeper.getFund(code))
            bar()
            for history in creeper.getHistory(code,10000):
                databaseOP.addHistory(DB, history)