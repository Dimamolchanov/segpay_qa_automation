import pymssql
import time
from datetime import datetime
from termcolor import colored

from pos.point_of_sale.utils import constants
from pos.point_of_sale.db_functions.DBManager import DBManager


class DBActions:
    cursor = None

    def __init__(self):
        self.cursor = DBManager.getInstance()

    def execute_select_one_with_wait(self, sql, condition):
        cnt = 0
        response = None
        sql = sql.format(condition)
        while response ==None and cnt <15:
            cnt+= 1
            time.sleep(1)
            self.cursor.execute(sql)
            response = self.cursor.fetchone()
        return response

    def execute_select_one_parameter(self, sql, condition):
        sql = sql.format(condition)
        #print(sql)
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        if not response:
            return None
        return response

    def execute_select_two_parameters(self, sql, condition_first, condition_second):
        sql = sql.format(condition_first, condition_second)
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        if not response:
            return None
        return response

    def execute_select_with_no_params(self, sql):
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        return response

    def execute_insert(self, sql, parameter):
        sql = sql.format(parameter)
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False

    def get_value_from_postback_configs(self, package_id, column_to_return):
        p_type_list = []
        sql = constants.POST_BACK_TYPES_FROM_CONFIG.format(package_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            p_type = row[column_to_return]
            #print(f'Adding {p_type} to the config list')
            p_type_list.append(p_type)
        if not p_type_list:
            print("No values to return for postback config")
        return p_type_list

    def get_value_from_postback_notif(self, trans_id, column_to_return):
        n_type_list = []
        sql = constants.POST_BACK_TYPES_FROM_NOTIFICATION.format(trans_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            p_type = row[column_to_return]
            #print(f'Adding {p_type} to the notification list')
            n_type_list.append(p_type)
        if not n_type_list:
            print("No values to return for postback notif")
        return n_type_list

    def get_collect_user_info_value(self, package_id):
        sql = constants.COLLECT_USER_INFO_BY_PACKAGE.format(package_id)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows[0]['CollectUserInfo']

    def get_url_from_config(self, postback_id):
        sql = constants.POST_BACK_CINFIG_URL_BY_ID.format(postback_id)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['PostbackURL']
        return temp

    def get_url_from_notif(self, postback_id, trans_id):
        sql = constants.POST_BACK_NOTIF_URL_BY_ID.format(trans_id, postback_id)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['PostData']
        return temp

    def get_postback_type_by_postback_id(self, postback_id):
        sql = constants.POST_BACK_TYPE_BY_POSTBACK_ID.format(postback_id)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['PostbackType']
        return temp

    def get_payment_acct_id(self, transaction_id):
        sql = constants.PAYMENT_ACCT_ID.format(transaction_id)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        if temp == None:
            return None
        temp = temp['value']
        return temp

    def get_postback_status_by_id(self, postback_id ,trans_id):
        sql = constants.POSTBACK_STATUS_BI_ID.format(postback_id, trans_id)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['status']
        return temp

    def get_trans_source(self, trans_id):
        sql = constants.POS_OR_SERVICE_TRANS_SOURCE.format(trans_id)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        return temp

    def verify_captures(self, transids):
        captures = {}
        for tid in transids:
            sql = f"select TransStatus, TransType from multitrans where TransID ={tid}"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            for row in rows:
                transstatus = row['TransStatus']
                transtype = row['TransType']
                if transtype == 101 and transstatus != 187:
                    captures[tid] = 'Status did not get updated to 187'
        if len(captures) == 0:
            print(colored(f"Captures  Verified  => Pass ", 'green'))
        else:
            print(colored(f"********************* Captures MissMatch ****************", 'red'))
        for k, v in captures.items():
            print(k, v)
        return captures

    def fraud_scrub(self, captures_date):
        sql = f"exec BEP_InsertFraudScrubCompletion 1,'{captures_date}','AutomationQA'"
        self.cursor.execute(sql)

    def refund_task(self, tasktype, tid):
        taskid = "0"
        taskype = tasktype  # "842"  # 843 refund only, 842 RC, 841 RE
        transid = tid
        reasonode = "825"
        enteredy = "automation"
        comment = "snowflakes"
        sql = f"Exec CS_Refund_Tasks_Insert {taskid},{taskype} ,{transid},{reasonode},{enteredy},{comment}"
        # print(sql)
        self.cursor.execute(sql)

    def tasks_table(self, tid):
        tasktype = ''
        status = ''
        sql = f"select * from tasks where TransID = {tid}"
        # print(sql)
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            for row in rows:
                tasktype = row['TaskType']
                status = row['Status']
            return [tasktype, status]
        except Exception as ex:
            print(ex)

    def update_processor(self, processor, package):
        sql = f'UPDATE Package set PrefProcessorID = {processor} where PackageID = {package}'
        self.cursor.execute(sql)

    def update_merchantbillconfig_oneclick(self, pricepointid, enabled):
        sql = f'UPDATE MerchantBillConfig set OneClickEnabled = {enabled} where billconfigid = {pricepointid}'
        self.cursor.execute(sql)

    def update_pp_singleuse_promo(self, pricepointid, featureid, enabled):
        sql = f"Select * from pricepointfeaturedetail where pricepointid = {pricepointid} and featureid = {featureid} "
        retry_flag = True
        retry_count = 0
        while retry_flag and retry_count < 3:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    sql = f"UPDATE pricepointfeaturedetail set enabled = {enabled} where pricepointid = {pricepointid} and featureid = {featureid}"
                    # print(sql)
                    self.cursor.execute(sql)
                    retry_flag = False
                else:
                    retry_count = retry_count + 1
            # rows = cursor.fetchall()
            except Exception  as ex:
                print(ex)
                print("Module dbs function update_pp_singleuse_promo")
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def update_package(self, package, merchantid, billconfigid):
        sql = f'Delete from PackageDetail where packageid = {package}'
        self.cursor.execute(sql)
        self.cursor.callproc('MP_PackageDetail_Update',
                        (package, merchantid, billconfigid, '2018-06-04 17:39:45.887', 'autotester', 1))
        sql = f"Update package set MerchantID = {merchantid} where PackageID = {package}"
        self.cursor.execute(sql)

    def multitrans_val(self, transguid):
        transid = 0
        purchaseid = 0
        transtype = 0
        retry_flag = True
        retry_count = 0
        sql = f"select PurchaseID,TransID ,TransType from multitrans where transguid ='{transguid}'  and TransType in ( 101,1011 ) "
        # sql = "select PurchaseID,TransID from multitrans where transguid ='" + transguid + "'"
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        transid = row['TransID']
                        purchaseid = row['PurchaseID']
                        transtype = row['TransType']
                    return [transid, purchaseid, transtype]
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def multitrans_full_record(self, transid, transguid, purchaseid):
        sql = ''
        if transid != '':
            sql = f"select * from multitrans where TransID ={transid}"
        elif transguid != '':
            sql = f"select * from multitrans where TransGuid ='{transguid}'"
        else:
            sql = f"select * from multitrans where PurchaseID ={purchaseid}"
        retry_flag = True
        retry_count = 0
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    return rows
                else:
                    retry_count = retry_count + 1
                    time.sleep(1)
            except Exception as ex:
                print(ex)
                print("Module DBS => Function: multitrans_full_record(transid, transguid, purchaseid)")
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def asset_full_record(self, purchaseid):
        retry_flag = True
        retry_count = 0
        sql = "select * from Assets where PurchaseID ='" + str(purchaseid) + "'"
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    return rows
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def merchantbillconfig(self, billconfigid):
        retry_flag = True
        retry_count = 0
        sql = f"select * from merchantbillconfig where billconfigid = {billconfigid}"
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    # row = ''
                    # for row in rows:
                    #     for key,value in row.items():
                    #         print (key , ":" , value)
                    return rows
            except Exception as ex:
                print(ex)
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def package(self, package):
        retry_flag = True
        retry_count = 0
        sql = f"select * from package where packageid ={package}"
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    # row = ''
                    # for row in rows:
                    #     for key,value in row.items():
                    #         print (key , ":" , value)
                    return rows
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def exc_rate(self, currency, billconfig_currency):
        exchange_rate = ''
        retry_flag = True
        retry_count = 0
        sql = (
            f"SELECT TOP 1 [Rate] FROM [sp_data].[dbo].[ExchangeRates] where ConsumerIso = '{currency}' and   MerchantIso = '{billconfig_currency}' order by importdatetime desc")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        exchange_rate = row['Rate']
                    return exchange_rate
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def url(self, urlid):
        domain = ''
        retry_flag = True
        retry_count = 0
        sql = (f"select Domain from Merchant_URL where urlid ={urlid}")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        domain = row['Domain']
                    return domain
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def encrypt_email(self, email):
        email_encrypted = ''
        retry_flag = True
        retry_count = 0
        sql = (f"select dbo.EncryptEMail('{email}') as email")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        email_encrypted = row['email']
                    return email_encrypted
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def encrypt_card(self, cc):
        card_encrypted = ''
        retry_flag = True
        retry_count = 0
        sql = (f"select dbo.EncryptCard('{cc}') as card")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        card_encrypted = row['card']
                    return card_encrypted
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def encrypt_string(self, str):
        string_encrypted = ''
        retry_flag = True
        retry_count = 0
        sql = (f"select dbo.EncryptString('{str}') as string_encrypted")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        string_encrypted = row['string_encrypted']
                    return string_encrypted
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def decrypt_string(self, str):
        string_decrypted = ''
        retry_flag = True
        retry_count = 0
        sql = (f"select dbo.DecryptString('{str}') as string_encrypted")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    row = ''
                    for row in rows:
                        string_decrypted = row['string_encrypted']
                    return string_decrypted
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def check_email_que(self, transid):
        retry_flag = True
        retry_count = 0
        sql = (f"SELECT * FROM [sp_data].[dbo].[PointOfSaleEmailQueue] where [DateQueued] > '{datetime.now().date()}' and EmailParameters like '%{str(transid)}%'")
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                # retry_count = retry_count + 1
                # time.sleep(1)
                if len(rows) > 0:
                    retry_flag = False
                    # row = ''
                    # for row in rows:
                    #     email_que = row['Domain']
                    return rows
                else:
                    retry_count = retry_count + 1
                    time.sleep(1)
            except Exception as ex:
                print(ex)
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)
                return 'noemail'

    def sql(self, sql):
        retry_flag = True
        retry_count = 0
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                retry_flag = False
                return rows
            else:
                retry_count = retry_count + 1
                time.sleep(1)
        except Exception as ex:
            print(ex)
            print("Retry after 1 sec")
            retry_count = retry_count + 1
            time.sleep(2)

    def get_pricingguid(self, merchantid, type):
        pricingguid = ''
        initial_price = ''
        retry_flag = True
        retry_count = 0
        sql = f"select top 1 * from PricingGuids where MerchantID ={merchantid} and pricepointtype = {type} "  # PricingGuid, InitialPrice
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    # row = ''
                    # for row in rows:
                    #     pricingguid = row['PricingGuid']
                    #     initial_price = row ['InitialPrice']
                    return rows
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def pricepoint_list(self, merchantid):
        pp_list = []
        retry_flag = True
        retry_count = 0
        sql = "select billconfigid from merchantbillconfig where merchantid = '" + str(merchantid) + "'"
        while retry_flag and retry_count < 30:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    retry_flag = False
                    for pp in rows:
                        pp_list.append(pp['billconfigid'])

                    # row = ''
                    # for row in rows:
                    #     for key,value in row.items():
                    #         print (key , ":" , value)
                    return pp_list
            except:
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)

    def pricepoint_type(self, merchantid, type):
        retry_flag = True
        retry_count = 0
        pricepoint_type_list = []
        rows = ''
        while retry_flag and retry_count < 30:
            for pricepoint_type in type:
                # sql = "select billconfigid from merchantbillconfig where merchantid = '" + str(merchantid) + "'"
                sql = f"select top 1 BillConfigID  from MerchantBillConfig where merchantid ={merchantid} and type = {pricepoint_type}  "
                try:
                    self.cursor.execute(sql)
                    rows = self.cursor.fetchall()
                    if len(rows) > 0:
                        retry_flag = False
                        pp_type = rows[0]['BillConfigID']
                        pricepoint_type_list.append(pp_type)
                except:
                    print("Retry after 1 sec")
                    retry_count = retry_count + 1
                    time.sleep(2)
            return pricepoint_type_list

    def __del__(self):
        DBManager.kill_db_session()
