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
import csv

test_cases_list = [[501, 'one_click_pos', 'EU', 'from_url', 0, 'not_configured'],
                   [501, 'one_click_pos', 'US', 'from_url', 1, 'not_configured'],
                   [501, 'one_click_pos', 'US', 'from_paypage', 2, 'configured'],
                   [501, 'oneclick_ws', 'EU', 'from_paypage', 1, 'configured'],
                   [501, 'oneclick_ws', 'US', 'from_url', 2, 'not_configured'],
                   [501, 'oneclick_ws', 'US', 'from_paypage', 0, 'not_configured'],
                   [501, 'singup', 'EU', 'from_url', 1, 'configured'],
                   [501, 'singup', 'EU', 'from_paypage', 2, 'not_configured'],
                   [501, 'singup', 'US', 'from_url', 0, 'configured'],
                   [502, 'one_click_pos', 'EU', 'from_url', 2, 'configured'],
                   [502, 'one_click_pos', 'US', 'from_paypage', 0, 'not_configured'],
                   [502, 'one_click_pos', 'US', 'from_paypage', 1, 'not_configured'],
                   [502, 'oneclick_ws', 'EU', 'from_paypage', 1, 'not_configured'],
                   [502, 'oneclick_ws', 'EU', 'from_paypage', 2, 'configured'],
                   [502, 'oneclick_ws', 'US', 'from_url', 0, 'configured'],
                   [502, 'singup', 'EU', 'from_paypage', 0, 'configured'],
                   [502, 'singup', 'US', 'from_url', 2, 'not_configured'],
                   [502, 'singup', 'US', 'from_url', 1, 'configured'],
                   [503, 'one_click_pos', 'EU', 'from_url', 0, 'not_configured'],
                   [503, 'one_click_pos', 'US', 'from_url', 1, 'configured'],
                   [503, 'one_click_pos', 'US', 'from_paypage', 2, 'not_configured'],
                   [503, 'oneclick_ws', 'EU', 'from_paypage', 1, 'not_configured'],
                   [503, 'oneclick_ws', 'EU', 'from_url', 2, 'configured'],
                   [503, 'oneclick_ws', 'US', 'from_paypage', 0, 'configured'],
                   [503, 'singup', 'EU', 'from_paypage', 2, 'configured'],
                   [503, 'singup', 'EU', 'from_paypage', 1, 'not_configured'],
                   [503, 'singup', 'US', 'from_url', 0, 'not_configured'],
                   [505, 'one_click_pos', 'EU', 'from_paypage', 0, 'not_configured'],
                   [505, 'one_click_pos', 'EU', 'from_url', 2, 'configured'],
                   [505, 'one_click_pos', 'US', 'from_paypage', 1, 'not_configured'],
                   [505, 'oneclick_ws', 'EU', 'from_url', 2, 'configured'],
                   [505, 'oneclick_ws', 'EU', 'from_paypage', 1, 'configured'],
                   [505, 'oneclick_ws', 'US', 'from_paypage', 0, 'not_configured'],
                   [505, 'singup', 'EU', 'from_url', 1, 'not_configured'],
                   [505, 'singup', 'US', 'from_url', 0, 'configured'],
                   [505, 'singup', 'US', 'from_paypage', 2, 'not_configured'],
                   [506, 'one_click_pos', 'EU', 'from_paypage', 0, 'configured'],
                   [506, 'one_click_pos', 'EU', 'from_url', 2, 'not_configured'],
                   [506, 'one_click_pos', 'US', 'from_paypage', 1, 'not_configured'],
                   [506, 'oneclick_ws', 'EU', 'from_url', 0, 'configured'],
                   [506, 'oneclick_ws', 'US', 'from_url', 1, 'not_configured'],
                   [506, 'oneclick_ws', 'US', 'from_paypage', 2, 'configured'],
                   [506, 'singup', 'EU', 'from_paypage', 1, 'configured'],
                   [506, 'singup', 'US', 'from_url', 0, 'not_configured'],
                   [506, 'singup', 'US', 'from_url', 2, 'not_configured'],
                   [510, 'one_click_pos', 'EU', 'from_url', 0, 'not_configured'],
                   [510, 'one_click_pos', 'US', 'from_paypage', 2, 'configured'],
                   [510, 'one_click_pos', 'US', 'from_paypage', 1, 'configured'],
                   [510, 'oneclick_ws', 'EU', 'from_paypage', 2, 'not_configured'],
                   [510, 'oneclick_ws', 'EU', 'from_url', 0, 'configured'],
                   [510, 'oneclick_ws', 'US', 'from_url', 1, 'configured'],
                   [510, 'singup', 'EU', 'from_url', 1, 'not_configured'],
                   [510, 'singup', 'US', 'from_url', 0, 'configured'],
                   [510, 'singup', 'US', 'from_url', 2, 'not_configured'],
                   [510, 'singup', 'US', 'from_paypage', 0, 'not_configured'],
                   [511, 'one_click_pos', 'EU', 'from_paypage', 1, 'configured'],
                   [511, 'one_click_pos', 'EU', 'from_url', 0, 'configured'],
                   [511, 'one_click_pos', 'US', 'from_url', 2, 'not_configured'],
                   [511, 'oneclick_ws', 'EU', 'from_url', 0, 'configured'],
                   [511, 'oneclick_ws', 'EU', 'from_paypage', 2, 'not_configured'],
                   [511, 'oneclick_ws', 'US', 'from_url', 1, 'configured'],
                   [511, 'singup', 'EU', 'from_url', 1, 'not_configured'],
                   [511, 'singup', 'US', 'from_paypage', 0, 'not_configured'],
                   [511, 'singup', 'US', 'from_url', 2, 'configured'],
                   [511, 'singup', 'US', 'from_url', 1, 'not_configured']]
