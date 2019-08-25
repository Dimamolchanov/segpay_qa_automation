from datetime import datetime
from datetime import timedelta
from termcolor import colored
from pos.point_of_sale.bep import bep
from pos.point_of_sale.config import config
import copy
import traceback
import time
from pos.point_of_sale.utils import constants
from pos.point_of_sale.db_functions.dbactions import DBActions

db_agent = DBActions()


def build_asset_signup(multitrans_base_record, multitrans_live_record):
	type = config.test_data['Type']
	asset = {}
	live_record = multitrans_live_record['full_record']
	current_date = (datetime.now().date())
	try:
		asset = {'RecurringAmount': config.test_data['RebillPrice'],
		         'PurchType': config.test_data['Type'],
		         'PurchPeriod': config.test_data['RebillLen'],
		         'MerchantID': live_record['MerchantID'],
		         'URLID': live_record['URLID'],
		         'PackageID': live_record['PackageID'],
		         'BillConfigID': live_record['BillConfigID'],
		         'CardType': live_record['CardType'],
		         'InitialAmount': multitrans_base_record['TransAmount'],
		         'AuthCurrency': multitrans_base_record['MerchantCurrency'],
		         'PurchTotal': multitrans_base_record['TransAmount'],
		         'CustLang': multitrans_base_record['Language'],
		         'Currency': config.test_data['Currency'],
		         'PurchaseID': multitrans_base_record['PurchaseID'],
		         'Processor': multitrans_base_record['Processor'],
		         'CustEMail': multitrans_base_record['CustEMail'],
		         'RefURL': multitrans_base_record['RefURL'],
		         'CardExpiration': multitrans_base_record['CardExpiration'],
		         'CustCountry': multitrans_base_record['CustCountry'],
		         'CustZip': multitrans_base_record['CustZip'],
		         'PaymentAcct': multitrans_base_record['PaymentAcct'],
		         'PCID': multitrans_base_record['PCID'],
		         'ExchRate': multitrans_base_record['ExchRate'],
		         'REF1': multitrans_base_record['REF1'],
		         'REF2': multitrans_base_record['REF2'],
		         'REF3': multitrans_base_record['REF3'],
		         'REF4': multitrans_base_record['REF4'],
		         'REF5': multitrans_base_record['REF5'],
		         'REF6': multitrans_base_record['REF6'],
		         'REF7': multitrans_base_record['REF7'],
		         'REF8': multitrans_base_record['REF8'],
		         'REF9': multitrans_base_record['REF9'],
		         'REF10': multitrans_base_record['REF10']
		         }
		if type == 511:
			asset['RecurringAmount'] = multitrans_live_record['recurringprice511']
			asset['PurchPeriod'] = multitrans_live_record['recurringlength511']
		elif type == 505:
			asset['PurchTotal'] = 0.00
			asset['InitialAmount'] = 0.00
		purchtype_recurring = [501, 505, 506, 507, 511]
		if multitrans_base_record['Authorized'] == 1:
			transdate = (datetime.now().date())
			if type in (purchtype_recurring):
				asset['PurchStatus'] = 801
				asset['StatusDate'] = current_date
				asset['PurchDate'] = current_date
				if type == 511:
					asset['NextDate'] = current_date + timedelta(days=multitrans_live_record['initiallength511'])
					asset['ExpiredDate'] = current_date + timedelta(days=multitrans_live_record['initiallength511'])
				elif type == 505:
					asset['NextDate'] = current_date + timedelta(days=config.test_data['InitialLen']) + timedelta(days=config.test_data['RebillLen'])
				else:
					asset['NextDate'] = current_date + timedelta(days=config.test_data['InitialLen'])
					asset['ExpiredDate'] = current_date + timedelta(days=config.test_data['InitialLen'])

				asset['CancelDate'] = None
				asset['ConvDate'] = None
				asset['LastDate'] = None
			else:
				asset['PurchStatus'] = 804
				if type in [503, 510]:
					asset['StatusDate'] = current_date
					asset['PurchDate'] = current_date
					asset['NextDate'] = None
					asset['ExpiredDate'] = current_date
					asset['CancelDate'] = current_date
					asset['ConvDate'] = current_date
					asset['LastDate'] = current_date
				elif type == 502:
					asset['PurchDate'] = current_date
					asset['NextDate'] = None
					asset['ExpiredDate'] = current_date + timedelta(days=config.test_data['InitialLen'])
					asset['CancelDate'] = current_date
					asset['ConvDate'] = current_date
					asset['LastDate'] = current_date
			asset['LastResult'] = None
			asset['Purchases'] = 1

		else:
			asset['PurchStatus'] = 806
			asset['LastResult'] = 'Declined'
			asset['PurchTotal'] = 0
			asset['Purchases'] = 0
			asset['StatusDate'] = current_date
			asset['PurchDate'] = current_date
			asset['NextDate'] = None
			asset['ExpiredDate'] = current_date
			asset['CancelDate'] = current_date
			asset['ConvDate'] = current_date
			asset['LastDate'] = current_date
		if config.test_data['aprove_or_decline'] == False:
			asset['LastResult'] = 'Declined'
			#asset['MerchantCurrency'] = 'USD'
			asset['AuthCurrency'] = 'USD'
			asset['LastResult'] = 'Declined'



	except Exception as ex:
		traceback.print_exc()
		print(f"Exception {Exception} ")
		pass

	return asset


