import traceback
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import options
from pos.point_of_sale.web import web

db_agent = DBActions()



# def sign_up_trans_web(test_data):
#     result = True
#     for selected_language in config.available_languages:
#         for dmc in config.available_currencies:
#             selected_options = [dmc, selected_language]
#             current_transaction_record = web.create_transaction(test_data['pricepoint_type'], test_data['eticket'], selected_options, config.merchants[0], test_data['url_options'], config.processors[0])
#             result &= TransActionService.verify_signup_transaction(current_transaction_record)
#     return result

def sign_up_trans_web1(test_data):  # Yan
    test_data = config.test_data # refactor needs
    current_transaction_record = {}
    for selected_language in config.available_languages:
        for dmc in config.available_currencies:
            try:
                selected_options = [dmc, selected_language]
                url_options = options.ref_variables() + options.refurl() + config.template
                config.test_data['url_options'] = url_options
                print("======================================| SignUp Transaction |======================================\n")
                config.logging.info('print("======================================| SignUp Transaction |======================================\n")')
                current_transaction_record = web.create_transaction(test_data['pricepoint_type'], test_data['eticket'], selected_options, config.merchants[0], url_options, config.processors[0])
                if current_transaction_record['full_record']['Authorized']:
                    config.oc_tokens[current_transaction_record['full_record']['PurchaseID']] = config.test_data['pricepoint_type']
                TransActionService.verify_signup_transaction(current_transaction_record)
            except Exception as ex:
                traceback.print_exc()
                print(f"{Exception}")
                config.logging.info(f"{Exception} ")
                pass

    return current_transaction_record

# def sign_up_trans_oc(oc_type, test_data):
#     result = True
#     for current_transaction in config.transaction_records:
#         selected_options = [current_transaction['merchant_currency'],current_transaction['paypage_lnaguage']]
#         multitrans_base_record = TransActionService.get_multitrans_base_record(current_transaction)
#         if oc_type == 'pos' or oc_type == 'ws':
#             one_click_record = web.one_click(oc_type, test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, current_transaction['email'], test_data['url_options'], selected_options)
#         else:
#             one_click_record= web.instant_conversion('pos', test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, current_transaction['email'], test_data['url_options'], test_data['merchantbillconfig'][0])
#         asset_base_record = TransActionService.get_asset_base_record_for_sign_up(multitrans_base_record, current_transaction)
#         result &= TransActionService.verify_signup_oc_transaction(oc_type, asset_base_record, one_click_record)
#     return result

def signup_oc(oc_type,eticket,test_data):  # Yan  # refactor
    result = True
    one_click_record = {}
    for current_transaction_id in config.transaction_records:
        try:
            print("\n======================================|       OneClick     |======================================\n")
            pricepoint = current_transaction_id['full_record']['BillConfigID']
            config.test_data = TransActionService.prepare_data(pricepoint, 1)
            selected_options = [current_transaction_id['merchant_currency'], current_transaction_id['paypage_lnaguage']]
            eticket = config.test_data['eticket']
            octoken = current_transaction_id['PurchaseID']
            if oc_type == 'pos':
                one_click_record = web.one_click_pos(eticket, octoken, selected_options, config.test_data['url_options'])
            elif oc_type == 'ws':
                one_click_record = web.one_click_services(eticket, octoken, selected_options, config.test_data['url_options'])
            result &= TransActionService.verify_oc_transaction(octoken, eticket, one_click_record, config.test_data['url_options'], selected_options)
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}  ")
            pass
    return result

def signup_oc_all(oc_type,eticket,test_data):  # Yan  # refactor
    result = True
    one_click_record = {}
    octokens = config.oc_tokens.keys()
    for current_transaction_id in config.transaction_records:
        for token in octokens:
            try:
                print("\n======================================|       OneClick     |======================================\n")
                config.logging.info("\n======================================|       OneClick     |======================================\n")
                config.logging.info('')
                pricepoint = current_transaction_id['full_record']['BillConfigID']
                config.test_data = TransActionService.prepare_data(pricepoint, 1)
                selected_options = [current_transaction_id['merchant_currency'], current_transaction_id['paypage_lnaguage']]
                eticket = config.test_data['eticket']
                octoken = token
                if oc_type == 'pos':
                    one_click_record = web.one_click_pos(eticket, octoken, selected_options, config.test_data['url_options'])
                elif oc_type == 'ws':
                    one_click_record = web.one_click_services(eticket, octoken, selected_options, config.test_data['url_options'])
                result &= TransActionService.verify_oc_transaction(octoken, eticket, one_click_record, config.test_data['url_options'], selected_options)
            except Exception as ex:
                traceback.print_exc()
                print(f"{Exception}  ")
                config.logging.info(f"{Exception}  ")
                pass
    return result


#
# def sign_up_oc_by_trnas_id(oc_type, test_data, trans_id): # Dima
#     result = True
#     multitrans_base_record = mts.build_multitrans_by_trans_id(config.test_data['merchantbillconfig'][0], config.test_data['package'][0], trans_id, config.test_data['url_options'])
#     selected_options = [multitrans_base_record['CustCountry'], multitrans_base_record['Language']]
#     email = db_agent.decrypt_string(multitrans_base_record['CustEMail'])
#     if oc_type == 'pos' or oc_type == 'ws':
#         one_click_record = web.one_click(oc_type, test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, email, test_data['url_options'], selected_options)
#     else:
#         one_click_record = web.instant_conversion('pos', test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, email, test_data['url_options'], test_data['merchantbillconfig'][0])
#     asset_base_record = asset.build_asset_signup_by_trans_id(config.test_data['merchantbillconfig'][0], multitrans_base_record, trans_id)
#     result &= TransActionService.verify_signup_oc_transaction(oc_type, asset_base_record, one_click_record)
#     return result

