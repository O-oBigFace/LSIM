"""
    本文件用来构建匹配用的LD, 并存入数据库中
"""
from server_config import *
from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
import pymysql
from segmentation import *
from Logger import logger
import json
from multiprocessing.pool import Pool
import time
import warnings
from collections import defaultdict
warnings.filterwarnings("ignore")

# connect to Allegrograph
server = AllegroGraphServer(**para_agraph)
catalog = server.openCatalog("")
graph = catalog.getRepository(repository_agraph, Repository.ACCESS)
graph.initialize()
conn_graph = graph.getConnection()

set_keys = {
            'abstract',
            'category',
            'externalLink',     # useless
            'relatedPage',
            'pageDisambiguates',
            'internalLink',
            'pageRedirects',    # 是否要记录下来？ 将此项单独放在一个表中
            }

weight_ld = {
    'abs': 1,
    'pro': 3.1,
    'cat': 3.1,
    'rel': 2.1,
    'ilk': 2.1
}


def db_execute(cursor, sql, values):
    try:
        cursor.execute(sql, values)
    except pymysql.err.IntegrityError:
        pass
    except pymysql.err.DataError:
        pass
    except pymysql.err.InternalError:
        pass


def db_executemany(cursor, sql, values):
    try:
        cursor.executemany(sql, values)
    except pymysql.err.IntegrityError:
        pass
    except pymysql.err.DataError:
        pass
    except pymysql.err.InternalError:
        pass


# 根据键值计算ld
def ld_process(info_dict):
    vec_sbj = dict()

    # abstract
    if len(info_dict.setdefault('abstract', list())) > 0:
        vec_sbj = to_vector(info_dict['abstract'][0], weight=weight_ld['abs'])

    # info box
    if len(info_dict.setdefault('property', list())) > 0:
        for term in info_dict['property']:
            vec_sbj = combination_dict(vec_sbj, to_vector(term, weight=weight_ld['pro']))

    # category
    if len(info_dict.setdefault('category', list())) > 0:
        for term in info_dict['category']:
            vec_sbj = combination_dict(vec_sbj, to_vector(term, weight=weight_ld['cat']))

    # related page
    if len(info_dict.setdefault('relatedPage', list())) > 0:
        for term in info_dict['relatedPage']:
            vec_sbj = combination_dict(vec_sbj, to_vector(term, weight=weight_ld['rel']))

    # internal link
    if len(info_dict.setdefault('internalLink', list())) > 0:
        for term in info_dict['internalLink']:
            vec_sbj = combination_dict(vec_sbj, to_vector(term, weight=weight_ld['ilk']))

    return vec_sbj


# 根据subject计算其ld向量
def calculate_sbj(sbj):
    tag_SBJ = conn_graph.createURI(sbj)
    info = defaultdict(list)    # 存储实体信息
    # start = time.time()
    with conn_graph.getStatements(subject=tag_SBJ) as statements:
        for s in statements:
            key = s.getPredicate().getURI().split("/")[-1]
            key = key if key in set_keys else "property"
            value = str(s.getObject())
            info[key].append(value)
    # print("time used:", time.time() - start)
    return ld_process(info)


# 构建ld向量并存入到相应数据库
def ld_constructor(name_pedia, init_id=0, batch_size=5000):
    batch = batch_size    # 预先决定 batch
    current_id = init_id  # 初始id置为0
    max_id = dict_pedias[name_pedia]

    # 初始化数据库
    conn = pymysql.connect(**para_mysql)
    cursor = conn.cursor()

    pool = Pool()  # 初始化线程池

    while current_id <= max_id:
        start = time.time()
        # 分批次查找subject
        max_batch_id = min(max_id, current_id + batch)

        sql_find_subject = ("select id, sbj from `subject_{tb_sbj}` where `id` >= {lb} and `id` < {ub}"
                            .format(tb_sbj=name_pedia,
                                    lb=current_id,
                                    ub=max_batch_id))
        # 数据库查找subject，多进程执行
        cursor.execute(sql_find_subject)
        f = cursor.fetchall()   # 获得数据库查询结果

        sbj_batch = [s[1] for s in f]
        sbj_id = [s[0] for s in f]
        res = [json.dumps(r) for r in pool.map(calculate_sbj, sbj_batch)]

        # 将结果存入数据库,插入语句
        num_table = current_id // 1000000 + 1   # 表id
        sql_create_table = r"CREATE TABLE IF NOT EXISTS `ld_%s_%d` like ld_zhwiki_1"
        cursor.execute(sql_create_table)    # 如果表不存在，则创建
        sql_insert_ld = ("""insert ignore into `{table}` (`id`, `ld`) VALUES (%s, %s) """
                         .format(table="ld_%s_%d" % (pedia, num_table)))
        db_executemany(cursor, sql_insert_ld, zip(sbj_id, res))
        conn.commit()
        logger.info("Current id: %d~%d | Time used: %.2f" % (current_id, current_id + batch_size, time.time() - start))
        current_id += batch


if __name__ == '__main__':
    ld_constructor(pedia, init_id=0)
