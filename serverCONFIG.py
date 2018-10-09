"""
configure
"""

pedia = "baidubaike"
# 表后缀
base = "baidubaike_13"
# 表起始id
begin_index = 12000000

# 表大小
dict_pedias = {'zhwiki': 991388,
               'hudongbaike': 4330761,
               'baidubaike': 14013129,

               'hudongbaike_1': 1000000,
               'hudongbaike_2': 1000000,
               'hudongbaike_3': 1000000,
               'hudongbaike_4': 1000000,
               'hudongbaike_5': 330800,

               'baidubaike_1': 1000000,
               'baidubaike_2': 1000000,
               'baidubaike_3': 1000000,
               'baidubaike_4': 1000000,
               'baidubaike_5': 1000000,
               'baidubaike_6': 1000000,
               'baidubaike_7': 1000000,
               'baidubaike_8': 1000000,
               'baidubaike_9': 1000000,
               'baidubaike_10': 1000000,
               'baidubaike_11': 1000000,
               'baidubaike_12': 1000000,
               'baidubaike_13': 1000000,
               }

# 表id下界
dict_pedias_lowerbound = {
                'zhwiki': 1,

                'hudongbaike_1': 1,
                'hudongbaike_2': 1000000,
                'hudongbaike_3': 2000000,
                'hudongbaike_4': 3000000,
                'hudongbaike_5': 4000000,

                'baidubaike_1': 1,
                'baidubaike_2': 1000000,
                'baidubaike_3': 2000000,
                'baidubaike_4': 3000000,
                'baidubaike_5': 4000000,
                'baidubaike_6': 5000000,
                'baidubaike_7': 6000000,
                'baidubaike_8': 7000000,
                'baidubaike_9': 8000000,
                'baidubaike_10': 9000000,
                'baidubaike_11': 10000000,
                'baidubaike_12': 11000000,
                'baidubaike_13': 12000000,
                }


# 表id上界
dict_pedias_upperbound = {
                'zhwiki': 991389,
                'hudongbaike': 4330761,
                'baidubaike': 14013129,

                'hudongbaike_1': 1000001,
                'hudongbaike_2': 2000001,
                'hudongbaike_3': 3000001,
                'hudongbaike_4': 4000001,
                'hudongbaike_5': 4330800,

                'baidubaike_1': 1000001,
                'baidubaike_2': 2000001,
                'baidubaike_3': 3000001,
                'baidubaike_4': 4000001,
                'baidubaike_5': 5000001,
                'baidubaike_6': 6000001,
                'baidubaike_7': 7000001,
                'baidubaike_8': 8000001,
                'baidubaike_9': 9000001,
                'baidubaike_10': 10000001,
                'baidubaike_11': 11000001,
                'baidubaike_12': 12000001,
                'baidubaike_13': 13000001,
                }

num_of_subjects = dict_pedias[base]


# agraph
repository_agraph = base
# host_agraph = "192.168.2.234"
host_agraph = "localhost"
port_agraph = 10035
user_agraph = 'john'
password_agraph = '123'

# db: mysql
db_mysql = "zhishi"
# host_mysql = '192.168.2.234'
host_mysql = 'localhost'
port_mysql = 3306
user_mysql = 'xyk'
password_mysql = "123"

table_vd = 'virtual_{base}'.format(base=base)  # 虚拟文档表
table_nv = 'name_{base}'.format(base=base)  # name vector 表
table_subject = 'subject_{base}'.format(base=pedia)  # subject表
table_inverted = 'inverted'  # 倒排索引表

