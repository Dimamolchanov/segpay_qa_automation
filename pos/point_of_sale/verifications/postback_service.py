from termcolor import colored
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import constants
from pos.point_of_sale.utils import options

db_agent = DBActions()
errors_dictionary = {}

def find_post_backs_received(package_id, trans_id):
    postback_type_config = get_post_back_config_type(package_id)
    if postback_type_config == None:
        print("Package does not have postback")
        return None
    postback_type_notif = get_post_back_notif_type(trans_id)
    if postback_type_notif == None:
        compare_results("Mathced postbacks in config and notif", postback_type_config, postback_type_notif)
        print("There is no records in POstBackNotification table")
        return None
    #print(postback_type_config)
    #print(postback_type_notif)
    result = []
    five_config = list(filter(lambda x: x == 5, postback_type_config))
    five_notif = list(filter(lambda x: x == 5, postback_type_notif))
    compare_results("Number of postbacks with type '5'",  len(five_notif), len(five_config))
    for element in postback_type_config:
        if element in postback_type_notif:
            result.append(element)
    return result

def find_post_backs_ids(package_id, trans_id):
    postback_id_config = get_post_back_config_id(package_id)
    postback_id_notif = get_post_back_notif_id(trans_id)
    result = []
    for element in postback_id_config:
        if element in postback_id_notif:
            result.append(element)
    #print("Postbacks IDS are: {}".format(result))
    return result



def get_collect_user_info(billconfigid):
    get_collect_user_status = db_agent.get_collect_user_info_value(billconfigid)
    #print("Collect user info code is: {}".format(get_collect_user_status))
    return get_collect_user_status


def parse_post_back_url(postback_url):
    if '?' not in postback_url:
        return None
    postback_url = postback_url.split('?')[1].split('&')
    params_map = {}
    for param in postback_url:
        temp = param.split('=')
        key = temp[0]
        value = temp[1]
        params_map[key.lower()] = value.lower()
    return params_map


def get_post_back_config_type(package_id):
    return db_agent.get_value_from_postback_configs(package_id, "PostbackType")


def get_post_back_notif_type(trans_id):
    return db_agent.get_value_from_postback_notif(trans_id, "PostbackType")


def get_post_back_config_id(package_id):
    return db_agent.get_value_from_postback_configs(package_id, "ID")


def get_post_back_notif_id(trans_id):
    return db_agent.get_value_from_postback_notif(trans_id, "PostbackConfigID")


def compare_results(text, actual, expected):
    #print("Verifying {}".format(text))
    if actual != expected:
        errors_dictionary[text] = ": Expected: {}, ==> Actual: {}".format(expected, actual)
    #else:
    #   print("Verification of '{}' passed -->OK".format(text))


