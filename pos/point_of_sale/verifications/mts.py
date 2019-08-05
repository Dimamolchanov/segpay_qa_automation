from datetime import datetime
from datetime import timedelta
from termcolor import colored
from decimal import Decimal
import traceback
from pos.point_of_sale.bep import bep
from pos.point_of_sale.db_functions.dbactions import DBActions

db_agent = DBActions()


def build_mt_oneclick(eticket, octoken, one_click_record,url_options,currency_lang):
	transdate = (datetime.now().date())
	ppid = eticket.split(':') ; multitrans_oneclick_record = {}
	sql = "select * from MerchantBillConfig where BillConfigID = {}"
	merchantbillconfig =  db_agent.execute_select_one_parameter(sql, ppid[1])
	pp_type = merchantbillconfig['Type']
	sql = "select * from assets where PurchaseID = {}"
	octoken_record = db_agent.execute_select_one_parameter(sql, octoken)
	try:
		multitrans = {
			'PurchaseID': one_click_record['PurchaseID'],
			'TransID': one_click_record['TransID'],
			'TRANSGUID': one_click_record['TRANSGUID'],
			'BillConfigID': int(ppid[1]),
			'PackageID': octoken_record['PackageID'],
			'AuthCode': 'OK:0',
			'Authorized': 1,
			'CardExpiration': octoken_record['CardExpiration'],
			'CustCountry': octoken_record['CustCountry'],
			'CustEMail': octoken_record['CustEMail'],
			'CustName': octoken_record['CustName'] ,
			'CustZip': octoken_record['CustZip'],
			'Language': currency_lang[1],
			'MerchantID': one_click_record['MerchantID'],
			'PaymentAcct': octoken_record['PaymentAcct'],
			'PCID': None,
			'Processor': octoken_record['Processor'],
			'ProcessorCurrency': octoken_record['Currency'],
			'MerchantCurrency': currency_lang[0],
			'STANDIN': one_click_record['STANDIN'],
			'TransBin': one_click_record['TransBin'],
			'URLID': octoken_record['URLID'],
			'URL': one_click_record['URL'],
			'REF1': None,
			'REF2': None,
			'REF3': None,
			'REF4': None,
			'REF5': None,
			'REF6': None,
			'REF7': None,
			'REF8': None,
			'REF9': None,
			'REF10': None,
			'RefURL': one_click_record['RefURL']
		}  #
		url_parameters = url_options.split('&')
		for var in url_parameters:
			tmp = var.split('=')
			if tmp[0] == 'ref1':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF1'] = val
			elif tmp[0] == 'ref2':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF2'] = val = val
			elif tmp[0] == 'ref3':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF3'] = val
			elif tmp[0] == 'ref4':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF4'] = val
			elif tmp[0] == 'ref5':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF5'] = val
			elif tmp[0] == 'ref6':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF6'] = val
			elif tmp[0] == 'ref7':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF7'] = val
			elif tmp[0] == 'ref8':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF8'] = val
			elif tmp[0] == 'ref9':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF9'] = val
			elif tmp[0] == 'ref10':
				val = db_agent.encrypt_string(tmp[1])
				multitrans['REF10'] = val
			elif tmp[0] == 'refurl':
				val = tmp[1][:256]
				multitrans['RefURL'] = val  # update refs  #
		multitrans['PaymentType'] = 131
		exchange_rate = 1
		if merchantbillconfig['Currency'] == currency_lang[0]:
			exchange_rate = 1
		else:
			exchange_rate = db_agent.exc_rate(currency_lang[0], merchantbillconfig['Currency'])

		multitrans['TxStatus'] = 2
		if pp_type in (502,503,510):
			multitrans['TransSource'] = 123
		else:
			multitrans['TransSource'] = 121


		multitrans['TransStatus'] = 186
		multitrans['TransType'] = 1011

		if pp_type == 511:
			trans_amount = one_click_record['511']['InitialPrice']
			multitrans['TransAmount'] = trans_amount
			multitrans['Markup'] = round(trans_amount * exchange_rate, 2)
		elif merchantbillconfig['Type'] == 510:
			trans_amount = one_click_record['510']
			multitrans['TransAmount'] = trans_amount
			multitrans['Markup'] = round(trans_amount * exchange_rate, 2)
		else:
			initial_price = merchantbillconfig['InitialPrice']
			multitrans['TransAmount'] = initial_price
			multitrans['Markup']= round(initial_price * exchange_rate, 2)
			#multitrans['RelatedTransID'] = 0
			multitrans['TransDate'] = transdate

		if merchantbillconfig['Type'] in [501, 506] and merchantbillconfig['InitialPrice'] == 0.00:
			multitrans['TransAmount'] = 1.00
		elif merchantbillconfig['Type'] == 511 and one_click_record['511']['InitialPrice'] == 0.00:
			multitrans['TransAmount'] = 1.00


		exchange_rate = round(exchange_rate, 2)
		multitrans['ExchRate'] = exchange_rate
		one_click_record['PCID'] = None
		return multitrans , octoken_record,merchantbillconfig




	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}  Eticket: {eticket,}  ")
		pass

