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
from pos.point_of_sale.web import web_module
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
br = web_module.Signup()


def joinlink(action, pp_type, merchantdid, eticket, from_url_param, merchant):
    extra_param = '&x-billname=QA+Segpay&x-billemail=qateam%40segpay.com&x-billaddr=123+Segpay+Street&x-billcity=Las+Vegas&x-billstate=ND&x-billzip=33063&x-billcntry=US&merchantpartnerid=rgvalitor&foreignid=validmember1&natssess=djslkafq3rf0i3wmefk34q434'
    joinlink = ''
    dynamic_price = ''
    ictoken = ''
    url_options = options.ref_variables() + options.refurl() + config.template

    try:
        if action == 'signup':
            joinlink = config.url + eticket + url_options
            config.test_data['link'] = joinlink
        elif action == 'ic_pos':
            ictoken = config.test_data['transguid']
            joinlink = f"{config.urlic}{ictoken}" + url_options

        elif action == 'ic_ws':
            ictoken = config.test_data['transguid']
            joinlink = f"{config.urlicws}{ictoken}" + url_options

        if from_url_param == 'from_url':
            joinlink = joinlink + extra_param
        return joinlink, url_options, ictoken
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
            elif purchtype == 506 and test_case['action'] == 'ic_pos' or purchtype == 506 and test_case['action'] == 'ic_ws':
                test_case['pp_type'] = 507
                convDate = 'CurrentDate'
                lastDate = 'CurrentDate'
                if config.test_data['ICAdjustTrial'] == 1:
                    nextDate = f"CurrentDate + {test_case['RebillLen']}"
                    expiredDate = f"CurrentDate + {test_case['RebillLen']}"

                else:
                    nextDate = f"CurrentDate + " + str((test_case['InitialLen'] + test_case['RebillLen']))
                    expiredDate = f"CurrentDate + " + str((test_case['InitialLen'] + test_case['RebillLen']))

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
        mt = {}
        pp_type = test_case['Type']
        if test_case['action'] == 'ic_ws':
            action = 'IC WS'
            transstatus = 186
            transtype = 108
            transsource = 122
        if test_case['action'] == 'signup':
            action = 'SignUP'
            transstatus = 184
            transsource = 121
            transtype = 101
        if test_case['action'] == 'ic_pos':
            action = 'IC POS'
            transstatus = 186
            transtype = 108
            transsource = 122

        mt['action'] = action
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
        # merchantbillconfig = db_agent.merchantbillconfig(test_case['pricepoint'])
        # config.test_data = {**config.test_data, **merchantbillconfig}
        # config.test_data = {**config.test_data, **package}
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



