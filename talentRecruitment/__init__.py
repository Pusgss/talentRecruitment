import pymysql
pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()# 告诉django用pymysql代替mysqldb连接数据库


from .celeryconfig import app as celery_app