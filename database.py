import uuid
from googleClient import  getKeyValue
import pyodbc
import sqlite3
# Azure SQL Database details
server = 'infinitydbserver.database.windows.net'
database = 'infinity'
username = 'CloudSAc2e67f07'
password = getKeyValue("sqlloginpwd")

# Connection string
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
)
connection = None

def establishDbConnection():
    global connection
    try:
        connection = pyodbc.connect(connection_string)
    except Exception as e:
        print("Error occurred while connecting to Azure SQL:", e)

def create_prompt(prompt,status,correlationId):
    global connection
    if connection is None:
        establishDbConnection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Prompt (prompt, status, correlationid) VALUES (?, ?, ?)', (prompt, status, correlationId))
    connection.commit()
    print("User created successfully!")

# Function to read all records
def read_prompts():
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM prompt')
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Function to update a record
def update_prompt(status,correlationId):
    global connection
    cursor = connection.cursor()
    cursor.execute('UPDATE prompt SET status = ? WHERE correlationid = ?', (status,correlationId))
    connection.commit()
    print("User updated successfully!")

def create_summary(summary,status,correlationId):
    global connection
    cursor = connection.cursor()
    cursor.execute('INSERT INTO ClientSummary (summary, status, correlationid) VALUES (?, ?, ?)', (summary, status, correlationId))
    connection.commit()
    print("Summary created successfully!")

# Function to read all records
def read_summary(correlationId):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM ClientSummary WHERE( correlationid = ? and status = ?)', (correlationId,0))
    rows = cursor.fetchall()
    return  rows
    # for row in rows:
    #     print(row)

# Function to update a record
def update_summary(status,correlationId):
    global connection
    cursor = connection.cursor()
    cursor.execute('UPDATE ClientSummary SET status = ? WHERE correlationid = ?', (status,correlationId))
    connection.commit()
    print("Summary updated successfully!")

def get_matching_question_action(correlationId):
    global connection
    cursor = connection.cursor()
    # cursor.execute('SELECT Prompt,Stage,Sources FROM Stage AS S, StageMetadata AS SM  WHERE S.correlationId = ? and  S.Status = 0 and count(*) = SELECT COUNT(*) FROM SM WHERE SM.CorrelationId=?', (correlationId,correlationId))
    cursor.execute("EXEC GetStageDetails ?",correlationId)
    rows = cursor.fetchall()
    return rows

# Function to update a record
def update_stagemetadata(status, correlationId):
    global connection
    cursor = connection.cursor()
    cursor.execute('UPDATE StageMetadata SET status = ? WHERE correlationid = ?', (1, correlationId))
    connection.commit()
    print("Stage updated successfully!")
