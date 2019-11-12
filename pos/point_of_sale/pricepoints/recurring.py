import traceback
from datetime import datetime
import random
import decimal
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.config.TransActionService import TransActionService
import requests
from xml.etree.ElementTree import fromstring
from pos.point_of_sale.utils import options
from termcolor import colored
from pos.point_of_sale.web import web
import yaml
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import psd2
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.verifications import postback_service
from pos.point_of_sale.verifications import emails
import csv

start_time = datetime.now()
packages = [197216, 197215]  # 197215 65 no 3ds  | 3ds 197216 44
db_agent = DBActions()
d_scenarios = {}
test_case = {}
packageid = 0
test_cases_list = {}

# br = web.Signup()


def recurring(merchantbillconfig, pricepointid, packageid):
    try:
        test_case_signup = {}
        test_case_oc_pos = {}
        test_case_oc_ws = {}
        test_case_oc_pos_diff_merchant = {}
        test_case_ic_pos = {}
        test_case_ic_ws = {}
        test_scenario = {}
        merchant = 0
        package = db_agent.package(packageid)
        eticket = str(packageid) + ':' + str(pricepointid)
        url_options = options.ref_variables() + options.refurl() + config.template
        merchantid = merchantbillconfig['MerchantID']
        if merchantid == 27001:
            merchant = 'US'
        elif merchantid == 21621:
            merchant = 'US'
        collectuserinfo = merchantbillconfig['CollectUserInfo']
        pp_type = merchantbillconfig['Type']
        # ----------------------------------------------------------------------------------------------------Scenarios
        if pp_type == 501:
            test_scenario['name'] = "Recurring: Type=501"
        elif pp_type == 506:
            test_scenario['name'] = "InstantConversion: Type=506"
        test_scenario['type'] = merchantbillconfig['Type']
        test_scenario['merchantbillconfig'] = merchantbillconfig
        test_scenario['is_3DS'] = options.is_3DS(merchantid, packageid)
        test_scenario['is_merchant_eu'] = options.is_EU(merchantid)
        test_scenario['package'] = package
        test_scenario['eticket'] = eticket
        test_scenario['paypal'] = True
        # ----------------------------------------------------------------------------------------------------test_case_signup
        test_case_signup['ref_variables'] = options.ref_variables()
        test_case_signup['refurl'] = options.refurl()
        test_case_signup['dmc'] = options.random_dmc()
        test_case_signup['lang'] = options.random_lang()
        test_case_signup['cc'] = options.approved_cards()
        joinlink = config.url + eticket + url_options
        test_case_signup['joinlink'] = joinlink
        # print(joinlink)
        # ----------------------------------------------------------------------------------------------------test_case_oc_pos
        test_case_oc_pos['ref_variables'] = options.ref_variables()
        test_case_oc_pos['refurl'] = options.refurl()
        test_case_oc_pos['dmc'] = options.random_dmc()
        test_case_oc_pos['lang'] = options.random_lang()
        test_case_oc_pos['octoken'] = options.oc_tokens(merchant)
        joinlink = f"{config.url}{eticket}&octoken={test_case_oc_pos['octoken']}{url_options}"
        test_case_oc_pos['joinlink'] = joinlink
        # print(joinlink)
        # ----------------------------------------------------------------------------------------------------test_case_oc_ws
        test_case_oc_ws['ref_variables'] = options.ref_variables()
        test_case_oc_ws['refurl'] = options.refurl()
        test_case_oc_ws['dmc'] = options.random_dmc()
        test_case_oc_ws['lang'] = options.random_lang()
        test_case_oc_ws['octoken'] = options.oc_tokens(merchant)
        joinlink = url = f"{config.urlws}{eticket}&octoken={test_case_oc_ws['octoken']}" + url_options
        test_case_oc_ws['joinlink'] = joinlink
        # print(joinlink)
        # ----------------------------------------------------------------------------------------------------test_case_oc_diff
        test_case_oc_pos_diff_merchant['ref_variables'] = options.ref_variables()
        test_case_oc_pos_diff_merchant['refurl'] = options.refurl()
        test_case_oc_pos_diff_merchant['dmc'] = options.random_dmc()
        test_case_oc_pos_diff_merchant['lang'] = options.random_lang()
        test_case_oc_pos_diff_merchant['octoken'] = options.oc_tokens(merchant)
        joinlink = f"{config.url}{eticket}&octoken={test_case_oc_pos['octoken']}{url_options}"
        test_case_oc_pos_diff_merchant['joinlink'] = joinlink
        # print(joinlink)
        test_scenario['test_case_signup'] = test_case_signup
        test_scenario['test_case_oc_pos'] = test_case_oc_pos
        test_scenario['test_case_oc_ws'] = test_case_oc_ws
        test_scenario['test_case_oc_pos_diff_merchant'] = test_case_oc_pos_diff_merchant
        if pp_type == 506:
            # ----------------------------------------------------------------------------------------------------test_case_ic POS
            test_case_ic_pos['ref_variables'] = options.ref_variables()
            test_case_ic_pos['refurl'] = options.refurl()
            test_case_ic_pos['dmc'] = options.random_dmc()
            test_case_ic_pos['lang'] = options.random_lang()
            test_case_ic_pos['ictoken'] = 'TRANSGUID of original transaction'
            joinlink = f"{config.urlic}{test_case_ic_pos['ictoken']}{url_options}"
            test_scenario['test_case_ic_pos'] = test_case_ic_pos
            test_scenario['test_case_ic_pos'] = test_case_ic_pos
            test_case_ic_pos['joinlink'] = joinlink
        return test_scenario
    except Exception as ex:
        traceback.print_exc()
        pass

