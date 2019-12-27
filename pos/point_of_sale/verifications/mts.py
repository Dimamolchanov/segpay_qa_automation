from pos.point_of_sale.config import config
from datetime import datetime
from datetime import timedelta
from termcolor import colored
from decimal import Decimal
import traceback
import time
from pos.point_of_sale.bep import bep
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import constants
import json
import simplexml
from pos.point_of_sale.utils import options

db_agent = DBActions()


def build_mt_oneclick(one_click_record, action):
    transdate = (datetime.now().date())
    d = config.test_data
    multitrans_oneclick_record = {}
    # sql = "select * from MerchantBillConfig where BillConfigID = {}"
    # merchantbillconfig = db_agent.execute_select_one_parameter(sql, d['eitcket'])
    pp_type = d['Type']

    try:
        url = db_agent.url(config.test_data['URLID'])
        sql = "select * from assets where PurchaseID = {}"
        octoken_record = db_agent.execute_select_one_parameter(sql, d['octoken'])
        if action == 'pos':
            currency = d['dmc']
            lang = d['lang']
        else:
            currency = octoken_record['Currency']
            lang = octoken_record['CustLang']
        multitrans = {
            'PurchaseID': one_click_record['PurchaseID'],
            'TransID': one_click_record['TransID'],
            'TRANSGUID': one_click_record['TRANSGUID'],
            'BillConfigID': int(d['pricepoint']),
            'PackageID': one_click_record['PackageID'],
            'AuthCode': 'OK:0',
            'Authorized': 1,
            'CardExpiration': octoken_record['CardExpiration'],
            'CustCountry': octoken_record['CustCountry'],
            'CustEMail': octoken_record['CustEMail'],
            'CustName': octoken_record['CustName'],
            'CustZip': octoken_record['CustZip'],
            'CustAddress': octoken_record['CustAddress'],
            'CustCity': octoken_record['CustCity'],
            'CustState': octoken_record['CustState'],
            'CustPhone': octoken_record['CustPhone'],
            'Language': lang,
            'MerchantID': one_click_record['MerchantID'],
            'PaymentAcct': octoken_record['PaymentAcct'],
            'PCID': None,
            # 'Processor': d['processor_name'],
            'ProcessorCurrency': d['Currency'],  # octoken_record['Currency'],
            'MerchantCurrency': currency,
            'STANDIN': one_click_record['STANDIN'],
            'TransBin': one_click_record['TransBin'],
            'URLID': config.test_data['URLID'], #octoken_record['URLID'],
            'URL': url, #one_click_record['URL'],
            'REF1': None,
            'REF2': None,
            'REF3': None,
            'REF4': None,
            'REF5': None,
            'REF6': None,
            'REF7': None,
            'REF8': None,
            'REF9': None,
            'REF10': None,
            'RefURL': one_click_record['RefURL']
        }  #
        #if config.test_data['payment'] == 'Paypal':
        multitrans['Processor'] = octoken_record['Processor']


        url_parameters = d['url_options'].split('&')
        for var in url_parameters:
            tmp = var.split('=')
            if tmp[0] == 'ref1':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF1'] = val
            elif tmp[0] == 'ref2':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF2'] = val = val
            elif tmp[0] == 'ref3':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF3'] = val
            elif tmp[0] == 'ref4':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF4'] = val
            elif tmp[0] == 'ref5':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF5'] = val
            elif tmp[0] == 'ref6':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF6'] = val
            elif tmp[0] == 'ref7':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF7'] = val
            elif tmp[0] == 'ref8':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF8'] = val
            elif tmp[0] == 'ref9':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF9'] = val
            elif tmp[0] == 'ref10':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF10'] = val
            elif tmp[0] == 'refurl':
                val = tmp[1][:256]
                multitrans['RefURL'] = val  # update refs  #
        if config.test_data['payment']  == 'CC':
            multitrans['PaymentType'] = 131
        elif config.test_data['payment']  == 'Pypal':
            multitrans['PaymentType'] = 1301

        #multitrans['PaymentType'] = octoken_record['PaymentType']
        exchange_rate = 1
        if d['Currency'] == d['dmc']:
            exchange_rate = 1
        else:
            exchange_rate = db_agent.exc_rate(d['dmc'], d['Currency'])

        multitrans['TxStatus'] = 2
        if pp_type in (502, 503, 510):
            multitrans['TransSource'] = 123
        else:
            multitrans['TransSource'] = 121

        multitrans['TransStatus'] = 186
        multitrans['TransType'] = 1011

        # if pp_type == 511:
        #     trans_amount = one_click_record['511']['InitialPrice']
        #     multitrans['TransAmount'] = trans_amount
        #     multitrans['Markup'] = round(trans_amount * exchange_rate, 2)
        if d['Type'] == 510:
            trans_amount = config.test_data['510']
            multitrans['TransAmount'] = trans_amount
            multitrans['Markup'] = round(trans_amount * exchange_rate, 2)
        else:
            initial_price = d['InitialPrice']
            multitrans['TransAmount'] = initial_price
            multitrans['Markup'] = round(initial_price * exchange_rate, 2)
            # multitrans['RelatedTransID'] = 0
            multitrans['TransDate'] = transdate

        if d['Type'] in [501, 506] and d['InitialPrice'] == 0.00:
            multitrans['TransAmount'] = 1.00
        elif d['Type'] == 511 and one_click_record['511']['InitialPrice'] == 0.00:
            multitrans['TransAmount'] = 1.00

        exchange_rate = round(exchange_rate, 2)
        multitrans['ExchRate'] = exchange_rate
        if multitrans['MerchantCurrency'] == 'JPY':
            multitrans['Markup'] = round(round(multitrans['TransAmount'] * exchange_rate, 2))
        one_click_record['PCID'] = None
        if one_click_record['ProcessorTransID'] == 'FREETRIAL':
            multitrans['TransStatus'] = 187
            multitrans['TransAmount'] = 0.00
        sql = 'select * from MultiTransValues where transid = {}'

        result = db_agent.execute_select_one_parameter(sql, one_click_record['TransID'])
        if 'PREAUTHFREETRIAL' in result:
            multitrans['Markup'] = 1.00
        if config.test_data['payment'] == 'Paypal':
            multitrans['CardExpiration'] = '9999'
            multitrans['CustAddress'] = ''
            multitrans['CustEMail'] = 'w2nMk0ozBbSpaz1vfCN+Rg=='
            multitrans['CustName'] = 'Yan Karob'
            multitrans['CustZip'] = ''
            multitrans['PaymentAcct'] = 'rWdXYj56QxCwTxPFzux5Rt8DqpSknfe2'
            multitrans['Processor'] = 'PAYPAL'
            multitrans['TransBin'] = 411111
            multitrans['PaymentType'] = 1301
        return multitrans, octoken_record, d
        
            
            
            

    except Exception as ex:
        traceback.print_exc()
        pass


