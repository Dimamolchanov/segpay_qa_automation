from pos.point_of_sale.postbacks import constants
from pos.point_of_sale.postbacks.db_connection import DB_connect


class DBActions:

    def get_value_from_postback_configs(self, package_id, column_to_return):
        p_type_list = []
        cursor = DB_connect.get_instance()
        sql = constants.POST_BACK_TYPES_FROM_CONFIG.format(package_id)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            p_type = row[column_to_return]
            #print(f'Adding {p_type} to the config list')
            p_type_list.append(p_type)
        DB_connect.kill_db_session()
        if not p_type_list:
            print("No values to return")
        return p_type_list

    def get_value_from_postback_notif(self, trans_id, column_to_return):
        n_type_list = []
        cursor = DB_connect.get_instance()
        sql = constants.POST_BACK_TYPES_FROM_NOTIFICATION.format(trans_id)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            p_type = row[column_to_return]
            #print(f'Adding {p_type} to the notification list')
            n_type_list.append(p_type)
        DB_connect.kill_db_session()
        if not n_type_list:
            print("No values to return")
        return n_type_list


    def get_collect_user_info_value(self, package_id):
        #p_type_list = []
        cursor = DB_connect.get_instance()
        sql = constants.COLLECT_USER_INFO_BY_PACKAGE.format(package_id)
        cursor.execute(sql)
        rows = cursor.fetchall()
        #for row in rows:
        #    p_type = row['CollectUserInfo']
        #    print(f'Adding {p_type} to the list')
        #    p_type_list.append(p_type)
        DB_connect.kill_db_session()
        return rows[0]['CollectUserInfo']


    def get_url_from_config(self, postback_id):
        cursor = DB_connect.get_instance()
        sql = constants.POST_BACK_CINFIG_URL_BY_ID.format(postback_id)
        cursor.execute(sql)
        temp = cursor.fetchone()
        temp = temp['PostbackURL']
        return temp


    def get_url_from_notif(self, postback_id, trans_id):
        cursor = DB_connect.get_instance()
        sql = constants.POST_BACK_NOTIF_URL_BY_ID.format(trans_id, postback_id)
        cursor.execute(sql)
        temp = cursor.fetchone()
        temp = temp['PostData']
        return temp

    def get_postback_type_by_postback_id(self, postback_id):
        cursor = DB_connect.get_instance()
        sql = constants.POST_BACK_TYPE_BY_POSTBACK_ID.format(postback_id)
        cursor.execute(sql)
        temp = cursor.fetchone()
        temp = temp['PostbackType']
        return temp

    def get_payment_acct_id(self, transaction_id):
        cursor = DB_connect.get_instance()
        sql = constants.PAYMENT_ACCT_ID.format(transaction_id)
        cursor.execute(sql)
        temp = cursor.fetchone()
        temp = temp['value']
        return temp


    def get_postback_status_by_id(self, postback_id):
        cursor = DB_connect.get_instance()
        sql = constants.POSTBACK_STATUS_BI_ID.format(postback_id)
        cursor.execute(sql)
        temp = cursor.fetchone()
        temp = temp['status']
        return temp

    def get_trans_source(self, trans_id):
        cursor = DB_connect.get_instance()
        sql = constants.POS_OR_SERVICE_TRANS_SOURCE.format(trans_id)
        cursor.execute(sql)
        temp = cursor.fetchone()
        DB_connect.kill_db_session()
        return temp



