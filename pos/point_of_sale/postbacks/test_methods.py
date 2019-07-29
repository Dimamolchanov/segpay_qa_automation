from pos.point_of_sale.web import web
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService



def sign_up_trans_web(test_data):
    result = True
    for selected_language in config.available_languages:
        for dmc in config.available_currencies:
            selected_options = [dmc, selected_language]
            current_transaction_record = web.create_transaction(test_data['pricepoint_type'], test_data['eticket'], selected_options, config.merchants[0], test_data['url_options'], config.processors[0])
            multitrans_base_record = TransActionService.get_multitrans_base_record(current_transaction_record)
            asset_base_record = TransActionService.get_asset_base_record_for_sign_up(multitrans_base_record, current_transaction_record)
            result &= TransActionService.verify_tarnsaction(current_transaction_record, multitrans_base_record, asset_base_record)
    return result

def sign_up_trans_oc_pos(test_data):
    result = True
    for current_transaction in config.transaction_records:
        selected_options = [current_transaction['paypage_lnaguage'], current_transaction['merchant_currency']]
        multitrans_base_record = TransActionService.get_multitrans_base_record(current_transaction)
        one_click_pos_record = web.one_click('pos', test_data['eticket'], test_data['pricepoint_type'], multitrans_base_record, current_transaction['email'], test_data['url_options'], selected_options)
        asset_base_record = TransActionService.get_asset_base_record_for_sign_up(multitrans_base_record, current_transaction)
        asset_base_oc_record = TransActionService.get_asset_base_record_for_oc(asset_base_record, one_click_pos_record[1])
        result &= TransActionService.verify_tarnsaction(one_click_pos_record[1], multitrans_base_record[2],  asset_base_oc_record)
    return result
