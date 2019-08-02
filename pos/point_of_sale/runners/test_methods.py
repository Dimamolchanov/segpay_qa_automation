from pos.point_of_sale.web import web
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.verifications import mts
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.db_functions.dbactions import DBActions

db_agent = DBActions()



def sign_up_trans_web(test_data):
    result = True
    for selected_language in config.available_languages:
        for dmc in config.available_currencies:
            selected_options = [dmc, selected_language]
            current_transaction_record = web.create_transaction(test_data['pricepoint_type'], test_data['eticket'], selected_options, config.merchants[0], test_data['url_options'], config.processors[0])
            result &= TransActionService.verify_signup_transaction(current_transaction_record)
    return result

def sign_up_trans_oc(oc_type, test_data):
    result = True
    for current_transaction in config.transaction_records:
        selected_options = [current_transaction['merchant_currency'],current_transaction['paypage_lnaguage']]
        multitrans_base_record = TransActionService.get_multitrans_base_record(current_transaction)
        if oc_type == 'pos' or oc_type == 'ws':
            one_click_record = web.one_click(oc_type, test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, current_transaction['email'], test_data['url_options'], selected_options)
        else:
            one_click_record= web.instant_conversion('pos', test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, current_transaction['email'], test_data['url_options'], test_data['merchantbillconfig'][0])
        asset_base_record = TransActionService.get_asset_base_record_for_sign_up(multitrans_base_record, current_transaction)
        result &= TransActionService.verify_signup_oc_transaction(oc_type, asset_base_record, one_click_record)
    return result

def sign_up_oc_by_trnas_id(oc_type, test_data, trans_id):
    result = True
    multitrans_base_record = mts.build_multitrans_by_trans_id(config.test_data['merchantbillconfig'][0], config.test_data['package'][0], trans_id, config.test_data['url_options'])
    selected_options = [multitrans_base_record['CustCountry'], multitrans_base_record['Language']]
    email = db_agent.decrypt_string(multitrans_base_record['CustEMail'])
    if oc_type == 'pos' or oc_type == 'ws':
        one_click_record = web.one_click(oc_type, test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, email, test_data['url_options'], selected_options)
    else:
        one_click_record = web.instant_conversion('pos', test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, email, test_data['url_options'], test_data['merchantbillconfig'][0])
    asset_base_record = asset.build_asset_signup_by_trans_id(config.test_data['merchantbillconfig'][0], multitrans_base_record, trans_id)
    result &= TransActionService.verify_signup_oc_transaction(oc_type, asset_base_record, one_click_record)
    return result

