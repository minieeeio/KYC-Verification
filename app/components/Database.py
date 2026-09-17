import sqlite3

class SQLdb(object):
    def __init__(self):
        print("Initialization for Database")
        self.conn=None
        self.cursor=None
        self.connect_db()
        
        
    def connect_db(self):
        self.conn=sqlite3.connect("KYC_Verification.db")
        self.cursor=self.conn.cursor()
        
    
        
        