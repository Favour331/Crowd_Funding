import mysql.connector
from config import my_db

try:
    user_table = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
    table_name = user_table.cursor()
    table_name.execute('Create Table if not exists USERS(Id INTEGER PRIMARY KEY, username Varchar(80) Unique not null, Email Varchar(120) Unique not null, Password Varchar(255) not null, First_name Varchar(100) not null, Last_name Varchar(100) not null, Bio Text, avater_url Varchar(500), Location Varchar(100), website Varchar(255), Role Enum("Backer","Creator","Admin"),is_verified Boolean, email_verified Boolean, failed_login Int, locked_until Datetime, last_login Datetime, created_at Datetime Default Current_Timestamp, updated_at Datetime Default Current_Timestamp)')
    table_name.close()
except Exception as e:
    print(e)