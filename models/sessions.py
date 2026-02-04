import mysql.connector

def create_sessions_table():
    session_table = mysql.connector.connect(host='127.0.0.1', user='root',passwd='',database='crowd_funding')
    try:
        session_table.autocommit = True
        cur = session_table.cursor()
        cur.execute('Create Table If not exists sessions(id Int Primary Key Auto_Increment, user_id Int, token Varchar(255) Unique, created_at Datetime, expires_at Datetime, last_activity Datetime, ip_address Varchar(45), user_agent Text, is_revoked Boolean, CONSTRAINT FOREIGN KEY(user_id) REFERENCES USERS(Id))')
        session_table.commit()
        cur.close()
        session_table.close()
    except mysql.connector.Error as e:
        print(str(e))
