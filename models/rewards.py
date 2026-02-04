import mysql.connector
from config import my_db

def create_rewards_table():
    rewards_table = mysql.connector.connect(host='localhost', user='root', passwd='',database='crowd_funding')
    reward = rewards_table.cursor()
    reward.execute("Create Table If not exists REWARDS(Id Int Primary Key, Project_Id Int, Description Text Not null, Amount Varchar(255)Not null,CONSTRAINT FOREIGN KEY(Project_Id) REFERENCES PROJECTS(Id))")
    reward.close()