import traceback
from datetime import datetime
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.utils import options
from termcolor import colored
from pos.point_of_sale.web import web_module
import yaml
import csv

start_time = datetime.now()
packages = [197216, 197215]  # 197215 65 no 3ds  | 3ds 197216 44
db_agent = DBActions()
d_scenarios = {}
test_case = {}
packageid = 0
test_cases_list = {}
failed_test_cases = {}
passed_test_cases = {}

br = web_module.Signup()

def joinlink():
    joinlink = ''
    dynamic_price = ''
    url_options = config.test_data['ref_variables'] + config.test_data['joinlink_xbill'] + config.test_data['joinlink_param'] + config.test_data['refurl'] + config.template
    octoken = config.test_data['octoken']
    pricingguid = ""  # db_agent.get_pricingguid(tc['MerchantID'], type)[0]
    
    try:
        if config.test_data['transaction_type'] == 'Signup' or config.test_data['transaction_type'] == 'FreeTrial_Signup' :
            if type == 511:
                joinlink = f"{config.url}{config.test_data['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}{url_options}"  # PricingGuid, InitialPrice
            else:
                joinlink = config.url + config.test_data['eticket'] + url_options
        
        elif config.test_data['transaction_type'] == 'OneClick_POS' or config.test_data['transaction_type'] == 'FreeTrial_POS':
            if type == 511:
                joinlink = f"{config.url}{config.test_data['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                joinlink = f"{config.url}{config.test_data['eticket']}&octoken={octoken}" + url_options
        
        elif config.test_data['transaction_type'] == 'OneClick_WS' or config.test_data['transaction_type'] == 'FreeTrial_WS':
            if type == 511:
                joinlink = f"{config.urlws}{config.test_data['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                joinlink = f"{config.urlws}{config.test_data['eticket']}&octoken={octoken}" + url_options
        
        config.test_data['link'] = joinlink
        config.test_data['url_options'] = url_options
        return joinlink  # , url_options, octoken
    except Exception as ex:
        traceback.print_exc()
        print(f"Function joinglink \n {Exception}")
        pass

def asset_verification(test_case):
    type = config.test_data['Type']
    dates = {}
    try:
        # current_date = (datetime.now().date())
        purchtype = config.test_data['Type']
        purchtype_recurring = [501, 505, 506, 511]
        statusDate = 'CurrentDate'
        purchDate = 'CurrentDate'
        if type in purchtype_recurring:
            purchStatus = 801
            cancelDate = 'Null'
            convDate = 'Null'
            lastDate = 'Null'
            if purchtype == 511:
                nextDate = f"CurrentDate + " + str((config.test_data['InitialLen'] + config.test_data['RebillLen']))
                expiredDate = f"CurrentDate + " + str(config.test_data['initiallength511'])
            elif purchtype == 505:
                nextDate = f"CurrentDate + " + str((config.test_data['InitialLen'] + config.test_data['RebillLen']))
                expiredDate = f"CurrentDate + {config.test_data['InitialLen']}"
            else:
                nextDate = f"CurrentDate + {config.test_data['InitialLen']}"
                expiredDate = f"CurrentDate + {config.test_data['InitialLen']}"
        else:
            purchStatus = 804
            nextDate = 'Null'
            cancelDate = 'CurrentDate'
            convDate = 'CurrentDate'
            lastDate = 'CurrentDate'
            if purchtype == 502:
                expiredDate = f"CurrentDate + " + str(config.test_data['InitialLen'])
            else:
                expiredDate = f"CurrentDate"
        
        dates['statusDate'] = statusDate
        dates['purchDate'] = purchDate
        dates['cancelDate'] = cancelDate
        dates['convDate'] = convDate
        dates['lastDate'] = lastDate
        dates['nextDate'] = nextDate
        dates['expiredDate'] = expiredDate
        dates['purchStatus'] = purchStatus
        return dates
    except Exception as ex:
        traceback.print_exc()
        pass

