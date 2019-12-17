import pymssql
import time
from datetime import datetime
from termcolor import colored
from pos.point_of_sale.config import config
from pos.point_of_sale.utils import constants
from pos.point_of_sale.db_functions.DBManager import DBManager
import traceback

def cnt_sql(sql, fn):
    tmpsql = sql.split('where')
    if tmpsql[0] in config.sql_dict:
        config.sql_dict[tmpsql[0]] = [config.sql_dict[tmpsql[0]][0] + 1, fn]
    else:
        config.sql_dict[tmpsql[0]] = [1, fn]

class DBActions:
    cursor = None
    
    def __init__(self):
        self.cursor = DBManager.getInstance()
    
    # --------------------------------------------------------------------------------------------------------------------------Yan for test cases
    def find_pricepoint(self, pp_type, packageid, userinfo):
        cnt = 0;
        pp_list = []
        rows = None
        try:
            sql = F"select * from PackageDetail where packageid = {packageid}"
            cnt_sql(sql, 'get_pricepoints')
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            while rows == None and cnt < 3:
                cnt += 1
                rows = self.cursor.fetchall()
                time.sleep(1)
            for pp in rows:
                pp_list.append(pp['BillConfigID'])
            for pricepointid in (pp_list):
                sql = F"select CollectUserInfo, Type from MerchantBillConfig where billconfigid = {pricepointid}"
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                
                if rows[0]['CollectUserInfo'] == userinfo and rows[0]['Type'] == pp_type:
                    return pricepointid
        
        except Exception as ex:
            traceback.print_exc
            pass
    
    # --------------------------------------------------------------------------------------------------------------------------
    def find_pricepoint_package1(self, merchantid, pp_type, userinfo):  # visa_secure
        package_for_pp = None
        package = None
        if config.test_data['MerchantID'] == 27001:
            package = self.package(900)
            package_for_pp = 900
        elif config.test_data['MerchantID'] == 21621:
            package = self.package(800)
            package_for_pp = 800
        cnt = 0
        currency = config.test_data['currency_base']
        pp_list = []
        tc = {}
        rows = None
        initial_price = 'InitialPrice > 0'
        try:
            if 'FreeTrial' in config.test_data['transaction_type'] and not pp_type == 506:
                sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                      F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice = 0"
            elif 'FreeTrial' in config.test_data['transaction_type'] and  pp_type == 506:
                if config.test_data['ic_istrial']:
                    sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                          F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice = 0 and ICAdjustTrial = 1"
                elif config.test_data['ic_istrial'] == False:
                    sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                          F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice = 0 and ICAdjustTrial = 0"
            elif pp_type == 506 :
                if config.test_data['ic_istrial']:
                    sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                          F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice > 0 and ICAdjustTrial = 1"
                elif config.test_data['ic_istrial'] == False:
                    sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                          F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice > 0 and ICAdjustTrial = 0"
            
                
            else:
                if pp_type == 511 or pp_type == 505:
                    sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                          F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice = 0"
                else:
                    sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                          F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and InitialPrice > 0"
            
            self.cursor.execute(sql)
            while rows == None and cnt < 3:
                cnt += 1
                rows = self.cursor.fetchall()
                time.sleep(1)
            if not rows:
                cnt = 0
                print(sql)
                self.insert_pricepoint_with_parameters(merchantid, pp_type, userinfo, currency)
                # self.fill_package_with_pricepoints(package, config.test_data['MerchantID'])
                time.sleep(1)
                self.cursor.execute(sql)
                while not rows and cnt < 3:
                    cnt += 1
                    rows = self.cursor.fetchall()
                    time.sleep(1)
                billconfigid = rows[0]['BillConfigID']
                sql = "insert into PackageDetail values({}, {}, {}, GETDATE(), 'autotest', 1)".format(package_for_pp, merchantid, billconfigid)
                self.cursor.execute(sql)
                print('tested')
            pricepoint = rows[0]['BillConfigID']
            tc = rows[0]
            tc = {**tc, **package}
            return tc
            z = 3
        except Exception as ex:
            traceback.print_exc
            pass
    def find_pricepoint_package(self, merchantid, pp_type, userinfo):  # visa_secure
        package_for_pp = None
        package = None
        if config.test_data['MerchantID'] == 27001:
            package = self.package(900)
            package_for_pp = 900
        elif config.test_data['MerchantID'] == 21621:
            package = self.package(800)
            package_for_pp = 800
        cnt = 0
        currency = config.test_data['currency_base']
        pp_list = []
        tc = {}
        rows = None
        initial_price = 'InitialPrice > 0'
        if 'FreeTrial' in config.test_data['transaction_type']:
            initial_price = 'InitialPrice = 0'
        try:
            sql = F"select top 1 * from merchantbillconfig where merchantid = {merchantid} and type = {pp_type} " \
                      F"and CollectUserinfo = {userinfo} and Currency = '{currency}' and {initial_price}"
            #print(sql)
            self.cursor.execute(sql)
            while rows == None and cnt < 3:
                cnt += 1
                rows = self.cursor.fetchall()
                time.sleep(1)
            if not rows:
                cnt = 0
                self.insert_pricepoint_with_parameters(merchantid, pp_type, userinfo, currency)
                time.sleep(1)
                self.cursor.execute(sql)
                while not rows and cnt < 3:
                    cnt += 1
                    rows = self.cursor.fetchall()
                    time.sleep(1)
                if not rows:
                    print('Failed to insert pricepoint')
                    return False
                billconfigid = rows[0]['BillConfigID']
                sql = "insert into PackageDetail values({}, {}, {}, GETDATE(), 'autotest', 1)".format(package_for_pp, merchantid, billconfigid)
                self.cursor.execute(sql)
                if (pp_type == 510 or pp_type == 511):
                    #sql = "insert into MerchantBillConfig_Extension values({}, 0, 15000.00, GETDATE(), 'dimasik@tut.by', NULL, NULL,NULL,NULL,NULL,NULL)".format(billconfigid)
                    sql = "insert into MerchantBillConfig_Extension values({}, 0.00, 40.00, GETDATE(), 'dimasik@tut.by', 2.95, 40.00,3,365,30,90)".format(billconfigid)
                    self.cursor.execute(sql)
            pricepoint = rows[0]['BillConfigID']
            tc = rows[0]
            tc = {**tc, **package}
            return tc
            z = 3
        except Exception as ex:
            traceback.print_exc()
            pass
    def insert_pricepoint_with_parameters(self, merchantid, pp_type, userinfo, currency):
        rebil_length = 30
        rebil_price = 2.00
        initial_price = 1
        is_postpay = 0
        if 'FreeTrial' in config.test_data['transaction_type']:
            initial_price = 0
        if (pp_type == 502 or pp_type == 503 or pp_type == 510):
            rebil_length = 0
            rebil_price = 0.00
        if (pp_type == 503 or pp_type == 510):
            is_postpay = 1
        sql = constants.INSERT_PRICE_POINT.format(merchantid, pp_type, currency, initial_price, rebil_price, rebil_length, userinfo, is_postpay)
        cnt_sql(sql, 'execute_insert')
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False
    
    def get_pricepoints(self):
        cnt = 0;
        pp_list = []
        rows = None
        try:
            sql = F"select * from PackageDetail where packageid = {config.test_data['packageid']}"
            cnt_sql(sql, 'get_pricepoints')
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            while rows == None and cnt < 3:
                cnt += 1
                rows = self.cursor.fetchall()
                time.sleep(1)
            for pp in rows:
                pp_list.append(pp['BillConfigID'])
            return pp_list
        except Exception as ex:
            if config.test_data['traceback']:
                traceback.print_exc()
            print(f"Function: get_pricepoints \n {Exception} ")
            pass
    
    def execute_select_one_with_wait(self, sql, condition):
        cnt = 0
        cnt_sql(sql, 'execute_select_one_with_wait')
        response = None
        sql = sql.format(condition)
        while response == None and cnt < 15:
            cnt += 1
            time.sleep(1)
            self.cursor.execute(sql)
            response = self.cursor.fetchone()
        return response
    
    def execute_select_one_parameter(self, sql, condition):
        cnt_sql(sql, 'execute_select_one_parameter')
        sql = sql.format(condition)
        # print(sql)
        try:
            self.cursor.execute(sql)
            response = self.cursor.fetchone()
            if not response:
                return None
            return response
        except Exception as ex:
            traceback.print_exc()
            pass
    
    def cardinal_actions(self, resulttype, scopetype):
        sql = f"select ResultAction from CardinalResultActions where ResultType = {resulttype} and ScopeType = {scopetype}"
        cnt_sql(sql, 'cardinal_actions')
        # print(sql)
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        if not response:
            return None
        return response
    
    def execute_select_two_parameters(self, sql, condition_first, condition_second):
        sql = sql.format(condition_first, condition_second)
        cnt_sql(sql, 'execute_select_two_parameters')
        cnt_sql(sql, 'execute_select_two_parameters')
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        if not response:
            return None
        return response
    
    def execute_select_with_no_params(self, sql):
        cnt_sql(sql, 'execute_select_with_no_params')
        # cnt_sql(sql, 'execute_select_with_no_params')
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        return response
    
    def execute_insert(self, sql, parameter):
        sql = sql.format(parameter)
        cnt_sql(sql, 'execute_insert')
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False
    
    def get_value_from_postback_configs(self, package_id, column_to_return):
        p_type_list = []
        sql = constants.POST_BACK_TYPES_FROM_CONFIG.format(package_id)
        cnt_sql(sql, 'get_value_from_postback_configs')
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            p_type = row[column_to_return]
            # print(f'Adding {p_type} to the config list')
            p_type_list.append(p_type)
        if not p_type_list:
            print("No values to return for postback config")
        return p_type_list
    
    def get_value_from_postback_notif(self, trans_id, column_to_return):
        cnt = 0
        n_type_list = []
        rows = None
        sql = constants.POST_BACK_TYPES_FROM_NOTIFICATION.format(trans_id)
        self.cursor.execute(sql)
        cnt_sql(sql, 'get_value_from_postback_notif')
        while rows == None and cnt < 2:
            cnt += 1
            time.sleep(0.5)
        rows = self.cursor.fetchall()
        if not rows:
            return None
        for row in rows:
            p_type = row[column_to_return]
            # print(f'Adding {p_type} to the notification list')
            n_type_list.append(p_type)
        if not n_type_list:
            print("No values to return for postback notif")
        return n_type_list
    
    def get_collect_user_info_value(self, billconfigid):
        # sql = constants.COLLECT_USER_INFO_BY_PACKAGE.format(package_id)
        sql = f"select CollectUserInfo from MerchantBillConfig where BillConfigID = {billconfigid} "
        
        cnt_sql(sql, 'get_collect_user_info_value')
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows[0]['CollectUserInfo']
    
    def get_url_from_config(self, postback_id):
        sql = constants.POST_BACK_CINFIG_URL_BY_ID.format(postback_id)
        cnt_sql(sql, 'get_url_from_config')
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        if not temp:
            return None
        temp = temp['PostbackURL']
        return temp
    
    def get_url_from_notif(self, postback_id, trans_id):
        sql = constants.POST_BACK_NOTIF_URL_BY_ID.format(trans_id, postback_id)
        cnt_sql(sql, 'get_url_from_notif')
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['PostData']
        return temp
    
    def get_postback_type_by_postback_id(self, postback_id):
        sql = constants.POST_BACK_TYPE_BY_POSTBACK_ID.format(postback_id)
        cnt_sql(sql, 'get_postback_type_by_postback_id')
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['PostbackType']
        return temp
    
    def get_payment_acct_id(self, transaction_id):
        sql = constants.PAYMENT_ACCT_ID.format(transaction_id)
        cnt_sql(sql, 'get_payment_acct_id')
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        if temp == None:
            return None
        temp = temp['value']
        return temp
    
    def get_postback_status_by_id(self, postback_id, trans_id):
        sql = constants.POSTBACK_STATUS_BI_ID.format(postback_id, trans_id)
        cnt_sql(sql, 'get_postback_status_by_id')
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        temp = temp['status']
        return temp
    
    def get_trans_source(self, trans_id):
        sql = constants.POS_OR_SERVICE_TRANS_SOURCE.format(trans_id)
        cnt_sql(sql, 'get_trans_source')
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        return temp
    
    def verify_captures(self, transids):
        captures = {}
        for tid in transids:
            sql = f"select TransStatus, TransType from multitrans where TransID ={tid}"
            cnt_sql(sql, 'verify_captures')
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
        cnt_sql(sql, 'fraud_scrub')
        self.cursor.execute(sql)
    
    def refund_task(self, tasktype, tid):
        taskid = "0"
        taskype = tasktype  # "842"  # 843 refund only, 842 RC, 841 RE
        transid = tid
        reasonode = "825"
        enteredy = "automation"
        comment = "snowflakes"
        sql = f"Exec CS_Refund_Tasks_Insert {taskid},{taskype} ,{transid},{reasonode},{enteredy},{comment}"
        cnt_sql(sql, 'refund_task')
        print(sql)
        try:
            self.cursor.execute(sql)
        except Exception as ex:
            if str(ex) == 'Specified as_dict=True and there are columns with no names: [0]':
                tmp = self.tasks_table(tid)
                if len(tmp) > 0:
                    pass
            else:
                traceback.print_exc()
    
    def tasks_table(self, tid):
        tasktype = ''
        status = ''
        sql = f"select * from tasks where TransID = {tid}"
        cnt_sql(sql, 'tasks_table')
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
        cnt_sql(sql, 'update_processor')
        self.cursor.execute(sql)
    
    def update_merchantbillconfig_oneclick(self, pricepointid, enabled):
        sql = f'UPDATE MerchantBillConfig set OneClickEnabled = {enabled} where billconfigid = {pricepointid}'
        cnt_sql(sql, 'update_merchantbillconfig_oneclick')
        self.cursor.execute(sql)
    
    def update_pp_singleuse_promo(self, pricepointid, featureid, enabled):
        sql = f"Select * from pricepointfeaturedetail where pricepointid = {pricepointid} and featureid = {featureid} "
        cnt_sql(sql, 'update_pp_singleuse_promo')
        retry_flag = True
        retry_count = 0
        while retry_flag and retry_count < 3:
            try:
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                if len(rows) > 0:
                    sql = f"UPDATE pricepointfeaturedetail set enabled = {enabled} where pricepointid = {pricepointid} and featureid = {featureid}"
                    cnt_sql(sql, 'update_pp_singleuse_promo')
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
    
    def deleteall_from_packagedetails(self, package):
        sql = f'Delete from PackageDetail where packageid = {package}'
        cnt_sql(sql, 'deleteall_from_packagedetails')
        self.cursor.execute(sql)
    
    def update_package(self, package, merchantid, billconfigid):
        sql = f'Delete from PackageDetail where packageid = {package}'
        cnt_sql(sql, 'update_package1')
        self.cursor.execute(sql)
        self.cursor.callproc('MP_PackageDetail_Update',
                             (package, merchantid, billconfigid, '2018-06-04 17:39:45.887', 'autotester', 1))
        sql = f"Update package set MerchantID = {merchantid} where PackageID = {package}"
        cnt_sql(sql, 'update_package')
        self.cursor.execute(sql)
    
    # ------------------------------------------------------------Yan to add all pricepoints to same package
    def get_all_pricepoints(self):
        cnt = 0;
        pp_list = []
        rows = None
        try:
            sql = f"select * from MerchantBillConfig where merchantid = {config.test_data['MerchantID']}"
            cnt_sql(sql, 'get_pricepoints')
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            # while rows == None and cnt < 3:
            #     cnt += 1
            #     rows = self.cursor.fetchall()
            #     time.sleep(1)
            for pp in rows:
                pp_list.append(pp['BillConfigID'])
            return pp_list
        except Exception as ex:
            if config.test_data['traceback']:
                traceback.print_exc()
            print(f"Function: get_pricepoints \n {Exception} ")
            pass
    
    def fill_package_with_pricepoints(self, package, merchantid, billconfigid):
        try:
            sql = "Select BillConfigID from PackageDetail where packageid = {} and billconfigid = {}"
            res = self.execute_select_two_parameters(sql, package, billconfigid)
            if res:
                print(f"Pricepoint{billconfigid} in the package {package} already {billconfigid}")
            else:
                self.cursor.callproc('MP_PackageDetail_Update',
                                     (package, merchantid, billconfigid, '2018-06-04 17:39:45.887', 'autotester', 1))
                sql = f"Update package set MerchantID = {merchantid} where PackageID = {package}"
                self.cursor.execute(sql)
                print(f"Pricepoint{billconfigid} in the package {package} incerted {billconfigid}")
            
            z = 3
        
        except Exception as ex:
            traceback.print_exc()
            pass
    
    # ---------------------------------------------------------------------------------------------------------------
    def merchant_us_or_eu(self, merchantid):
        sql = f'select MerchantCountry from merchants where merchantid ={merchantid}'
        cnt_sql(sql, 'merchant_us_or_eu')
        # print(sql)
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()
        return temp
    
    def multitrans_val(self, transguid):
        transid = 0
        purchaseid = 0
        transtype = 0
        retry_flag = True
        retry_count = 0
        sql = f"select PurchaseID,TransID ,TransType from multitrans where transguid ='{transguid}'  and TransType in ( 101,1011 ) "
        cnt_sql(sql, 'multitrans_val')
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
        cnt_sql(sql, 'multitrans_full_record')
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
        cnt_sql(sql, 'asset_full_record')
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
        cnt_sql(sql, 'merchantbillconfig')
        try:
            self.cursor.execute(sql)
            response = self.cursor.fetchone()
            return response
        except Exception as ex:
            traceback.print_exc()
            pass
        # while retry_flag and retry_count < 30:
        #     try:
        #         self.cursor.execute(sql)
        #         rows = self.cursor.fetchall()
        #         if len(rows) > 0:
        #             retry_flag = False
        #             # row = ''
        #             # for row in rows:
        #             #     for key,value in row.items():
        #             #         print (key , ":" , value)
        #             return rows
        #     except Exception as ex:
        #         print(ex)
        #         print("Retry after 1 sec")
        #         retry_count = retry_count + 1
        #         time.sleep(2)
    
    def package(self, package):
        retry_flag = True
        retry_count = 0
        sql = f"select * from package where packageid ={package}"
        cnt_sql(sql, 'package')
        self.cursor.execute(sql)
        response = self.cursor.fetchone()
        return response
        # while retry_flag and retry_count < 30:
        #     try:
        #         self.cursor.execute(sql)
        #         rows = self.cursor.fetchall()
        #         if len(rows) > 0:
        #             retry_flag = False
        #             # row = ''
        #             # for row in rows:
        #             #     for key,value in row.items():
        #             #         print (key , ":" , value)
        #             return rows
        #     except:
        #         print("Retry after 1 sec")
        #         retry_count = retry_count + 1
        #         time.sleep(2)
    
    def exc_rate(self, currency, billconfig_currency):
        exchange_rate = ''
        retry_flag = True
        retry_count = 0
        sql = (
            f"SELECT TOP 1 [Rate] FROM [sp_data].[dbo].[ExchangeRates] where ConsumerIso = '{currency}' and   MerchantIso = '{billconfig_currency}' order by importdatetime desc")
        cnt_sql(sql, 'exc_rate')
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
        cnt_sql(sql, 'url')
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
        # cnt_sql(sql, 'encrypt_email')
        while retry_flag and retry_count < 5:
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
        # cnt_sql(sql, 'encrypt_card')
        while retry_flag and retry_count < 5:
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
        # cnt_sql(sql, 'encrypt_string')
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
        # cnt_sql(sql, 'decrypt_string')
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
        sql = (
            f"SELECT * FROM [sp_data].[dbo].[PointOfSaleEmailQueue] where [DateQueued] > '{datetime.now().date()}' and EmailParameters like '%{str(transid)}%'")
        cnt_sql(sql, 'check_email_que')
        while retry_flag and retry_count < 10:
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
                    time.sleep(0.5)
            except Exception as ex:
                print(ex)
                print("Retry after 1 sec")
                retry_count = retry_count + 1
                time.sleep(2)
                return 'noemail'
    
    def sql(self, sql):
        retry_flag = True
        cnt_sql(sql, 'sql')
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
    
    def get_pricingguid_records(self, merchantid, type):  # used in recurring dynamic
        pricingguid = ''
        initial_price = ''
        retry_flag = True
        retry_count = 0
        sql = f"select  * from PricingGuids where MerchantID ={merchantid} and pricepointtype = {type} "  # PricingGuid, InitialPrice
        cnt_sql(sql, 'get_pricingguid')
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
    
    def get_pricingguid(self, merchantid, type):
        pricingguid = ''
        initial_price = ''
        retry_flag = True
        retry_count = 0
        sql = f"select top 1 * from PricingGuids where MerchantID ={merchantid} and pricepointtype = {type} "  # PricingGuid, InitialPrice
        cnt_sql(sql, 'get_pricingguid')
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
        cnt_sql(sql, 'pricepoint_list')
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
                cnt_sql(sql, 'pricepoint_type')
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
