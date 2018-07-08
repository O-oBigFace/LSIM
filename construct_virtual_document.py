from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import pymysql
import re
from urllib import parse
import segmentation as seg
import json
import serverCONFIG as scg
from multiprocessing import Process


# config
repository_agraph = scg.repository_agraph
host_agraph = scg.host_agraph
port_agraph = scg.port_agraph
user_agraph = scg.user_agraph
password_agraph = scg.password_agraph


db_mysql = scg.db_mysql
host_mysql = scg.host_mysql
port_mysql = scg.port_mysql
user_mysql = scg.user_mysql
password_mysql =scg.password_mysql
table_vd = scg.table_vd
table_nv = scg.table_nv
table_subject = scg.table_subject


sql_insert = """insert into `{table}` (`sbj`, `vd`) VALUES (%s, %s) """.format(table=table_vd)

weight_of_subject = 3.1
weight_of_category = 2.1

# connect to Allegrograph
server = AllegroGraphServer(host=host_agraph, port=port_agraph, user=user_agraph, password=password_agraph)
catalog = server.openCatalog("")
graph = catalog.getRepository(repository_agraph, Repository.ACCESS)
graph.initialize()
conn_graph = graph.getConnection()


def construct(id_lowerbound, id_upperbound, batch=150):
    # connect to mysql
    conn_db = pymysql.connect(host=host_mysql, port=port_mysql, user=user_mysql, password=password_mysql, db=db_mysql)
    """
    对mysql中的subject表构造出相应的虚拟文档，存到虚拟文档表中．

    为了程序支持多进程，所以函数的输入为，
    id_lowerbound: 起始id
    id_upperbound: 结束id + 1

    batch: (单个进程中)每一个批次处理sbj的个数,默认为150

    """

    # Loop1:批次
    while id_lowerbound < id_upperbound:
        # 分批次处理
        sql_find_subject = ("select sbj from `{tb_sbj}` where `id` >= {lb} and `id` < {ub}"
                            .format(tb_sbj=table_subject, lb=id_lowerbound, ub=min(id_lowerbound+batch, id_upperbound)))

        # mysql查找
        with conn_db.cursor() as cursor:
            cursor.execute(sql_find_subject)

            """
            Loop2: 单个sbj in 所有sbj
            fetchall: tuple(tuple(sbj))
            这里fetchall正确运行时不会Error
            """
            for f in cursor.fetchall():
                # 结果集合,如果当前sbj为空,跳过
                sbj = f[0].strip()
                if sbj is '':
                    continue

                tag_SBJ = conn_graph.createURI(sbj)
                tag_ABS = ''
                tag_CTGs = []

                """查找每个sbj的abstract和category"""
                with conn_graph.getStatements(subject=tag_SBJ, predicate='<http://zhishi.me/ontology/abstract>') as abstract:
                    for a in abstract:
                        tag_ABS = a.getObject()

                with conn_graph.getStatements(subject=tag_SBJ, predicate='<http://zhishi.me/ontology/category>') as ctg:
                    for c in ctg:
                        tag_CTGs.append(str(c.getObject()).strip())

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

                '''向数据表nv_插入名称向量'''
                sql_insert_nv = """insert into `{table}` (`sbj`, `nv`) VALUES (%s, %s) """.format(table=table_nv)

                try:
                    cursor.execute(sql_insert_nv, (SBJ, json.dumps(vector_SBJ)))
                except pymysql.err.IntegrityError:
                    pass
                except pymysql.err.DataError:
                    pass
                except pymysql.err.InternalError:
                    pass

                '''计算虚拟文档'''
                virtual_document = seg.combination_dict(
                     seg.combination_dict(vector_ABS, vector_CTGs, weight_of_category), vector_SBJ, weight_of_subject)

                '''
                向数据表 vd_zhwiki 中插入虚拟文档
                '''
                sql_insert_vd = """insert into `{table}` (`sbj`, `vd`) VALUES (%s, %s) """.format(table=table_vd)
                try:
                    cursor.execute(sql_insert_vd, (SBJ, json.dumps(virtual_document)))
                except pymysql.err.IntegrityError:
                    pass
                except pymysql.err.DataError:
                    pass
                except pymysql.err.InternalError:
                    pass

            conn_db.commit()


        # 更新id下界
        id_lowerbound += batch


if __name__ == "__main__":
    total = scg.num_of_subjects
    parts = 1

    """7月7日 第一部分"""

    num_of_process = 4

    quarter = total / parts / num_of_process + 1

    no_begin = 0

    arglist =[(1 + no_begin, quarter + no_begin),
              (quarter + no_begin, quarter*2+1 + no_begin),
              (quarter*2+1 + no_begin, quarter*3+1 + no_begin),
              (quarter*3+1 + no_begin, quarter*4+1 + no_begin),
              (quarter*4+1 + no_begin, quarter*5+1 + no_begin),
              ]

    """num 进程"""
    for i in range(1, num_of_process + 1):
        p = Process(target=construct, args=arglist[i-1])
        print(i)
        p.start()