def build_multitrans():
    transdate = (datetime.now().date())
    url = db_agent.url(config.test_data['URLID'])
    multitrans = {}
    d = config.test_data
    b_address = ''
    b_city = ''
    b_state = ''
    try:
        link = d['link']
        if '&x-bill' in link:
            tmp = link.split('&')
            for xbill in tmp:
                if 'x-billaddr' in xbill:
                    val = xbill.split('=')[1]
                    if '+' in val: b_address = val.replace('+', ' ')
                elif 'x-billcity' in xbill:
                    val = xbill.split('=')[1]
                    if '+' in val: b_city = val.replace('+', ' ')
                elif 'x-billstate' in xbill:
                    b_state = xbill.split('=')[1]

    except Exception as ex:
        traceback.print_exc()
        pass
    try:
        multitrans = {
            'PurchaseID': config.test_data['PurchaseID'],
            'TransID': config.test_data['TransID'],
            'TRANSGUID': config.test_data['transguid'],
            'BillConfigID': config.test_data['BillConfigID'],
            'PackageID': config.test_data['PackageID'],
            'AuthCode': 'OK:0',
            'Authorized': 1,
            'CardExpiration': config.test_data['expiration_date'] + config.test_data['year'][-2:],
            'CustCountry': config.test_data['merchant_country'],
            'CustAddress': b_address,
            'CustCity': b_city,
            'CustState': b_state,
            'CustPhone': '',
            'CustEMail': config.test_data['email_encrypt'],
            'CustName': config.test_data['firstname'] + ' ' + config.test_data['lastname'],
            'CustZip': config.test_data['zip'],
            'Language': config.test_data['paypage_lnaguage'],
            'MerchantID': config.test_data['MerchantID'],
            'PaymentAcct': config.test_data['card_encrypted'],
            'PCID': None,
            'Processor': config.test_data['processor_name'],
            'ProcessorCurrency': config.test_data['Currency'],
            'MerchantCurrency': config.test_data['merchant_currency'],
            'STANDIN': config.test_data['AllowStandin'],
            'TransBin': config.test_data['transbin'],
            'URLID': config.test_data['URLID'],
            'URL': url,
            'REF1': None,
            'REF2': None,
            'REF3': None,
            'REF4': None,
            'REF5': None,
            'REF6': None,
            'REF7': None,
            'REF8': None,
            'REF9': None,
            'REF10': None,
            'RefURL': None
        }  # dictionary from paypage
        # analyzing url
        url_parameters = config.test_data['url_options'].split('&')
        for var in url_parameters:
            tmp = var.split('=')
            if tmp[0] == 'ref1':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF1'] = val
            elif tmp[0] == 'ref2':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF2'] = val = val
            elif tmp[0] == 'ref3':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF3'] = val
            elif tmp[0] == 'ref4':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF4'] = val
            elif tmp[0] == 'ref5':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF5'] = val
            elif tmp[0] == 'ref6':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF6'] = val
            elif tmp[0] == 'ref7':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF7'] = val
            elif tmp[0] == 'ref8':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF8'] = val
            elif tmp[0] == 'ref9':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF9'] = val
            elif tmp[0] == 'ref10':
                val = db_agent.encrypt_string(tmp[1])
                multitrans['REF10'] = val
            elif tmp[0] == 'refurl':
                val = tmp[1][:256]
                multitrans['RefURL'] = val  # update refs  #

        multitrans['PaymentType'] = 131
        exchange_rate = 1
        if config.test_data['Currency'] == config.test_data['merchant_currency']:
            exchange_rate = 1
        else:
            exchange_rate = db_agent.exc_rate(config.test_data['merchant_currency'], config.test_data['Currency'])

        multitrans['TxStatus'] = 2
        if config.test_data['Type'] == 505 and config.test_data['aprove_or_decline']:
            multitrans['TransSource'] = 122
            multitrans['TransStatus'] = 184
            multitrans['TransType'] = 105
            sql = "Select TransID from multitrans where purchaseid = {} and TransSource = 121"
            tid = db_agent.execute_select_one_parameter(sql, config.test_data['PurchaseID'])['TransID']
            multitrans['RelatedTransID'] = tid
        elif config.test_data['Type'] == 505 and config.test_data['aprove_or_decline'] == False:
            multitrans['TransSource'] = 122
            multitrans['TransStatus'] = 187
            multitrans['TransType'] = 105
            sql = "Select TransID from multitrans where purchaseid = {} and TransSource = 121"
            tid = db_agent.execute_select_one_parameter(sql, config.test_data['PurchaseID'])['TransID']
            multitrans['RelatedTransID'] = tid
        else:
            multitrans['TransSource'] = 121
            multitrans['TransStatus'] = 184
            multitrans['TransType'] = 101

        # if config.test_data['Type'] == 511:
        #     multitrans['TransAmount'] = config.test_data['initialprice511']
        #     multitrans['Markup'] = round(config.test_data['initialprice511'] * exchange_rate, 2)
        if config.test_data['Type'] == 510:
            multitrans['TransAmount'] = config.test_data['510'] #config.test_data['initialprice510']
        else:
            if config.test_data['Type'] == 505 and config.test_data['record_to_check']['TransSource'] == 122:
                multitrans['TransAmount'] = config.test_data['RebillPrice']
                multitrans['TransDate'] = transdate + timedelta(days=config.test_data['InitialLen'])
            # sql = f"select  RelatedTransID  from multitrans where PurchaseID = {config.test_data['PurchaseID']}  and TransSource = 121 "
            # multitrans['RelatedTransID'] = db_agent.sql(sql)[0]['RelatedTransID']
            else:
                multitrans['TransDate'] = transdate
                multitrans['TransAmount'] = config.test_data['InitialPrice']
                multitrans['Markup'] = round(config.test_data['InitialPrice'] * exchange_rate, 2)
                multitrans['RelatedTransID'] = 0
        type = config.test_data['Type']
        if type in [501, 506] and config.test_data['InitialPrice'] == 0.00 and config.test_data['aprove_or_decline']:
            multitrans['TransStatus'] = 186
            multitrans['TransAmount'] = 1.00
        elif type in [501, 506] and config.test_data['InitialPrice'] == 0.00 and config.test_data['aprove_or_decline'] == False:
            multitrans['TransStatus'] = 184
            multitrans['TransAmount'] = 0.00

        # if config.test_data['Type'] in [501, 506] and config.test_data['InitialPrice'] == 0.00 and config.test_data['aprove_or_decline']:
        # 	multitrans['TransStatus'] = 186
        # 	multitrans['TransAmount'] = 1.00
        # elif config.test_data['Type'] == 501 and config.test_data['InitialPrice'] == 0.00 and config.test_data['aprove_or_decline'] ==False:
        # 	multitrans['TransStatus'] = 184
        # 	multitrans['TransAmount'] = 1.00
        # elif config.test_data['Type'] == 506 and config.test_data['InitialPrice'] == 0.00 and config.test_data['aprove_or_decline'] ==False:
        # 	multitrans['TransStatus'] = 186
        # 	multitrans['TransAmount'] = 1.00
        exchange_rate = round(exchange_rate, 2)
        multitrans['ExchRate'] = exchange_rate
        if multitrans['MerchantCurrency'] == 'JPY':
            multitrans['Markup'] = round(round(multitrans['TransAmount'] * exchange_rate, 2))

        if config.test_data['scope']:
            if 'aprove_or_decline' in config.test_data:
                if config.test_data['aprove_or_decline'] == False:
                    multitrans['Authorized'] = 0
                    multitrans['Markup'] = 0.00
                    multitrans['ExchRate'] = 0.00
                    multitrans['MerchantCurrency'] = 'USD'
                    del multitrans['AuthCode']
        else:
            if config.test_data['record_to_check']['Authorized'] == False:
                if config.test_data['aprove_or_decline'] == False:
                    multitrans['Authorized'] = 0
                    multitrans['Markup'] = 0.00
                    multitrans['ExchRate'] = 0.00
                    multitrans['MerchantCurrency'] = 'USD'
                    del multitrans['AuthCode']
        sql = 'select * from MultiTransValues where transid = {}'
        result = db_agent.execute_select_one_parameter(sql, config.test_data['TransID'])
        if 'PREAUTHFREETRIAL' in result:
            multitrans['Markup'] = 1.00

        if config.test_data['record_to_check']['ProcessorTransID'] == 'FREETRIAL':
            multitrans['TransStatus'] = 187
            multitrans['TransAmount'] = 0.00
        if config.test_data['payment'] == 'Paypal':
            multitrans['CardExpiration'] = '9999'
            multitrans['CustAddress'] = ''
            multitrans['CustEMail'] = 'w2nMk0ozBbSpaz1vfCN+Rg=='
            multitrans['CustName'] = 'Yan Karob'
            multitrans['CustZip'] = ''
            multitrans['CustState'] = ''
            multitrans['PaymentAcct'] = 'rWdXYj56QxCwTxPFzux5Rt8DqpSknfe2'
            multitrans['Processor'] = 'PAYPAL'
            multitrans['TransBin'] = 411111
            multitrans['PaymentType'] = 1301
    except Exception as ex:
        traceback.print_exc()
        pass
    return multitrans


