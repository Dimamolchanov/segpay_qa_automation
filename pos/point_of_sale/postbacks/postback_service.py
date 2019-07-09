from pos.point_of_sale.postbacks.dbactions import DBActions

merchant_id = 20004
#package_id = 270109
#trans_id = 1534615290
db_agent = DBActions()


def find_post_backs_received(package_id, trans_id):
    postback_type_config = get_post_back_config_type(package_id)
    postback_type_notif = get_post_back_notif_type(trans_id)
    result = []
    five_config = list(filter(lambda x: x == 5, postback_type_config))
    five_notif = list(filter(lambda x: x == 5, postback_type_notif))
    if len(five_config) != len(five_notif):
        raise Exception("Lists are not equal!!")
    for element in postback_type_config:
        if element in postback_type_notif:
            result.append(element)
    print("Postbacks are: {}".format(result))
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


def verify_postback_url(action, package_id, trans_id):
    get_collect_user_info_code = get_collect_user_info(package_id)
    matched_postback_types = find_post_backs_received(package_id, trans_id)
    print("Matched postback types are: {}".format(matched_postback_types))
    if action == "SignUp":
        if get_collect_user_info_code == 0:
            assert 1 not in matched_postback_types and 2 not in matched_postback_types, "Incorrect types 1 and 2 in the list"
            print('Collect user info postbacks types are correct')
        elif get_collect_user_info_code == 1:
            assert 1 in matched_postback_types and 2 in matched_postback_types, "Incorrect types 1 and 2 in the list"
            print('Collect user info postbacks types are correct')
        elif get_collect_user_info_code == 2:
            assert 1 not in matched_postback_types and 2 in matched_postback_types, "Incorrect types 1 and 2 in the list"
            print('Collect user info postbacks types are correct')
        matched_postback_ids = find_post_backs_ids(package_id, trans_id)
        for id in matched_postback_ids:
            postback_type = db_agent.get_postback_type_by_postback_id(id)
            if postback_type == 1:
                expected_action = "Probe"
            elif postback_type == 2:
                expected_action = "Enable"
            else:
                expected_action = "auth"
            postback_status = db_agent.get_postback_status_by_id(id)
            assert postback_status == 864, "Postback status is incorrect: '863' expected but found - {}".format(postback_status)
            current_config_URL = db_agent.get_url_from_config(id)
            if not parse_post_back_url(current_config_URL):
                print('Default postback config is used')
                notif_param_map = parse_post_back_url(db_agent.get_url_from_notif(id, trans_id))
                assert notif_param_map.get('trantype') == "sale", "TranType is incorret: value: {}".format(notif_param_map.get('trantype'))
                print("Trantype is corret: {}".format(notif_param_map.get('trantype')))
                assert notif_param_map.get('action') == expected_action.lower(), "Action is incorret"
                print("Action is corret: {}".format(notif_param_map.get('action')))
                assert notif_param_map.get('stage') == "initial", "Stage is incorret"
                print("Stage is corret: {}".format(notif_param_map.get('stage')))
                if postback_type == 5:
                    expected_payment_account_id = db_agent.get_payment_acct_id(trans_id)
                    assert notif_param_map.get('paymentaccountid') == expected_payment_account_id, "Payment is incorret: expected payment: {}, but found: {}".format(expected_payment_account_id, notif_param_map.get('paymentaccountid'))
                    print("Payment is corret: {}".format(notif_param_map.get('paymentaccountid')))

















