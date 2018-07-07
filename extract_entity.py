# import pymysql
# from franz.openrdf.sail.allegrographserver import AllegroGraphServer
# from franz.openrdf.repository.repository import Repository
# import serverCONFIG as scg
# from multiprocessing import Process
# import time
#
# """
# 预处理部分：
# 为了弥补图数据库的缺陷，所以先将所有的subject提取出来.
# """
#
# # config
# repository_agraph = scg.repository_agraph
# host_agraph = scg.host_agraph
# port_agraph = scg.port_agraph
# user_agraph = scg.user_agraph
# password_agraph = scg.password_agraph
#
#
# db_mysql = scg.db_mysql
# host_mysql = scg.host_mysql
# port_mysql = scg.port_mysql
# user_mysql = scg.user_mysql
# password_mysql =scg.password_mysql
# table_subject = scg.table_subject
#
#
# # connect to Allegrograph
# server = AllegroGraphServer(host=host_agraph, port=port_agraph, user=user_agraph, password=password_agraph)
# catalog = server.openCatalog("")
# graph = catalog.getRepository(repository_agraph, Repository.ACCESS)
# graph.initialize()
# conn_graph = graph.getConnection()
#
# # connect to mysql
# conn_db = pymysql.connect(host=host_mysql, port=port_mysql, user=user_mysql, password=password_mysql, db=db_mysql)
#
# number_of_triples = 15349786
#
#
# """
# tip:
# id_start: the location that the first triple begins.
# id_end: the next location of the last triple
# """
#
#
# def extractor_sbj(id_start, id_end, table):
#     start = time.clock()
#     for num in range(id_start, id_end):
#         statement = conn_graph.getStatementsById(num)
#
#         tag_SBJ = None
#         for result in statement:
#             tag_SBJ = result.getPredicate()
#
#         sql_insert_sbj = """insert into `{table}` (`sbj`) VALUES (%s) """.format(table=table)
#
#         # insert into mysql
#         try:
#             with conn_db.cursor() as cursor:
#                 cursor.execute(sql_insert_sbj, [str(tag_SBJ)])
#         except pymysql.err.IntegrityError:
#             # print('IntegrityError!')
#             pass
#         except pymysql.err.DataError:
#             print('Data Error!')
#             print(str(tag_SBJ))
#         except pymysql.err.InternalError:
#             print('InternalError')
#             print(str(tag_SBJ))
#         # 问题出在这里　commit
#
#         # try:
#         #     conn_db.commit()
#         # except pymysql.err.IntegrityError:
#         #     print("strange")
#         #     conn_db.rollback()
#         #     pass
#
#         if num % 100000 is 0:
#             conn_db.commit()
#     print("Time used", start - time.clock())
#
#
# if __name__ == "__main__":
#
#     extractor_sbj(1, number_of_triples+1, 'zhwiki')
#     conlist = [(1, 3837447, table_subject[0]),
#                (3837447, 3837447*2+1, table_subject[1]),
#                (3837447*2+1, 3837447*3+1, table_subject[2]),
#                (3837447*3+1, 15349787, table_subject[3]),
#                ]
#     for i in range(1, 5):
#         p = Process(target=extractor_sbj, args=conlist[i-1],)
#         p.start()
#
#