def multitrans_compare(multitrans_base_record, live_record):
    differences = {}
    try:
        multitrans_live_record = live_record  # [0]
        live_record['PCID'] = None
        try:
            multitrans_live_record['TransDate'] = multitrans_live_record['TransDate'].date()
        except Exception as ex:
            #traceback.print_exc()
            pass

        differences = bep.dictionary_compare(multitrans_base_record, multitrans_live_record)
        if len(differences) == 0:
            print(colored(f"Mulitrans  Record Compared =>  Pass", 'green'))
            options.append_list("Mulitrans  Record Compared =>  Pass")
        else:
            print(colored(f"********************* Multitrans MissMatch ****************", 'red'))
            options.append_list("********************* Multitrans MissMatch ****************")
            for k, v in differences.items():
                tmp = k + " " + v
                options.append_list(tmp)
                print(k, v)
    # config.logging.info(k,v)
    except Exception as ex:
        traceback.print_exc()
        print(f"Exception {Exception} ")
        # config.logging.info(f"Exception {Exception} ")
        pass
    return differences


def multitrans_check_conversion(rebills):
    rkeys = rebills.keys()
    rebills_completed_mt = []
    rebills_failed_mt = []
    try:
        for tid in rkeys:
            differences = {}
            pid = rebills[tid]['PurchaseID']
            base_record = rebills[tid]
            base_record['TxStatus'] = 6
            base_record['TransStatus'] = 186
            base_record['TransSource'] = 122
            sql = "Select RecurringAmount from Assets where PurchaseID = {}"
            rebill_amount = db_agent.execute_select_one_parameter(sql, pid)
            base_record['TransAmount'] = rebill_amount['RecurringAmount']
            base_record['ProcessorTransID'] = ''
            base_record['TransID'] = 0
            base_record['SOURCEMACHINE'] = ''
            base_record['TransDate'] = datetime.date(base_record['TransDate'])
            base_record['TransTime'] = datetime.date(base_record['TransTime'])
            base_record['PCID'] = None
            base_record['TRANSGUID'] = ''
            base_record['IPCountry'] = 'N/A'
            base_record['BinCountry'] = 'N/A'
            base_record['AffiliateID'] = None
            base_record['RefURL'] = None
            base_record['CustAddress'] = ''
            base_record['CustCity'] = ''
            base_record['CustState'] = ''
            base_record['CustPhone'] = ''

            sql = "select TOP 1 Rate from ExchangeRates as rate where ConsumerIso = '{}' " \
                  "and   MerchantIso = '{}' order by importdatetime desc"

            exchange_rate = db_agent.execute_select_two_parameters(sql, base_record['MerchantCurrency'], base_record['ProcessorCurrency'])

            if base_record['MerchantCurrency'] == 'JPY':
                excr = round((base_record['TransAmount'] * exchange_rate['Rate']), 2)
                excr = round((excr))
                excr = str(excr) + '.00'
                excr = Decimal(excr)
                base_record['Markup'] = excr
            else:
                base_record['Markup'] = round((base_record['TransAmount'] * exchange_rate['Rate']), 2)

            sql = "Select * from multitrans where PurchaseID = {} and TransSource = 122"
            live_record = db_agent.execute_select_one_parameter(sql, pid)

            if base_record['TransType'] == 1011:
                base_record['TransType'] = 101
                base_record['RelatedTransID'] = 0

            live_record['ProcessorTransID'] = ''
            tid = live_record['TransID']
            live_record['TransID'] = 0
            live_record['SOURCEMACHINE'] = ''
            live_record['TransDate'] = datetime.date(live_record['TransDate'])
            live_record['TransTime'] = datetime.date(live_record['TransTime'])
            live_record['TRANSGUID'] = ''
            live_record['RefURL'] = None

            differences = bep.dictionary_compare(base_record, live_record)
            if len(differences) == 0:
                rebills_completed_mt.append(live_record)
            else:
                rebills_failed_mt.append(live_record)
                print(colored(f"********************* Conversion Multitrans MissMatch Beginning**************** | PurchaseID = {pid} | TransID: {tid}", 'red'))
                print()
                for k, v in differences.items():
                    print(k, v)
                print()
                print(colored(f"********************* Conversion Multitrans MissMatch End ****************", 'red'))


    except Exception as ex:
        traceback.print_exc()
        # (f"{Exception}  Tid: {tid,}   Task: {tasks_type_status[0]} , {tasks_type_status[1]}  SQL: {sql}  BaseRecord: {base_record}")
        pass

    if len(rebills_failed_mt) == 0:
        print(colored(f"Rebills => Multitrans Records Compared => Pass ", 'green'))
    else:
        print(colored(f"********************* Rebills => Multitrans MissMatch => CHeck Manually ****************", 'blue'))

    return [rebills_completed_mt, rebills_failed_mt]


