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
import random
import decimal
import requests
from xml.etree.ElementTree import fromstring

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
    dynamiclink_websrevices = 'https://qasvc.segpay.com/OneClickSales.asmx/SalesServiceDynamic?eticketid='
    joinlink = ''
    dynamic_price = ''
    dmc_from = ''
    url_options = config.test_data['ref_variables'] + config.test_data['joinlink_xbill'] + config.test_data['joinlink_param'] + config.test_data['refurl'] + config.template
    octoken = config.test_data['octoken']
    pricingguid = ""
    if config.test_data['pp_type'] == 510:
        dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
        hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
        resp = requests.get(hash_url)
        dynamic_hash = fromstring(resp.text).text
        config.test_data['510'] = dynamic_price
    elif config.test_data['pp_type'] == 511:
        pricingguid_records = db_agent.get_pricingguid_records(config.test_data['MerchantID'], config.test_data['pp_type'])
        if config.test_data['transaction_type'] == 'FreeTrial_Signup' or config.test_data['transaction_type'] == 'FreeTrial_POS':
            for pguid in pricingguid_records:
                if pguid['InitialPrice'] == 0:
                    pricingguid = pguid
                    break
        else:
            for pguid in pricingguid_records:
                if pguid['InitialPrice'] > 0:
                    pricingguid = pguid
                    break
        config.test_data['InitialLen'] = pricingguid['InitialLength']
        config.test_data['RebillLen'] = pricingguid['RecurringLength']
        config.test_data['RebillPrice'] = pricingguid['RecurringPrice']
        config.test_data['InitialPrice'] = pricingguid['InitialPrice']


    try:
        dmc_from = config.test_data['dmc_from']

        if dmc_from == 'p':
            dmc_from = ''
        elif dmc_from == 'u':
            dmc_from = f"&DMCURRENCY={config.test_data['dmc']}"

        lang_from = config.test_data['lang_from']
        if lang_from == 'p':
            lang_from = ''
        elif lang_from == 'u':
            lang_from = f"&paypagelanguage={config.test_data['lang']}"

        if config.test_data['transaction_type'] == 'IC_POS' or config.test_data['transaction_type'] == 'IC_WS':
            dmc_from = ''
            lang_from = ''

        if config.test_data['transaction_type'] == 'Signup' or config.test_data['transaction_type'] == 'FreeTrial_Signup':
            if config.test_data['pp_type'] == 511:
                joinlink = f"{config.url}{config.test_data['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}{url_options}{dmc_from}" + lang_from  # PricingGuid, InitialPrice
            elif config.test_data['pp_type'] == 510:
                joinlink = f"{config.url}{config.test_data['eticket']}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST{url_options}{dmc_from}" + lang_from
            else:
                joinlink = config.url + config.test_data['eticket'] + url_options + dmc_from + lang_from

        elif config.test_data['transaction_type'] == 'OneClick_POS' or config.test_data['transaction_type'] == 'FreeTrial_POS':
            if config.test_data['pp_type'] == 511:
                joinlink = f"{config.url}{config.test_data['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}{dmc_from}" + url_options + lang_from
            elif config.test_data['pp_type'] == 510:
                joinlink = f"{config.url}{config.test_data['eticket']}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}{url_options}{dmc_from}" + lang_from
            else:
                joinlink = f"{config.url}{config.test_data['eticket']}&octoken={octoken}" + url_options + dmc_from + lang_from

        elif config.test_data['transaction_type'] == 'OneClick_WS' or config.test_data['transaction_type'] == 'FreeTrial_WS':
            if config.test_data['pp_type'] == 511:
                joinlink = f"{config.urlws}{config.test_data['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options + dmc_from + lang_from
            elif config.test_data['pp_type'] == 510:
                joinlink = f"{dynamiclink_websrevices}{config.test_data['eticket']}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}{url_options}{dmc_from}" + lang_from
            else:
                joinlink = f"{config.urlws}{config.test_data['eticket']}&octoken={octoken}" + url_options + dmc_from + lang_from




        elif config.test_data['transaction_type'] == 'IC_WS':
            joinlink = f"{config.urlic}[InstantCondersion ICtoken => transguid from the original transaction]"
        elif config.test_data['transaction_type'] == 'IC_POS':
            joinlink = f"{config.urlicws}[InstantCondersion ICtoken => transguid from the original transaction]"

        joinlink = f"{joinlink}&testcase={config.test_data['test_case_number']}"
        #print(joinlink)
        config.test_data['link'] = joinlink
        config.test_data['url_options'] = url_options
        return joinlink  # , url_options, octoken
    except Exception as ex:
        traceback.print_exc()
        print(f"Function joinglink \n {Exception}")
        pass
