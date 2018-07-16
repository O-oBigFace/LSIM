from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import pymysql
import re
from urllib import parse
import segmentation as seg
import json
import serverCONFIG as scg
from DBUtils import PooledDB


weight_of_subject = 3.1
weight_of_category = 2.1

# connect to Allegrograph
server = AllegroGraphServer(host=scg.host_agraph,
                            port=scg.port_agraph,
                            user=scg.user_agraph,
                            password=scg.password_agraph)
catalog = server.openCatalog("")
graph = catalog.getRepository(scg.repository_agraph, Repository.ACCESS)
graph.initialize()
conn_graph = graph.getConnection()

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


def db_execute(cursor, sql, values):
    try:
        cursor.execute(sql, values)
    except pymysql.err.IntegrityError:
        pass
    except pymysql.err.DataError:
        pass
    except pymysql.err.InternalError:
        pass


def construct(id_lowerbound, id_upperbound, batch=1500):
    # connect to mysql
    # 获得数据库连接
    conn_db = pool_db.connection()
    cursor = conn_db.cursor()

    """
    对mysql中的subject表构造出相应的虚拟文档，存到虚拟文档表中．
    为了程序支持多进程，所以函数的输入为，
    id_lowerbound: 起始id
    id_upperbound: 结束id + 1
    batch: (单个进程中)每一个批次处理sbj的个数,默认为1500
    """

    ''' 
    分批次处理 
    从subjuect表中查找id, sbj
    '''
    # sql_find_subject = ("select sbj from `{tb_sbj}` where `id` >= {lb} and `id` < {ub}"
    #                     .format(tb_sbj=scg.table_subject,
    #                             lb=id_lowerbound,
    #                             ub=min(id_lowerbound + batch, id_upperbound)))
    sql_find_subject = ("select sbj,id from `{tb_sbj}` where `id` >= {lb} and `id` < {ub}"
                        .format(tb_sbj=scg.table_subject,
                                lb=id_lowerbound,
                                ub=min(id_lowerbound + batch, id_upperbound)))

    ''' 向数据表nv_插入名称向量 '''
    # sql_insert_nv = ("""insert ignore into `{table}` (`sbj`, `nv`) VALUES (%s, %s) """
    #                  .format(table=scg.table_nv))
    sql_insert_nv = ("""insert ignore into `{table}` (`id`, `sbj`, `nv`) VALUES (%s, %s, %s) """
                     .format(table=scg.table_nv))

    ''' 向数据表 vd_zhwiki 中插入虚拟文档 '''
    # sql_insert_vd = ("""insert ignore into `{table}` (`sbj`, `vd`) VALUES (%s, %s) """
    #                  .format(table=scg.table_vd))
    sql_insert_vd = ("""insert ignore into `{table}` (`id`, `sbj`, `vd`) VALUES (%s, %s, %s) """
                     .format(table=scg.table_vd))

    # Loop1:批次
    while id_lowerbound < id_upperbound:
        # mysql查找
        cursor.execute(sql_find_subject)
        """
        Loop2: 单个sbj in 所有sbj
        fetchall: tuple(tuple(sbj))
        这里fetchall正确运行时不会Error
        """

        

        f = {c[0].strip() for c in cursor.fetchall()}
        for sbj in f:
            # 结果集合,如果当前sbj为空,跳过
            if len(sbj) < 1:
                continue

            tag_SBJ = conn_graph.createURI(sbj)
            tag_ABS = ''

            """查找每个sbj的abstract和category"""
            with conn_graph.getStatements(subject=tag_SBJ,
                                          predicate=conn_graph
                                          .createURI('<http://zhishi.me/ontology/abstract>')) as abstract:
                for a in abstract:
                    tag_ABS = a.getObject()

            with conn_graph.getStatements(subject=tag_SBJ,
                                          predicate=conn_graph
                                          .createURI('<http://zhishi.me/ontology/category>')) as ctg:
                tag_CTGs = [str(c.getObject()).strip() for c in ctg]

            # subject,abstract分出的向量
            vector_SBJ = dict()
            vector_ABS = dict()
            """construct name vector"""
            pattern = re.compile('/resource/(.*)>')
            mo = pattern.search(str(tag_SBJ))
            SBJ = ''

            try:
                SBJ = mo.group(1)
                # 分词模块,过滤中文
                vector_SBJ = seg.to_vector(parse.unquote(SBJ), 'cn')
            except Exception as e:
                print(tag_SBJ, str(e))
                pass

            db_execute(cursor, sql_insert_nv, (SBJ, json.dumps(vector_SBJ)))

            '''摘要分词'''
            try:
                vector_ABS = seg.to_vector(str(tag_ABS), 'cn')
            except Exception:
                pass

            '''类别分词'''
            list_CTGs = list()
            pattern = re.compile('/category/(.*)>')
            for item in tag_CTGs:
                try:
                    mo = pattern.search(str(item))
                    list_CTGs += seg.to_vector(parse.unquote(mo.group(1)), returntf=False)
                except Exception:
                    continue
            vector_CTGs = seg.tf_counter(list_CTGs)

            '''计算虚拟文档'''
            virtual_document = seg.combination_dict(
                 seg.combination_dict(vector_ABS, vector_CTGs, weight_of_category), vector_SBJ, weight_of_subject)

            db_execute(cursor, sql_insert_vd, (SBJ, json.dumps(virtual_document)))

            conn_db.commit()

        # 更新id下界
        id_lowerbound += batch
    cursor.close()
    conn_db.close()














