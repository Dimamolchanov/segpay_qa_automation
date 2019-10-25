import traceback
from datetime import datetime
from functools import partial
from pos.point_of_sale.bep import bep
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.runners import test_methods
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web
from pos.point_of_sale.utils import options
import yaml

db_agent = DBActions()

# sql = "select TransID from multitrans where TransTime > '2019-10-19 18:55:44.000' and TransTime < '2019-10-21 23:55:44.000'   and Transtype in ( 101,1011) and Authorized = 1"
# total_records = db_agent.sql(sql)
# tids = total_records['transid']

total_records = [1000078274,
1000078342,
1000078341,
1000078225,
1000078224,
1000078353,
1000078352,
1000078351,
1000078350,
1000078349,
1000078348,
1000078347,
1000078346,
1000078345,
1000078344,
1000078343]


for tid in total_records:
    refund_tasks = db_agent.refund_task(841, tid)
    #refund_tasks = db_agent.refund_task(841, tid['TransID'])


    print(tid) #tid['transid']

lal = 3
