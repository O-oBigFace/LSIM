"""
configure
"""

base = "hudongbaike"

# agraph
repository_agraph = base
host_agraph = "localhost"
port_agraph = 10035
user_agraph = 'john'
password_agraph = '123'

# db: mysql
db_mysql = "zhishi"
host_mysql = 'localhost'
port_mysql = 3306
user_mysql = 'root'
password_mysql = "123"
table_entity = 'entity_{base}'.format(base=base)
table_vd = 'vd_{base}'.format(base=base)
table_nv = 'nv_{base}'.format(base=base)
table_subject = 'subject_{base}'.format(base=base)