def mt_verification(test_case):
    try:
        transsource = 0
        transstatus = ''
        transtype = ''
        mt = {}
        pp_type = config.test_data['Type']
        if config.test_data['transaction_type'] == 'OneClick_POS':
            transstatus = 186
            transtype = 1011
            if pp_type in (502, 503, 510):
                transsource = 123
            else:
                transsource = 121
        if config.test_data['transaction_type'] == 'Signup':
            transstatus = 184
            transsource = 121
            transtype = 101
        if config.test_data['transaction_type'] == 'OneClick_WS':
            transstatus = 186
            transtype = 1011
            if pp_type in (502, 503, 510):
                transsource = 123
            else:
                transsource = 121
        
        mt['transstatus'] = transstatus
        mt['transtype'] = transtype
        mt['transsource'] = transsource
        
        return mt
    except Exception as ex:
        traceback.print_exc()
        pass

def scenario_heading():
    scn_heading = []
    print("==================================================== *** Scenario - Recurring *** ==========================================================================")
    print(f"| ------------------------------------ | Merchants: EU and US | 3DS Configured | Payments: CC and PayPal |--------------------------------------------------|")
    print(f"| TestCases: | SignUp | OneClick POS | OneClick WS | OneClick POS to Different Merchant | Void | Capture | Refund | Rebill | Reactivate | Aprove | Decline -|")
    print(f"| -----------------------------------------------  Base Currencies | USD | EUR | GPB |----------------------------------------------------------------------|")
    print("============================================================================================================================================================\n")
    scn_heading.append(
            "==================================================== *** Scenario - Recurring *** ==========================================================================")
    scn_heading.append(
            f"| ------------------------------------ | Merchants: EU and US | 3DS Configured | Payments: CC and PayPal |--------------------------------------------------|")
    scn_heading.append(
            f"| TestCases: | SignUp | OneClick POS | OneClick WS | OneClick POS to Different Merchant | Void | Capture | Refund | Rebill | Reactivate | Aprove | Decline -|")
    scn_heading.append(
            f"| -----------------------------------------------  Base Currencies | USD | EUR | GPB |----------------------------------------------------------------------|")
    scn_heading.append(
            "============================================================================================================================================================\n")
    return scn_heading

