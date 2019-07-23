import pymssql
from pos.point_of_sale.config import config
import traceback


class DBManager:
    __instance = None
    connection = None
    user = "SPStaff"
    password = 'Toccata200e'
    server = config.server
    @staticmethod
    def getInstance():
        """ Static access method. """
        if not DBManager.__instance:
            DBManager()
        return DBManager.__instance

    def __init__(self):
      """ Virtually private constructor. """
      if DBManager.__instance != None:
         raise Exception("This class is a singleton!")
      else:
          try:
           DBManager.connection = pymssql.connect(DBManager.server, DBManager.user, DBManager.password, "SP_Data")
           # print("Connection with DB is established")
           cursor = DBManager.connection.cursor(as_dict=True)
           DBManager.connection.autocommit(True)
           DBManager.__instance = cursor
          except:
              traceback.print_exc()

    @staticmethod
    def kill_db_session():
       """Closes DB connection"""
       DBManager.connection.close()
