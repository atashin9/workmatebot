import mysql.connector
from config import *

def get_user_by_id(cid):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM USERS WHERE CID = %s
    """, (cid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_all_users():
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM USERS ORDER BY REGISTER_DATE DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_project_by_id(project_id):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM PROJECTS WHERE ID = %s
    """, (project_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_all_projects():
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM PROJECTS ORDER BY REGISTER_DATE DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_projects_for_manager(cid):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM PROJECTS
        WHERE MANAGER_CID = %s
        ORDER BY REGISTER_DATE DESC
    """, (cid,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_today_attendance(cid=None):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    if cid is None:
        cur.execute("""
            SELECT * FROM ATTENDANCE
            WHERE WORK_DATE = CURDATE()
            ORDER BY REGISTER_DATE DESC
        """)
        rows = cur.fetchall()
    else:
        cur.execute("""
            SELECT * FROM ATTENDANCE
            WHERE CID = %s AND WORK_DATE = CURDATE()
            ORDER BY REGISTER_DATE DESC
        """, (cid,))
        rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_task_by_id(task_id):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM TASKS WHERE ID = %s
    """, (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_tasks_for_project(project_id):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM TASKS
        WHERE PROJECT_ID = %s
        ORDER BY REGISTER_DATE DESC
    """, (project_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_tasks_for_user(cid):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM TASKS
        WHERE ASSIGNEE_CID = %s
        ORDER BY REGISTER_DATE DESC
    """, (cid,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_open_attendance(cid):
    conn = mysql.connector.connection.MySQLConnection(**database_config, database=database_name)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM ATTENDANCE
        WHERE CID = %s AND WORK_DATE = CURDATE() AND CHECKOUT_TIME IS NULL
        LIMIT 1
    """, (cid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row