packages = [197216, 197215]  # 197215 65 no 3ds  | 3ds 197216 44
db_agent = DBActions()
d_scenarios = {}
test_case = {}
packageid = 0
br = web.Signup()


def joinlink(action, pp_type, merchantdid, eticket, from_url_param, merchant):
    extra_param = '&x-billname=QA+Segpay&x-billemail=qateam%40segpay.com&x-billaddr=123+Segpay+Street&x-billcity=Las+Vegas&x-billstate=ND&x-billzip=33063&x-billcntry=US&merchantpartnerid=rgvalitor&foreignid=validmember1&natssess=djslkafq3rf0i3wmefk34q434'
    joinlink = ''
    dynamic_price = ''
    octoken = ''
    url_options = options.ref_variables() + options.refurl() + config.template

    try:
        if action == 'singup':
            if pp_type == 510:
                dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
                hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
                print(hash_url)
                resp = requests.get(hash_url)
                dynamic_hash = fromstring(resp.text).text
                joinlink = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST{url_options}"
            elif pp_type == 511:
                pricingguid = db_agent.get_pricingguid(merchantdid, pp_type)[0]
                joinlink = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}{url_options}"  # PricingGuid, InitialPrice
            else:
                joinlink = config.url + eticket + url_options
            config.test_data['link'] = joinlink
            if pp_type == 511:
                config.test_data['initialprice511'] = pricingguid['InitialPrice']
                config.test_data['initiallength511'] = pricingguid['InitialLength']
                config.test_data['recurringlength511'] = pricingguid['RecurringLength']
                config.test_data['recurringprice511'] = pricingguid['RecurringPrice']
            elif pp_type == 510:
                config.test_data['initialprice510'] = dynamic_price
        elif action == 'one_click_pos':
            octoken = options.oc_tokens(merchant)

            if pp_type == 510:
                dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
                hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
                resp = requests.get(hash_url)
                dynamic_hash = fromstring(resp.text).text
                joinlink = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}" + url_options
            elif pp_type == 511:
                pricingguid = db_agent.get_pricingguid(merchantid, pp_type)[0]
                joinlink = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                joinlink = f"{config.url}{eticket}&octoken={octoken}" + url_options
        elif action == 'oneclick_ws':
            octoken = options.oc_tokens(merchant)
            if pp_type == 510:
                dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
                hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
                resp = requests.get(hash_url)
                dynamic_hash = fromstring(resp.text).text
                joinlink = f"{config.urlws}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}" + url_options
            elif pp_type == 511:
                pricingguid = db_agent.get_pricingguid(merchantid, pp_type)[0]
                joinlink = f"{config.urlws}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                joinlink = f"{config.urlws}{eticket}&octoken={octoken}" + url_options

        if from_url_param == 'from_url':
            joinlink = joinlink + extra_param
        return joinlink, url_options, octoken
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
        mt = {}
        pp_type = test_case['Type']
        if test_case['action'] == 'one_click_pos':
            action = 'OneClick POS'
            transstatus = 186
            transtype = 1011
            if pp_type in (502, 503, 510):
                transsource = 123
            else:
                transsource = 121
        if test_case['action'] == 'singup':
            action = 'SignUp'
            transstatus = 184
            transsource = 121
            transtype = 101
        if test_case['action'] == 'oneclick_ws':
            action = 'OneClick WebService'
            transstatus = 186
            transtype = 1011
            # transsource = 123 if pp_type in (502, 503, 510) else transsource = 121
            if pp_type in (502, 503, 510):
                transsource = 123
            else:
                transsource = 121

        mt['action'] = action
        mt['transstatus'] = transstatus
        mt['transtype'] = transtype
        mt['transsource'] = transsource

        return mt
    except Exception as ex:
        traceback.print_exc()
        pass