def conversion(action, signup_record):  # Yan

    pass_fail = False
    multitrans_base_record = {}
    current_transaction_record = {}
    aprove_or_decline = None
    try:
        if action == 'pos':
            tmp = br.instant_conversion('pos', signup_record)
            if tmp:
                current_transaction_record = tmp[1]
                multitrans_base_record = tmp[0]
            else:
                return False

        else:
            tmp = br.instant_conversion('ws', signup_record)
            if tmp:
                current_transaction_record = tmp[1]
                multitrans_base_record = tmp[0]
            else:
                return False
        del multitrans_base_record['TransID']
        del multitrans_base_record['RelatedTransID']
        del multitrans_base_record['TRANSGUID']
        del multitrans_base_record['ProcessorTransID']
        del multitrans_base_record['USERDATA']
        del multitrans_base_record['REF10']
        del multitrans_base_record['REF9']
        del multitrans_base_record['REF1']
        del multitrans_base_record['REF2']
        del multitrans_base_record['REF3']
        del multitrans_base_record['REF4']
        del multitrans_base_record['REF5']
        del multitrans_base_record['REF6']
        del multitrans_base_record['REF7']
        del multitrans_base_record['REF8']
        del multitrans_base_record['Markup']
        config.test_data['transaction_to_check'] = current_transaction_record
        print(colored(f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}", 'yellow'))
        config.test_case['actual'] = [f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}"]
        if current_transaction_record['Authorized']:
            tmpstr = f"Transaction Aproved : AuthCode:{current_transaction_record['AuthCode']}"
            print(colored(tmpstr, 'cyan', attrs=['bold']))
            differences_multitrans = mt.multitrans_compare(multitrans_base_record, current_transaction_record)
            asset_base_record = asset.asset_instant_conversion()
            differences_asset = asset.asset_compare(asset_base_record)
            if current_transaction_record['Authorized'] == 1:
                check_email = emails.check_email_que(config.test_data['Type'], current_transaction_record, 'signup')
                config.test_data['aproved_transids'] = current_transaction_record['TransID']
            differences_postback = postback_service.verify_postback_url("SignUp", config.test_data['PackageID'], current_transaction_record['TransID'])
            config.transids.append(current_transaction_record['TransID'])
            config.transaction_records.append(current_transaction_record)
            if not differences_multitrans and not differences_asset and not differences_postback:
                pass_fail = True
        else:
            tmpstr = f"Transaction DECLINED : AuthCode:{current_transaction_record['AuthCode']}"
            print(colored(tmpstr, 'red', attrs=['bold']))


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
    except Exception as ex:
        traceback.print_exc()
        pass
    return current_transaction_record


def print_scenario(scenario, testcase):
    action = ''
    pp = ''
    try:
        if testcase['pp_type'] == 501: pp = 'Recurring 501'
        if testcase['pp_type'] == 502: pp = 'OneTime 502'
        if testcase['pp_type'] == 503: pp = 'Digital 503'
        if testcase['pp_type'] == 505: pp = 'DelayCapture 505'
        if testcase['pp_type'] == 506: pp = 'Instant Conversion 506'
        if testcase['pp_type'] == 510: pp = 'Dynamic 510'
        if testcase['pp_type'] == 511: pp = 'Dynamic Recurring 511'

        visa_secure = '3DS Configured' if testcase['visa_secure'] == 'configured' else '3DS Not Configured'
        param = 'From JoinLink' if scenario[3] == 'from_url' else 'From PayPage'
        userinfo = 'From JoinLink' if scenario[3] == 'from_url' else 'From PayPage'
        if test_case['PostBackID']:
            postbacks = f"PostBackNotifications  should have postbacks for PostBackID: {test_case['PostBackID']}"
        else:
            postbacks = f"PostBackNotifications  should not have postbacks for current transaction"
        if visa_secure == "configured" and scenario[2] == 'signup':
            v_secure = f"3DS:         | Cardinal3dsRequests should have the response from Cardinal"
        else:
            v_secure = f"3DS:         | No 3DS"

        test_case['scenario'] = scenario[2]
        d = asset_verification(test_case)
        mt = mt_verification(test_case)
        purchases = 1
        if testcase['pp_type'] == 507:
            pp = 'Instant Conversion Complete 507'
            purchases = 2

        tc = []

        print(f"TestCase_____________________________________________________________________________________________________________________{test_case['idx']}")
        print(f"| {pp} | Merchant: {testcase['merchant']}| {visa_secure}  | Action: {mt['action']} | CollectUserInfo: {test_case['userinfo']}")
        print(
            f"| Processor: {test_case['processor_name']}  | Parameters: {param} | DMC: {test_case['dmc']} | Language: {test_case['lang']} | PostBackID: {test_case['PostBackID']}")
        print(f"| This Transactions should be aproved | Eticket: {test_case['eticket']} | CC: {test_case['cc']}")
        print("|________________________________________________________________________________________________________________________________\n")
        print(f"JoinLink : {test_case['link']}\n")
        print("Expected:")
        print(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("Note:        | Please check all PostBacks and Emails")
        print(
            f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} |"
            f" CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
        print(f"Assets:      | PurchStatus: {d['purchStatus']} | AuthCurrency: {test_case['dmc']} |  Purchases: {purchases} | PurchType: {test_case['pp_type']}")
        print(
            f"Dates :      | Status: {d['statusDate']} | Purch: {d['statusDate']}  | Cancel: {d['cancelDate']} | Conv: {d['convDate']} | Last: {d['lastDate']} | Next: {d['nextDate']} | Expire: {d['expiredDate']} ")
        print(f"Email:       | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        print(f"PostBacks    | {postbacks} ")
        print(v_secure)
        print(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")
        print("Actual Results:")
        print(
            "________________________________________________________________________________________________________________________________________________________________________Results\n")

        # test cases
        tc.append(f"TestCase_____________________________________________________________________________________________________________________{test_case['idx']}")
        tc.append(f"| {pp} | Merchant: {testcase['merchant']}| {visa_secure}  | Action: {mt['action']} | CollectUserInfo: {test_case['userinfo']}")
        tc.append(
            f"| Processor: {test_case['processor_name']}  | Parameters: {param} | DMC: {test_case['dmc']} | Language: {test_case['lang']} | PostBackID: {test_case['PostBackID']}")
        tc.append(f"| This Transactions should be aproved | Eticket: {test_case['eticket']} | CC: {test_case['cc']}")
        tc.append("|________________________________________________________________________________________________________________________________\n")
        tc.append(f"JoinLink : {test_case['link']}\n")
        tc.append("Expected:")
        tc.append(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        tc.append("Note:        | Please check all PostBacks and Emails")
        tc.append(
            f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} |"
            f" CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
        tc.append(f"Assets:      | PurchStatus: {d['purchStatus']} | AuthCurrency: {test_case['dmc']} |  Purchases: {purchases} | PurchType: {test_case['pp_type']}")
        tc.append(
            f"Dates :      | Status: {d['statusDate']} | Purch: {d['statusDate']}  | Cancel: {d['cancelDate']} | Conv: {d['convDate']} | Last: {d['lastDate']} | Next: {d['nextDate']} | Expire: {d['expiredDate']} ")
        tc.append(f"Email:       | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        tc.append(f"PostBacks    | {postbacks} ")
        tc.append(v_secure)
        tc.append("Note: REF Variables should be Encrypted  in DB and UnEncrypted in postbacks | PaymentAcount and Email should be encrypted in DB ")
        tc.append(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")


        return tc

    except Exception as ex:
        traceback.print_exc()
        pass


# for idx,scenario in enumerate(test_cases_list):
filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\ic.csv"
saved_test_cases = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\ic.yaml"
with open(filename, newline='') as csvfile:
    tc_reader = csv.reader(csvfile, delimiter=',', quotechar='"', escapechar='\\')
    merchantid = ''
    for scenario in tc_reader:
        if scenario[1] != 'Merchant':
            scenario[0] = int(scenario[0])
            scenario[4] = int(scenario[4])
            # scenario[5] = int(scenario[5])
            if scenario[1] == 'EU':
                test_case['dmc'] = options.random_dmc()  # 'USD'  #
                merchantid = 27001
            else:
                merchantid = 21621
                test_case['dmc'] = 'USD'
            test_case['idx'] = scenario[0]
            test_case['lang'] = options.random_lang()
            test_case['cc'] = options.approved_cards()
            test_case['pp_type'] = 506  # scenario[1]
            test_case['action'] = scenario[2]
            test_case['merchant'] = scenario[1]
            test_case['from'] = scenario[3]
            test_case['userinfo'] = scenario[4]
            test_case['visa_secure'] = scenario[5]
            scenario_name = f"{scenario[1]}:{scenario[2]}:{scenario[3]}:{scenario[4]}:{scenario[5]}:"
            
            find_pp_package = db_agent.find_pricepoint_package(merchantid, test_case['pp_type'], test_case['userinfo'], test_case['visa_secure'])
            pricepointid = find_pp_package['BillConfigID']
            packageid = find_pp_package['PackageID']
            # if scenario[1] == 'EU' and scenario[5] == 'configured':
            #     packageid = 197216
            #     merchantid = 27001
            # elif scenario[1] == 'EU' and scenario[5] == 'not_configured':
            #     packageid = 197215
            #     merchantid = 27001
            # elif scenario[1] == 'US' and scenario[5] == 'configured':
            #     packageid = 197218
            #     merchantid = 21621
            # elif scenario[1] == 'US' and scenario[5] == 'not_configured':
            #     packageid = 197219
            #     merchantid = 21621
            #pricepointid = db_agent.find_pricepoint(506, packageid, scenario[4])
            eticket = str(packageid) + ':' + str(pricepointid)
            test_case['eticket'] = eticket
            test_case['pricepoint'] = str(pricepointid)
            test_case['payment'] = 'cc'

            test_case['action'] = 'signup'
            result = joinlink(test_case['action'], 506, merchantid, eticket, scenario[3], scenario[1])
            test_case['link'] = url = result[0]
            test_case['url_options'] = result[1]
            test_case['ictoken'] = result[2]
            test_case = prepare_data(test_case, find_pp_package)
            test_cases_list[f"{scenario[0]}:{scenario_name}"] = print_scenario(scenario, test_case)
            signup_record = sign_up()
            test_cases_list[f"{scenario[0]}:{scenario_name}"] = [test_cases_list[f"{scenario[0]}:{scenario_name}"],config.test_data]
            test_case['action'] = scenario[2]
            result = joinlink(test_case['action'], 506, merchantid, eticket, scenario[3], scenario[1])
            test_case['link'] = result[0]
            test_case['url_options'] = result[1]
            test_case['ictoken'] = result[2]
            try:
                if signup_record['full_record']['Authorized']:
                    if test_case['action'] == 'ic_pos':
                        test_case = prepare_data(test_case, find_pp_package)
                        test_case['transguid'] = signup_record['transguid']
                        test_case['dmc'] = signup_record['full_record']['MerchantCurrency']
                        test_case['lang'] = signup_record['full_record']['Language']
                        test_cases_list[f"{scenario[0]}:{scenario_name}"] = print_scenario(scenario, test_case)
                        if conversion('pos', signup_record):
                            test_cases_list[f"{scenario[0]}:{scenario_name}"] = [test_cases_list[f"{scenario[0]}:{scenario_name}"], config.test_data]
                        else:
                            print("Instant Conversion Failed : Purchase not eligible for Instant Conversion.(ERR303)")
                    elif test_case['action'] == 'ic_ws':
                        test_case = prepare_data(test_case, find_pp_package)
                        test_case['transguid'] = signup_record['transguid']
                        test_case['dmc'] = signup_record['full_record']['MerchantCurrency']
                        test_case['lang'] = signup_record['full_record']['Language']
                        test_cases_list[f"{scenario[0]}:{scenario_name}"] = print_scenario(scenario, test_case)
                        if conversion('ws', signup_record):
                            test_cases_list[f"{scenario[0]}:{scenario_name}"] = [test_cases_list[f"{scenario[0]}:{scenario_name}"], config.test_data]
                        else:
                            print("******  Instant Conversion Failed : Purchase not eligible for Instant Conversion.(ERR303)*****\n")
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
