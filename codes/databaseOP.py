# by concyclics
import pymysql
import fundation


def DBconnect(hosts='localhost',*, username='root', password='root'):
    try:
        pymysql.connect(host=hosts, user=username, passwd=password)
    except:
        DB = 'link failed!'
        return False
    else:
        database = pymysql.connect(host=hosts, user=username, passwd=password)
        return database


def splitSql(sql: str):
    sqllist = sql.split(';')
    return sqllist[0:-1]


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
    delete from history;"""
    try:
        for line in splitSql(reset_sql):
            cursor.execute(line)
            database.commit()
    except:
        database.rollback()
    else:
        return True


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


if __name__ == '__main__':
    DB = DBconnect()
    print(DBinit(DB))
    fund1 = fundation.fund(code='1122')
    history1 = fundation.history(code='1122')
    print(addFund(DB, fund1))
    print(addHistory(DB, history1))
    fund2 = getFund(DB, "1122")
    fund2.display()