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
    
def splitSql(sql:str):
    sqllist=sql.split(';')
    return sqllist[0:-1]
    
def DBinit(database):
    if type(database).__name__!='Connection':
        return False
    cursor=database.cursor()
    reset_sql="""
    drop database fundation;
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
        value float not null check (value>0),
        day date,
        primary key(code,day),
        foreign key(code) references funds(code)
            on delete cascade
            on update cascade
    );
    delete from funds;
    delete from history;"""
    try:
        for line in splitSql(reset_sql):
            cursor.execute(line)
            database.commit()
    except:
        database.rollback()
        return False
    else:
        return True
    
def addFund():

def addHistory():
    


if __name__=='__main__':
    DB=DBconnect()
    print(DBinit(DB))