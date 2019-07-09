from pos.point_of_sale.web import web
from pos.point_of_sale.db_functions import dbs
import random
from pos.point_of_sale.verifications import mts as mt
import string


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
        pricepoints = dbs.pricepoint_type(merchantid, [501, 502, 503, 504, 505, 506, 510, 511])
    elif pricepoints_options == 'list':
        pricepoints = dbs.pricepoint_list(merchantid)
    return pricepoints

def string_after(value, a):
    # Find and validate first part.
    pos_a = value.rfind(a)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= len(value): return ""
    return value[adjusted_pos_a:]