def build_multitrans(merchantbillconfig, package, data_from_paypage, url_options):
	transdate = (datetime.now().date())
	url = db_agent.url(package['URLID'])

	multitrans = {
		'PurchaseID': data_from_paypage['PurchaseID'],
		'TransID': data_from_paypage['TransID'],
		'TRANSGUID': data_from_paypage['transguid'],
		'BillConfigID': merchantbillconfig['BillConfigID'],
		'PackageID': package['PackageID'],
		'AuthCode': 'OK:0',
		'Authorized': 1,
		'CardExpiration': data_from_paypage['expiration_date'] + data_from_paypage['year'][-2:],
		'CustCountry': data_from_paypage['merchant_country'],
		'CustEMail': data_from_paypage['email_encrypt'],
		'CustName': data_from_paypage['firstname'] + ' ' + data_from_paypage['lastname'],
		'CustZip': data_from_paypage['zip'],
		'Language': data_from_paypage['paypage_lnaguage'],
		'MerchantID': merchantbillconfig['MerchantID'],
		'PaymentAcct': data_from_paypage['card_encrypted'],
		'PCID': None,
		'Processor': data_from_paypage['processor'],
		'ProcessorCurrency': merchantbillconfig['Currency'],
		'MerchantCurrency': data_from_paypage['merchant_currency'],
		'STANDIN': package['AllowStandin'],
		'TransBin': data_from_paypage['transbin'],
		'URLID': package['URLID'],
		'URL': url,
		'REF1': None,
		'REF2': None,
		'REF3': None,
		'REF4': None,
		'REF5': None,
		'REF6': None,
		'REF7': None,
		'REF8': None,
		'REF9': None,
		'REF10': None,
		'RefURL': None
	}  # dictionary from paypage

	# analyzing url
	url_parameters = url_options.split('&')
	for var in url_parameters:
		tmp = var.split('=')
		if tmp[0] == 'ref1':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF1'] = val
		elif tmp[0] == 'ref2':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF2'] = val = val
		elif tmp[0] == 'ref3':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF3'] = val
		elif tmp[0] == 'ref4':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF4'] = val
		elif tmp[0] == 'ref5':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF5'] = val
		elif tmp[0] == 'ref6':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF6'] = val
		elif tmp[0] == 'ref7':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF7'] = val
		elif tmp[0] == 'ref8':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF8'] = val
		elif tmp[0] == 'ref9':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF9'] = val
		elif tmp[0] == 'ref10':
			val = db_agent.encrypt_string(tmp[1])
			multitrans['REF10'] = val
		elif tmp[0] == 'refurl':
			val = tmp[1][:256]
			multitrans['RefURL'] = val  # update refs  #

	multitrans['PaymentType'] = 131
	exchange_rate = 1
	if merchantbillconfig['Currency'] == data_from_paypage['merchant_currency']:
		exchange_rate = 1
	else:
		exchange_rate = db_agent.exc_rate(data_from_paypage['merchant_currency'], merchantbillconfig['Currency'])

	multitrans['TxStatus'] = 2
	if merchantbillconfig['Type'] == 505:
		multitrans['TransSource'] = 122
		multitrans['TransStatus'] = 184
		multitrans['TransType'] = 105
	else:
		multitrans['TransSource'] = 121
		multitrans['TransStatus'] = 184
		multitrans['TransType'] = 101

	if merchantbillconfig['Type'] == 511:
		multitrans['TransAmount'] = data_from_paypage['initialprice511']
		multitrans['Markup'] = round(data_from_paypage['initialprice511'] * exchange_rate, 2)
	elif merchantbillconfig['Type'] == 510:
		multitrans['TransAmount'] = data_from_paypage['initialprice510']
	else:
		if merchantbillconfig['Type'] == 505 and data_from_paypage['full_record'][0]['TransSource'] == 122:
			multitrans['TransAmount'] = merchantbillconfig['RebillPrice']
			multitrans['TransDate'] = transdate + timedelta(days=merchantbillconfig['InitialLen'])
			sql = f"select  RelatedTransID  from multitrans where PurchaseID = {data_from_paypage['PurchaseID']}  and TransSource = 121 "
			multitrans['RelatedTransID'] = db_agent.sql(sql)[0]['RelatedTransID']
		else:
			multitrans['TransDate'] = transdate
			multitrans['TransAmount'] = merchantbillconfig['InitialPrice']
			multitrans['Markup']= round(merchantbillconfig['InitialPrice'] * exchange_rate, 2)
			multitrans['RelatedTransID'] = 0

	if merchantbillconfig['Type'] in [501, 506] and merchantbillconfig['InitialPrice'] == 0.00:
		multitrans['TransStatus'] = 186
		multitrans['TransAmount'] = 1.00
	exchange_rate = round(exchange_rate, 2)
	multitrans['ExchRate'] = exchange_rate
	return multitrans


