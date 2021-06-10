# by concyclics
import pymysql
import fundation
import creeper
import time
import datetime
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count

#链接数据库
def DBconnect(hosts='localhost',*, username='root', password='19260817'):
    try:
        pymysql.connect(host=hosts, user=username, passwd=password)
    except:
        return False
    else:
        database = pymysql.connect(host=hosts, user=username, passwd=password)
        return database


#sql命令分段
def splitSql(sql: str):
    sqllist = sql.split(';')
    return sqllist[0:-1]


#检测数据库是否存在
def DBexist(database):
    cursor = database.cursor()
    try:
        cursor.execute("USE fundation;")
    except Exception:
        return False
    
    return True

#数据库初始化
def DBinit(database):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    reset_sql = """
    drop database if exists fundation;
    create database fundation;
    use fundation;
    create table funds
    (
        code varchar(20),
        name varchar(255),
        found_date date,
        sharp_rate float,
        max_down float,
        volatility float,
        primary key(code)
    );
    create table history
    (
        code varchar(20),
        value float not null check (value>=0),
        day date,
        primary key(code,day),
        foreign key(code) references funds(code)
            on delete cascade
            on update cascade
    );
    delete from funds;
    delete from history;
    create index code_ind on funds(code);
    create index code_ind on history(code);
    create index value_ind on history(value);
    create index day_ind on history(day);
    """
    try:
        for line in splitSql(reset_sql):
            cursor.execute(line)
            database.commit()
    except:
        database.rollback()
    else:
        return True


#多线程测试
def update_mult():
    pool=ThreadPool(cpu_count())
    
    DB=DBconnect('localhost',username='root',password='19260817')
    
    def mult_uni(code:str):
        DB11=DBconnect('localhost',username='root',password='19260817')
        updateFundInfo(DB11,code)
        DB11.close()
    
    for code in getFundlist(DB):
        pool.apply_async(mult_uni,(code[0],))
        
    pool.close()
    pool.join()
    
    DB.close()
    


def updateALL(DB):
    
    for code in getFundlist(DB):
        code=code[0]
        
        tmp=creeper.getFund(code)
        updateFund(DB,code,tmp)
            
        last=getLatestDate(DB,code)
        if last == False:
            diff=10000
        else:
            last=time.strptime(last,'%Y-%m-%d')
            last=datetime.datetime(last[0],last[1],last[2])
            today=time.localtime(time.time())
            today=datetime.datetime(today[0],today[1],today[2])
            diff=(today-last).days
            
        for history in creeper.getHistory(code,diff):
            addHistory(DB, history)
            
            
def updateFundInfo(DB,code:str):
        
    #print(code+' start')
    
    tmp=creeper.getFund(code)
    if addFund(DB,tmp)==False:
        updateFund(DB,code,tmp)
            
    last=getLatestDate(DB,code)
    if last == False:
        diff=10000
    else:
        last=time.strptime(last,'%Y-%m-%d')
        last=datetime.datetime(last[0],last[1],last[2])
        today=time.localtime(time.time())
        today=datetime.datetime(today[0],today[1],today[2])
        diff=(today-last).days
        
    for history in creeper.getHistory(code,diff):
        addHistory(DB, history)
        
        #print(code+' end')

def addFund(database, fund1: fundation.fund):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_insert = "(\"" + str(fund1.code) + "\", \"" + str(fund1.name) + "\", \"" + str(fund1.found_date) \
                 + "\", " + str(fund1.sharp_rate) + ", " + str(fund1.max_down) \
                 + ", " + str(fund1.volatility) + ");"
    insert_sql = """
         USE fundation;
         INSERT INTO funds(CODE, NAME, FOUND_DATE, SHARP_RATE, MAX_DOWN, VOLATILITY)
         VALUES""" + sql_insert
    # print(insert_sql)
    try:
        for line in splitSql(insert_sql):
            cursor.execute(line)
            database.commit()
    except Exception:
        database.rollback()
        return False
    else:
        return True


def addHistory(database, History1: fundation.history):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_insert = "(\"" + str(History1.code) + "\", \"" + str(History1.day) \
                 + "\", " + str(History1.value) + ");"
    insert_sql = """
         USE fundation;
         INSERT INTO history(CODE, DAY, VALUE) 
         VALUES""" + sql_insert
    # print(insert_sql)
    try:
        for line in splitSql(insert_sql):
            cursor.execute(line)
            database.commit()
    except Exception:
        database.rollback()
        return False
    else:
        return True


def getFund(database, code: str):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_select = """
    select *
    from funds
    where code = \"""" + str(code) + "\";"
    # print(sql_select)
    cursor.execute('use fundation;')
    try:
        cursor.execute(sql_select)
        row = cursor.fetchone()
        # print(row)
        fund2 = fundation.fund(code=row[0], name=row[1], found_date=row[2], sharp_rate=row[3], max_down=row[4],
                               volatility=row[5])
    except Exception:
        database.rollback()
        return False
    else:
        return fund2

