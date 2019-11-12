import traceback
from datetime import datetime
import time
from functools import partial
from pos.point_of_sale.bep import bep
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.runners import test_methods
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web
from pos.point_of_sale.utils import options
import yaml
import random

db_agent = DBActions()
start_time = datetime.now()


def onetime_502(merchantbillconfig, pricepointid, packageid):
    try:
        test_case_signup = {}
        test_case_oc_pos = {}
        test_case_oc_ws = {}
        test_case_oc_pos_diff_merchant = {}
        test_scenario = {}
        package = db_agent.package(packageid)
        eticket = str(packageid) + ':' + str(pricepointid)
        url_options = options.ref_variables() + options.refurl() + config.template
        merchantid = merchantbillconfig['MerchantID']
        if merchantid == 27001:
            merchant = 'US'
        elif merchantid == 21621:
            merchant = 'US'
        collectuserinfo = merchantbillconfig['CollectUserInfo']
        # ----------------------------------------------------------------------------------------------------Scenarios
        test_scenario['name'] = "OneTime: Type=502"
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
        #print(joinlink)
        # ----------------------------------------------------------------------------------------------------test_case_oc_pos
        test_case_oc_pos['ref_variables'] = options.ref_variables()
        test_case_oc_pos['refurl'] = options.refurl()
        test_case_oc_pos['dmc'] = options.random_dmc()
        test_case_oc_pos['lang'] = options.random_lang()
        test_case_oc_pos['octoken'] = options.oc_tokens(merchant)
        joinlink = f"{config.url}{eticket}&octoken={test_case_oc_pos['octoken']}{url_options}"
        test_case_oc_pos['joinlink'] = joinlink
        #print(joinlink)
        # ----------------------------------------------------------------------------------------------------test_case_oc_ws
        test_case_oc_ws['ref_variables'] = options.ref_variables()
        test_case_oc_ws['refurl'] = options.refurl()
        test_case_oc_ws['dmc'] = options.random_dmc()
        test_case_oc_ws['lang'] = options.random_lang()
        test_case_oc_ws['octoken'] = options.oc_tokens(merchant)
        joinlink = url = f"{config.urlws}{eticket}&octoken={test_case_oc_ws['octoken']}" + url_options
        test_case_oc_ws['joinlink'] = joinlink
        #print(joinlink)
        # ----------------------------------------------------------------------------------------------------test_case_oc_diff
        test_case_oc_pos_diff_merchant['ref_variables'] = options.ref_variables()
        test_case_oc_pos_diff_merchant['refurl'] = options.refurl()
        test_case_oc_pos_diff_merchant['dmc'] = options.random_dmc()
        test_case_oc_pos_diff_merchant['lang'] = options.random_lang()
        test_case_oc_pos_diff_merchant['octoken'] = options.oc_tokens(merchant)
        joinlink = f"{config.url}{eticket}&octoken={test_case_oc_pos['octoken']}{url_options}"
        test_case_oc_pos_diff_merchant['joinlink'] = joinlink
        #print(joinlink)

        test_scenario['test_case_signup'] = test_case_signup
        test_scenario['test_case_oc_pos'] = test_case_oc_pos
        test_scenario['test_case_oc_ws'] = test_case_oc_ws
        test_scenario['test_case_oc_pos_diff_merchant'] = test_case_oc_pos_diff_merchant

        return test_scenario
    except Exception as ex:
        traceback.print_exc()
        pass


