"""
configure
"""

base = "zhwiki"

dict_pedias = {'zhwiki': 991388, 'hudongbaike': 4330761, 'baidubaike': 14013129}

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
# table_vd = 'vd_{base}'.format(base=base)  # 虚拟文档表
# table_nv = 'nv_{base}'.format(base=base)  # name vector 表
table_vd = 'virtual_{base}'.format(base=base)  # 虚拟文档表
table_nv = 'name_{base}'.format(base=base)  # name vector 表
table_subject = 'subject_{base}'.format(base=base)  # subject表
table_inverted = 'inverted'  # 倒排索引表