def getHistory(database, code: str, begin_time, end_time):
    if type(database).__name__ != 'Connection':
        return False
    if begin_time > end_time:
        return False
    cursor = database.cursor()
    sql_select = """
    select *
    from history
    where code = \"""" + str(code) + "\" and day >= \"" + str(begin_time) + "\" and day <= \"" + str(end_time) + "\";"
    #print(sql_select)
    return_value = list()
    try:
        cursor.execute("USE fundation;")
        cursor.execute(sql_select)
        total = cursor.fetchall()
        for row in total:
            history2 = fundation.history(code=row[0], day=row[2], value=row[1])
            return_value.append(history2)
        # print(row)

    except Exception:
        database.rollback()
        return False
    else:
        return return_value


def getFundlist(database):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_select = """
    select code
    from funds;"""
    #print(sql_select)
    cursor.execute('use fundation;')
    return_value = list();
    try:
        cursor.execute(sql_select)
        total = cursor.fetchall()
        for row in total:
            temp = row;
            return_value.append(temp)
        # print(row）

    except Exception:
        database.rollback()
        return False
    else:
        return return_value

def checkFund(database, code: str):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_select = """
    select *
    from funds
    where code = \"""" + str(code) + "\";"
    #print(sql_select)
    try:
        cursor.execute("USE fundation;")
        cursor.execute(sql_select)
        total = cursor.fetchall()
        for line in total:
            return True
        return False
    except Exception:
        database.rollback()
        return False
    else:
        return False

def checkHistory(database, code:str, day):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_select = """
    select *
    from history
    where code = \"""" + str(code) + "\" and day = \"" + str(day) + "\";"
    #print(sql_select)
    try:
        cursor.execute("USE fundation;")
        cursor.execute(sql_select)
        total = cursor.fetchall()
        for line in total:
            return True
        return False
        # print(row)
    except Exception:
        database.rollback()
        return False
    else:
        return False

def updateFund(database, code:str, fund1:fundation.fund):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    update_sql = """
    use fundation;
    UPDATE funds
    set found_date = \"""" + str(fund1.found_date) + "\", sharp_rate = "\
    + str(fund1.sharp_rate) + ", max_down = "\
    + str(fund1.max_down) + ", volatility = "\
    + str(fund1.volatility)\
    +"""
    where code = \"""" + str(code) + "\";"
    #print(update_sql)
    try:
        for line in splitSql(update_sql):
            cursor.execute(line)
            database.commit()
    except Exception:
        database.rollback()
        return False
    else:
        return True

def updateHistory(database, code:str, day, history1:fundation.history):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    update_sql = """
    use fundation;
    UPDATE history
    set value = """ + str(history1.value) \
    +"""
    where code = \"""" + str(code) + "\" and day = \"" + str(day) + "\";"
    #print(update_sql)
    try:
        for line in splitSql(update_sql):
            cursor.execute(line)
            database.commit()
    except Exception:
        database.rollback()
        return False
    else:
        return True

def getLatestDate(database, code:str):
    if type(database).__name__ != 'Connection':
        return False
    cursor = database.cursor()
    sql_select = """
    select *
    from history
    where code = \"""" + str(code) + "\""\
    +"\norder by day desc;"
    #print(sql_select)
    cursor.execute('use fundation;')
    try:
        cursor.execute(sql_select)
        row = cursor.fetchone()
        # print(row)
        fund3 = fundation.history(code=row[0], day=row[2], value=row[1])
    except Exception:
        database.rollback()
        return False
    else:
        return str(fund3.day)

if __name__ == '__main__':
    #DB = DBconnect()
    #print(DBinit(DB))
    #updateFundInfo(DB,'CSI1029')
    print(cpu_count())
    #print("OK")
    #updateALL(DB)
    print("OK")
    
    update_mult()
    print("OK2")
    #print(DBexist(DB))
#    fund1 = fundation.fund(code='1122')
#    history1 = fundation.history(code='1122', day='2000-01-01')
#    print(addFund(DB, fund1))
#    print(addHistory(DB, history1))
#    fund2 = getFund(DB, "1122")
#    fund2.display()
#    print(checkFund(DB, "1122"))
#    print(checkHistory(DB, "1122", "2000-01-01"))
#    history_set = getHistory(DB, "1122", '1999-10-12', '2009-12-30')
#    history_set[0].display()
#    fund2 = fundation.fund(code='1122', name="nishizhu", found_date="2001-11-16", sharp_rate=1.0, max_down=9.0, volatility=9)
#    updateFund(DB, "1122", fund2)
#    history2 = fundation.history(code='1122', day='2000-01-01', value= 10)
#    updateHistory(DB, "1122", "2000-01-01", history2)
#    print(getLatestDate(DB, "CSI1029"))
#    print(getFundlist(DB));
#    