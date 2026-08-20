import mysql.connector
from config import *

def drop_n_create_database(database_name_param=database_name):
    conn = mysql.connector.connection.MySQLConnection(**database_config)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {database_name_param}")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {database_name_param}")
    conn.commit()
    cur.close()
    conn.close()

def create_users_table():
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            CID BIGINT UNSIGNED NOT NULL PRIMARY KEY,
            FIRST_NAME VARCHAR(100) NOT NULL,
            LAST_NAME VARCHAR(100),
            USERNAME VARCHAR(150),
            PHONE VARCHAR(20),
            ROLE ENUM('USER', 'MANAGER', 'ADMIN') NOT NULL DEFAULT 'USER',
            IS_BLOCKED ENUM('YES', 'NO') NOT NULL DEFAULT 'NO',
            REGISTER_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            LAST_UPDATE DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_projects_table():
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PROJECTS (
            ID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            NAME VARCHAR(150) NOT NULL,
            DESCRIPTION VARCHAR(255),
            MANAGER_CID BIGINT UNSIGNED,
            START_DATE DATE,
            DEADLINE DATE,
            STATUS ENUM('ACTIVE', 'PAUSED', 'DONE') NOT NULL DEFAULT 'ACTIVE',
            REGISTER_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            LAST_UPDATE DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (MANAGER_CID) REFERENCES USERS(CID)
        ) AUTO_INCREMENT=1000
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_attendance_table():
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ATTENDANCE (
            ID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            CID BIGINT UNSIGNED NOT NULL,
            CHECKIN_TIME DATETIME,
            CHECKOUT_TIME DATETIME,
            WORK_DATE DATE NOT NULL,
            NOTE VARCHAR(255),
            REGISTER_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            LAST_UPDATE DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (CID) REFERENCES USERS(CID),
            UNIQUE KEY unique_user_day (CID, WORK_DATE)
        ) AUTO_INCREMENT=10000
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_tasks_table():
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TASKS (
            ID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            PROJECT_ID INT UNSIGNED NOT NULL,
            ASSIGNEE_CID BIGINT UNSIGNED,
            TITLE VARCHAR(150) NOT NULL,
            DESCRIPTION VARCHAR(255),
            DEADLINE DATE,
            STATUS ENUM('TODO', 'DOING', 'DONE') NOT NULL DEFAULT 'TODO',
            PROGRESS TINYINT UNSIGNED NOT NULL DEFAULT 0,
            REGISTER_DATE DATETIME DEFAULT CURRENT_TIMESTAMP,
            LAST_UPDATE DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (PROJECT_ID) REFERENCES PROJECTS(ID),
            FOREIGN KEY (ASSIGNEE_CID) REFERENCES USERS(CID)
        ) AUTO_INCREMENT=10000
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_tables():
    create_users_table()
    create_projects_table()
    create_attendance_table()
    create_tasks_table()