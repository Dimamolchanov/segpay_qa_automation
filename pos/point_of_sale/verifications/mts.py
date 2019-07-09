from pos.point_of_sale.db_functions import dbs
from datetime import datetime
from datetime import timedelta
from termcolor import colored


def build_multitrans(merchantbillconfig, package, data_from_paypage, url_options):
	transdate = (datetime.now().date())
	url = dbs.url(package['URLID'])
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
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF1'] = val
		elif tmp[0] == 'ref2':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF2'] = val = val
		elif tmp[0] == 'ref3':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF3'] = val
		elif tmp[0] == 'ref4':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF4'] = val
		elif tmp[0] == 'ref5':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF5'] = val
		elif tmp[0] == 'ref6':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF6'] = val
		elif tmp[0] == 'ref7':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF7'] = val
		elif tmp[0] == 'ref8':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF8'] = val
		elif tmp[0] == 'ref9':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF9'] = val
		elif tmp[0] == 'ref10':
			val = dbs.encrypt_string(tmp[1])
			multitrans['REF10'] = val
		elif tmp[0] == 'refurl':
			val = tmp[1][:256]
			multitrans['RefURL'] = val  # update refs  #

	multitrans['PaymentType'] = 131
	exchange_rate = 1
	if merchantbillconfig['Currency'] == data_from_paypage['merchant_currency']:
		exchange_rate = 1
	else:
		exchange_rate = dbs.exc_rate(data_from_paypage['merchant_currency'], merchantbillconfig['Currency'])
		if data_from_paypage['merchant_currency'] != 'JPY':
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
			multitrans['RelatedTransID'] = dbs.sql(sql)[0]['RelatedTransID']
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