def build_asset_oneclick(merchantbillconfig, multitrans_base_record, multitrans_live_record, octoken_record):
	type = merchantbillconfig['Type']
	asset = {}
	current_date = (datetime.now().date())

	try:
		if type in (502, 503, 510):
			asset = octoken_record
			asset['PCID'] = None
		else:
			asset = {'RecurringAmount': merchantbillconfig['RebillPrice'],
			         'PurchType': merchantbillconfig['Type'],
			         'PurchPeriod': merchantbillconfig['RebillLen'],
			         'MerchantID': multitrans_base_record['MerchantID'],
			         'URLID': multitrans_base_record['URLID'],
			         'PackageID': multitrans_base_record['PackageID'],
			         'BillConfigID': multitrans_base_record['BillConfigID'],
			         'CardType': multitrans_live_record['CardType'],
			         'InitialAmount': multitrans_base_record['TransAmount'],
			         'AuthCurrency': multitrans_base_record['MerchantCurrency'],
			         'PurchTotal': multitrans_base_record['TransAmount'],
			         'CustLang': multitrans_base_record['Language'],
			         'Currency': multitrans_base_record['ProcessorCurrency'],
			         'PurchaseID': multitrans_base_record['PurchaseID'],
			         'Processor': multitrans_base_record['Processor'],
			         'CustEMail': multitrans_base_record['CustEMail'],
			         'RefURL': multitrans_base_record['RefURL'],
			         'CardExpiration': multitrans_base_record['CardExpiration'],
			         'CustCountry': multitrans_base_record['CustCountry'],
			         'CustZip': multitrans_base_record['CustZip'],
			         'PaymentAcct': multitrans_base_record['PaymentAcct'],
			         'PCID': multitrans_base_record['PCID'],
			         'ExchRate': multitrans_base_record['ExchRate'],
			         'REF1': multitrans_base_record['REF1'],
			         'REF2': multitrans_base_record['REF2'],
			         'REF3': multitrans_base_record['REF3'],
			         'REF4': multitrans_base_record['REF4'],
			         'REF5': multitrans_base_record['REF5'],
			         'REF6': multitrans_base_record['REF6'],
			         'REF7': multitrans_base_record['REF7'],
			         'REF8': multitrans_base_record['REF8'],
			         'REF9': multitrans_base_record['REF9'],
			         'REF10': multitrans_base_record['REF10']
			         }
			if type == 511:
				asset['InitialAmount'] = multitrans_live_record['511']['InitialPrice']
				asset['RecurringAmount'] = multitrans_live_record['511']['RecurringPrice']
				asset['PurchPeriod'] = multitrans_live_record['511']['RecurringLength']
			elif type == 510:
				asset['InitialAmount'] = multitrans_live_record['510']

			purchtype_recurring = [501, 506, 511]
			if multitrans_live_record['Authorized'] == 1:
				transdate = (datetime.now().date())
				if type in (purchtype_recurring):
					asset['PurchStatus'] = 801
					asset['StatusDate'] = current_date
					asset['PurchDate'] = current_date
					if type == 511:
						asset['NextDate'] = current_date + timedelta(days=multitrans_live_record['511']['InitialLength'])
						asset['ExpiredDate'] = current_date + timedelta(days=multitrans_live_record['511']['InitialLength'])
					else:
						asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen'])
						asset['ExpiredDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen'])
					asset['CancelDate'] = None
					asset['ConvDate'] = None
					asset['LastDate'] = None
				else:
					asset['PurchStatus'] = 804
					if type in [503, 510]:
						asset['StatusDate'] = current_date
						asset['PurchDate'] = current_date
						asset['NextDate'] = None
						asset['ExpiredDate'] = current_date
						asset['CancelDate'] = current_date
						asset['ConvDate'] = current_date
						asset['LastDate'] = current_date
					elif type == 502:
						asset['PurchDate'] = current_date
						asset['NextDate'] = None
						asset['ExpiredDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen'])
						asset['CancelDate'] = current_date
						asset['ConvDate'] = current_date
						asset['LastDate'] = current_date
				asset['LastResult'] = None
				asset['Purchases'] = 1
			else:
				asset['PurchStatus'] = 806
				asset['LastResult'] = 'Declined'
				asset['PurchTotal'] = 0
				asset['Purchases'] = 0
				asset['StatusDate'] = current_date
				asset['PurchDate'] = current_date
				asset['NextDate'] = None
				asset['ExpiredDate'] = current_date
				asset['CancelDate'] = current_date
				asset['ConvDate'] = current_date
				asset['LastDate'] = current_date

	except Exception as ex:
		traceback.print_exc()
		print(f"Exception {Exception} ")
		config.logging.info(f"Exception {Exception} ")
		pass
	return asset


