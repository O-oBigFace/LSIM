"""
configure
"""

base = "zhwiki"

dict_pedias = {'zhwiki': 991388, 'hugongbaike': 4330761, 'baidubaike': 14013129}

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
table_vd = 'vd_{base}'.format(base=base)
table_nv = 'nv_{base}'.format(base=base)
table_subject = 'subject_{base}'.format(base=base)

