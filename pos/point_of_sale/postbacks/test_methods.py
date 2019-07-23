from pos.point_of_sale.web import web
from pos.point_of_sale.config import config



def sign_up_trans_create(test_data):
    for selected_language in config.available_languages:
        for dmc in config.available_currencies:
            selected_options = [dmc, selected_language]
            transaction_record = web.create_transaction(test_data['pricepoint_type'], test_data['eticket'], selected_options, config.merchants[0], test_data['url_options'], config.processors[0])
            return transaction_record