def prepare_data(test_case, packageid):
    try:
        config.test_data = {}
        config.test_data = test_case  # {**test_case, **config.initial_data}
        package = db_agent.package(packageid)
        config.test_data['processor'] = package['PrefProcessorID']
        merchantbillconfig = db_agent.merchantbillconfig(test_case['pricepoint'])
        config.test_data = {**config.test_data, **merchantbillconfig}
        config.test_data = {**config.test_data, **package}
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
        print(f"Function: prepare_data1 \n {Exception} ")
        pass
    return config.test_data


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
        aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
        print(colored(f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}", 'yellow'))
        config.test_case['actual'] = [f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}"]
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
            print(colored(f"Scenario completed: All Passed", 'green', attrs=['bold', 'underline', 'dark']))
        else:
            print(colored(f"Scenario had some issues: Failed | Re-Check Manually |", 'red', attrs=['bold', 'underline', 'dark']))
            pf = "Scenario had some issues: Failed | Re-Check Manually |"

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
        print(f"{Exception}")
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
        param = 'From JoinLink' if scenario[4] == 'from_url' else 'From PayPage'
        userinfo = 'From JoinLink' if scenario[4] == 'from_url' else 'From PayPage'
        # if scenario[1] == 'one_click_pos':
        #     action = 'OneClick POS'
        #     transstatus = 186
        #     transtype = 1011
        #     transsource = 121
        # if scenario[1] == 'singup':
        #     action = 'SignUp'
        #     transstatus = 184
        #     transsource = 121
        #     transtype = 101
        # if scenario[1] == 'oneclick_ws':
        #     action = 'OneClick WebService'
        #     transstatus = 186
        #     transtype = 1011
        #     transsource = 123
        if test_case['PostBackID']:
            postbacks = f"PostBackNotifications  should have postbacks for PostBackID: {test_case['PostBackID']}"
        else:
            postbacks = f"PostBackNotifications  should not have postbacks for current transaction"
        if visa_secure == "configured" and scenario[2] == 'singup':
            v_secure = f"3DS:         | Cardinal3dsRequests should have the response from Cardinal"
        else:
            v_secure = f"3DS:         | No 3DS"

        test_case['scenario'] = scenario[2]
        d = asset_verification(test_case)
        mt = mt_verification(test_case)

        print(f"TestCase_____________________________________________________________________________________________________________________{test_case['idx']}")
        print(f"| {pp} | Merchant: {testcase['merchant']}| {visa_secure}  | Action: {mt['action']} | CollectUserInfo: {scenario[5]}")
        print(
            f"| Processor: {test_case['processor_name']}  | Parameters: {param} | DMC: {test_case['dmc']} | Language: {test_case['lang']} | PostBackID: {test_case['PostBackID']}")
        print(f"| This Transactions should be aproved | Eticket: {test_case['eticket']} | ")
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
        print(v_secure)
        print(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")
        print("Actual Results:")
        print(
            "________________________________________________________________________________________________________________________________________________________________________Results\n")

    except Exception as ex:
        traceback.print_exc()
        pass


# for idx,scenario in enumerate(test_cases_list):
filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\signup.csv"
with open(filename, newline='') as csvfile:
    tc_reader = csv.reader(csvfile, delimiter=',',quotechar='"', escapechar='\\')
    merchantid = ''
    for scenario in tc_reader:
        if scenario[3] != 'Merchant':
            scenario[0] = int(scenario[0])
            scenario[1] = int(scenario[1])
            scenario[5] = int(scenario[5])
            if scenario[3] == 'EU':
                test_case['dmc'] = options.random_dmc()
            else:
                test_case['dmc'] = 'USD'
            test_case['idx'] = scenario[0]
            test_case['lang'] = options.random_lang()
            test_case['cc'] = options.approved_cards()
            test_case['pp_type'] = scenario[1]
            test_case['action'] = scenario[2]
            test_case['merchant'] = scenario[3]
            test_case['from'] = scenario[4]
            test_case['userinfo'] = scenario[5]
            test_case['visa_secure'] = scenario[6]
            scenario_name = str(scenario[1]) + '_' + scenario[2] + '_' + scenario[3] + '_' + scenario[4] + '_' + str(scenario[5]) + '_' + scenario[6]
            if scenario[3] == 'EU' and scenario[6] == 'configured':
                packageid = 197216
                merchantid = 27001
            elif scenario[3] == 'EU' and scenario[6] == 'not_configured':
                packageid = 197215
                merchantid = 27001
            elif scenario[3] == 'US' and scenario[6] == 'configured':
                packageid = 197218
                merchantid = 21621
            elif scenario[3] == 'US' and scenario[6] == 'not_configured':
                packageid = 197219
                merchantid = 21621
            pricepointid = db_agent.find_pricepoint(scenario[1], packageid, scenario[5])
            eticket = str(packageid) + ':' + str(pricepointid)

            #joinlink(action, pp_type, merchantdid, eticket, from_url_param, merchant):
            result = joinlink(scenario[2], scenario[1], merchantid, eticket, scenario[4], scenario[3])
            test_case['link'] = url = result[0]
            test_case['url_options'] = result[1]
            test_case['eticket'] = eticket
            test_case['pricepoint'] = str(pricepointid)
            test_case['payment'] = 'cc'
            test_case['octoken'] = result[2]

            if test_case['action'] == 'singup':
                test_case = prepare_data(test_case, packageid)
                print_scenario(scenario, test_case)
                results = sign_up()
            elif test_case['action'] == 'one_click_pos':
                test_case = prepare_data(test_case, packageid)
                print_scenario(scenario, test_case)
                one_click_record = br.oc_pos()
                if one_click_record:
                    rs = TransActionService.verify_oc(one_click_record, 'pos')
            elif test_case['action'] == 'oneclick_ws':
                test_case = prepare_data(test_case, packageid)
                test_case['dmc'] = 'USD'
                print_scenario(scenario, test_case)
                one_click_record = br.oc_ws()
                if one_click_record:
                    s = TransActionService.verify_oc(one_click_record, 'ws')
            d_scenarios[scenario_name] = test_case
            z = 3
