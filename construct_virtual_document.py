from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import pymysql
import re
from urllib import parse
import segmentation as seg
import time
import json
import serverCONFIG as scg

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
table_entity = scg.table_entity


sql_insert = """insert into `{table}` (`sbj`, `vd`) VALUES (%s, %s) """.format(table=table_entity)


weight_of_subject = 3.1
weight_of_category = 2.1

number_of_triples = 15349786


# connect to Allegrograph
server = AllegroGraphServer(host=host_agraph, port=port_agraph, user=user_agraph, password=password_agraph)
catalog = server.openCatalog("")
graph = catalog.getRepository(repository_agraph, Repository.ACCESS)
graph.initialize()
conn_graph = graph.getConnection()

# connect to mysql
conn_db = pymysql.connect(host=host_mysql, port=port_mysql, user=user_mysql, password=password_mysql, db=db_mysql)


# list:record subjects that have been executed recently
list_sbj = list()


def construct():
    for num in range(number_of_triples):
        start = time.clock()
        statement = conn_graph.getStatementsById(num + 1)
        print("####################", num + 1, "####################")

        tag_SBJ = None
        for result in statement:
            tag_SBJ = result.getPredicate()

        # Loop controller

        # construct name vector
        try:
            pattern = re.compile('/resource/(.*)>')
            mo = pattern.search(str(tag_SBJ))
            SBJ = parse.unquote(mo.group(1))
            vector_SBJ = seg.to_vector(parse.unquote(mo.group(1)), 'punctuation')
        except Exception:
            continue

        # find abstract and category respectively,then process
        # abstract, weight = 1
        tag_ABS = None
        vector_ABS = dict()

        with conn_graph.getStatements(subject=tag_SBJ, predicate='<http://zhishi.me/ontology/abstract>') as abs:
            for a in abs:
                tag_ABS = a.getObject()

        try:
            vector_ABS = seg.to_vector(str(tag_ABS), 'cn')
        except Exception:
            print('no abstract')

        #category, weight = 2
        tag_CTGs = []
        list_CTGs = list()

        with conn_graph.getStatements(subject=tag_SBJ, predicate='<http://zhishi.me/ontology/category>') as ctg:
            for c in ctg:
                tag_CTGs.append(c.getObject())

        pattern = re.compile('/category/(.*)>')
        for item in tag_CTGs:
            try:
                mo = pattern.search(str(item))
                list_CTGs += seg.to_vector(parse.unquote(mo.group(1)), returntf=False)
            except Exception:
                continue

        vector_CTGs = seg.tf_counter(list_CTGs)

        virtual_document = seg.combination_dict(
            seg.combination_dict(vector_ABS, vector_CTGs, weight_of_category), vector_SBJ, weight_of_subject)

        # virtual_document = seg.simple_normalization(virtual_document)

        print(SBJ)
        print(virtual_document)
        print('Time used:', time.clock() - start)

        # insert into mysql
        try:
            with conn_db.cursor() as cursor:
                cursor.execute(sql_insert, [str(tag_SBJ), json.dumps(virtual_document)])
        except pymysql.err.IntegrityError:
            print('IntegrityError!')
        except pymysql.err.DataError:
            print('Data Error!')
        except pymysql.err.InternalError:
            print('InternalError')
        if num % 233 is 0:
            conn_db.commit()


if __name__ == "__main__":
    construct()




















