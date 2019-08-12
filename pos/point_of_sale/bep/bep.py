import random
from datetime import datetime
from datetime import timedelta
import traceback

from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import web_service

db_agent = DBActions()

def get_data_before_action(tids, action):
	asset_before_action = {}
	pid = 0
	tid = 0
	sql = ''
	mt_before_action = {}
	rebill_dates = {}

	if action == 'rebill':
		try:
			for tid in tids:
				sql = "Select * from MultiTrans where TransID = {}"
				mt_tmp = db_agent.execute_select_one_parameter(sql, tid)
				pid = mt_tmp["PurchaseID"]
				sql = "Select * from Assets where PurchaseID = {}"
				tmp = db_agent.execute_select_one_parameter(sql, pid)

				if tmp['PurchType'] in [501, 506, 511]:
					mt_before_action[tid] = mt_tmp
					asset_before_action[pid] = tmp
					rebill_date = datetime.date(tmp['NextDate'])
					if rebill_date not in rebill_dates:
						rebill_dates[rebill_date] = 1
		except Exception as ex:
			print(f"{Exception}  Tid: {tid,}   PID: {pid}  SQL: {sql} ")
			traceback.print_exc()
			pass

		return asset_before_action, mt_before_action, rebill_dates
	elif action == 'refund' or action == 'reactivation':
		try:
			for tid in tids:
				sql = "Select * from MultiTrans where TransID = {}"
				mt_tmp = db_agent.execute_select_one_parameter(sql, tid)
				pid = mt_tmp["PurchaseID"]
				sql = "Select * from Assets where PurchaseID = {}"
				tmp = db_agent.execute_select_one_parameter(sql, pid)
				mt_before_action[tid] = mt_tmp
				if pid not in asset_before_action:
					asset_before_action[pid] = tmp

		except Exception as ex:
			print(f"{Exception}  Tid: {tid,}   PID: {pid}  SQL: {sql} ")
			traceback.print_exc()
			pass

		return asset_before_action, mt_before_action

def process_captures():
	current_date = (datetime.now().date())
	captures_url = config.captures_url + str(current_date)
	print()
	print("======================================| Starting  Captures |======================================")
	db_agent.fraud_scrub(current_date + timedelta(days=1))
	print(captures_url)
	response = web_service.process_request("Captures", captures_url, 200)
	print("End Captures")
	if response:
		return 'Captured'
	else:
		return 'Captures=>SomethingWrong'


def process_refund(transids, taskid=0):
	print()
	print("======================================| Starting   Refunds |======================================")
	tid = 0
	not_processed = [] ; tasks_type = {}
	refunds = get_data_before_action(transids, 'refund')
	tasks = []
	try:
		for tid in refunds[1]:

			if taskid == 0:
				tasktype = random.choice([841, 842, 843, 844])
			else:
				tasktype = taskid
			tasks.append(tasktype)
			refund_tasks = db_agent.refund_task(tasktype, tid)
			pid = refunds[1][tid]['PurchaseID']
			#refunds[0][pid]['tasktype'] = tasktype
			tasks_type[pid] = tasktype

		print(f"Tasks inserted : {tasks}")
		tmp = web_service.process_request("Refund", config.refund_url, 200)
		config.tasks_type = tasks_type
		return refunds[0], refunds[1], not_processed
	except Exception as ex:
		print(ex)
		traceback.print_exc()
		not_processed.append(tid)
		pass


def process_rebills(tids):
	resp = ''
	data_before_action = get_data_before_action(tids, 'rebill')
	rebill_dates = data_before_action[2]
	print()
	print("======================================| Starting   Rebills |======================================")
	for rebill_date in rebill_dates:
		rebill_url = config.rebill_url + str(rebill_date) + '%2023:59:59'
		print(rebill_url)
		resp = web_service.process_request("Rebill", rebill_url, 300)
	print("Rebills Completed")
	if resp:
		return data_before_action[0], data_before_action[1]
	else:
		return None


def dictionary_compare(base_record, live_record):
	differences = {} ; live_value = '' ; base_value = ''
	for key in base_record:
		try:

			if 'time'  in str(key).lower() or 'date'  in str(key).lower() :
				tmp_str = (str(base_record[key])).split(' ')
				base_value = tmp_str[0]
				tmp_str = (str(live_record[key])).split(' ')
				live_value = tmp_str[0]

				#print(f"{key} : Base: {base_value}  Live: {live_value}")
			else:
				live_value = live_record[key]
				base_value = base_record[key]



			if base_value != live_value:
				differences[key] = f"Base:{base_value} => Live:{live_value}"
		except Exception as ex:
			print(f"{Exception}  Key: {key,}")
			traceback.print_exc()
			pass

	return differences