def asset_verification(test_case):
    type = config.test_data['pp_type']
    dates = {}

    try:
        purchtype = config.test_data['pp_type']
        purchtype_recurring = [501, 505, 506, 511]
        statusDate = 'CurrentDate'
        purchDate = 'CurrentDate'
        if type in purchtype_recurring:
            if config.test_data['action_bep'] == 'Decline':
                purchStatus = 806
                config.test_data['PurchTotal'] = 0
                purchases = 0
                statusDate = 'CurrentDate'

                nextDate = None
                expiredDate = 'CurrentDate'
                cancelDate = 'CurrentDate'
                convDate = 'CurrentDate'
                lastDate = 'CurrentDate'
            else:
                purchStatus = 801
                cancelDate = 'Null'
                convDate = 'Null'
                lastDate = 'Null'
                if purchtype == 505:
                    nextDate = f"CurrentDate + " + str((config.test_data['InitialLen'] + config.test_data['RebillLen']))
                    expiredDate = f"CurrentDate + {config.test_data['InitialLen']}"
                elif purchtype == 506:
                    if config.test_data['ICAdjustTrial'] == 1:
                        nextDate = f"CurrentDate + {test_case['RebillLen']}"
                        expiredDate = f"CurrentDate + {test_case['RebillLen']}"
                    else:
                        nextDate = f"CurrentDate + " + str((test_case['InitialLen'] + test_case['RebillLen']))
                        expiredDate = f"CurrentDate + " + str((test_case['InitialLen'] + test_case['RebillLen']))
                else:
                    nextDate = f"CurrentDate + {config.test_data['InitialLen']}"
                    expiredDate = f"CurrentDate + {config.test_data['InitialLen']}"
        else:
            if config.test_data['action_bep'] == 'Decline':
                purchStatus = 806
                config.test_data['PurchTotal'] = 0
                purchases = 0
                statusDate = 'CurrentDate'

                nextDate = None
                expiredDate = 'CurrentDate'
                cancelDate = 'CurrentDate'
                convDate = 'CurrentDate'
                lastDate = 'CurrentDate'
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

        config.test_data['statusDate'] = statusDate
        config.test_data['purchDate'] = purchDate
        config.test_data['cancelDate'] = cancelDate
        config.test_data['convDate'] = convDate
        config.test_data['lastDate'] = lastDate
        config.test_data['nextDate'] = nextDate
        config.test_data['expiredDate'] = expiredDate
        config.test_data['purchStatus'] = purchStatus
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
        # if config.test_data['transaction_type'] == 'OneClick_POS':
        #     transstatus = 186
        #     transtype = 1011
        #     if pp_type in (502, 503, 510):
        #         transsource = 123
        #     else:
        #         transsource = 121
        if config.test_data['transaction_type'] == 'Signup' :
            transstatus = 184
            transsource = 121
            transtype = 101
        elif config.test_data['transaction_type'] == 'FreeTrial_Signup':
            transstatus = 187
            transsource = 121
            transtype = 101
        elif config.test_data['transaction_type'] == 'FreeTrial_POS':
            transstatus = 187
            transtype = 1011
            if pp_type in (502, 503, 510):
                transsource = 123
            else:
                transsource = 121
        elif config.test_data['transaction_type'] == 'OneClick_WS'  or config.test_data['transaction_type'] == 'OneClick_POS':
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
def pricepoint_type():
    pp = ''
    try:
        if config.test_data['pp_type'] == 501: pp = 'Recurring 501'
        if config.test_data['pp_type'] == 503: pp = 'Digital 503'
        if config.test_data['pp_type'] == 502: pp = 'OneTime 502'
        if config.test_data['pp_type'] == 511: pp = 'Dynamic Recurring 511'
        if config.test_data['pp_type'] == 510: pp = 'Dynamic  510'
        if config.test_data['pp_type'] == 505: pp = 'Delay Capture 505'
        if config.test_data['pp_type'] == 506 and config.test_data['ic_istrial'] == False:
            if config.test_data['transaction_type'] == 'IC_POS' or config.test_data['transaction_type'] == 'IC_WS':
                pp = 'Instant Conversion 507 [Regular]'
            else:
                pp = 'Instant Conversion 506 [Regular]'
        if config.test_data['pp_type'] == 506 and config.test_data['ic_istrial']:
            if config.test_data['transaction_type'] == 'IC_POS' or config.test_data['transaction_type'] == 'IC_WS':
                pp = 'Instant Conversion 507 [ With Adjust Trial period ]'
            else:
                pp = 'Instant Conversion 506 [ With Adjust Trial period ]'
        return pp
    except Exception as ex:
        traceback.print_exc()
        print(f"{Exception}")
        pass