def asset_oneclick(merchantbillconfig, asset_base_record, multitrans_live_record):
	type = merchantbillconfig['Type']
	live_record = multitrans_live_record[0]
	updated_record = copy.deepcopy((asset_base_record))
	current_date = (datetime.now().date())
	if type in [501, 505, 506, 511]:
		updated_record['PurchaseID'] = live_record['PurchaseID']

	return updated_record


def asset_instant_conversion(merchantbillconfig, asset_base_record, multitrans_live_record):
	type = merchantbillconfig['Type']
	current_date = (datetime.now().date())
	live_record = multitrans_live_record[0]
	updated_record = copy.deepcopy((asset_base_record))
	current_date = (datetime.now().date())
	updated_record['PurchType'] = 507
	updated_record['Purchases'] = 2
	updated_record['LastResult'] = 'OK:0'
	updated_record['PurchTotal'] = updated_record['PurchTotal'] + multitrans_live_record[0]['TransAmount']
	updated_record['ConvDate'] = current_date
	updated_record['LastDate'] = current_date
	updated_record['NextDate'] = current_date + timedelta(days=merchantbillconfig['RebillLen'])
	updated_record['ExpiredDate'] = current_date + timedelta(days=merchantbillconfig['RebillLen'])
	return updated_record


def asset_compare(asset_base_record):  # signup
	differences = {}
	purchaseid = asset_base_record['PurchaseID']
	asset_live_record = db_agent.asset_full_record(purchaseid)[0]
	asset_live_record['PCID'] = None

	differences = bep.dictionary_compare(asset_base_record, asset_live_record)

	if len(differences) == 0:
		print(colored(f"Asset      Record Compared =>  Pass  ", 'green'))
	else:
		print(colored(f"********************* Asset  MissMatch ****************", 'red'))
		for k, v in differences.items():
			print(k, v)

	return differences


def asseets_check_rebills(rebills):
	rkeys = rebills.keys()
	rebills_completed = []
	rebills_failed = []

	sql = "Select * from Assets where PurchaseID = {}"
	print("Checking asset after rebill")
	for pid in rkeys:
		differences = {}
		base_record = rebills[pid]
		base_record['Purchases'] = base_record['Purchases'] + 1
		base_record['PurchTotal'] = base_record['PurchTotal'] + base_record['RecurringAmount']
		base_record['ConvDate'] = (datetime.now().date())
		base_record['LastDate'] = (datetime.now().date())

		date_fromat = base_record['NextDate'] + timedelta(days=base_record['PurchPeriod'])
		base_record['NextDate'] = datetime.date(date_fromat)
		base_record['ExpiredDate'] = datetime.date(date_fromat)
		base_record['LastResult'] = 'OK:0'
		base_record['Retries'] = 0
		base_record['ModBy'] = 'Rebiller'

		live_record = db_agent.execute_select_one_parameter(sql, pid)
		# live_record['ConvDate'] = (datetime.now().date())
		# live_record['LastDate'] = (datetime.now().date())
		# tmp = live_record['NextDate']
		# live_record['NextDate'] =  datetime.date(tmp) # (datetime.now().date()) #datetime.date(date_fromat)
		# live_record['ExpiredDate'] = datetime.date(tmp)# datetime.date(date_fromat)

		differences = bep.dictionary_compare(base_record, live_record)

		if len(differences) == 0:
			rebills_completed.append(live_record)
		else:
			rebills_failed.append(live_record)
			print(colored(f"********************* Rebill Asset MissMatch Beginning****************", 'red'))
			print(f"PurchaseID = {pid}")
			for k, v in differences.items():
				print(k, v)
			print(colored(f"********************* Rebill Asset MissMatch End ****************", 'red'))

	if len(rebills_failed) == 0:
		print(colored(f"Rebills {len(rebills_completed)} records  => Assets Records Compared => Pass ", 'green'))
	else:
		print(colored(f"Rebills {len(rebills_completed)} records  => Assets Records Compared => Pass ", 'green'))
		print(colored(f"Warning ************* Rebills {len(rebills_failed)} records => Asset MissMatch => CHeck Manually ****************", 'blue'))

	return [rebills_completed, rebills_failed]