def generate_scenario(scenario):
    s = 3
    payment_type = ''
    visa_secure = ''
    merchant = ''
    try:
        if scenario['paypal']:
            payment_type = 'PayPal and Credit Card'
        else:
            payment_type = 'Credit Card'
        if scenario['is_3DS']:
            visa_secure = "3DS Configured"
        else:
            visa_secure = "3DS Not Configured"
        if scenario['is_merchant_eu'] == 1:
            merchant = "EU"
        else:
            merchant = "US"
        if scenario['package']['PostBackID']:
            postbacks = f"PostBackNotifications  should have postbacks for PostBackID: {scenario['package']['PostBackID']}"
        else:
            postbacks = f"PostBackNotifications  should not have postbacks for current transaction"

        rebill_date = f"NextDate: CurrentDate"

        print("==================================================== *** Scenario *** ==========================================================================")
        print(f"| ------------------------- {scenario['name']} | Merchant:{merchant}| {visa_secure}  | PaymentType: {payment_type} | --------------------|")
        print(f"| -------------------------  TestCases: | SignUp | OneClick POS | OneClick WS | OneClick POS to Different Merchant ----------------------------|")
        print(f"| -----------------------------------------------  This Transactions should be aproved --------------------------------------------------------|")
        print("================================================================================================================================================\n")
        paymentid = ''
        payment = ''
        processor = ''
        d = scenario['test_case_signup']
        if scenario['paypal']:
            payments = ['CC', 'PayPal']
        else:
            payments = ['CC']

        for i in payments: # Singup
            if i == 'CC':
                payment = 'CC'
                paymentid = f"CC: {d['cc']}"
                processor = f"PPID: {scenario['package']['PrefProcessorID']}"
                pay_type = f"PaymentType: 131"
                transtype = '101'
            elif i == 'PayPal':
                payment = 'PayPal'
                paymentid = f"PayPal"
                processor = 'Processor: PayPal'
                pay_type = f"PaymentType: 1301"
                transtype = '105'
            print(f"Test Case_______________________________________________SingUp__________________________________________________________{payment}\n")
            print(
                f"Eticket: {scenario['eticket']} | DMC: {d['dmc']} | Language: {d['lang']} | {paymentid} | {processor}"
                f"| Template: {scenario['package']['PayPageTemplate']} | DMCStatus: {scenario['package']['DMCStatus']} ")
            print(f"Link: {d['joinlink']} \n")
            print('|Excptected Results |')
            print("--------------------------------------------------------------------------------------------------------------------------")
            print(f"Multitrans: | AuthCode:OK:0 | TransSource: 121 | TransStatus: 184 | TransType: {transtype} | {pay_type} | MerchantCurrency: {d['dmc']} | Language: {d['lang']} |"
                  f"CustAddress,CustCity,CustState,CustPhone => Blank ")
            print(f"Assets:     | PurchStatus: 801 | PurchType: 502 | AuthCurrency: {d['dmc']} |  Purchases: 1 | CustAddress,CustCity,CustState,CustPhone: Blank | {rebill_date}")
            print(f"Email:      | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
            print(f"PostBacks   | {postbacks} ")
            if visa_secure == "3DS Configured":
                print(f"3DS:        | Cardinal3dsRequests should have the response from Cardinal")
            print("------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")#Signup
        d = scenario['test_case_oc_pos']
        for i in payments:
            if i == 'CC':
                payment = 'CC'
                paymentid = f"Credit Card"
                processor = f"PPID: {scenario['package']['PrefProcessorID']}"
                pay_type = f"PaymentType: 131"
                transtype = '101'
            elif i == 'PayPal':
                payment = 'PayPal'
                paymentid = f"PayPal"
                processor = 'Processor: PayPal'
                pay_type = f"PaymentType: 1301"
                transtype = '105'
            print(f"Test Case_______________________________________________OneClick POS__________________________________________________________{payment}\n")
            print(
                f"Eticket: {scenario['eticket']} | DMC: {d['dmc']} | Language: {d['lang']} | {paymentid} | {processor} "
                f"| Template: {scenario['package']['PayPageTemplate']} | DMCStatus: {scenario['package']['DMCStatus']} | OcToken:  ")
            print(f"Link: {d['joinlink']} \n")
            print('|Excptected Results |')
            print("--------------------------------------------------------------------------------------------------------------------------")
            print(f"Multitrans: | AuthCode:OK:0 | TransSource: 123 | TransStatus: 186 | TransType: 1011 | {pay_type} | MerchantCurrency: {d['dmc']} | Language: {d['lang']} |"
                  f"CustAddress,CustCity,CustState,CustPhone => Blank ")
            print(f"Assets:     | PurchStatus: 801 | PurchType: 502 | AuthCurrency: {d['dmc']} |  Purchases: 1 | CustAddress,CustCity,CustState,CustPhone: Blank | {rebill_date}")
            print(f"Email:      | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
            print(f"PostBacks   | {postbacks} ")
            if visa_secure == "3DS Configured":
                print(f"3DS:        | Cardinal3dsRequests should have the response from Cardinal")
            print(f"PurchaseID: | New PurchaseID should be created | OcToken: {d['octoken']}")
            print("------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")

        d = scenario['test_case_oc_ws']
        print(f"Test Case_______________________________________________OneClick WS___________________________________________________________'CC\n")
        print(
            f"Eticket: {scenario['eticket']} | DMC: {d['dmc']} | Language: {d['lang']} | Credit Card | PPID: {scenario['package']['PrefProcessorID']} "
            f"| Template: {scenario['package']['PayPageTemplate']} | DMCStatus: {scenario['package']['DMCStatus']} ")
        print(f"Link: {d['joinlink']} \n")
        print('|Excptected Results |')
        print("--------------------------------------------------------------------------------------------------------------------------")
        print(f"Multitrans: | AuthCode:OK:0 | TransSource: 123 | TransStatus: 186 | TransType: 1011 | PaymentType: 131 | MerchantCurrency: {d['dmc']} | Language: {d['lang']} |"
              f"CustAddress,CustCity,CustState,CustPhone => Blank ")
        print(f"Assets:     | PurchStatus: 801 | PurchType: 502 | AuthCurrency: {d['dmc']} |  Purchases: 1 | CustAddress,CustCity,CustState,CustPhone: Blank | {rebill_date}")
        print(f"Email:      | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        print(f"PostBacks   | {postbacks} ")
        if visa_secure == "3DS Configured":
            print(f"3DS:        | Cardinal3dsRequests should have the response from Cardinal")
        print(f"PurchaseID: | New PurchaseID should be created | OcToken: {d['octoken']}")
        print("------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")

        d = scenario['test_case_oc_ws']
        print(f"Test Case_______________________________________________OneClick POS Different Merchant___________________________________________CC\n")
        print(
            f"Eticket: {scenario['eticket']} | DMC: {d['dmc']} | Language: {d['lang']} | Credit Card | PPID: {scenario['package']['PrefProcessorID']} "
            f"| Template: {scenario['package']['PayPageTemplate']} | DMCStatus: {scenario['package']['DMCStatus']} ")
        print(f"Link: {d['joinlink']} \n")
        print('|Excptected Results |')
        print("--------------------------------------------------------------------------------------------------------------------------")
        print(f"Multitrans: | AuthCode:OK:0 | TransSource: 121 | TransStatus: 186 | TransType: 1011 | PaymentType: 131 | MerchantCurrency: {d['dmc']} | Language: {d['lang']} |"
              f"CustAddress,CustCity,CustState,CustPhone => Blank ")
        print(f"Assets:     | PurchStatus: 801 | PurchType: 502 | AuthCurrency: {d['dmc']} |  Purchases: 1 | CustAddress,CustCity,CustState,CustPhone: Blank | {rebill_date}")
        print(f"Email:      | PointOfSaleEmailQueue should  have email | EmailTypeID: 981  ")
        print(f"PostBacks   | {postbacks} ")
        if visa_secure == "3DS Configured":
            print(f"3DS:        | Cardinal3dsRequests should have the response from Cardinal")
        print(f"PurchaseID: | New PurchaseID should be created | OcToken: {d['octoken']}")
        print("------------------------------------------------------------------------------------------------------------------------------------End_TestCase\n")

    except Exception as ex:
        traceback.print_exc()
        pass


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
#                 sscenario = onetime_502(merchantbillconfig, pricepoint, packageid)
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
