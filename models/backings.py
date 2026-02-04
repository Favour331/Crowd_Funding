import mysql.connector
from config import my_db

def create_backing_table():
    try:
        backings_table = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
        back = backings_table.cursor()
        back.execute('Create Table If Not Exists BACKINGS(Id Int Primary Key Auto_Increment, Backer_id Int Not null,Project_Id Int not null, Amount Varchar(255) not null, Reward_tier Varchar(100), reward_desc text, estimated_delivery Date not null, Status Enum("pledge","processing","completed","refunded","cancelled"),is_anonymous Boolean, payment_id int, payment_status Varchar(50), created_at Datetime,updated_at datetime, refunded_at Datetime,CONSTRAINT FOREIGN KEY(Project_Id) REFERENCES PROJECTS(Id) ON DELETE CASCADE,CONSTRAINT FOREIGN KEY(Backer_Id) REFERENCES USERS(Id) ON DELETE CASCADE)')
        back.close()
    except mysql.connector.Error as e:
        print(e)
    finally:
        backings_table.close()
        back.close()