def multitrans_compare(multitrans_base_record, live_record):
	differences = {}
	try:
		multitrans_live_record = live_record #[0]
		live_record['PCID'] = None
		multitrans_live_record['TransDate'] =   multitrans_live_record['TransDate'].date()

		differences = bep.dictionary_compare(multitrans_base_record, multitrans_live_record)

		if len(differences) == 0:
			#print(f"PurchaseID:{multitrans_base_record['PurchaseID']} | TransId:{multitrans_base_record['TransID']} |"
			      #f" TransGuid: {multitrans_base_record['TRANSGUID']}")
			print(colored(f"Mulitrans  Record Compared =>  Pass", 'green'))
		else:
			print(f"PurchaseID:{multitrans_base_record['PurchaseID']} | TransId:{multitrans_base_record['TransID']} |"
			      f" TransGuid: {multitrans_base_record['TRANSGUID']}")
			print(colored(f"********************* Multitrans MissMatch ****************", 'red'))
			for k, v in differences.items():
				print(k, v)
	except Exception as ex:
		traceback.print_exc()
		print(f"Exception {Exception} ")
		pass
	return differences

def multitrans_check_conversion(rebills):
	rkeys = rebills.keys()
	rebills_completed_mt = []
	rebills_failed_mt = []
	try:
		for tid in rkeys:
			differences = {}
			pid = rebills[tid]['PurchaseID']
			base_record = rebills[tid]
			base_record['TxStatus'] = 6
			base_record['TransStatus'] = 186
			base_record['TransSource'] = 122
			sql = "Select RecurringAmount from Assets where PurchaseID = {}"
			rebill_amount = db_agent.execute_select_one_parameter(sql, pid)
			base_record['TransAmount'] = rebill_amount['RecurringAmount']
			base_record['ProcessorTransID'] = ''
			base_record['TransID'] = 0
			base_record['SOURCEMACHINE'] = ''
			base_record['TransDate'] = datetime.date(base_record['TransDate'])
			base_record['TransTime'] = datetime.date(base_record['TransTime'])
			base_record['PCID'] = None
			base_record['TRANSGUID'] = ''
			base_record['IPCountry'] = 'N/A'
			base_record['BinCountry'] = 'N/A'
			base_record['AffiliateID'] = None
			base_record['RefURL'] = None

			sql = "select TOP 1 Rate from ExchangeRates as rate where ConsumerIso = '{}' " \
				"and   MerchantIso = '{}' order by importdatetime desc"

			exchange_rate = db_agent.execute_select_two_parameters(sql, base_record['MerchantCurrency'], base_record['ProcessorCurrency'])

			if base_record['MerchantCurrency'] == 'JPY':
				excr = round((base_record['TransAmount'] * exchange_rate['Rate']), 2)
				excr = round((excr))
				excr = str(excr) + '.00'
				excr = Decimal(excr)
				base_record['Markup'] = excr
			else:
				base_record['Markup'] = round((base_record['TransAmount'] * exchange_rate['Rate']), 2)

			sql = "Select * from multitrans where PurchaseID = {} and TransSource = 122"
			live_record = db_agent.execute_select_one_parameter(sql, pid)

			if base_record['TransType'] == 1011:
				base_record['TransType'] = 101
				base_record['RelatedTransID'] = 0

			live_record['ProcessorTransID'] = ''
			tid = live_record['TransID']
			live_record['TransID'] = 0
			live_record['SOURCEMACHINE'] = ''
			live_record['TransDate'] = datetime.date(live_record['TransDate'])
			live_record['TransTime'] = datetime.date(live_record['TransTime'])
			live_record['TRANSGUID'] = ''
			live_record['RefURL'] = None

			differences = bep.dictionary_compare(base_record, live_record)
			if len(differences) == 0:
				rebills_completed_mt.append(live_record)
			else:
				rebills_failed_mt.append(live_record)
				print(colored(f"********************* Conversion Multitrans MissMatch Beginning**************** | PurchaseID = {pid} | TransID: {tid}", 'red'))
				print()
				for k, v in differences.items():
					print(k, v)
				print()
				print(colored(f"********************* Conversion Multitrans MissMatch End ****************", 'red'))


	except Exception as ex:
		traceback.print_exc()
		#(f"{Exception}  Tid: {tid,}   Task: {tasks_type_status[0]} , {tasks_type_status[1]}  SQL: {sql}  BaseRecord: {base_record}")
		pass

	if len(rebills_failed_mt) == 0:
		print(colored(f"Rebills => Multitrans Records Compared => Pass ", 'green'))
	else:
		print(colored(f"********************* Rebills => Multitrans MissMatch => CHeck Manually ****************", 'blue'))

	return [rebills_completed_mt,rebills_failed_mt]

