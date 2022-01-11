import sqlite3
from sqlite3 import Error

def database():
    try:
        con = sqlite3.connect("fastfood_db.db")
        cur = con.cursor()
        
    except Error as e:
        print(f"The bot is not able to connect to your database\n\n{e}")

    return con , cur

con , cur = database()
admin = 895876106


    
    
    
   










