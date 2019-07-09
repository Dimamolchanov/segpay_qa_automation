import pymssql


class DB_connect(object):
    instance = None
    conn = None

    @staticmethod
    def get_instance():
        """Returns Cursor instance"""
        if DB_connect.instance is None and DB_connect.conn is None:
            global conn
            DB_connect()
            user = "SPStaff"
            password = 'Toccata200e'
            conn = pymssql.connect("QADB1", user, password, "SP_Data")
            #print("Connection with DB is established")
            cursor = conn.cursor(as_dict=True)
            conn.autocommit(True)
            return cursor
        else:
            cursor = DB_connect.instance
            return cursor

    @staticmethod
    def kill_db_session():
        """Closes DB connection"""
        global conn
        conn.commit()
        conn.close()
        #print("Connection to DB is closed")