def multitrans_check_refunds():
    refunds = config.results[1]
    rkeys = refunds.keys();
    live_record = {};
    tasks_type_status = []
    refunds_completed_mt = [];
    base_record = {};
    sql = '';
    pid = 0
    refunds_failed_mt = []

    for tid in rkeys:
        try:
            differences = {}
            base_record = refunds[tid]
            pid = base_record['PurchaseID']
            tasks_type_status = db_agent.tasks_table(tid)
            sql = ''
            if tasks_type_status[0] == '':
                print(f"Task was not inserted TID: {tid} PID: #{pid}")
            elif tasks_type_status[0] == 844:
                print(f"Task - 844 Cancel => Nothing to refund => PID: {pid} | TID: {tid}")
                refunds_failed_mt.append(live_record)
            else:
                if base_record['TransStatus'] == 184:  # Void
                    base_record['TransType'] = 107
                    base_record['TxStatus'] = 8
                    base_record['TransStatus'] = 182
                    sql = "Select * from multitrans where PurchaseID = {} and TransType = 107 and RelatedTransID = {}"
                else:  # Refund
                    sql = "Select * from multitrans where PurchaseID = {} and TransType = 102 and RelatedTransID = {}"
                    base_record['TransType'] = 102
                    base_record['TxStatus'] = 7
                    base_record['TransStatus'] = 186

                live_record = db_agent.execute_select_two_parameters(sql, pid, base_record['TransID'])
                # live_record['TransTime'] = datetime.date(live_record['TransTime'])

                base_record['TransAmount'] = (-base_record['TransAmount'])
                base_record['Markup'] = (-base_record['Markup'])
                base_record['TransSource'] = 125
                base_record['RelatedTransID'] = base_record['TransID']
                base_record['TransID'] = live_record['TransID']
                base_record['CustAddress'] = ''
                base_record['CustCity'] = ''
                base_record['CustState'] = ''
                base_record['CustPhone'] = ''

                # base_record['TransTime'] = datetime.date(base_record['TransTime'])

                for record in [base_record, live_record]:
                    record['TRANSGUID'] = ''
                    record['ProcessorTransID'] = None
                    record['PCID'] = None
                    record['SOURCEMACHINE'] = None
                    record['IPCountry'] = None
                    record['BinCountry'] = None
                    record['RefURL'] = None
                    record['AffiliateID'] = None

                differences = bep.dictionary_compare(base_record, live_record)

                if len(differences) == 0:
                    refunds_completed_mt.append(live_record)
                else:
                    refunds_failed_mt.append(live_record)
                    print(colored(f"********************* Refunds Multitrans MissMatch Beginning**************** | PurchaseID = {pid} | TransID: {tid}", 'red'))
                    print()
                    for k, v in differences.items():
                        print(k, v)
                    print()
                    print(colored(f"******************** Refund Multitrans MissMatch End ***************", 'red'))
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}  Tid: {tid,}   Task: {tasks_type_status[0]} , {tasks_type_status[1]}  SQL: {sql}  BaseRecord: {base_record}")
            pass

    if len(refunds_failed_mt) == 0:
        print(colored(f"Refund => Multitrans {len(refunds_completed_mt)} - Records Compared => Pass ", 'green'))
    else:
        print(colored(f"Refund => Multitrans {len(refunds_completed_mt)} - Records Compared => Pass ", 'green'))
        print()
        print(colored(f"******************** Refund {len(refunds_failed_mt)} transactions    => Multitrans MissMatch => Check Manually ***************", 'blue'))

    return config.results  # [refunds_completed_mt, refunds_failed_mt]


