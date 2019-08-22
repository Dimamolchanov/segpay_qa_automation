import random
import string

from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.config import config
from pos.point_of_sale.utils import constants


db_agent = DBActions()

eu_countries = ['BE', 'BG', 'BL', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GF', 'GG', 'GI', 'GP', 'GR', 'HR', 'HU', 'IE', 'IM', 'IS', 'IT', 'JE', 'LI', 'LT', 'LU', 'LV', 'MF', 'MQ', 'MT']


def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def refurl():
    tmpurl = randomString(270)
    refurl = '&refurl=wwww.test.com/' + tmpurl
    return refurl


def ref_variables():
    refs = f"&ref1={randomString(5)}&ref2={randomString(4)}&ref3={randomString(5)}&ref4={randomString(4)}" \
           f"&ref5={randomString(5)}&ref6={randomString(4)}&ref7={randomString(5)}&ref8={randomString(4)}" \
           f"&ref9={randomString(5)}&ref10={randomString(4)}"
    return refs
    #
    # ref1 = randomString(4)
    # ref2 = randomString(4)
    # ref3 = randomString(5)
    # ref4 = randomString(6)
    # ref5 = randomString(4)
    # ref6 = randomString(4)
    # ref7 = randomString(4)
    # ref8 = randomString(2)
    # ref9 = randomString(11)
    # ref10 = randomString(8)
    # return ref1,ref4


def pricepoints_options(pricepoints_options,merchantid):
    pricepoints = []
    if pricepoints_options == 'single':
        pricepoints = [100120]
    elif pricepoints_options == 'type':
        pricepoints = db_agent.pricepoint_type(merchantid, [501, 502, 503, 504, 505, 506, 510, 511])
    elif pricepoints_options == 'list':
        pricepoints = db_agent.pricepoint_list(merchantid)
    return pricepoints


def string_after(value, a):
    # Find and validate first part.
    pos_a = value.rfind(a)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= len(value): return ""
    return value[adjusted_pos_a:]

def is_visa_secure():
    is_merchant_configured = db_agent.execute_select_two_parameters(constants.GET_DATA_FROM_3D_SECURE_CONFIG, config.merchants[0], config.packageid)
    is_eu_merchant = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MERCHANT_EXTENSION, config.merchants[0])['VISARegion']
    is_card_eu = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_GLOBALBINDETAILS,
                                                       str(config.test_data['cc'])[0:9])
    if is_card_eu:
        is_card_eu = is_card_eu['PrePaid'] == 'N' and is_card_eu['IssCountry'] in eu_countries
    if not is_merchant_configured or not is_card_eu:
        return 0
    elif is_merchant_configured and is_eu_merchant == 1 and is_card_eu:
        return 1
    elif is_merchant_configured and is_eu_merchant != 1:
        return 2




