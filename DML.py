import mysql.connector
from config import *

def insert_user_data(cid, first_name, last_name=None, username=None, phone=None, role='USER', is_blocked='NO'):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO USERS (CID, FIRST_NAME, LAST_NAME, USERNAME, PHONE, ROLE, IS_BLOCKED)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (cid, first_name, last_name, username, phone, role, is_blocked))
    conn.commit()
    cur.close()
    conn.close()
    return True

def insert_project_data(name, description=None, manager_cid=None, start_date=None, deadline=None, status='ACTIVE'):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO PROJECTS (NAME, DESCRIPTION, MANAGER_CID, START_DATE, DEADLINE, STATUS)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, description, manager_cid, start_date, deadline, status))
    conn.commit()
    pid = cur.lastrowid
    cur.close()
    conn.close()
    return pid

def insert_attendance(cid, checkin_time, work_date, checkout_time=None, note=None):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ATTENDANCE (CID, CHECKIN_TIME, WORK_DATE, CHECKOUT_TIME, NOTE)
        VALUES (%s, %s, %s, %s, %s)
    """, (cid, checkin_time, work_date, checkout_time, note))
    conn.commit()
    aid = cur.lastrowid
    cur.close()
    conn.close()
    return aid

def update_checkout(cid, work_date, checkout_time):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        UPDATE ATTENDANCE
        SET CHECKOUT_TIME = %s
        WHERE CID = %s AND WORK_DATE = %s
    """, (checkout_time, cid, work_date))
    conn.commit()
    cur.close()
    conn.close()
    return True

def insert_task(project_id, title, description=None, assignee_cid=None, deadline=None, status='TODO', progress=0):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO TASKS (PROJECT_ID, TITLE, DESCRIPTION, ASSIGNEE_CID, DEADLINE, STATUS, PROGRESS)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (project_id, title, description, assignee_cid, deadline, status, progress))
    conn.commit()
    tid = cur.lastrowid
    cur.close()
    conn.close()
    return tid

def update_task_progress(task_id, progress=None, status=None):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor()
    if progress is not None and status is not None:
        cur.execute("""
            UPDATE TASKS
            SET PROGRESS = %s, STATUS = %s
            WHERE ID = %s
        """, (progress, status, task_id))
    elif progress is not None:
        cur.execute("""
            UPDATE TASKS
            SET PROGRESS = %s
            WHERE ID = %s
        """, (progress, task_id))
    elif status is not None:
        cur.execute("""
            UPDATE TASKS
            SET STATUS = %s
            WHERE ID = %s
        """, (status, task_id))
    conn.commit()
    cur.close()
    conn.close()
    return True