def joinlink(tc, type):
    joinlink = ''
    dynamic_price = ''
    url_options = tc['ref_variables'] + tc['joinlink_xbill'] + tc['joinlink_param'] + tc['refurl'] + config.template
    octoken = test_case['octoken'] = options.oc_tokens(tc['merchant'])
    pricingguid = ""  # db_agent.get_pricingguid(tc['MerchantID'], type)[0]
    
    try:
        if tc['transaction_type'] == 'Signup':
            if type == 511:
                joinlink = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}{url_options}"  # PricingGuid, InitialPrice
            else:
                joinlink = config.url + eticket + url_options
        
        elif tc['transaction_type'] == 'OneClick_POS':
            if type == 511:
                joinlink = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                joinlink = f"{config.url}{eticket}&octoken={octoken}" + url_options
        
        elif tc['transaction_type'] == 'OneClick_WS':
            if type == 511:
                joinlink = f"{config.urlws}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                joinlink = f"{config.urlws}{eticket}&octoken={octoken}" + url_options
        
        test_case['link'] = joinlink
        test_case['url_options'] = url_options
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
        purchtype = test_case['Type']
        purchtype_recurring = [501, 505, 506, 511]
        statusDate = 'CurrentDate'
        purchDate = 'CurrentDate'
        if type in purchtype_recurring:
            purchStatus = 801
            cancelDate = 'Null'
            convDate = 'Null'
            lastDate = 'Null'
            if purchtype == 511:
                nextDate = f"CurrentDate + " + str((test_case['InitialLen'] + test_case['RebillLen']))
                expiredDate = f"CurrentDate + " + str(test_case['initiallength511'])
            elif purchtype == 505:
                nextDate = f"CurrentDate + " + str((test_case['InitialLen'] + test_case['RebillLen']))
                expiredDate = f"CurrentDate + {test_case['InitialLen']}"
            else:
                nextDate = f"CurrentDate + {test_case['InitialLen']}"
                expiredDate = f"CurrentDate + {test_case['InitialLen']}"
        else:
            purchStatus = 804
            nextDate = 'Null'
            cancelDate = 'CurrentDate'
            convDate = 'CurrentDate'
            lastDate = 'CurrentDate'
            if purchtype == 502:
                expiredDate = f"CurrentDate + " + str(test_case['InitialLen'])
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
        pp_type = test_case['Type']
        if test_case['transaction_type'] == 'OneClick_POS':
            transstatus = 186
            transtype = 1011
            if pp_type in (502, 503, 510):
                transsource = 123
            else:
                transsource = 121
        if test_case['transaction_type'] == 'Signup':
            transstatus = 184
            transsource = 121
            transtype = 101
        if test_case['transaction_type'] == 'OneClick_WS':
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

