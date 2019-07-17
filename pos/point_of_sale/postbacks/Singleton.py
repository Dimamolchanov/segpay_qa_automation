import pymssql
from pos.point_of_sale import config


class Singleton:
   __instance = None
   connection = None
   user = "SPStaff"
   password = 'Toccata200e'
   server = config.server
   @staticmethod
   def getInstance():
      """ Static access method. """
      if Singleton.__instance == None:
         Singleton()
      return Singleton.__instance

   def __init__(self):
      """ Virtually private constructor. """
      if Singleton.__instance != None:
         raise Exception("This class is a singleton!")
      else:
          try:
           Singleton.connection = pymssql.connect(Singleton.server, Singleton.user, Singleton.password, "SP_Data")
           # print("Connection with DB is established")
           cursor = Singleton.connection.cursor(as_dict=True)
           Singleton.connection.autocommit(True)
           Singleton.__instance = cursor
          except Exception as ex:
              print(ex.__traceback__)

   @staticmethod
   def kill_db_session():
       """Closes DB connection"""
       Singleton.connection.close()