def ifpostbacks():
    try:
        if config.test_data['PostBackID']:
            postbacks = f"PostBackNotifications  should have postbacks for PostBackID: {config.test_data['PostBackID']}"
        else:
            postbacks = f"PostBackNotifications  should not have postbacks for current transaction"
        return postbacks
    except Exception as ex:
        traceback.print_exc()
        pass
def visa_secure():
    if config.test_data['merchant'] == 'EU': visa_secure_msg = "3DS                | Cardinal3dsRequests should have the response from Cardinal"
    if config.test_data['merchant'] == 'US': visa_secure_msg = '3DS                | Multitrans UserData should have responce from Cardinal'
    return visa_secure_msg
def lang_dmc():
    dmc_msg = ''
    lang_msg = ''
    if config.test_data['dmc_from'] == 'p':
        dmc_msg = "DMC From PayPage:"
    elif config.test_data['dmc_from'] == 'u':
        dmc_msg = "DMC From JoinLink:"

    if config.test_data['lang_from'] == 'p':
        lang_msg = "Language From PayPage:"
    elif config.test_data['lang_from'] == 'u':
        lang_msg = "Language From JoinLink:"

    if config.test_data['transaction_type'] == 'IC_POS' or config.test_data['transaction_type'] == 'IC_WS':
        dmc_msg = "DMC From :"
        lang_msg = "Language From :"
    return lang_msg, dmc_msg
