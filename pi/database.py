#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""Contain functions to create and manipulate a db
createdb(mode, name): create a database named name
writetherm: write the temperature and humidity into the database."""

import sqlite3
import hashlib
import time
import random
import json

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def createdb(db_name, mode):
    """If mode == "thermo", create table with name for data from sensors
    mode == user, create table with username & password"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor()
    if mode == "thermo":
        crsr.execute("""CREATE TABLE IF NOT EXISTS therm (  
        time INTEGER,
        sensorname TEXT,  
        temperature REAL,  
        humidity REAL);""")
    elif mode == "users":
        crsr.execute("""CREATE TABLE IF NOT EXISTS users (  
        time INTEGER PRIMARY KEY,
        username TEXT,  
        password TEXT,
        salt TEXT);""")
    elif mode == "emails":
        crsr.execute("""CREATE TABLE IF NOT EXISTS emails (  
        time INT PRIMARY KEY,
        email TEXT);""")
    connection.commit()
    connection.close()

def write_therm(db_name, sensor_name, temp, humid):
    """Write the temperature and humidity to db"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    current_time = int(time.time())
    crsr.execute("INSERT INTO therm VALUES (?, ?, ?, ?)",
        (current_time, sensor_name, temp, humid) )
    connection.commit()
    connection.close()

def write_email(db_name, email):
    """Write the email to db"""
    #time.sleep(1)
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    current_time = int(time.time())
    crsr.execute("INSERT INTO emails VALUES (?, ?)",
        (current_time, email) )
    connection.commit()
    connection.close()

def fetch_one(db_name, paraname, table, num=None):
    """
    fetching columns in a table from db. if num is specified then fetch {num} lastest lines from a table
    """
    res = []
    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row
    crsr = connection.cursor()
    if num == None: 
        crsr.execute(f"SELECT * FROM {table}") 
        ans = crsr.fetchall()
        for i in ans:
            res.append(i[paraname])
    else:
        crsr.execute(f"SELECT * FROM {table} ORDER BY time DESC")
        ans = crsr.fetchmany(num)
        for i in ans:
            res.append(i[paraname])
    connection.commit()
    connection.close()
    return res

def fetch_all(db_name, table, num=None, sensor=None):
    """Get n lastest line from a table in a db"""
    connection = sqlite3.connect(db_name)
    crsr = connection.cursor()
    if num == None:
        crsr.execute(f"SELECT * FROM {table}")
        return_list = crsr.fetchall()
    else:
        if sensor == None:
            crsr.execute(f"SELECT * FROM {table} ORDER BY time DESC")
            return_list = crsr.fetchmany(num)
        else:
            crsr.execute(f"SELECT temperature, humidity FROM therm where sensorname=? ORDER BY time DESC",(sensor,))
            return_list = crsr.fetchone()
    connection.commit()
    connection.close()
    return return_list

def fetch_oneline(db_name, table, username):
    """Get a specific row from a table in a db"""
    connection = sqlite3.connect(db_name)
    crsr = connection.cursor()
    crsr.execute(f"SELECT * FROM {table} WHERE username=?",(username,))
    return_list = crsr.fetchone()
    connection.commit()
    connection.close()
    return return_list

def remove_email(db_name, email):
    """remove an email from db"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    crsr.execute(f"DELETE FROM emails WHERE email=?",(email,)) 
    connection.commit()
    connection.close()

def hash_encode(string: str):
    """Return the SHA3-256 hash of string"""
    return hashlib.sha3_256(string.encode('utf-8')).hexdigest()

def create_user(db_name, username, hashed_password):
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor()  
    current_time = int(time.time())
    chars = ''
    for i in range(16):
        chars = chars + random.choice(ALPHABET)
    new_password = hashed_password + chars
    crsr.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
        (current_time, username, hash_encode(new_password), chars) )
    connection.commit()
    connection.close()

def update_password(db_name, old_user, new_user, new_password):
    connection = sqlite3.connect(db_name)
    crsr = connection.cursor()
    cur_time = int(time.time())
    zchars = ''
    for i in range(16):
        zchars = zchars + random.choice(ALPHABET)
    hashed_pass = hash_encode(new_password + zchars)
    crsr.execute(f"UPDATE users SET time = ?, username = ?, password = ?, salt = ? WHERE username=?",(cur_time,new_user,hashed_pass,zchars,old_user))
    connection.commit()
    connection.close()

def remove_user(db_name, username):
    """remove an user from db"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    crsr.execute(f"DELETE FROM users WHERE username=?",(username,)) 
    connection.commit()
    connection.close()

def get_sensor(db_name):
    """fetch all sensors from db"""
    result = []
    connection = sqlite3.connect('vgu.db') 
    crsr = connection.cursor()
    crsr.execute("SELECT DISTINCT sensorname FROM therm")
    record = crsr.fetchall()
    for i in record:
        result.append(i[0])
    connection.commit()
    connection.close()
    return result

if __name__ == "__main__": 
    '''connection = sqlite3.connect('vgu.db') 
    crsr = connection.cursor()
    crsr.execute('SELECT * FROM therm ORDER BY time DESC LIMIT 1')
    ans = crsr.fetchone()
    curr_time = ans[0]
    import random
    haha = []
    for x in range(1000):
        curr_time = curr_time + 300
        num1 = round(random.uniform(32,33),4)
        num2 = round(random.uniform(68,69),2)
        crsr.execute("INSERT INTO therm VALUES (?, ?, ?, ?)",
        (curr_time, 'thien', num1, num2) )
        #print(curr_time)
    connection.commit()
    connection.close()'''
