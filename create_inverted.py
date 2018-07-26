import serverCONFIG as scg
import pymysql
from DBUtils import PooledDB
import json
from multiprocessing import Process
import multiprocessing
import time

import warnings
warnings.filterwarnings('ignore')


# connect to mysql
db_config = {
            'host': scg.host_mysql,
            'port': scg.port_mysql,
            'user': scg.user_mysql,
            'password': scg.password_mysql,
            'db': scg.db_mysql,
            'charset': 'utf8'
            }
pool_db = PooledDB.PooledDB(pymysql, mincached=2, maxcached=6, blocking=True, **db_config)


def create_inverted(lock, table, pattern, id_lowerbound, id_upperbound, batch=200000):
    """
        name: create_inverted
        function: 为名称向量、虚拟文档构建倒排索引表
        args:
            table - string - 指定需要生成倒排索引的表
            pattern - string - 表的含义 nv OR vd？
            id_lowerbound - int - 生成范围下界
            id_upperbound - int - 生成范围上界
            batch - interesting - 批次数量，缺省值 20000
    """

    # 获得数据库连接
    conn_db = pool_db.connection()
    cursor = conn_db.cursor()

    # Loop: 分批次处理
    while id_lowerbound < id_upperbound:
        '''查找到的数据是一个string，可以用json解析'''
        sql_select = ('''select {pattern} from {table} where id >= {id_lowerbound} and id <= {id_upperbound}'''
                      .format(pattern=pattern,
                              table=table,
                              id_lowerbound=id_lowerbound,
                              id_upperbound=min(id_upperbound, id_upperbound + batch)))

        '''插入数据库的是一个词语(string)'''
        sql_insert = ('''insert ignore into {inverted_table} (inverted) values (%s)'''
                      .format(inverted_table=scg.table_inverted))

        # 从table中获取name vector/虚拟文档的字符串形式
        cursor.execute(sql_select)
        # fetall()返回元组对象 ((表项1), (表项2), ...)
        f = cursor.fetchall()
        result = {k for s in f if len(s[0]) > 1 for k in json.loads(s[0]).keys()}

        lock.acquire()
        cursor.executemany(sql_insert, result)
        id_lowerbound += batch
        print(id_lowerbound)
        try:
            start = time.clock()
            conn_db.commit()
            print('Time used:', time.clock() - start)
        finally:
            lock.release()

    cursor.close()
    conn_db.close()


if __name__ == "__main__":
    # 列出需要创建倒排索引的表
    raw_tables = [
        'zhwiki',
        'hudongbaike_1',
        'hudongbaike_2',
        'hudongbaike_3',
        'hudongbaike_4',
        'hudongbaike_5',
    ]
 
    lock = multiprocessing.Lock()

    for table in raw_tables:
        process = Process(target=create_inverted,
                          args=(lock, 'name_' + table, 'nv', scg.dict_pedias_lowerbound[table], scg.dict_pedias_upperbound[table]),
                          )

        process.start()
        print(process.pid)


