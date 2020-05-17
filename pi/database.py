#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""Contain functions to create and manipulate a db
createdb(mode, name): create a database named name
writetherm: write the temperature and humidity into the database."""


import sqlite3
import hashlib
import time

def createdb(mode, name):
    """If mode == "thermo", create table with name for data from sensors
    mode == user, create table with username & password"""
    if mode == "thermo":
        connection = sqlite3.connect(name) 
        crsr = connection.cursor()
        crsr.execute("""CREATE TABLE IF NOT EXISTS therm (  
        time INTEGER ,
        sensorname INTEGER,  
        temperature REAL,  
        humidity REAL);""")
        connection.commit()
        connection.close()
    if mode == "user":
        connection = sqlite3.connect(name) 
        crsr = connection.cursor()
        crsr.execute("""CREATE TABLE IF NOT EXISTS user (  
        time INTEGER ,
        username INTEGER,  
        password INTEGER);""")
        connection.commit()
        connection.close()


def writetherm(db_name, sensor_name, temp, humid):
    """Write the temperature and humidity to db"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    current_time = int(time.time())
    crsr.execute("INSERT INTO therm VALUES (?, ?, ?, ?)",
        (current_time, sensor_name, temp, humid) )
    connection.commit()
    connection.close()

def writeuser(db_name, username, password):
    """Write the username and password to db"""
    connection = sqlite3.connect(db_name) 
    crsr = connection.cursor() 
    current_time = int(time.time())
    crsr.execute("INSERT INTO user VALUES (?, ?, ?)",
        (current_time, username, password) )
    connection.commit()
    connection.close()

def hash(string):
    """Return the SHA3-512 hash of string"""
    return hashlib.sha3_512(string.encode('utf-8')).hexdigest

def create_user(name, hased_password, db_name):
    pass

def match_user(user, hashed_password, db_name):
    pass

def remove_user(user, db_name):
    pass

if __name__ == "__main__": 
    #createdb("thermo","my.db")
    #writetherm("my.db",1,23.3,12.3)
    createdb("user","username.db")
    writeuser("username.db","abc","xyz")