from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import pymysql
import re
from urllib import parse
import segmentation as seg
import json
from server_config import *
from multiprocessing import Process
import time
import warnings

"""
    本文件可用于构建分块所需的name vector和初始的virtual document
"""

warnings.filterwarnings('ignore')

weight_of_subject = 3.1
weight_of_category = 2.1

# connect to Allegrograph
server = AllegroGraphServer(**para_agraph)
catalog = server.openCatalog("")
graph = catalog.getRepository(repository_agraph, Repository.ACCESS)
graph.initialize()
conn_graph = graph.getConnection()


# 注意: 表插入操作过于频繁!!!!
def construct(id_lowerbound, id_upperbound, batch=1500):
    id_upperbound = min(id_upperbound, dict_pedias_upperbound[base])
    print("construct: ", id_lowerbound, "~", id_upperbound)
    # connect to mysql
    # 获得数据库连接
    # conn_db = pool_db.connection()
    conn_db = pymysql.connect(**para_mysql)
    cursor = conn_db.cursor()

    """
    对mysql中的subject表构造出相应的虚拟文档，存到虚拟文档表中．
    为了程序支持多进程，所以函数的输入为，
    id_lowerbound: 起始id
    id_upperbound: 结束id + 1
    batch: (单个进程中)每一个批次处理sbj的个数,默认为1500
    """

    # Loop1:批次
    while id_lowerbound < id_upperbound:
        ''' 
        分批次处理 
        从subjuect表中查找id, sbj
        '''
        sql_find_subject = ("select id, sbj from `{tb_sbj}` where `id` >= {lb} and `id` < {ub}"
                            .format(tb_sbj=table_subject,
                                    lb=id_lowerbound,
                                    ub=min(id_lowerbound + batch, id_upperbound)))

        ''' 向数据表nv_插入名称向量 '''

        sql_insert_nv = ("""insert ignore into `{table}` (`id`, `sbj`, `nv`) VALUES (%s, %s, %s) """
                         .format(table=table_nv))

        ''' 向数据表 vd_zhwiki 中插入虚拟文档 '''

        sql_insert_vd = ("""insert ignore into `{table}` (`id`, `sbj`, `vd`) VALUES (%s, %s, %s) """
                         .format(table=table_vd))

        # mysql查找
        cursor.execute(sql_find_subject)
        """
        Loop2: 单个sbj in 所有sbj
        fetchall: tuple(tuple(sbj))
        这里fetchall正确运行时不会Error
        """
        insert_list_nv = list()
        intert_list_vd = list()
        result = cursor.fetchall()
        for r in result:
            id = r[0]
            sbj = r[1]  #URL形式
            if len(sbj) < 1:
                continue

            tag_SBJ = conn_graph.createURI(sbj)
            tag_ABS = str()

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
            SBJ = str()

            try:
                SBJ = parse.unquote(mo.group(1))
                # 分词模块,过滤中文
                vector_SBJ = seg.to_vector(SBJ, 'cn')
            except Exception as e:
                print(tag_SBJ, str(e))
                pass

            # db_execute(cursor, sql_insert_nv, (id, SBJ, json.dumps(vector_SBJ)))
            insert_list_nv.append((id, SBJ, json.dumps(vector_SBJ)))
            '''摘要分词'''
            try:
                vector_ABS = seg.to_vector(str(tag_ABS), 'cn')
            except Exception as e:
                # print("abstract:", e)
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

            # db_execute(cursor, sql_insert_vd, (id, SBJ, json.dumps(virtual_document)))
            intert_list_vd.append((id, SBJ, json.dumps(virtual_document)))

        # 这里可能需要加锁
        db_executemany(cursor, sql_insert_nv, insert_list_nv)
        db_executemany(cursor, sql_insert_vd, intert_list_vd)
        conn_db.commit()

        # 更新id下界
        id_lowerbound += batch

    cursor.close()
    # conn_db.close()


def multi_run(function_name, num_of_process):
    total = num_of_subjects
    quarter = int(total / num_of_process) + 1
    no_begin = begin_index
    arglist = [(quarter * i + no_begin, quarter * (i + 1) + no_begin) for i in range(10)]
    print(arglist)
    """num 进程"""
    for i in range(1, num_of_process + 1):
        p = Process(target=function_name, args=arglist[i-1])
        p.start()
        time.sleep(30)


if __name__ == '__main__':
    multi_run(construct, 4)