def mt_check_reactivation():
    reactivated = config.mt_reactivated
    rkeys = reactivated.keys()
    cnt = 0
    tasks_type_status = []
    reactivated_completed_mt = []
    base_record = {}
    sql = ''
    pid = 0
    reactivated_failed_mt = []

    for tid in rkeys:
        try:
            differences = {}
            base_record = reactivated[tid][tid]
            pid = base_record['PurchaseID']
            tasks_type_status = db_agent.tasks_table(tid)
            sql = "Select RecurringAmount, CardExpiration,PurchStatus from assets where PurchaseID = {}"
            asset_data = db_agent.execute_select_one_parameter(sql, pid)
            live_record = None
            if tasks_type_status[0] == 841:
                while live_record == None and cnt < 5:
                    cnt += 1
                    sql = "Select * from multitrans where PurchaseID = {} and TransSource = 127"
                    live_record = db_agent.execute_select_one_parameter(sql, pid)
                    time.sleep(1)
                if live_record == None:
                    print(f"******* Warning => transaction with PurchaseID: {pid} is reactivated but there is no MultiTrans record for it!! *******")
                    raise Exception('norecord')
                # refactor after fixes for address
                live_record['CustAddress'] = 'N/A'
                live_record['CustCity'] = 'N/A'

                base_record['TransSource'] = 127
                base_record['TransType'] = 101
                base_record['TransAmount'] = asset_data['RecurringAmount']
                base_record['CustZip'] = config.test_data['zip']
                card_encrypted = db_agent.encrypt_card(int(config.test_data['cc']))
                base_record['PaymentAcct'] = card_encrypted
                base_record['CardExpiration'] = config.test_data['month'] + config.test_data['year'][-2:]
                base_record['CustName'] = live_record['CustName']
                base_record['RelatedTransID'] = 0
                base_record['CustAddress'] = ''
                base_record['CustCity'] = ''
                base_record['CustState'] = ''
                base_record['CustPhone'] = ''

                base_record['Markup'] = round((base_record['TransAmount'] * base_record['ExchRate']), 2)
                exchange_rate = 1
                if base_record['ProcessorCurrency'] == base_record['MerchantCurrency']:
                    exchange_rate = 1
                else:
                    exchange_rate = db_agent.exc_rate(base_record['MerchantCurrency'], base_record['ProcessorCurrency'])
                if base_record['MerchantCurrency'] == 'JPY':
                    excr = round((base_record['TransAmount'] * exchange_rate), 2)
                    excr = round((excr))
                    excr = str(excr) + '.00'
                    excr = Decimal(excr)
                    base_record['Markup'] = excr
                else:
                    base_record['Markup'] = round((base_record['TransAmount'] * exchange_rate), 2)

                base_record['TransStatus'] = 186
                base_record['TransID'] = live_record['TransID']

                for record in [base_record, live_record]:
                    record['TRANSGUID'] = ''
                    record['ProcessorTransID'] = None
                    record['PCID'] = None
                    record['SOURCEMACHINE'] = None
                    record['USERDATA'] = None
                    # record['IPCountry'] = None
                    # record['BinCountry'] = None
                    record['RefURL'] = None
                    record['AffiliateID'] = None
                    # make sure they need it or not
                    record['REF1'] = None
                    record['REF2'] = None
                    record['REF3'] = None
                    record['REF4'] = None
                    record['REF5'] = None
                    record['REF6'] = None
                    record['REF7'] = None
                    record['REF8'] = None
                    record['REF9'] = None
                    record['REF10'] = None

                differences = bep.dictionary_compare(base_record, live_record)

                if len(differences) == 0:
                    reactivated_completed_mt.append(live_record)
                else:
                    reactivated_failed_mt.append(live_record)
                    print(colored(f"********************* Reactivation Multitrans MissMatch Beginning**************** | PurchaseID = {pid} | TransID: {tid}", 'red'))
                    print()
                    for k, v in differences.items():
                        print(k, v)
                        print()
                    print()
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}  Tid: {tid,}   Task: {tasks_type_status[0]} , {tasks_type_status[1]}  SQL: {sql}  BaseRecord: {base_record}")
            pass

    if len(reactivated_failed_mt) == 0:
        print(colored(f"Reactivation {len(reactivated_completed_mt)} records reactivated  - Multitrans Records Compared => Pass ", 'green'))
    else:
        if len(reactivated_completed_mt) > 0:
            print(colored(f"Reactivation {len(reactivated_completed_mt)} records reactivated  - Multitrans Records Compared => Pass ", 'green'))
        print()
        print(colored(f"******************** Reactivation {len(reactivated_failed_mt)} transactions    => Multitrans MissMatch => Check Manually ***************", 'blue'))

    return [reactivated_completed_mt, reactivated_failed_mt]


