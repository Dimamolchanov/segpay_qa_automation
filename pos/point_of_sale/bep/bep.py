import random
from datetime import datetime
from datetime import timedelta

from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import web_service


db_agent = DBActions()


def process_captures():
    current_date = (datetime.now().date())
    captures_url = config.captures_url + str(current_date)
    print("Starting Captures")
    db_agent.fraud_scrub(current_date + timedelta(days=1))
    print(captures_url)
    response = web_service.process_request("Captures", captures_url, 200)
    print("End Captures")
    if response:
        return 'Captured'
    else:
        return 'Captures=>SomethingWrong'


def process_refund(transids, taskid=0):
    before_refunds = {}
    before_refunds_mt = {}
    for tid in transids:
        if taskid == 0:
            tasktype = random.choice([841, 842, 843, 844])
        else:
            tasktype = taskid
        print(tasktype)
        db_agent.refund_task(tasktype, tid)
        sql = "Select * from multitrans where TransID = {}"
        temp = db_agent.execute_select_one_parameter(sql, tid)
        before_refunds_mt[tid] = temp
        pid = temp['PurchaseID']
        sql = "Select * from Assets where PurchaseID = {}"
        temp = db_agent.execute_select_one_parameter(sql, pid)
        before_refunds[pid] = temp
    print(config.refund_url)
    refund = web_service.process_request("Refund", config.refund_url, 200)
    if refund:
        return before_refunds_mt,before_refunds
    else:
        return "Refunder=>SomethingWrong"


def process_rebills(purchase_ids):
    rebill_dates = {}
    before_rebill = {}
    before_rebill_mt = {}
    #REFACTOR
    for purchase_id in purchase_ids:
        sql1 = "Select * from Assets where PurchaseID = {}"
        temp = db_agent.execute_select_one_parameter(sql1, purchase_id)
        before_rebill[purchase_id] = temp
        temp = datetime.date(temp['NextDate'])
        if temp not in rebill_dates:
            rebill_dates[temp] = 1
        #REFACTOR - FOR SURE!
        sql2 = "Select * from multitrans where PurchaseID = {}"
        temp = db_agent.execute_select_one_parameter(sql2, purchase_id)
        before_rebill_mt[purchase_id] = temp
    print("Starting Rebill")
    for rebill_date in rebill_dates:
        rebill_url = config.rebill_url.format(rebill_date)
        print(rebill_url)
        resp = web_service.process_request("Rebill", rebill_url, 300)
    print("Finished Rebill")
    if resp:
        return before_rebill, before_rebill_mt
    else:
        return None
