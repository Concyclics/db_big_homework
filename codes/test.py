#by concyclics
#by concyclics
import databaseOP
import creeper
import fundation



danjuan=['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
danjuan.sort()

qieman=['ZH001798','ZH012926','ZH039471','ZH010246','ZH006498','ZH000193','ZH009664','ZH030684','ZH017252','ZH007973','ZH037807','ZH007974','ZH017409','ZH035411','ZH043108','ZH043126']
qieman.sort() 

if __name__=='__main__':
    codes=danjuan+qieman
    creeper.getFund(codes[14]).display()
    creeper.getHistory(codes[14])