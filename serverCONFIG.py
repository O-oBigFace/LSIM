"""
configure
"""

pedia = "hudongbaike"
# 表后缀
base = "hudongbaike_5"
# 表起始id
begin_index = 4000000

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
                }

num_of_subjects = dict_pedias[base]


# agraph
repository_agraph = base
host_agraph = "192.168.1.101"
port_agraph = 10035
user_agraph = 'john'
password_agraph = '123'

# db: mysql
db_mysql = "zhishi"
host_mysql = '192.168.1.101'
port_mysql = 3306
user_mysql = 'xyk'
password_mysql = "123"

table_vd = 'virtual_{base}'.format(base=base)  # 虚拟文档表
table_nv = 'name_{base}'.format(base=base)  # name vector 表
table_subject = 'subject_{base}'.format(base=pedia)  # subject表
table_inverted = 'inverted'  # 倒排索引表

