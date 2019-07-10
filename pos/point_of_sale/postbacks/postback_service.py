from pos.point_of_sale.postbacks.dbactions import DBActions
from termcolor import colored

merchant_id = 20004
db_agent = DBActions()
errors_dictionary = {}

def find_post_backs_received(package_id, trans_id):
    postback_type_config = get_post_back_config_type(package_id)
    postback_type_notif = get_post_back_notif_type(trans_id)
    print(postback_type_config)
    print(postback_type_notif)
    result = []
    five_config = list(filter(lambda x: x == 5, postback_type_config))
    five_notif = list(filter(lambda x: x == 5, postback_type_notif))
    compare_results("Number of postbacks with type '5'", len(five_config), len(five_notif))
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
    print("Postbacks IDS are: {}".format(result))
    return result



def get_collect_user_info(package_id):
    get_collect_user_status = db_agent.get_collect_user_info_value(package_id)
    print("Collect user info code is: {}".format(get_collect_user_status))
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
        errors_dictionary[text] = "Expected: {}, ==> Actual: {}".format(expected, actual)
    else:
        print("Verification of '{}' passed -->OK".format(text))


def verify_postback_url(action, package_id, trans_id):
    get_collect_user_info_code = get_collect_user_info(package_id)
    matched_postback_types = find_post_backs_received(package_id, trans_id)
    print("Matched postback types are: {}".format(matched_postback_types))

    if action == "SignUp":
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
            else:
                expected_action = "auth"
            actual_postback_status = db_agent.get_postback_status_by_id(id)
            expected_postback_status = 863
            expected_trantype = "sale"
            expected_stage = "initial"
            expected_payment_account_id = db_agent.get_payment_acct_id(trans_id)

            compare_results("Postback Status", actual_postback_status, expected_postback_status)

            current_config_URL = db_agent.get_url_from_config(id)
            parsed_config_url = parse_post_back_url(current_config_URL)
            parsed_notif_url = parse_post_back_url(db_agent.get_url_from_notif(id, trans_id))
            if not parsed_config_url:
                print('Default postback config is used')
                compare_results("TranType", parsed_notif_url.get('trantype'), expected_trantype.lower())
                compare_results("Action", parsed_notif_url.get('action'), expected_action.lower())
                compare_results("Stage", parsed_notif_url.get('stage'), expected_stage.lower())
                if postback_type == 5:
                    compare_results("Payment Account ID", parsed_notif_url.get('paymentaccountid'), expected_payment_account_id)
            else:
                print('Parameterized postback config is used')
                #assert compares amount of parameters in config and notification and compares the result with amount of matched parameters
                #where len(parsed_config_url.keys() & parsed_notif_url.keys()) - number of mathced parameters in both URLs
                compare_results("Amount of parameters for non-default postback", len(parsed_config_url) == len(parsed_notif_url) == len(parsed_config_url.keys() & parsed_notif_url.keys()), True)
                for key, value in parsed_config_url.items():
                    temp = value[1:-1]
                    if temp == "trantype":
                        compare_results("TranType", parsed_notif_url.get(key), expected_trantype.lower())
                    if temp == "action":
                        compare_results("Action", parsed_notif_url.get(key), expected_action.lower())
                    if temp == "stage":
                        compare_results("Stage", parsed_notif_url.get(key), expected_stage.lower())
                    if temp == "paymentaccountid" and postback_type == 5:
                        compare_results("Payment Account ID", parsed_notif_url.get(key), expected_payment_account_id)

    if not errors_dictionary:
         print(colored(f"Postback Record Compared =>  Pass", 'green'))
    else:
         print(colored(f"********************* Postbacks MissMatch ****************", 'red'))
         for param, value in errors_dictionary.items():
             print(param, value)
    return errors_dictionary

















