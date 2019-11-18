from pos.point_of_sale.config import config
from pos.point_of_sale.utils import options
from pos.point_of_sale.web import web_module
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import psd2
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.verifications import postback_service
from pos.point_of_sale.verifications import emails
from termcolor import colored
import traceback
import random
import yaml

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
    def prepare_data1(pricepoint, packageid, one_click_enabled):
        try:
            #config.test_data['cnt'] = config.test_data['cnt'] + 1
            config.test_data= {}
            config.test_data = {**config.test_data, **config.initial_data}
            merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
            config.test_data = {**config.test_data,**merchantbillconfig}
            package = db_agent.package(packageid)
            config.test_data = {**config.test_data,**package}
            db_agent.update_merchantbillconfig_oneclick(pricepoint, one_click_enabled)
            db_agent.update_pp_singleuse_promo(pricepoint, 1, config.single_use_promo)
            eticket = str(packageid) + ':' + str(pricepoint)
            config.test_data['eticket'] = eticket
            url_options = options.ref_variables() + options.refurl() + config.template
            config.test_data['cc'] = random.choice(config.random_cards)
            config.test_data['visa_secure'] = options.is_visa_secure()
            if config.test_data['Merchant'] == 'EU':
                config.test_data['processor'] = config.test_data['eu_processors']
                db_agent.update_processor(config.test_data['eu_processors'], packageid)
            else:
                config.test_data['processor'] = config.test_data['us_processors']
                db_agent.update_processor(config.test_data['us_processors'], packageid)
            #print(yaml.dump(config.test_data))
        except Exception as ex:
            traceback.print_exc()
            print(f"Function: prepare_data1 \n {Exception} ")
            pass
        return config.test_data


    @staticmethod
    def prepare_data(pricepoint, one_click_enabled):
        merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
        db_agent.update_merchantbillconfig_oneclick(pricepoint, one_click_enabled)
        db_agent.update_pp_singleuse_promo(pricepoint, 1, config.single_use_promo)
        pricepoint_type = merchantbillconfig[0]['Type']
        merchant = config.test_data['merchant_us_or_eu']
        merchant_data = config.merchant_data[merchant]
        packageid = merchant_data[1]
        package = db_agent.package(packageid)
        config.packageid = packageid
        db_agent.update_processor(merchant_data[2], packageid)
        db_agent.update_package(packageid, config.test_data['merchantid'], pricepoint)
        eticket = str(packageid) + ':' + str(pricepoint)
        url_options = options.ref_variables() + options.refurl() + config.template
        config.test_data['pricepoint_type'] = pricepoint_type
        config.test_data['package'] = package
        config.test_data['eticket'] = eticket
        config.test_data['url_options'] = url_options
        config.test_data['merchantbillconfig'] = merchantbillconfig
        config.test_data['cc'] = random.choice(config.random_cards)
        config.test_data['processor'] = merchant_data[2]
        return config.test_data



    @staticmethod
    def verify_signup_transaction(transaction_to_check):
        save_case ={}
        multitrans_base_record = mt.build_multitrans()
        config.test_case['base_record'] = multitrans_base_record
        asset_base_record = asset.build_asset_signup(multitrans_base_record, transaction_to_check)
        differences_multitrans = mt.multitrans_compare(multitrans_base_record, transaction_to_check)
        differences_asset = asset.asset_compare(asset_base_record)
        if transaction_to_check['Authorized'] == 1:
            check_email = emails.check_email_que(config.test_data['Type'], multitrans_base_record, 'signup')
            config.test_data['aproved_transids'] = transaction_to_check['TransID']
        differences_postback = postback_service.verify_postback_url("SignUp", config.test_data['PackageID'], transaction_to_check['TransID'])
        differences_3ds = psd2.cardinal3dsrequests(transaction_to_check['TransID'])
        config.transids.append(transaction_to_check['TransID'])
        config.transaction_records.append(transaction_to_check)
        if not differences_multitrans and not differences_asset and not differences_postback : #and not differences_3ds:
            return True
        else:
            return False


    @staticmethod # Yan
    def verify_oc_transaction(octoken,eticket, one_click_record, selected_options): # Yan
        try:
            mt_octoken_mbconfig_record = mt.build_mt_oneclick(eticket, octoken, one_click_record, config.test_data['url_options'], selected_options)
            multitrans_base_oc_record = mt_octoken_mbconfig_record[0]
            differences_mt_oc = mt.multitrans_compare(multitrans_base_oc_record, one_click_record)
            asset_base_oc_record = asset.build_asset_oneclick(mt_octoken_mbconfig_record[2], multitrans_base_oc_record, one_click_record, mt_octoken_mbconfig_record[1])
            differences_asset_oc = asset.asset_compare(asset_base_oc_record)
            if one_click_record['Authorized'] == 1:
                check_email_oc = emails.check_email_que(mt_octoken_mbconfig_record[2]['Type'], one_click_record, 'signup')
            differences_postback = postback_service.verify_postback_url("SignUp", config.test_data['PackageID'], one_click_record['TransID'])
            card = db_agent.decrypt_string(one_click_record['PaymentAcct'])
            config.test_data['cc'] = card
            differences_3ds = psd2.cardinal3dsrequests(one_click_record['TransID'])
            config.transids.append(one_click_record['TransID'])
            if not differences_mt_oc and not differences_asset_oc and not differences_postback:
                return True
            else:
                return False
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}")

    @staticmethod  # Yan
    def verify_oc(one_click_record,action):  # Currently in use by Recurring
        #build_mt_oneclick(eticket, octoken, one_click_record, url_options, currency_lang):
        d = config.test_data
        try:
            mt_octoken_mbconfig_record = mt.build_mt_oneclick( one_click_record,action)
            multitrans_base_oc_record = mt_octoken_mbconfig_record[0]
            #return multitrans, octoken_record, d

            differences_mt_oc = mt.multitrans_compare(multitrans_base_oc_record, one_click_record)
            asset_base_oc_record = asset.build_asset_oneclick(mt_octoken_mbconfig_record[2], multitrans_base_oc_record, one_click_record, mt_octoken_mbconfig_record[1])
            differences_asset_oc = asset.asset_compare(asset_base_oc_record)
            if one_click_record['Authorized'] == 1:
                check_email_oc = emails.check_email_que(mt_octoken_mbconfig_record[2]['Type'], one_click_record, 'signup')
            differences_postback = postback_service.verify_postback_url("SignUp", config.test_data['PackageID'], one_click_record['TransID'])
            card = db_agent.decrypt_string(one_click_record['PaymentAcct'])
            config.test_data['cc'] = card
            # if action == 'pos':
            #     differences_3ds = psd2.cardinal3dsrequests(one_click_record['TransID'])
            config.transids.append(one_click_record['TransID'])
            print()

            if not differences_mt_oc and not differences_asset_oc and not differences_postback:
                #print(colored(f"Scenario completed: All Passed\n", 'green', attrs=['bold', 'underline', 'dark']))
                return True
            else:
                #print(colored(f"Scenario had some issues: Failed | Re-Check Manually |\n", 'red', attrs=['bold', 'underline', 'dark']))
                return False
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}")



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
            web_module.browser_quit()
            print("Webdriver closed")
        except Exception as ex:
            print(ex)
