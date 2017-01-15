#!/usr/bin/env python3
# -*- coding=utf-8 -*-
import datetime
import sqlite3
import argparse
from sys import argv
from os.path import basename

# KPIM
# functions and globals variables
__version__="0.1"
DBNAME="kpim.db"
# Table version
# VERSION (table_name,version, creationdt)
table_version_creation = 'CREATE TABLE VERSION (table_name TEXT PRIMARY KEY \
                        ,version TEXT \
                        , creationdt DATE)'

def check_version(table_name):
    """ Check version column for the table_name in VERSION table """
    vers = []
    try:
        conn, c = connect()
        c.execute("select version from VERSION where table_name='"+table_name+"'")
        vers = c.fetchall()
        close(conn)
    except:
        print('Error in check_version')
    return vers

def check_table(table_name):
    """ check if table_name exist """
    exist = []
    try:
        conn, c = connect()
        c.execute('PRAGMA table_info({})'.format(table_name))
        exist = c.fetchall()
        close(conn)
    except:
        print('Error in check_table')
    return exist

def create_version():
    """ Create table VERSION """
    try:
        conn, c = connect()
        c.execute(table_version_creation)
        conn.commit()
        close(conn)
        return True
    except:
        print('Error in create_version')
        return False

def add_version(table_version, table_name):
    """ add a row in table VERSION with table_name and table_version """
    try:
        conn, c = connect()
        c.execute('INSERT INTO VERSION VALUES (?, ?, ?)', (table_name, table_version, current_time()))
        conn.commit()
        close(conn)
        return True
    except:
        print('Error in add_version')
        return False

def execdml(query):
    """ this function is for DML, query is executed, but no row in return """
    try:
        conn, c = connect()
        query=query.replace("'None'",'NULL') 
        c.execute(query)
        conn.commit()
        close(conn)
        return True
    except:
        print('Error in execution of the DML query')
        return False

def execquery(query):
    """ this function is for data selection, query is executed, row are returned """
    res = []
    try:
        conn, c = connect()
        c.execute(query)
        res = c.fetchall()
        close(conn)
    except:
        print('Error in execution of the query')
    return res

# kpim only
arg_desc='Kpim - Personnal Information Manager \
        \nCreated by KalyParker \
        \n - use kpim-css.py for writing cheatsheet \
        \n - use kpim-contacts.py for managing your contacts \
        \n - use kpim-links.py for keeping favorite url'


def check_args():
    """
    Check args
    -v: check version
    -h: help
    """

    parser = argparse.ArgumentParser(description=arg_desc,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v','--version',action='version',version=basename(argv[0]) + ' version: ' + __version__)
    args = parser.parse_args()

    if len(argv)==1:
        parser.print_help()
        exit(1)


def current_time():
    """ return sysdate """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def connect():
    """ Make connection to SQLite database file """
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    return conn, c

def close(conn):
    """ Close connection to the database """
    conn.close()

if __name__ == '__main__':
    check_args()
