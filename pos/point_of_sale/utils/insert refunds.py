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
from pos.point_of_sale.web import web_module
from pos.point_of_sale.utils import options
import yaml

db_agent = DBActions()

# sql = "select TransID from multitrans where TransTime > '2019-10-19 18:55:44.000' and TransTime < '2019-10-21 23:55:44.000'   and Transtype in ( 101,1011) and Authorized = 1"
# total_records = db_agent.sql(sql)
# tids = total_records['transid']

total_records = [223773089]


for tid in total_records:
    refund_tasks = db_agent.refund_task(844, tid)
    #refund_tasks = db_agent.refund_task(841, tid['TransID'])


    print(tid) #tid['transid']

lal = 3
