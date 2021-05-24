#by concyclics
import pymysql



def DBconnect(hosts='localhost',username='root',password='19260817'):
    try: pymysql.connect(host=hosts,user=username,passwd=password)
    except :
        DB='link failed!'
        return False
    else:
        database=pymysql.connect(host=hosts,user=username,passwd=password)
        return database
    
    
def DBinit(database):
    if type(database).__name__!='Connection':
        return False
    

'''
cursor=DB.cursor()
print(cursor)

'''
if __name__=='__main__':
    DB=DBconnect()
    print(DBinit(DB))