def print_scenario():
    action = ''
    pp = ''
    bep_msg = ''
    postbacks = ''
    visa_secure_msg = ''
    test_case = config.test_data
    try:
        if config.test_data['pp_type'] == 501: pp = 'Recurring 501'
        if config.test_data['pp_type'] == 511: pp = 'Dynamic Recurring 511'
        try:
            if config.test_data['PostBackID']:
                postbacks = f"PostBackNotifications  should have postbacks for PostBackID: {config.test_data['PostBackID']}"
            else:
                postbacks = f"PostBackNotifications  should not have postbacks for current transaction"
        except Exception as ex:
            traceback.print_exc()
            pass
        
        if config.test_data['merchant'] == 'EU': visa_secure_msg = "3DS          | Cardinal3dsRequests should have the response from Cardinal"
        if config.test_data['merchant'] == 'US':  visa_secure_msg = '3DS          | Multitrans UserData should have responce from Cardinal'
        d = asset_verification(test_case)
        mt = mt_verification(test_case)
        if config.test_data['payment'] == 'CC':
            payment = f"Payment Method: Credit Card [ {config.test_data['cc']} ]"
        else:
            payment = f"Payment Method: PayPal"
        
        if config.test_data['action_bep'] == 'Cancel':
            bep_msg = '| This Transaction need to be canceled in Merchant Portal after Completion'
        if config.test_data['action_bep'] == 'Void_Refund_Cancel':
            bep_msg = '| This Transaction will be voided - Select (Refund and Cancel)  in Merchant Portal after Completion'
        if config.test_data['action_bep'] == 'Void_Refund_Expire':
            bep_msg = '| This Transaction will be voided - Select (Refund and Expire)  in Merchant Portal after Completion'
        
        print(
                f"TestCase_____________________________________________________________________________________________________________________{config.test_data['test_case_number']}")
        print(
                f"| {pp} | Merchant: {config.test_data['merchant']}| 3DS Configured | Action: {config.test_data['transaction_type']} | CollectUserInfo: {config.test_data['userinfo']}")
        print(
                f"| Processor: {config.test_data['processor_name']}  | DMCStatus: {config.test_data['DMCStatus']} | DMC: {config.test_data['dmc']} | Language: {config.test_data['lang']} | PostBackID: {config.test_data['PostBackID']}")
        print(f"| This Transactions should be aproved | Eticket: {config.test_data['eticket']} | {payment}")
        print(bep_msg)
        print("|________________________________________________________________________________________________________________________________\n")
        print(f"JoinLink : {config.test_data['link']}\n")
        print("Expected:")
        print(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("Note:        | Please check all PostBacks and Emails")
        print(
                f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} |"
                f" CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
        print(f"Assets:      | PurchStatus: {d['purchStatus']} | AuthCurrency: {config.test_data['dmc']} |  Purchases: 1 | PurchType: {scenario[1]}")
        print(
                f"Dates :      | Status: {d['statusDate']} | Purch: {d['statusDate']}  | Cancel: {d['cancelDate']} | Conv: {d['convDate']} | Last: {d['lastDate']} | Next: {d['nextDate']} | Expire: {d['expiredDate']} ")
        print(f"Email:       | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        print(f"PostBacks    | {postbacks} ")
        print(visa_secure_msg)
        print("SegPayLogs:  | Please check SegpayLogs after each transaction to see if there are any related errors.")
        print(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")
        print(colored("Actual Results:", 'cyan', attrs=['bold']))
        print(
                "________________________________________________________________________________________________________________________________________________________________________Results\n")
        
        # test cases
        tc = []
        tc.append(
                f"TestCase_____________________________________________________________________________________________________________________{config.test_data['test_case_number']}")
        tc.append(
                f"| {pp} | Merchant: {config.test_data['merchant']}| 3DS Configured | Action: {config.test_data['transaction_type']} | CollectUserInfo: {config.test_data['userinfo']}")
        tc.append(
                f"| Processor: {config.test_data['processor_name']}  | DMCStatus: {config.test_data['DMCStatus']} | DMC: {config.test_data['dmc']} | Language: {config.test_data['lang']} | PostBackID: {config.test_data['PostBackID']}")
        tc.append(f"| This Transactions should be aproved | Eticket: {config.test_data['eticket']} | {payment}")
        tc.append(bep_msg)
        tc.append("|________________________________________________________________________________________________________________________________\n")
        tc.append(f"JoinLink : {config.test_data['link']}\n")
        tc.append("Expected:")
        tc.append(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        tc.append("Note:        | Please check all PostBacks and Emails")
        tc.append(
                f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} |"
                f" CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
        tc.append(f"Assets:      | PurchStatus: {d['purchStatus']} | AuthCurrency: {config.test_data['dmc']} |  Purchases: 1 | PurchType: {scenario[1]}")
        tc.append(
                f"Dates :      | Status: {d['statusDate']} | Purch: {d['statusDate']}  | Cancel: {d['cancelDate']} | Conv: {d['convDate']} | Last: {d['lastDate']} | Next: {d['nextDate']} | Expire: {d['expiredDate']} ")
        tc.append(f"Email:       | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        tc.append(f"PostBacks    | {postbacks} ")
        tc.append(visa_secure_msg)
        tc.append("SegPayLogs:  | Please check SegpayLogs after each transaction to see if there are any related errors.")
        tc.append(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")
        return tc
    
    except Exception as ex:
        traceback.print_exc()
        pass

def verify_transaction(transaction_type, current_transaction_record):
    pass_fail = ''
    if current_transaction_record['Authorized']:
        config.test_data['authorized'] = True
        aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
        print(colored(
                f"PurchaseID: {current_transaction_record['PurchaseID']} | TransId:{current_transaction_record['TransID']} | TransGuid: {current_transaction_record['TRANSGUID']}",
                'yellow'))
        config.test_data['actual'] = [
            f"PurchaseID: {current_transaction_record['PurchaseID']} | TransId:{current_transaction_record['TransID']} | TransGuid: {current_transaction_record['TRANSGUID']}"]
        config.oc_tokens[current_transaction_record['PurchaseID']] = [config.test_data['Type'], current_transaction_record['MerchantCurrency'],
                                                                      current_transaction_record['Language']]
        tmpstr = f"Transaction Aproved : AuthCode:{current_transaction_record['AuthCode']}"
        print(colored(tmpstr, 'cyan', attrs=['bold']))
    else:
        result = current_transaction_record['full_record']
        tmpstr = f"Transaction DECLINED : AuthCode:{result['AuthCode']}"
        print(colored(tmpstr, 'red', attrs=['bold']))
    
    if transaction_type == 'OneClick_POS' or transaction_type == 'FreeTrial_POS':
        pass_fail = TransActionService.verify_oc(current_transaction_record, 'pos')
    elif transaction_type == 'Signup' or transaction_type == 'FreeTrial_Signup':
        pass_fail = TransActionService.verify_signup_transaction(current_transaction_record)
    elif transaction_type == 'OneClick_WS' or transaction_type == 'FreeTrial_WS':
        pass_fail = TransActionService.verify_oc(current_transaction_record, 'ws')
    if current_transaction_record:
        if pass_fail:
            print(colored(f"Scenario completed: All Passed", 'green', attrs=['bold', 'underline', 'dark']))
            options.get_error_from_log()
            print(
                    "____________________________________________________________________________________________________________________________________________________________________End_Results\n\n")
            return True
        else:
            print(colored(f"Scenario had some issues: Failed | Re-Check Manually |", 'red', attrs=['bold', 'underline', 'dark']))
            options.get_error_from_log()
            print(
                    "____________________________________________________________________________________________________________________________________________________________________End_Results\n\n")
            return False

def create_transaction():
    transaction_type = config.test_data['transaction_type']
    current_transaction_record = {}
    try:
        
        if transaction_type == 'OneClick_POS' or transaction_type == 'FreeTrial_POS':
            current_transaction_record = br.oc_pos()
        
        elif transaction_type == 'Signup' or transaction_type == 'FreeTrial_Signup' :
            current_transaction_record = br.create_signup()
        elif transaction_type == 'OneClick_WS' or transaction_type == 'FreeTrial_WS':
            current_transaction_record = br.oc_ws()
        
        if current_transaction_record:
            print(f"{transaction_type} => Eticket: {config.test_data['eticket']}  | Processor: {current_transaction_record['Processor']} "
                  f"| Lnaguage: {config.test_data['lang']} | Type: {config.test_data['Type']} | DMC: {config.test_data['dmc']}")
            config.test_data['record_to_check'] = current_transaction_record
            config.test_data['PurchaseID'] = current_transaction_record['PurchaseID']
            config.test_data['TransID'] = current_transaction_record['TransID']
        
        return current_transaction_record
    except Exception as ex:
        traceback.print_exc()
        pass

def create_test_case(scenario):
    merchantid = ''
    test_case_number = 0
    try:
        config.test_data = {}
        test_case_number += 1
        find_pp_package = None
        cnt = 0
        if scenario[0] == 'EU_EUR':
            config.test_data['currency_base'] = 'EUR'
            config.test_data['merchant'] = 'EU'
            config.test_data['octoken'] = options.oc_tokens('EU')
        # elif scenario[0] == 'EU_GPB':
        #     config.test_data['currency_base'] = 'GPB'
        #     config.test_data['merchant'] = 'EU'
        #     config.test_data['octoken'] = options.oc_tokens('EU')
        elif scenario[0] == 'EU':
            config.test_data['merchant'] = 'EU'
            config.test_data['currency_base'] = 'USD'
            config.test_data['octoken'] = options.oc_tokens('EU')
        elif scenario[0] == 'US':
            config.test_data['merchant'] = 'US'
            config.test_data['currency_base'] = 'USD'
            config.test_data['octoken'] = options.oc_tokens('US')
        elif scenario[0] == 'EU_US':
            config.test_data['merchant'] = 'EU'
            config.test_data['currency_base'] = 'USD'
            config.test_data['octoken'] = options.oc_tokens('US')
        elif scenario[0] == 'US_EU':
            config.test_data['merchant'] = 'US'
            config.test_data['currency_base'] = 'USD'
            config.test_data['octoken'] = options.oc_tokens('EU')
        
        config.test_data['name'] = f"{test_case_number}:{scenario[0]}:{scenario[1]}:{scenario[2]}:{scenario[3]}"
        config.test_data['test_case_number'] = test_case_number
        # config.test_data['merchant'] = scenario[0]  # eu vs us
        config.test_data['payment'] = scenario[1]
        config.test_data['transaction_type'] = scenario[2]
        config.test_data['action_bep'] = scenario[3]
        if config.test_data['transaction_type'] == 'OneClick_WS':
            sql = "Select AuthCurrency,CustLang  from Assets where purchaseid = {} "
            result = db_agent.execute_select_one_parameter(sql, config.test_data['octoken'])
            config.test_data['dmc'] = result['AuthCurrency']
            config.test_data['lang'] = result['CustLang']
        else:
            config.test_data['lang'] = options.random_lang()
            if config.test_data['merchant'] == 'EU':
                config.test_data['dmc'] = options.random_dmc()
            else:
                config.test_data['dmc'] = 'USD'
        if config.test_data['merchant'] == 'EU':
            merchantid = 27001
        else:
            merchantid = 21621
        config.test_data['MerchantID'] = merchantid
        config.test_data['userinfo'] = options.collect_userinfo()
        config.test_data['joinlink_param'] = options.joinlink_param()
        config.test_data['joinlink_xbill'] = options.joinlink_xbill()
        config.test_data['ref_variables'] = options.ref_variables()
        config.test_data['refurl'] = options.refurl()
        config.test_data['cc'] = options.approved_cards()
        config.test_data['pp_type'] = 501
        config.test_data['visa_secure'] = 'configured'
        
        find_pp_package = find_package_pricepoint()
        
        if find_pp_package:
            link = joinlink()
            config.test_data['visa_secure'] = options.is_visa_secure()
            processor_name = {
                26: 'PAYVISIONWE',
                42: 'ROCKETGATEISO',
                57: 'SPCATISO',
                44: 'PAYVISIONPRIVMS',
                65: 'SPKAISO1',
                74: 'SPHBIPSP'
            }
            config.test_data['processor_name'] = processor_name[config.test_data['PrefProcessorID']]
            return True
        else:
            return False
    
    except Exception as ex:
        traceback.print_exc()
        print()
        # pass

def find_package_pricepoint():
    find_pp_package = None
    cnt = 0
    
    try:
        while find_pp_package == None and cnt < 3:
            cnt += 1
            find_pp_package = db_agent.find_pricepoint_package(config.test_data['MerchantID'], config.test_data['pp_type'], config.test_data['userinfo'])
        if find_pp_package == None:
            return False
        pricepointid = find_pp_package['BillConfigID']
        packageid = find_pp_package['PackageID']
        eticket = str(packageid) + ':' + str(pricepointid)
        config.test_data['eticket'] = eticket
        config.test_data['pricepoint'] = str(pricepointid)
        config.test_data = {**config.test_data, **find_pp_package}
        return True
    except Exception as ex:
        traceback.print_exc()
        pass

filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\recurring.csv"
saved_test_cases = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\recurring.yaml"
count_transactions = 0
with open(filename, newline='') as csvfile:
    tc_reader = csv.reader(csvfile, delimiter=',', quotechar='"', escapechar='\\')
    merchantid = ''
    test_case_number = 0
    heading = scenario_heading()
    for scenario in tc_reader:
        try:
            if scenario[0] == 'Merchant'  or scenario[1] == 'Paypal':
                print()  # ("skiping for now \n") # EU_EUR
            
            else:
                if create_test_case(scenario):
                    test_cases_list[f"{config.test_data['name']}"] = print_scenario()
                    transaction_created = create_transaction()
                    if transaction_created:
                        count_transactions += 1
                        pass_fail = verify_transaction(config.test_data['transaction_type'], transaction_created)
                        test_cases_list[f"{config.test_data['name']}"] = [{config.test_data['name']}, config.test_data]
                        config.test_data['action'] = scenario[2]
                        if pass_fail:
                            passed_test_cases[config.test_data['name']] = config.test_data
                        else:
                            failed_test_cases[config.test_data['name']] = config.test_data
                    else:
                        print(colored("Transaction did not get created - retry Manually", 'red', attrs=['bold']))
                        failed_test_cases[config.test_data['name']] = config.test_data
                        raise Exception('Transaction was not created')
        
        except Exception as ex:
            traceback.print_exc()
            print()
            pass
br.close()
try:
    with open(saved_test_cases, 'w') as f:
        data = yaml.dump(test_cases_list, f)
except Exception as ex:
    traceback.print_exc()
    pass
try:
    for item in test_cases_list:
        x = test_cases_list[item][0]
        if len(x) < 30:
            for i in x:
                print(i)

except Exception as ex:
    traceback.print_exc()
    pass
end_time = datetime.now()
print('Full test Duration: {}'.format(end_time - start_time))
print(f"Number of scenarious: {count_transactions}")
