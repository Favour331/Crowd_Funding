import mysql.connector

db = mysql.connector.connect(host='Localhost', user='root', passwd='',)
my_db = db.cursor()
my_db.execute('Create Database If not exists CROWD_FUNDING')
my_db.close()