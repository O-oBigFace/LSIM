"""
configure
"""

base = "zhwiki"
num_of_subjects = 991388




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
table_entity = 'entity_{base}'.format(base=base)
table_vd = 'vd_{base}'.format(base=base)
table_nv = 'nv_{base}'.format(base=base)
table_subject = 'subject_{base}'.format(base=base)

