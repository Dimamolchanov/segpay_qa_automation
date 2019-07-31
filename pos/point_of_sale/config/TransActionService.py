from pos.point_of_sale.config import config
from pos.point_of_sale.utils import options
from pos.point_of_sale.web import web
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.verifications import postback_service


db_agent = DBActions()


class TransActionService:
    @staticmethod
    def load_data():
        if config.pricepoints[0] == 'type':
            pricepoints = db_agent.pricepoint_type(config.merchants[0], [511, 501, 506])
        elif config.pricepoints[0] == 'list':
            pricepoints = db_agent.pricepoint_list(config.merchants[0])
        else:
            pricepoints = config.pricepoints
        return pricepoints

    @staticmethod
    def prepare_data(pricepoint, one_click_enabled):
        test_data = {}
        merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
        db_agent.update_merchantbillconfig_oneclick(pricepoint, one_click_enabled)
        db_agent.update_pp_singleuse_promo(pricepoint, 1, config.single_use_promo)
        pricepoint_type = merchantbillconfig[0]['Type']
        package = db_agent.package(config.packageid)
        db_agent.update_processor(config.processors[0], config.packageid)
        db_agent.update_package(config.packageid, config.merchants[0], pricepoint)
        eticket = str(config.packageid) + ':' + str(pricepoint)
        url_options = options.ref_variables() + options.refurl() + config.template
        test_data['pricepoint_type'] = pricepoint_type
        test_data['package'] = package
        test_data['eticket'] = eticket
        test_data['url_options'] = url_options
        test_data['merchantbillconfig'] = merchantbillconfig
        return test_data



    @staticmethod
    def verify_signup_transaction(transaction_to_check):
        multitrans_base_record = mt.build_multitrans(config.test_data['merchantbillconfig'][0], config.test_data['package'][0], transaction_to_check, config.test_data['url_options'])
        asset_base_record = asset.build_asset_signup(config.test_data['merchantbillconfig'][0], multitrans_base_record, transaction_to_check)
        differences_multitrans = mt.multitrans_compare(multitrans_base_record, transaction_to_check['full_record'])
        differences_asset = asset.asset_compare(asset_base_record)
        differences_postback = postback_service.verify_postback_url("SignUp", config.packageid, transaction_to_check['TransID'])
        config.transids.append(transaction_to_check['TransID'])
        config.transaction_records.append(transaction_to_check)
        print('*********************SignUp Transaction Verification Complete*********************')
        print()
        if not differences_multitrans and not differences_asset and not differences_postback:
            return True
        else:
            return False


    @staticmethod
    def verify_signup_oc_transaction(oc_type, asset_base_record, one_click_pos_record):
        asset_base_record_onelick = asset.asset_oneclick(config.test_data['merchantbillconfig'][0], asset_base_record, one_click_pos_record[1])
        differences_oneclick_pos = mt.multitrans_compare(one_click_pos_record[0], one_click_pos_record[1])
        differences_asset = asset.asset_compare(asset_base_record_onelick)
        differences_postback = postback_service.verify_postback_url("SignUp", config.packageid, one_click_pos_record[1][0]['TransID'])
        config.transids.append(one_click_pos_record[1][0]['TransID'])
        print(('*********************OneClick {} Transaction Verification Complete*********************').format(oc_type.upper()))
        print()
        if not differences_oneclick_pos and not differences_asset and not differences_postback:
            return True
        else:
            return False




























    @staticmethod
    def get_multitrans_base_record(current_transaction_record):
        multitrans_base_record = mt.build_multitrans(config.test_data['merchantbillconfig'][0], config.test_data['package'][0], current_transaction_record, config.test_data['url_options'])
        return multitrans_base_record

    @staticmethod
    def get_asset_base_record_for_sign_up(multitrans_base_record, current_transaction_record):
        asset_base_record = asset.build_asset_signup(config.test_data['merchantbillconfig'][0], multitrans_base_record, current_transaction_record)
        return asset_base_record

    @staticmethod
    def get_asset_base_record_for_oc(asset_base_record, one_click_pos_record):
        asset_base_record = asset.asset_oneclick(config.test_data['merchantbillconfig'][0], asset_base_record, one_click_pos_record)
        return asset_base_record

    @staticmethod
    def close_browser():
        try:
            web.browser_quit()
            print("Webdriver closed")
        except Exception as ex:
            print(ex)
