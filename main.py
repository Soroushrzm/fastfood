from pyrogram import Client , filters
from pyrogram.types import Message
from pyromod import listen
import sqlite3
from sqlite3 import Error




bot = Client(session_name= "fastfood" , config_file= "config.ini")


    
print("ALIVE YET !")
bot.run()