def multitrans_check_refunds(refunds):
	rkeys = refunds.keys() ; live_record = {} ; tasks_type_status = []
	refunds_completed_mt = [] ; base_record = {} ; sql = '' ; pid = 0
	refunds_failed_mt = []

	for tid in rkeys:
		try:
			differences = {}
			base_record = refunds[tid]
			pid = base_record['PurchaseID']
			tasks_type_status = db_agent.tasks_table(tid)
			sql = ''
			if tasks_type_status[0] == '':
				print(f"Task was not inserted TID: {tid} PID: #{pid}")
			elif tasks_type_status[0] == 844:
				print(f"Task - 844 Cancel => Nothing to refund => PID: {pid} | TID: {tid}")
				refunds_failed_mt.append(live_record)
			else:
				if base_record['TransStatus'] == 184:  # Void
					base_record['TransType'] = 107
					base_record['TxStatus'] = 8
					base_record['TransStatus'] = 182
					sql = "Select * from multitrans where PurchaseID = {} and TransType = 107 and RelatedTransID = {}"
				else: # Refund
					sql = "Select * from multitrans where PurchaseID = {} and TransType = 102 and RelatedTransID = {}"
					base_record['TransType'] = 102
					base_record['TxStatus'] = 7
					base_record['TransStatus'] = 186

				live_record = db_agent.execute_select_two_parameters(sql, pid, base_record['TransID'])
				#live_record['TransTime'] = datetime.date(live_record['TransTime'])

				base_record['TransAmount'] = (-base_record['TransAmount'])
				base_record['Markup'] = (-base_record['Markup'])
				base_record['TransSource'] = 125
				base_record['RelatedTransID'] = base_record['TransID']
				base_record['TransID'] = live_record['TransID']
				#base_record['TransTime'] = datetime.date(base_record['TransTime'])

				for record in [base_record,live_record]:
					record['TRANSGUID'] = ''
					record['ProcessorTransID'] = None
					record['PCID'] = None
					record['SOURCEMACHINE'] = None
					record['IPCountry'] = None
					record['BinCountry'] = None
					record['RefURL'] = None
					record['AffiliateID'] = None

				differences = bep.dictionary_compare(base_record,live_record)

				if len(differences) == 0:
					refunds_completed_mt.append(live_record)
				else:
					refunds_failed_mt.append(live_record)
					print(colored(f"********************* Refunds Multitrans MissMatch Beginning**************** | PurchaseID = {pid} | TransID: {tid}", 'red'))
					print()
					for k, v in differences.items():
						print(k, v)
					print()
					print(colored(f"******************** Refund Multitrans MissMatch End ***************", 'red'))
		except Exception as ex:
			traceback.print_exc()
			print(f"{Exception}  Tid: {tid,}   Task: {tasks_type_status[0]} , {tasks_type_status[1]}  SQL: {sql}  BaseRecord: {base_record}")
			pass

	if len(refunds_failed_mt) == 0:
		print(colored(f"Refund => Multitrans {len(refunds_completed_mt)} - Records Compared => Pass ", 'green'))
	else:
		print(colored(f"Refund => Multitrans {len(refunds_completed_mt)} - Records Compared => Pass ", 'green'))
		print()
		print(colored(f"******************** Refund {len(refunds_failed_mt)} transactions    => Multitrans MissMatch => Check Manually ***************", 'blue'))

	return [refunds_completed_mt, refunds_failed_mt]