def asseets_check_refunds():
	refunds = config.refunds[0]
	rkeys = refunds.keys()
	rebills_completed = []
	rebills_failed = []
	sql = "Select * from Assets where PurchaseID = {}"
	for pid in rkeys:
		try:
			differences = {}
			base_record = refunds[pid]
			tasks_type = config.tasks_type[pid]   #refunds[pid]['tasktype']
			#del refunds[pid]['tasktype']
			if refunds[pid]['PurchType'] in [501, 505, 506, 511]:
				if tasks_type == 842 or tasks_type == 844:
					base_record['PurchStatus'] = 802
				else:
					base_record['PurchStatus'] = 803
					base_record['ExpiredDate'] = (datetime.now().date())
				base_record['ModBy'] = 'automation'
			else:
				base_record['PurchStatus'] = 804
				base_record['ModBy'] = 'SIGNUP'
			base_record['CancelDate'] = (datetime.now().date())
			live_record = db_agent.execute_select_one_parameter(sql, pid)
			differences = bep.dictionary_compare(base_record, live_record)
			if len(differences) == 0:
				rebills_completed.append(live_record)
			else:
				rebills_failed.append(live_record)
				print(colored(f"********************* Refunds Asset MissMatch Beginning****************", 'red'))
				print(f"PurchaseID = {pid}")
				for k, v in differences.items():
					print(k, v)
				print(colored(f"********************* Refunds Asset MissMatch End ****************", 'red'))
		except Exception as ex:
			traceback.print_exc()
			print(f"Exception {Exception} Module : assets.asseets_check_refunds(refunds) ")
			pass

	if len(rebills_failed) == 0:
		print(colored(f"Refunds    => Assets {len(rebills_completed)}     Records Compared => Pass ", 'green'))
	else:
		print(colored(f"Refunds {len(rebills_completed)} records  => Assets Records Compared => Pass ", 'green'))
		print(colored(f"Warning ************* Refunds {len(rebills_failed)} records => Asset MissMatch => CHeck Manually ****************", 'blue'))

	return [rebills_completed, rebills_failed]


def assets_check_reactivation():
	reactivated = config.asset_reactivated
	rkeys = reactivated.keys()
	reactivation_completed = []
	reactivation_completed_failed = []
	current_date = (datetime.now().date())
	sql = "Select * from Assets where PurchaseID = {}"
	for pid in rkeys:
		try:
			differences = {}
			time.sleep(1)
			live_record = db_agent.execute_select_one_parameter(sql, pid)
			base_record = reactivated[pid][pid]
			base_record['CustName'] = config.test_data['firstname'] + ' ' + config.test_data['lastname']
			base_record['PurchStatus'] = 801
			task_type = config.tasks_type[pid]
			if task_type == 841:
				base_record['ConvDate'] = current_date
				base_record['LastDate'] = current_date
				base_record['NextDate'] = current_date + timedelta(days=base_record['PurchPeriod'])
				base_record['ExpiredDate'] = current_date + timedelta(days=base_record['PurchPeriod'])
				base_record['Purchases'] = base_record['Purchases'] + 1

				base_record['PurchTotal'] = base_record['PurchTotal'] + base_record['RecurringAmount']

				base_record['CustZip'] = config.test_data['zip']
				card_encrypted = db_agent.encrypt_card(int(config.test_data['cc']))
				base_record['PaymentAcct'] = card_encrypted
				base_record['CardExpiration'] = config.test_data['month'] + config.test_data['year'][-2:]




			base_record['CancelDate'] = None
			base_record['Retries'] = 0
			base_record['LastResult'] = 'Reactivated'
			#base_record['CardExpiration'] = live_record['CardExpiration']
			if len(base_record['CardExpiration']) < 4:
				print("Check Card Expiration - assets | Something is wrong")
			differences = bep.dictionary_compare(base_record, live_record)
			if len(differences) == 0:
				reactivation_completed.append(live_record)
			else:
				reactivation_completed_failed.append(live_record)
				print(colored(f"********************* Reactivation Asset MissMatch Beginning****************", 'red'))
				print(f"PurchaseID = {pid}")
				for k, v in differences.items():
					print(k, v)
				print()
		except Exception as ex:
			print(f"{Exception}    PID: {pid} ")
			traceback.print_exc()
			pass

	if len(reactivation_completed_failed) == 0:
		print(colored(f"Reactivation {len(reactivation_completed)} records reactivated => Assets Records Compared => Pass ", 'green'))
	else:
		if len(reactivation_completed) > 0:
			print(colored(f"Reactivation {len(reactivation_completed)} records  => Assets Records Compared => Pass ", 'green'))
		print(colored(f"Warning ************* Reactivation {len(reactivation_completed_failed)} records => Asset MissMatch => Check Manually ****************", 'blue'))

	return [reactivation_completed, reactivation_completed_failed]

