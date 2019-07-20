from datetime import datetime
from datetime import timedelta
from termcolor import colored
from decimal import Decimal

from pos.point_of_sale.db_functions.dbactions import DBActions

db_agent = DBActions()

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
		'PCID': '0',
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
		'RefURL': ''
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
		# if data_from_paypage['merchant_currency'] != 'JPY':
		# 	exchange_rate = round(exchange_rate, 2)
	exchange_rate = round(exchange_rate, 2)
	multitrans['ExchRate'] = exchange_rate

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
			multitrans['Markup']: round(multitrans['InitialPrice'] * exchange_rate, 2)
			multitrans['RelatedTransID'] = 0

	if merchantbillconfig['Type'] in [501, 506] and merchantbillconfig['InitialPrice'] == 0.00:
		multitrans['TransStatus'] = 186
		multitrans['TransAmount'] = 1.00

	return multitrans


def multitrans_compare(multitrans_base_record, live_record):
	differences = {}
	multitrans_live_record = live_record[0]
	for key in multitrans_base_record:
		live_value = multitrans_live_record[key]
		base_value = multitrans_base_record[key]
		if key == 'TransDate':
			live_value = multitrans_live_record['TransDate'].date()
		if base_value != live_value:
			differences[key] = f"Base:{base_value} => Live:{live_value}"  # Key:{key}

	# if multitrans_base_record['TransType'] == 1011:
	#     msg = ''

	if len(differences) == 0:
		print(f"PurchaseID:{multitrans_base_record['PurchaseID']} | TransId:{multitrans_base_record['TransID']} |"
		      f" TransGuid: {multitrans_base_record['TRANSGUID']}")
		print(colored(f"Mulitrans Record Compared =>  Pass", 'green'))
	else:
		print(f"PurchaseID:{multitrans_base_record['PurchaseID']} | TransId:{multitrans_base_record['TransID']} |"
		      f" TransGuid: {multitrans_base_record['TRANSGUID']}")
		print(colored(f"********************* Multitrans MissMatch ****************", 'red'))
		for k, v in differences.items():
			print(k, v)
	return differences




def multitrans_check_conversion(rebills):
	rkeys = rebills.keys()
	rebills_completed_mt = []
	rebills_failed_mt = []

	for pid in rkeys:
		differences = {}
		base_record = rebills[pid]

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
		#print(sql)
		exchange_rate = db_agent.execute_select_two_parameters(sql, base_record['MerchantCurrency'], base_record['ProcessorCurrency'])
		#exchange_rate = xyz['Rate']

		if base_record['MerchantCurrency'] == 'JPY':
			excr = round((base_record['TransAmount'] * exchange_rate['Rate']), 2)
			excr = round((excr))
			excr = str(excr) + '.00'
			excr = Decimal(excr)
			base_record['Markup'] = excr #Decimal(round((base_record['TransAmount'] * exchange_rate['Rate']), 2))
		else:
			base_record['Markup'] = round((base_record['TransAmount'] * exchange_rate['Rate']), 2)


		#print(xyz['Rate'])



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
		for key in base_record:
			live_value = live_record[key]
			base_value = base_record[key]
			if base_value != live_value:
				differences[key] = f"Base:{base_value} => Live:{live_value}"

		if len(differences) == 0:
			rebills_completed_mt.append(live_record)
			#print(colored(f"Asset Record Compared => Pass  | PurchaseID:{purchaseid} ", 'green'))
		else:
			rebills_failed_mt.append(live_record)
			print(colored(f"********************* Rebill Multitrans MissMatch Beginning****************", 'red'))
			print(f"PurchaseID = {pid} | TransID: {tid}")
			for k, v in differences.items():
				print(k, v)
			print(colored(f"********************* Rebill Multitrans MissMatch End ****************", 'red'))

	if len(rebills_failed_mt) == 0:
		print(colored(f"Rebills => Multitrans Records Compared => Pass ", 'green'))
	else:
		print(colored(f"********************* Rebills => Multitrans MissMatch => CHeck Manually ****************", 'blue'))

	return [rebills_completed_mt,rebills_failed_mt]

def multitrans_check_refunds(refunds, capture):
	rkeys = refunds.keys()
	refunds_completed_mt = []
	refunds_failed_mt = []
	live_record = ''

	pid = ''
	for tid in rkeys:
		try:
			differences = {}
			base_record = refunds[tid]
			pid = base_record['PurchaseID']
			tasks_type_status = db_agent.tasks_table(tid)
			sql = ''
			if tasks_type_status[0] == 842 and capture == False and base_record['TransType'] == 101:
				sql = "Select * from multitrans where PurchaseID = {} and TransType = 107"
				base_record['TransType'] = 107
				base_record['TxStatus'] = 8
				base_record['TransStatus'] = 182
			elif (tasks_type_status[0] == 842 and capture == True) or base_record['TransType'] == 1011:
				sql = "Select * from multitrans where PurchaseID = {} and TransType = 102"
				base_record['TransType'] = 102
				base_record['TxStatus'] = 7
				base_record['TransStatus'] = 186
				base_record['IPCountry'] = 'N/A'
				base_record['BinCountry'] = 'N/A'
				base_record['RefURL'] = None
				base_record['AffiliateID'] = None

			base_record['PCID'] = None
			base_record['TransSource'] = 125
			base_record['TRANSGUID'] = ''
			base_record['ProcessorTransID'] = ''
			base_record['SOURCEMACHINE'] = ''
			base_record['TransTime'] = datetime.date(base_record['TransTime'])
			base_record['TransAmount'] = (-base_record['TransAmount'])
			base_record['Markup'] = (-base_record['Markup'])

			print(sql)
			live_record = db_agent.execute_select_one_parameter(sql, tid)
			live_record['TransTime'] = datetime.date(live_record['TransTime'])
			live_record['TRANSGUID'] = ''
			live_record['ProcessorTransID'] = ''
			live_record['SOURCEMACHINE'] = ''
			live_record['PCID'] = None
			base_record['RelatedTransID'] = base_record['TransID']
			base_record['TransID'] = live_record['TransID']

			for key in base_record:
				live_value = live_record[key]
				base_value = base_record[key]
				if base_value != live_value:
					differences[key] = f"Base:{base_value} => Live:{live_value}"

			if len(differences) == 0:
				refunds_completed_mt.append(live_record)
			else:
				refunds_completed_mt.append(live_record)
				print(colored(f"********************* Refund Multitrans MissMatch Beginning****************", 'red'))
				print(f"PurchaseID = {pid} | TransID: {tid}")
				for k, v in differences.items():
					print(k, v)
				print(colored(f"******************** Refund Multitrans MissMatch End ***************", 'red'))
		except Exception as ex:
			print(ex)
			pass

	if len(refunds_failed_mt) == 0:
		print(colored(f"Refund => Multitrans Records Compared => Pass ", 'green'))
	else:
		print(colored(f"******************** Refund => Multitrans MissMatch => Check Manually ***************", 'blue'))

	return [refunds_completed_mt, refunds_failed_mt]