def prepare_data(test_case, tc):
    try:
        config.test_data = {}
        config.test_data = {**test_case, **tc}
        
        # config.test_data = test_case  # {**test_case, **config.initial_data}
        # package = db_agent.package(packageid)
        config.test_data['processor'] = tc['PrefProcessorID']
        
        config.test_data['visa_secure'] = options.is_visa_secure()
        processor_name = {
            26: 'PAYVISIONWE',
            42: 'ROCKETGATEISO',
            57: 'SPCATISO',
            44: 'PAYVISIONPRIVMS',
            65: 'SPKAISO1',
            74: 'SPHBIPSP'
        }
        config.test_data['processor_name'] = processor_name[config.test_data['processor']]
        test_case = config.test_data
        return test_case
    except Exception as ex:
        traceback.print_exc()
        print(ex)
        pass

def sign_up():  # Yan
    pass_fail = False
    current_transaction_record = {}
    aprove_or_decline = None
    try:
        current_transaction_record = br.create_transaction(config.test_data['Type'],
                                                           config.test_data['eticket'], '',
                                                           config.test_data['MerchantID'], '',
                                                           config.test_data['processor'])
        
        config.test_data['transaction_to_check'] = current_transaction_record
        # aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
        config.test_data['aprove_or_decline'] = True
        print(colored(f"This Transaction should be Aproved |", 'grey', attrs=['bold']))
        print(colored(f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}", 'yellow'))
        config.test_case['actual'] = [f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}"]
        if current_transaction_record:
            if current_transaction_record['full_record']['Authorized']:
                tmp = current_transaction_record['full_record']
                config.oc_tokens[tmp['PurchaseID']] = [config.test_data['Type'], tmp['MerchantCurrency'], tmp['Language']]
                result = current_transaction_record['full_record']
                tmpstr = f"Transaction Aproved : AuthCode:{result['AuthCode']}"
                print(colored(tmpstr, 'cyan', attrs=['bold']))
            
            else:
                result = current_transaction_record['full_record']
                tmpstr = f"Transaction DECLINED : AuthCode:{result['AuthCode']}"
                print(colored(tmpstr, 'red', attrs=['bold']))
            
            pass_fail = TransActionService.verify_signup_transaction(current_transaction_record)
            if pass_fail:
                pf = "Scenario completed: All Passed"
                config.test_data['result'] = True
                print(colored(f"Scenario completed: All Passed", 'green', attrs=['bold', 'underline', 'dark']))
            else:
                print(colored(f"Scenario had some issues: Failed | Re-Check Manually |", 'red', attrs=['bold', 'underline', 'dark']))
                pf = "Scenario had some issues: Failed | Re-Check Manually |"
                config.test_data['result'] = False
            
            options.append_list(tmpstr)
            options.append_list(pf)
            options.append_list('_____Finished Scenario_______')
            
            config.test_cases[config.test_data['TransID']] = config.test_case
            config.test_case = {}
            
            print(colored(
                    "___________________________________________________________Finished Scenario_______________________________________________________________________________________________________",
                    'grey', 'on_yellow', attrs=['bold', 'dark']))
            print()
            print()
            return current_transaction_record
        else:
            return False
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

def print_scenario(testcase):
    action = ''
    pp = ''
    bep_msg = ''
    postbacks = ''
    visa_secure_msg = ''
    try:
        if testcase['pp_type'] == 501: pp = 'Recurring 501'
        if testcase['pp_type'] == 511: pp = 'Dynamic Recurring 511'
        try:
            if test_case['PostBackID']:
                postbacks = f"PostBackNotifications  should have postbacks for PostBackID: {test_case['PostBackID']}"
            else:
                postbacks = f"PostBackNotifications  should not have postbacks for current transaction"
        except Exception as ex:
            traceback.print_exc()
            pass
        
        if testcase['merchant'] == 'EU' : visa_secure_msg = "3DS          | Cardinal3dsRequests should have the response from Cardinal"
        if testcase['merchant'] == 'US':  visa_secure_msg = '3DS          | Multitrans UserData should have responce from Cardinal'
        d = asset_verification(test_case)
        mt = mt_verification(test_case)
        if testcase['payment'] == 'CC':
            payment = f"Payment Method: Credit Card [ {testcase['cc']} ]"
        else:
            payment = f"Payment Method: PayPal"
        
        if testcase['action_bep'] == 'Cancel':
            bep_msg = '| This Transaction need to be canceled in Merchant Portal after Completion'
        if testcase['action_bep'] == 'Void_Refund_Cancel':
            bep_msg = '| This Transaction will be voided - Select (Refund and Cancel)  in Merchant Portal after Completion'
        if testcase['action_bep'] == 'Void_Refund_Expire':
            bep_msg = '| This Transaction will be voided - Select (Refund and Expire)  in Merchant Portal after Completion'

        print(f"TestCase_____________________________________________________________________________________________________________________{test_case['test_case_number']}")
        print(f"| {pp} | Merchant: {testcase['merchant']}| 3DS Configured | Action: {testcase['transaction_type']} | CollectUserInfo: {testcase['userinfo']}")
        print(
                f"| Processor: {testcase['processor_name']}  | DMCStatus: {testcase['DMCStatus']} | DMC: {testcase['dmc']} | Language: {testcase['lang']} | PostBackID: {testcase['PostBackID']}")
        print(f"| This Transactions should be aproved | Eticket: {test_case['eticket']} | {payment}")
        print(bep_msg)
        print("|________________________________________________________________________________________________________________________________\n")
        print(f"JoinLink : {test_case['link']}\n")
        print("Expected:")
        print(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("Note:        | Please check all PostBacks and Emails")
        print(
                f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} |"
                f" CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
        print(f"Assets:      | PurchStatus: {d['purchStatus']} | AuthCurrency: {test_case['dmc']} |  Purchases: 1 | PurchType: {scenario[1]}")
        print(
                f"Dates :      | Status: {d['statusDate']} | Purch: {d['statusDate']}  | Cancel: {d['cancelDate']} | Conv: {d['convDate']} | Last: {d['lastDate']} | Next: {d['nextDate']} | Expire: {d['expiredDate']} ")
        print(f"Email:       | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        print(f"PostBacks    | {postbacks} ")
        print(visa_secure_msg)
        print(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")
        print("Actual Results:")
        print(
                "________________________________________________________________________________________________________________________________________________________________________Results\n")
        
        # test cases
        tc = []
        tc.append(f"TestCase_____________________________________________________________________________________________________________________{test_case['test_case_number']}")
        tc.append(f"| {pp} | Merchant: {testcase['merchant']}| 3DS Configured | Action: {testcase['transaction_type']} | CollectUserInfo: {testcase['userinfo']}")
        tc.append(
                f"| Processor: {testcase['processor_name']}  | DMCStatus: {testcase['DMCStatus']} | DMC: {testcase['dmc']} | Language: {testcase['lang']} | PostBackID: {testcase['PostBackID']}")
        tc.append(f"| This Transactions should be aproved | Eticket: {test_case['eticket']} | {payment}")
        tc.append(bep_msg)
        tc.append("|________________________________________________________________________________________________________________________________\n")
        tc.append(f"JoinLink : {test_case['link']}\n")
        tc.append("Expected:")
        tc.append(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        tc.append("Note:        | Please check all PostBacks and Emails")
        tc.append(
                f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} |"
                f" CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
        tc.append(f"Assets:      | PurchStatus: {d['purchStatus']} | AuthCurrency: {test_case['dmc']} |  Purchases: 1 | PurchType: {scenario[1]}")
        tc.append(
                f"Dates :      | Status: {d['statusDate']} | Purch: {d['statusDate']}  | Cancel: {d['cancelDate']} | Conv: {d['convDate']} | Last: {d['lastDate']} | Next: {d['nextDate']} | Expire: {d['expiredDate']} ")
        tc.append(f"Email:       | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        tc.append(f"PostBacks    | {postbacks} ")
        tc.append(visa_secure_msg)
        tc.append(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")
        return tc
    
    
    
    
    
    except Exception as ex:
        traceback.print_exc()
        pass

filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\recurring.csv"
saved_test_cases = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\recurring.yaml"
with open(filename, newline='') as csvfile:
    tc_reader = csv.reader(csvfile, delimiter=',', quotechar='"', escapechar='\\')
    merchantid = ''
    test_case_number = 0
    heading = scenario_heading()
    for scenario in tc_reader:
        test_case_number += 1
        try:
            if scenario[0] != 'Merchant':
                test_case['name'] = f"{scenario[0]}:{scenario[1]}:{scenario[2]}:{scenario[3]}"
                test_case['test_case_number'] = test_case_number
                test_case['merchant'] = scenario[0]  # eu vs us
                test_case['payment'] = scenario[1]
                test_case['transaction_type'] = scenario[2]
                test_case['action_bep'] = scenario[3]
                test_case['lang'] = options.random_lang()
                if test_case['merchant'] == 'EU':
                    test_case['dmc'] = options.random_dmc()  # 'USD'  #
                    merchantid = 27001
                else:
                    merchantid = 21621
                    test_case['dmc'] = 'USD'
                test_case['MerchantID'] = merchantid
                test_case['userinfo'] = options.collect_userinfo()
                test_case['joinlink_param'] = options.joinlink_param()
                test_case['joinlink_xbill'] = options.joinlink_xbill()
                test_case['ref_variables'] = options.ref_variables()
                test_case['refurl'] = options.refurl()
                test_case['cc'] = options.approved_cards()
                test_case['pp_type'] = 501
                test_case['visa_secure'] = 'configured'
                find_pp_package = db_agent.find_pricepoint_package(merchantid, test_case['pp_type'], test_case['userinfo'])
                if find_pp_package == None:
                    raise Exception('No record')
                pricepointid = find_pp_package['BillConfigID']
                packageid = find_pp_package['PackageID']
                eticket = str(packageid) + ':' + str(pricepointid)
                test_case['eticket'] = eticket
                test_case['pricepoint'] = str(pricepointid)
                link = joinlink(test_case, test_case['pp_type'])
                
                # test_case['octoken'] = options.oc_tokens(test_case['merchant'])
                test_case = prepare_data(test_case, find_pp_package)
                test_cases_list[f"{test_case['test_case_number']}:{test_case['name']}"] = print_scenario(test_case)
                signup_record = sign_up()
                test_cases_list[f"{test_case['test_case_number']}:{test_case['name']}"] = [test_cases_list[f"{test_case['test_case_number']}:{test_case['name']}"], config.test_data]
                test_case['action'] = scenario[2]
                result = joinlink(test_case['action'], 506, merchantid, eticket, scenario[3], scenario[1])
                test_case['link'] = result[0]
                test_case['url_options'] = result[1]
                test_case['ictoken'] = result[2]
        
        except Exception as ex:
            traceback.print_exc()
            pass

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
# ==================================================================================================> Begining of the script
# for packageid in config.packages:
#     config.test_data['packageid'] = packageid
#     pricepoints = db_agent.get_pricepoints()
#     scenarious = {}
#     for pricepoint in pricepoints:
#         try:
#             merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
#             pp_type = merchantbillconfig['Type']
#             if pp_type == 501:
#                 sscenario = recurring_501(merchantbillconfig, pricepoint, packageid)
#                 generate_scenario(sscenario)
#
#             z = 3
#             # config.test_data = TransActionService.prepare_data1(pricepoint, packageid, 1)
#             # config.test_data['payment'] = 'cc'
#             # test_methods.sign_up_trans_web()
#         except Exception as ex:
#             traceback.print_exc()
#             print(f"Exception {Exception} ")
#             pass
#
#     config.oc_tokens = {}
