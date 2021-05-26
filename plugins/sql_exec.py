import sqlite3
import os.path


def sql_execute(sql):
	sql.replace("'","").replace('"','')
	base_dir=os.path.dirname(os.path.abspath(__file__))
	db_path=os.path.join(base_dir, 'db','eve.db')
	db = sqlite3.connect(db_path)
	cursor = db.cursor()
	sql = '''{}'''.format(sql)
	cursor.execute(sql)
	db.commit()
	content = cursor.fetchall()
	cursor.close()
	db.close()
	return content

def sqlite_exec(name,command):
	base_dir=os.path.dirname(os.path.abspath(__file__))
	db_path=os.path.join(base_dir, 'db', name)
	db = sqlite3.connect(db_path)
	cs=db.execute('''{}'''.format(command))
	res = cs.fetchall()
	db.commit()
	db.close()
	return res