def print_scenario():
    action = ''
    bep_msg = ''
    dmc_msg = 'DMC:'
    lang_msg = 'Language:'
    test_case = config.test_data
    authcode = 'AuthCode: OK:0'

    try:
        pp = pricepoint_type()
        postbacks = ifpostbacks()
        visa_secure_msg = visa_secure()
        aprove_msg = 'This Transactions should be Approved'
        email_msg = 'PointOfSaleEmailQueue should  have email | EmailTypeID: 981'
        tmp = lang_dmc()
        lang_msg = tmp[0]
        dmc_msg = tmp[1]
        # d = asset_verification(test_case)
        mt = mt_verification(test_case)

        if config.test_data['payment'] == 'CC':
            if config.test_data['action_bep'] == 'Decline':
                config.test_data['cc'] = '4000000000001042'

            payment = f"Payment Method: Credit Card [ {config.test_data['cc']} ]"
            cardtype = 171
            paymenttype = 131
            processor = config.test_data['processor_name']
        else:
            payment = f"Payment Method: PayPal"
            processor = 'PayPal For Adult | PayPalMS for MainStream'
            cardtype = 1704
            paymenttype = 1301

        if config.test_data['action_bep'] == 'Cancel': bep_msg = '| This Transaction need to be Canceled in Merchant Portal after Completion'
        if config.test_data['action_bep'] == 'Void_Refund_Cancel': bep_msg = '| This Transaction will be voided (before capture) or refunded (after capture) - Select [Refund and Cancel]  in Merchant Portal after Completion'
        if config.test_data['action_bep'] == 'Void_Refund_Expire': bep_msg = '| This Transaction will be voided (before capture) or refunded (after capture) - Select [Refund and Expire]  in Merchant Portal after Completion'
        if config.test_data['action_bep'] == 'No_action': bep_msg = '| No BEP actions'
        if config.test_data['action_bep'] == 'Decline':
            if config.test_data['transaction_type'] == 'OneClick_POS':
                bep_msg = "| No Bep actions  | To decline OneClick use the wrong cvv in live testing:"
            else:
                bep_msg = '| No Bep actions'
            authcode = 'Authorized = 0'
            config.test_data['transaction_type'] = config.test_data['transaction_type'] + '_Decline'
            aprove_msg = 'This Transactions should be Declined'
            email_msg = 'No Email for Declined transaction'
        if config.test_data['cross_merchant']:
            cross_merchant = config.test_data['cross_merchant']
        else:
            cross_merchant = config.test_data['merchant']

        print(
            f"TestCase_____________________________________________________________________________________________________________________{config.test_data['test_case_number']}")
        print(
            f"| {pp} | Merchant: {cross_merchant}| 3DS Configured | Action: {config.test_data['transaction_type']} | CollectUserInfo: {config.test_data['userinfo']}")
        print(
            f"| Processor: {processor}  | DMCStatus: {config.test_data['DMCStatus']} | {dmc_msg} {config.test_data['dmc']} | {lang_msg} {config.test_data['lang']} | PostBackID: {config.test_data['PostBackID']}")
        print(f"| {aprove_msg} | Eticket: {config.test_data['eticket']} | {payment}")
        print(bep_msg)
        print("|________________________________________________________________________________________________________________________________\n")
        print(f"JoinLink : {config.test_data['link']}\n")
        print("Expected after the transaction has been created:")
        print(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        
       
        
        
        if config.test_data['pp_type'] == 505:
            print("Note:              | Delay Capture will have 2 transaction in Multitrans | Please check all PostBacks and Emails")
            print(
                f"Multitranse:    | {authcode} | TxStatus: 2 | TransSource free record: 121 | TransStatus: 187 | TransType: 105 | TransAmount: 0.00 | ProcessorTransID: FREETRIAL | Processor: {processor} | PaymentType: {paymenttype}  | CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
            print(
                f"Multitranse:    | {authcode} | TxStatus: 2 | TransSource Pay record:  122 | TransStatus: 184 | TransType: 105 | TransAmount: Conversion Amount | Processor: {processor} | PaymentType: {paymenttype} | CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
            print(f"Assets:            | PurchStatus: {config.test_data['purchStatus']} | AuthCurrency: {config.test_data['dmc']} |  PurchType: {scenario[1]}")
            print(
                f"Dates :            | Status: {config.test_data['statusDate']} | Purch: {config.test_data['statusDate']}  | Cancel: {config.test_data['cancelDate']} | Conv: {config.test_data['convDate']} | Last: {config.test_data['lastDate']} | Next: {config.test_data['nextDate']} | Expire: {config.test_data['expiredDate']} ")

        elif config.test_data['pp_type'] == 506 and (config.test_data['transaction_type'] == 'IC_POS' or config.test_data['transaction_type'] == 'IC_WS'):
            print("Note:              | Please check all PostBacks and Emails")
            print(f"Multitranse:    | {authcode} | TxStatus: 2 | TransSource: 122 | TransStatus: 186 | TransType: 108 "
                  f"| Processor: {processor} | PaymentType: {paymenttype}"
                  f" | CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
            print(f"Assets:            | PurchStatus: {config.test_data['purchStatus']} | AuthCurrency: {config.test_data['dmc']} |  PurchType: 507")

            print(
                f"Dates :            | Status: {config.test_data['statusDate']} | Purch: {config.test_data['statusDate']}  | Cancel: {config.test_data['cancelDate']} | Conv: CurrentDate | Last: CurrentDate | Next: {config.test_data['nextDate']} | Expire: {config.test_data['expiredDate']} ")

        else:
            print("Note:              | Please check all PostBacks and Emails")
            print(f"Multitranse:    | {authcode} | TxStatus: 2 | TransSource: {mt['transsource']} | TransStatus: {mt['transstatus']} | TransType: {mt['transtype']} "
                  f"| Processor: {processor} | PaymentType: {paymenttype}"
                  f" | CustAddress,CustCity,CustState,CustPhone => Blank or Value from JoinLink")
            print(f"Assets:            | PurchStatus: {config.test_data['purchStatus']} | AuthCurrency: {config.test_data['dmc']} |  PurchType: {scenario[1]}")
            print(
                f"Dates :            | Status: {config.test_data['statusDate']} | Purch: {config.test_data['statusDate']}  | Cancel: {config.test_data['cancelDate']} | Conv: {config.test_data['convDate']} |"
                f" Last: {config.test_data['lastDate']} | Next: {config.test_data['nextDate']} | Expire: {config.test_data['expiredDate']} ")
        print(f"Email:             | {email_msg}  ")
        print(f"PostBacks       | {postbacks} ")

        if config.test_data['transaction_type'] == 'Signup' or config.test_data['transaction_type'] == 'FreeTrial_Signup':
            print(visa_secure_msg)
        print("SegPayLogs:     | Please check SegpayLogs after each transaction to see if there are any related errors.\n\n")

        
        
        print("Actual Result:____________________________________________________________________________________________________________________________________________________________________________________________\n")
        print("PurchaseID =             | UserName:                   | Email:                | Pass/Fail =         | Comments:           |  ScreenShot if there is a problem:                                        ")
        print("|_________________________________________________________________________________________________________________________________________________________________________________________________________\n\n")
        
        if not (config.test_data['action_bep'] == 'Decline' or config.test_data['action_bep'] == 'No_action'):
            print(f"Expected After {config.test_data['action_bep']}:")
            print(
                "------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

            if config.test_data['action_bep'] == 'Void_Refund_Expire':
                purchstatus = 803
                nextdate = 'Null'
                expiredate = 'CurrentDate'
                transamount = 'TransAmount: Negative'
                mt_msg = f"Multitranse: | TransAmount: Negative | TxStatus: 7 | TransSource: 125 | TransStatus: 186 | TransType: 102 | CustAddress,CustCity,CustState,CustPhone => Blank or Value"
                email = 'Refund'
                email_type = 993
                postbacks_bep = "Disable postback type 3 and Cancel postback type 4"
            elif config.test_data['action_bep'] == 'Void_Refund':
                mt_msg = f"Multitranse: | TransAmount: Negative | TxStatus: 7 (Void) or 8 (refund) | TransSource: 125 | TransStatus: 186 | TransType:  107 (Void) or 102 (Refund) | CustAddress,CustCity,CustState,CustPhone => Blank or Value"
                transamount = 'TransAmount: Negative'
                email = 'Refund'
                email_type = 993
                if config.test_data['pp_type'] in (503, 510):
                    purchstatus = config.test_data['purchStatus']
                    canceldate = 'CurrentDate'
                    nextdate = 'CurrentDate'
                    expiredate = 'CurrentDate'
                    postbacks_bep = "No additional postbacks"

            elif config.test_data['action_bep'] == 'Cancel':
                purchstatus = 802
                mt_msg = f"No Additional records in Multitrans"
                canceldate = 'CurrentDate'
                nextdate = 'Null'
                expiredate = config.test_data['expiredDate']
                email = 'Cancelation'
                email_type = 991
                postbacks_bep = "Cancelation postback type 4"
            elif config.test_data['action_bep'] == 'Void_Refund_Cancel':
                mt_msg = f"Multitranse: | TransAmount: Negative | TxStatus: 7 | TransSource: 125 | TransStatus: 186 | TransType: 102 | CustAddress,CustCity,CustState,CustPhone => Blank or Value"
                purchstatus = 802
                transamount = 'TransAmount: Negative'
                canceldate = 'CurrentDate'
                nextdate = config.test_data['nextDate']
                expiredate = config.test_data['expiredDate']
                email = 'Cancelation'
                email_type = 991
                postbacks_bep = "Cancelation postback type 4"

            print(f"Multitranse: | {mt_msg} ")
            print(f"Assets:      | PurchStatus: {purchstatus} | RetryDate: Null |  LastResult: Null | CustAddress,CustCity,CustState,CustPhone => Blank or Value")
            print(
                f"Dates :      | Status: {config.test_data['statusDate']} | Purch: {config.test_data['statusDate']}  | Cancel: CurrentDate | Conv: Null | Last: Null | Next: {nextdate} | Expire: {expiredate} ")
            print(f"Email:       | PointOfSaleEmailQueue should  have {email} email | EmailTypeID: {email_type}  ")
            print(f"PostBacks    | {postbacks} + {postbacks_bep}")

        print(
            "------------------------------------------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")

        # print(colored("Actual Results:", 'cyan', attrs=['bold']))
        # print(
        #         "________________________________________________________________________________________________________________________________________________________________________Results\n")
        print()

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
        tc.append(f"Assets:      | PurchStatus: {config.test_data['purchStatus']} | AuthCurrency: {config.test_data['dmc']} |  Purchases: 1 | PurchType: {scenario[1]}")
        tc.append(
            f"Dates :      | Status: {config.test_data['statusDate']} | Purch: {config.test_data['statusDate']}  | Cancel: {config.test_data['cancelDate']} | Conv: {config.test_data['convDate']} | Last: {config.test_data['lastDate']} | Next: {config.test_data['nextDate']} | Expire: {config.test_data['expiredDate']} ")
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
    aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
    
    #options.get_error_from_log()
    if current_transaction_record['Authorized']:
        config.test_data['authorized'] = True
        
        if config.test_data['transaction_type'] == 'Decline':
            aprove_or_decline = False
        else:
            aprove_or_decline = True
        config.test_data['aprove_or_decline'] = aprove_or_decline
        # aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
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
        config.test_data['aprove_or_decline'] = False
        tmpstr = f"Transaction DECLINED : AuthCode:{current_transaction_record['AuthCode']}"
        print(colored(tmpstr, 'red', attrs=['bold']))

    if transaction_type == 'OneClick_POS' or transaction_type == 'FreeTrial_POS':
        pass_fail = TransActionService.verify_oc(current_transaction_record, 'pos')
    elif transaction_type == 'Signup' or transaction_type == 'Signup_Decline' or transaction_type == 'FreeTrial_Signup':
        pass_fail = TransActionService.verify_signup_transaction(current_transaction_record)
    elif transaction_type == 'OneClick_WS' or transaction_type == 'FreeTrial_WS':
        pass_fail = TransActionService.verify_oc(current_transaction_record, 'ws')
    
    if current_transaction_record:
        if pass_fail:
            print(colored(f"Scenario completed: All Passed", 'green', attrs=['bold', 'underline', 'dark']))
            print(
                "____________________________________________________________________________________________________________________________________________________________________End_Results\n\n")
            return True
        else:
            print(colored(f"Scenario had some issues: Failed | Re-Check Manually |", 'red', attrs=['bold', 'underline', 'dark']))
            #options.get_error_from_log()
            print(
                "____________________________________________________________________________________________________________________________________________________________________End_Results\n\n")
            return False
def create_transaction():
    transaction_type = config.test_data['transaction_type']
    current_transaction_record = {}
    options.get_error_before_action("initial_time")
    try:
        if transaction_type == 'OneClick_POS' or transaction_type == 'FreeTrial_POS':
            current_transaction_record = br.oc_pos()

        elif transaction_type == 'Signup' or transaction_type == 'Signup_Decline'  or transaction_type == 'FreeTrial_Signup':
            current_transaction_record = br.create_signup()
        elif transaction_type == 'OneClick_WS' or transaction_type == 'FreeTrial_WS':
            current_transaction_record = br.oc_ws()
        #options.get_error_before_action("cutoff_time")
        if current_transaction_record:
            print(f"{transaction_type} => Eticket: {config.test_data['eticket']}  | Processor: {current_transaction_record['Processor']} "
                  f"| Lnaguage: {config.test_data['lang']} | Type: {config.test_data['Type']} | DMC: {config.test_data['dmc']}")
            config.test_data['record_to_check'] = current_transaction_record
            config.test_data['PurchaseID'] = current_transaction_record['PurchaseID']
            config.test_data['TransID'] = current_transaction_record['TransID']
            options.get_error_before_action("cutoff_time")
            options.get_error_from_log()
            return current_transaction_record
        else:
            options.get_error_before_action("cutoff_time")
            options.get_error_from_log()

        
        
    except Exception as ex:
        traceback.print_exc()
        pass
def random_lang_cur():
    config.test_data['lang'] = options.random_lang()
    opt_lang = random.choice(['p', 'u'])
    if opt_lang == 'u':
        config.test_data['lang_from'] = 'u'
    if config.test_data['merchant'] == 'EU':
        dmc_currency = options.random_dmc()
        config.test_data['dmc'] = dmc_currency
        opt_currency = random.choice(['p', 'u'])
        if opt_currency == 'u':
            config.test_data['dmc_from'] = 'u'
    else:
        config.test_data['dmc'] = 'USD'
def create_test_case(scenario):
    merchantid = ''
    try:
        config.test_data = {}
        config.test_data['cross_merchant'] = None
        if scenario[4] == '506':
            if scenario[5] == '0':
                config.test_data['ic_istrial'] = True
            elif scenario[5] == '1':
                config.test_data['ic_istrial'] = False
        test_case_number = config.test_case_number
        #config.test_case_number = test_case_number = config.test_case_number + 1
        find_pp_package = None
        cnt = 0
        config.test_data['name'] = f"{test_case_number}:{scenario[0]}:{scenario[1]}:{scenario[2]}:{scenario[3]}"
        config.test_data['test_case_number'] = test_case_number
        config.test_data['pp_type'] = int(scenario[4])
        config.test_data['payment'] = scenario[1]
        config.test_data['transaction_type'] = scenario[2]
        config.test_data['action_bep'] = scenario[3]
        config.test_data['dmc_from'] = 'p'
        config.test_data['lang_from'] = 'p'
        if scenario[0] == 'EU_EUR':
            config.test_data['currency_base'] = 'EUR'
            config.test_data['merchant'] = 'EU'
            config.test_data['octoken'] = options.oc_tokens('EU')
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
            config.test_data['cross_merchant'] = 'CrossMerchant EU to US'
            config.test_data['octoken'] = options.oc_tokens('US')
        elif scenario[0] == 'US_EU':
            config.test_data['merchant'] = 'US'
            config.test_data['currency_base'] = 'USD'
            config.test_data['octoken'] = options.oc_tokens('EU')
            config.test_data['cross_merchant'] = 'CrossMerchant US to EU'
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
        config.test_data['visa_secure'] = 'configured'
        config.test_data['PurchTotal'] = 1
        find_pp_package = find_package_pricepoint()
        asset_verification(config.test_data)
        if 'OneClick' in config.test_data['transaction_type']:
            sql = "Select *  from Assets where purchaseid = {} "
            result = db_agent.execute_select_one_parameter(sql, config.test_data['octoken'])
            if config.test_data['pp_type'] in (501, 505, 506, 511) or result['PurchType'] in (503, 502, 510) or config.test_data['cross_merchant']:  # always new purchaseid
                if config.test_data['transaction_type'] == 'OneClick_WS':
                    config.test_data['dmc'] = result['AuthCurrency']
                    config.test_data['lang'] = result['CustLang']
                    config.test_data['purchStatus'] = result['PurchStatus']
                    config.test_data['purchDate'] = result['PurchDate']
                    config.test_data['cancelDate'] = result['CancelDate']
                    config.test_data['convDate'] = result['ConvDate']
                    config.test_data['lastDate'] = result['LastDate']
                    config.test_data['nextDate'] = result['NextDate']
                    config.test_data['expiredDate'] = result['ExpiredDate']
                    config.test_data['statusDate'] = result['StatusDate']
                else:
                    random_lang_cur()

            else:
                config.test_data['dmc'] = result['AuthCurrency']
                config.test_data['lang'] = result['CustLang']
                config.test_data['purchStatus'] = result['PurchStatus']

                config.test_data['purchDate'] = result['PurchDate']
                config.test_data['cancelDate'] = result['CancelDate']
                config.test_data['convDate'] = result['ConvDate']
                config.test_data['lastDate'] = result['LastDate']
                config.test_data['nextDate'] = result['NextDate']
                config.test_data['expiredDate'] = result['ExpiredDate']
                config.test_data['statusDate'] = result['StatusDate']
        else:
            random_lang_cur()

        if config.test_data['action_bep'] == 'Decline': config.test_data['purchStatus'] = 806

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
def print_failed_scenarios(failed_scenarios):
    for sc in failed_scenarios:
        print(sc)

filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\p.csv"

saved_test_cases = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\p.yaml"
count_transactions = 0
failed_scenarios = ['Failed']
with open(filename, newline='') as csvfile:
    tc_reader = csv.reader(csvfile, delimiter=',', quotechar='"', escapechar='\\')
    merchantid = ''
    #test_case_number = 0
    config.test_case_number = 0
    for scenario in tc_reader:
        try:
            config.test_case_number = config.test_case_number + 1
            #test_case_number
            if scenario[0] == 'Merchant' or (scenario[1] == 'Paypal' and scenario[2] == 'OneClick_WS') or ( 'OneClick' in  scenario[2] and scenario[3]) == 'Decline' or ( scenario[1] == 'Paypal' and scenario[3]) == 'Decline':
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
                            failed_scenarios.append(scenario)
                    else:
                        print(colored("Transaction did not get created - retry Manually", 'red', attrs=['bold']))
                        failed_test_cases[config.test_data['name']] = config.test_data
                        failed_scenarios.append(scenario)
                        print("\n\n")
                        #raise Exception('Transaction was not created')
                
        except Exception as ex:
            traceback.print_exc()
            print()
            pass
br.close()
print("Failed Scenarios")
print_failed_scenarios(failed_scenarios)


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