def verify_postback_url(action, package_id, trans_id):
    id = 0 ;actual_postback_status = '' ; expected_postback_status = ''
    errors_dictionary.clear()
    get_collect_user_info_code = get_collect_user_info(config.test_data['BillConfigID'])
    matched_postback_types = find_post_backs_received(package_id, trans_id)
    if matched_postback_types == None:
        #print("NO postbacks in Notification table. Skipping further verification")
        return 0
    
    result = db_agent.get_trans_source(trans_id)
    is_service_transaction = result['Value'] != 'OC Web Service'
    
    trans_data = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MULTITRANS_BY_TRANS_ID, trans_id)
    is_trans_authorized = trans_data['Authorized']
    trans_type = trans_data['TransType']
    data_from_3d_request = db_agent.execute_select_one_parameter(constants.IS_3DSAUTHENTICATED, trans_data['TRANSGUID'])
    if not data_from_3d_request:
        scarequired = 'no'
        is3dsauthenticated = 'no'
    else:
        if data_from_3d_request['AuthResponseData']:
            scarequired = 'yes'
            request = db_agent.decrypt_string(data_from_3d_request['AuthResponseData'])
            if '"PAResStatus":"A"' in request or '"PAResStatus":"Y"' in request:
                is3dsauthenticated = 'yes'
            else:
                is3dsauthenticated = 'no'
        else:
            scarequired = 'no'
            is3dsauthenticated = 'no'


    if action == "SignUp":
        purchase_id = trans_data['PurchaseID']
        related_trans_data = db_agent.execute_select_one_parameter(
            constants.GET_DATA_FROM_MULTITRANS_BY_RELATED_TRANS_ID, trans_id)
        if is_service_transaction and is_trans_authorized:
            if get_collect_user_info_code == 0:
                compare_results("Collect user info", (1 not in matched_postback_types and 2 not in matched_postback_types), True)
            elif get_collect_user_info_code == 1:
                compare_results("Collect user info", (1 in matched_postback_types and 2 in matched_postback_types), True)
            elif get_collect_user_info_code == 2:
                compare_results("Collect user info", (1 not in matched_postback_types and 2 in matched_postback_types), True)

        matched_postback_ids = find_post_backs_ids(package_id, trans_id)
        for id in matched_postback_ids:

            postback_type = db_agent.get_postback_type_by_postback_id(id)
            if postback_type == 1:
                expected_action = "Probe"
            elif postback_type == 2:
                expected_action = "Enable"
            elif postback_type == 5:
                expected_action = "auth"
            actual_postback_status = db_agent.get_postback_status_by_id(id, trans_id)
            expected_postback_status = 863
            expected_trantype = "sale"
            if  trans_type == 108:
                expected_stage = "instantconversion"
            elif trans_type == 1011:
                related_purchase_id = related_trans_data['PurchaseID']
                if purchase_id == related_purchase_id:
                    expected_stage = 'rebill'
                else:
                    expected_stage = 'initial'
            else:
                expected_stage = "initial"
            if trans_data['TransSource'] == 122:
                expected_stage = 'conversion'
            expected_payment_account_id = db_agent.get_payment_acct_id(trans_id)
            if expected_payment_account_id == None:
                expected_payment_account_id = "Wrong => Check MT values"



    elif action == "refund":

        data_from_multitrans = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MULTITRANS_BY_TRANS_ID, trans_id)

        initial_trans_id = data_from_multitrans['RelatedTransID']

        refund_type = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_TASKS, trans_id)

        if refund_type == 841:

            compare_results("Collect user info", (3 in matched_postback_types and 4 in matched_postback_types), True)

        elif refund_type == 842:

            compare_results("Collect user info", (3 not in matched_postback_types and 4 in matched_postback_types), True)

        elif refund_type == 843:

            compare_results("Collect user info", (3 not in matched_postback_types and 4 not in matched_postback_types), True)

        matched_postback_ids = find_post_backs_ids(package_id, trans_id)

        for id in matched_postback_ids:

            initial_parsed_notif_url = parse_post_back_url(db_agent.get_url_from_notif(id, initial_trans_id))

            parsed_notif_url = parse_post_back_url(db_agent.get_url_from_notif(id, trans_id))

            postback_type = db_agent.get_postback_type_by_postback_id(id)

            if postback_type == 5:
                compare_results("Check scarequired", parsed_notif_url.get('scarequired'), initial_parsed_notif_url.get('scarequired'))

                compare_results("Check is3dsauthenticated", parsed_notif_url.get('is3dsauthenticated'), initial_parsed_notif_url.get('is3dsauthenticated'))

            if postback_type == 3:

                expected_action = "Disable"

            elif postback_type == 4:

                expected_action = "Cancel"

            elif postback_type == 5:

                if trans_type == 102:

                    expected_action = "auth"

                elif trans_type == 107:

                    expected_action = "void"

                else:

                    print("Trans type {} is no allowed for REFUND".format(trans_type))

            actual_postback_status = db_agent.get_postback_status_by_id(id, trans_id)

            expected_postback_status = 863

            if trans_type == 102:

                expected_trantype = "credit"

            elif trans_type == 107:

                expected_trantype = "sale"

            else:

                print("Trans type {} is no allowed for REFUND".format(trans_type))

            expected_stage = "initial"

            expected_payment_account_id = db_agent.get_payment_acct_id(trans_id)

            if expected_payment_account_id == None:
                expected_payment_account_id = "Wrong => Check MT values"

    elif action == "rebill":
       matched_postback_ids = find_post_backs_ids(package_id, trans_id)
       is_first_rebill = (db_agent.execute_select_one_parameter(constants.GET_COUNT_OF_REBILLS_FROM_MULTITRANS, trans_id) == 1)
       for id in matched_postback_ids:
            postback_type = db_agent.get_postback_type_by_postback_id(id)
            expected_action = "auth"
            actual_postback_status = db_agent.get_postback_status_by_id(id, trans_id)
            expected_postback_status = 863
            expected_trantype = "sale"
            if is_first_rebill:
                expected_stage = "conversion"
            else:
                expected_stage = "rebill"
            expected_payment_account_id = db_agent.get_payment_acct_id(trans_id)
            if expected_payment_account_id == None:
                expected_payment_account_id = "Wrong => Check MT values"

    elif action == "reactivation":
       compare_results("Collect user info", (3 in matched_postback_types and 7 in matched_postback_types), True)
       matched_postback_ids = find_post_backs_ids(package_id, trans_id)
       for id in matched_postback_ids:
            postback_type = db_agent.get_postback_type_by_postback_id(id)
            expected_action = "auth"
            actual_postback_status = db_agent.get_postback_status_by_id(id, trans_id)
            expected_postback_status = 863
            expected_trantype = "sale"
            expected_stage = "reactivation"
            expected_payment_account_id = db_agent.get_payment_acct_id(trans_id)
            if expected_payment_account_id == None:
                expected_payment_account_id = "Wrong => Check MT values"

    compare_results("Postback Status for {}".format(id), actual_postback_status, expected_postback_status)

    current_config_URL = db_agent.get_url_from_config(id)
    parsed_config_url = parse_post_back_url(current_config_URL)
    parsed_notif_url = parse_post_back_url(db_agent.get_url_from_notif(id, trans_id))
    #print('----------------------------------------------------------------------------')  # Printg of postbcack params
    #print(parsed_notif_url)
    config.logging.info('')
    config.logging.info(parsed_notif_url)
    config.logging.info('')
   # print('----------------------------------------------------------------------------')
    if not parsed_config_url:
        #print('Default postback config is used')
        compare_results("TranType {}".format(id), parsed_notif_url.get('trantype'), expected_trantype.lower())
        compare_results("Action {}".format(id), parsed_notif_url.get('action'), expected_action.lower())
        compare_results("Stage {}".format(id), parsed_notif_url.get('stage'), expected_stage.lower())
        if postback_type == 5:
            compare_results("Check scarequired", parsed_notif_url.get('scarequired'), scarequired)
            compare_results("Check is3dsauthenticated", parsed_notif_url.get('is3dsauthenticated'), is3dsauthenticated)
            compare_results("Payment Account ID {}".format(id), parsed_notif_url.get('paymentaccountid'), expected_payment_account_id)
    else:
        add_to_number = 3 if postback_type == 5 else 0
        compare_results("Number of parameters for non-default postback {}".format(id), len(parsed_config_url)+add_to_number, len(parsed_notif_url))
        compare_results("Parameters keys for non-default postback {}".format(id), len(parsed_config_url), len(parsed_config_url.keys() & parsed_notif_url.keys()))
        if postback_type ==5:
            compare_results("Check is3dsauthenticated", parsed_notif_url.get('is3dsauthenticated'), is3dsauthenticated)
            compare_results("Check scarequired", parsed_notif_url.get('scarequired'), scarequired)
        for key, value in parsed_config_url.items():
            temp = value[1:-1]
            if temp == "trantype":
                compare_results("TranType {}".format(id), parsed_notif_url.get(key), expected_trantype.lower())
            if temp == "action":
                compare_results("Action {}".format(id), parsed_notif_url.get(key), expected_action.lower())
            if temp == "stage":
                compare_results("Stage {}".format(id), parsed_notif_url.get(key), expected_stage.lower())
            if temp == "paymentaccountid" and postback_type == 5:

                compare_results("Payment Account ID {}".format(id), parsed_notif_url.get(key), expected_payment_account_id)


    if not errors_dictionary:
        options.append_list(f"Postback Record Compared =>  Passed for collect user info: '{get_collect_user_info_code}' and postback types: {matched_postback_types}")
        print(colored(f"Postback Record Compared =>  Passed for collect user info: '{get_collect_user_info_code}' and postback types: {matched_postback_types}", 'green'))
    else:
         print(colored(f"********************* Postbacks MissMatch ****************", 'red'))
         options.append_list("********************* Postbacks MissMatch ****************")
         for param, value in errors_dictionary.items():
             tmp = param + " " + value
             options.append_list(tmp)
             print(param, value)

    return errors_dictionary

