def mt_check_reactivation(reactivated):
	rkeys = reactivated.keys()
	live_record = {}
	tasks_type_status = []
	reactivated_completed_mt = []
	base_record = {}
	sql = ''
	pid = 0
	reactivated_failed_mt = []

	for tid in rkeys:
		try:
			differences = {}
			base_record = reactivated[tid][tid]
			pid = base_record['PurchaseID']
			tasks_type_status = db_agent.tasks_table(tid)

			sql = "Select RecurringAmount, CardExpiration from assets where PurchaseID = {}"
			trans_amount = db_agent.execute_select_one_parameter(sql, pid)

			sql = "Select * from multitrans where PurchaseID = {} and TransSource = 127"
			live_record = db_agent.execute_select_one_parameter(sql, pid)
			base_record['TransSource'] = 127
			base_record['TransAmount'] = trans_amount['RecurringAmount']
			base_record['CardExpiration'] = trans_amount['CardExpiration']
			base_record['Markup'] = round((base_record['TransAmount'] * base_record['ExchRate']), 2)

			exchange_rate = 1
			if base_record['ProcessorCurrency'] == base_record['MerchantCurrency']:
				exchange_rate = 1
			else:
				exchange_rate = db_agent.exc_rate(base_record['MerchantCurrency'], base_record['ProcessorCurrency'])

			#exchange_rate = round(exchange_rate, 2)



			if base_record['MerchantCurrency'] == 'JPY':
				excr = round((base_record['TransAmount'] * exchange_rate), 2)
				excr = round((excr))
				excr = str(excr) + '.00'
				excr = Decimal(excr)
				base_record['Markup'] = excr
			else:
				base_record['Markup'] = round((base_record['TransAmount'] * exchange_rate), 2)

			base_record['TransStatus'] = 186
			base_record['TransID'] = live_record['TransID']

			for record in [base_record, live_record]:
				record['TRANSGUID'] = ''
				record['ProcessorTransID'] = None
				record['PCID'] = None
				record['SOURCEMACHINE'] = None
				record['USERDATA'] = None
				#record['IPCountry'] = None
				#record['BinCountry'] = None
				record['RefURL'] = None
				record['AffiliateID'] = None
				# make sure they need it or not
				record['REF1'] = None
				record['REF2'] = None
				record['REF3'] = None
				record['REF4'] = None
				record['REF5'] = None
				record['REF6'] = None
				record['REF7'] = None
				record['REF8'] = None
				record['REF9'] = None
				record['REF10'] = None


			differences = bep.dictionary_compare(base_record, live_record)

			if len(differences) == 0:
				reactivated_completed_mt.append(live_record)
			else:
				reactivated_failed_mt.append(live_record)
				print(colored(f"********************* Reactivation Multitrans MissMatch Beginning**************** | PurchaseID = {pid} | TransID: {tid}", 'red'))
				print()
				for k, v in differences.items():
					print(k, v)
					print()
				print(colored(f"******************** Reactivation Multitrans MissMatch End ***************", 'red'))
				print()
		except Exception as ex:
			traceback.print_exc()
			print(f"{Exception}  Tid: {tid,}   Task: {tasks_type_status[0]} , {tasks_type_status[1]}  SQL: {sql}  BaseRecord: {base_record}")
			pass

	if len(reactivated_failed_mt) == 0:
		print(colored(f"Reactivation => Multitrans {len(reactivated_completed_mt)} - Records Compared => Pass ", 'green'))
	else:
		print(colored(f"Reactivation => Multitrans {len(reactivated_completed_mt)} - Records Compared => Pass ", 'green'))
		print()
		print(colored(f"******************** Reactivation {len(reactivated_failed_mt)} transactions    => Multitrans MissMatch => Check Manually ***************", 'blue'))

	return [reactivated_completed_mt, reactivated_failed_mt]