def build_multitrans_by_trans_id(merchantbillconfig, package, trans_id, url_options):
    data_from_multitrans = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MULTITRANS_BY_TRANS_ID, trans_id)
    transdate = (datetime.now().date())
    url = db_agent.url(package['URLID'])
    multitrans = {
        'PurchaseID': data_from_multitrans['PurchaseID'],
        'TransID': trans_id,
        'TRANSGUID': data_from_multitrans['TRANSGUID'],
        'BillConfigID': merchantbillconfig['BillConfigID'],
        'PackageID': package['PackageID'],
        'AuthCode': 'OK:0',
        'Authorized': 1,
        'CardExpiration': data_from_multitrans['CardExpiration'],
        'CustCountry': data_from_multitrans['CustCountry'],
        'CustEMail': data_from_multitrans['CustEMail'],
        'CustName': data_from_multitrans['CustName'],
        'CustZip': data_from_multitrans['CustZip'],
        'Language': data_from_multitrans['Language'],
        'MerchantID': merchantbillconfig['MerchantID'],
        'PaymentAcct': data_from_multitrans['PaymentAcct'],
        'PCID': '0',
        'Processor': data_from_multitrans['Processor'],
        'ProcessorCurrency': merchantbillconfig['Currency'],
        'MerchantCurrency': data_from_multitrans['MerchantCurrency'],
        'STANDIN': package['AllowStandin'],
        'TransBin': data_from_multitrans['TransBin'],
        'URLID': package['URLID'],
        'CustAddress': '',
        'CustCity': '',
        'CustState': '',
        'CustPhone': '',
        'URL': url,
        'REF1': None,
        'REF2': None,
        'REF3': None,
        'REF4': None,
        'REF5': None,
        'REF6': None,
        'REF7': None,
        'REF8': None,
        'REF9': None,
        'REF10': None,
        'RefURL': ''
    }  # dictionary from paypage

    # analyzing url
    url_parameters = url_options.split('&')
    for var in url_parameters:
        tmp = var.split('=')
        if tmp[0] == 'ref1':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF1'] = val
        elif tmp[0] == 'ref2':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF2'] = val = val
        elif tmp[0] == 'ref3':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF3'] = val
        elif tmp[0] == 'ref4':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF4'] = val
        elif tmp[0] == 'ref5':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF5'] = val
        elif tmp[0] == 'ref6':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF6'] = val
        elif tmp[0] == 'ref7':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF7'] = val
        elif tmp[0] == 'ref8':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF8'] = val
        elif tmp[0] == 'ref9':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF9'] = val
        elif tmp[0] == 'ref10':
            val = db_agent.encrypt_string(tmp[1])
            multitrans['REF10'] = val
        elif tmp[0] == 'refurl':
            val = tmp[1][:256]
            multitrans['RefURL'] = val  # update refs  #

    multitrans['PaymentType'] = 131
    exchange_rate = 1
    if merchantbillconfig['Currency'] == data_from_multitrans['MerchantCurrency']:
        exchange_rate = 1
    else:
        exchange_rate = db_agent.exc_rate(data_from_multitrans['MerchantCurrency'], merchantbillconfig['Currency'])

    multitrans['TxStatus'] = 2
    if merchantbillconfig['Type'] == 505:
        multitrans['TransSource'] = 122
        multitrans['TransStatus'] = 184
        multitrans['TransType'] = 105
    else:
        multitrans['TransSource'] = 121
        multitrans['TransStatus'] = 184
        multitrans['TransType'] = 101

    if merchantbillconfig['Type'] == 511:
        multitrans['TransAmount'] = data_from_multitrans['TransAmount']
        multitrans['Markup'] = round(data_from_multitrans['TransAmount'] * exchange_rate, 2)
    elif merchantbillconfig['Type'] == 510:
        multitrans['TransAmount'] = data_from_multitrans['TransAmount']
    else:
        if merchantbillconfig['Type'] == 505 and data_from_multitrans['TransSource'] == 122:
            multitrans['TransAmount'] = merchantbillconfig['RebillPrice']
            multitrans['TransDate'] = transdate + timedelta(days=merchantbillconfig['InitialLen'])
            sql = f"select  RelatedTransID  from multitrans where PurchaseID = {trans_id}  and TransSource = 121 "
            multitrans['RelatedTransID'] = db_agent.sql(sql)[0]['RelatedTransID']
        else:
            multitrans['TransDate'] = transdate
            multitrans['TransAmount'] = merchantbillconfig['InitialPrice']
            multitrans['Markup']: round(multitrans['InitialPrice'] * exchange_rate, 2)
            multitrans['RelatedTransID'] = 0

    if merchantbillconfig['Type'] in [501, 506] and merchantbillconfig['InitialPrice'] == 0.00:
        multitrans['TransStatus'] = 186
        multitrans['TransAmount'] = 1.00
    exchange_rate = round(exchange_rate, 2)
    multitrans['ExchRate'] = exchange_rate
    return multitrans
