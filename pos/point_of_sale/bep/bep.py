import time
import random
from datetime import datetime
from datetime import timedelta
import requests

from pos.point_of_sale import config
from pos.point_of_sale.web import web
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import web_service


db_agent = DBActions()


def process_captures():
	current_date = (datetime.now().date())
	captures_url = config.captures_url + str(current_date)
	print("Starting Captures")
	complete_scrub = db_agent.fraud_scrub(current_date + timedelta(days=1))
	print(captures_url)
	start_time = datetime.now()
	response = web_service.process_request("Captures", captures_url, 200)
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))
	print("End Captures")
	if response:
		return 'Captured'
	else:
		return 'Captures=>SomethingWrong'

	# try:
	#
	# 	captures = web.captures(current_date)
	# 	return 'Captured'
	# except Exception as ex:
	# 	print(ex)
	# 	return 'Captures => SomethingWrong'


def process_refund(transids, taskid=0):
	before_refunds = {}
	before_refunds_mt = {}
	try:
		for tid in transids:

			if taskid == 0:
				tasktype = random.choice([841, 842, 843, 844])
			else:
				tasktype = taskid
			print(tasktype)
			refund_tasks = db_agent.refund_task(tasktype, tid)
			sql = "Select * from multitrans where TransID = {}"
			temp = db_agent.execute_select_one_parameter(sql, tid)
			before_refunds_mt[tid] = temp
			pid = temp['PurchaseID']

			sql = "Select * from Assets where PurchaseID = {}"
			temp = db_agent.execute_select_one_parameter(sql, pid)
			before_refunds[pid] = temp

		refund = web.refund()
		return before_refunds_mt,before_refunds
	except Exception as ex:
		print(ex)
		return "Refunder=>SomethingWrong"


def process_rebills(pids):
	rebill_dates = {}
	before_rebill = {}
	before_rebill_mt = {}
	#REFACTOR
	for pid in pids:
		# sql = f"SELECT CONVERT(char(10), NextDate,126) as NextDate from Assets where PurchaseID = {pid}"
		sql1 = "Select * from Assets where PurchaseID = {}"
		temp = db_agent.execute_select_one_parameter(sql1, pid)
		# asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen']) + timedelta(days=merchantbillconfig['RebillLen'])
		before_rebill[pid] = temp
		temp = datetime.date(temp['NextDate'])
		if temp not in rebill_dates:
			rebill_dates[temp] = 1
        #REFACTOR - FOR SURE!
		sql2 = "Select * from multitrans where PurchaseID = {}"
		temp = db_agent.execute_select_one_parameter(sql2, pid)
		before_rebill_mt[pid] = temp
	print("Starting Rebill")
	start_time = datetime.now()
	for rebill_date in rebill_dates:
		rebill_url = config.rebill_url + str(rebill_date) + '%2023:59:59'
		print(rebill_url)
		# br.driver.set_page_load_timeout(600)
		resp = web_service.process_request("Rebill", rebill_url, 300)
		#web.br.visit(rebill_url)
		#while web.br.url != rebill_url:
		#	time.sleep(1)
		#time.sleep(1)
	print("Finished Rebill")
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))
	if resp:
		return before_rebill, before_rebill_mt  # ['RebillsFinished', before_rebill]
	else:
		return None
