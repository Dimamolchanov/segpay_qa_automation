from datetime import datetime
from datetime import timedelta
from termcolor import colored
from db_functions import dbs
import copy


def build_asset_signup(merchantbillconfig, multitrans_base_record, multitrans_live_record):
	type = merchantbillconfig['Type']
	live_record = multitrans_live_record['full_record'][0]
	current_date = (datetime.now().date())
	# transaction_record['full_record']
	asset = {'RecurringAmount': merchantbillconfig['RebillPrice'],
	         'PurchType': merchantbillconfig['Type'],
	         'PurchPeriod': merchantbillconfig['RebillLen'],
	         'MerchantID': live_record['MerchantID'],
	         'URLID': live_record['URLID'],
	         'PackageID': live_record['PackageID'],
	         'BillConfigID': live_record['BillConfigID'],
	         'CardType': live_record['CardType'],
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
		# asset['InitialAmount'] = multitrans_live_record['initialprice511']
		asset['RecurringAmount'] = multitrans_live_record['recurringprice511']
		asset['PurchPeriod'] = multitrans_live_record['recurringlength511']
	elif type == 505:
		asset['PurchTotal'] = 0.00
		asset['InitialAmount'] = 0.00
		# asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen']) +  timedelta(days=merchantbillconfig['RebillLen'])

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
				asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen']) + timedelta(days=merchantbillconfig['RebillLen'])
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
		assets['PurchStatus'] = 806
		assets['LastResult'] = 'Declined'
		assets['PurchTotal'] = 0
		assets['Purchases'] = 0
		asset['StatusDate'] = current_date
		asset['PurchDate'] = current_date
		asset['NextDate'] = None
		asset['ExpiredDate'] = current_date
		asset['CancelDate'] = current_date
		asset['ConvDate'] = current_date
		asset['LastDate'] = current_date

	return asset


def asset_oneclick(merchantbillconfig, asset_base_record, multitrans_live_record):
	type = merchantbillconfig['Type']
	live_record = multitrans_live_record[0]
	updated_record = copy.deepcopy((asset_base_record))
	current_date = (datetime.now().date())
	if type in [501, 505, 506, 511]:
		updated_record['PurchaseID'] = live_record['PurchaseID']

	# transaction_record['full_record']
	# asset = {'RecurringAmount': merchantbillconfig['RebillPrice'],
	#     #          'PurchType': merchantbillconfig['Type'],
	#     #          'PurchPeriod': merchantbillconfig['RebillLen'],
	#     #          'MerchantID': live_record['MerchantID'],
	#     #          'URLID': live_record['URLID'],
	#     #          'PackageID' : live_record['PackageID'],
	#     #          'BillConfigID' : live_record['BillConfigID'],
	#     #          'CardType' : live_record['CardType'],
	#     #          'InitialAmount': multitrans_base_record['TransAmount'],
	#     #          'AuthCurrency': multitrans_base_record['MerchantCurrency'],
	#     #          'PurchTotal': multitrans_base_record['TransAmount'],
	#     #          'CustLang': multitrans_base_record['Language'],
	#     #          'Currency': multitrans_base_record['ProcessorCurrency'],
	#     #          'PurchaseID': multitrans_base_record['PurchaseID'],
	#     #          'Processor': multitrans_base_record['Processor'],
	#     #          'CustEMail': multitrans_base_record['CustEMail'],
	#     #          'RefURL': multitrans_base_record['RefURL'],
	#     #          'CardExpiration': multitrans_base_record['CardExpiration'],
	#     #          'CustCountry': multitrans_base_record['CustCountry'],
	#     #          'CustZip': multitrans_base_record['CustZip'],
	#     #          'PaymentAcct': multitrans_base_record['PaymentAcct'],
	#     #          'PCID': multitrans_base_record['PCID'],
	#     #          'ExchRate': multitrans_base_record['ExchRate'],
	#     #          'REF1': multitrans_base_record['REF1'],
	#     #          'REF2': multitrans_base_record['REF2'],
	#     #          'REF3': multitrans_base_record['REF3'],
	#     #          'REF4': multitrans_base_record['REF4'],
	#     #          'REF5': multitrans_base_record['REF5'],
	#     #          'REF6': multitrans_base_record['REF6'],
	#     #          'REF7': multitrans_base_record['REF7'],
	#     #          'REF8': multitrans_base_record['REF8'],
	#     #          'REF9': multitrans_base_record['REF9'],
	#     #          'REF10': multitrans_base_record['REF10']
	#     #          }
	#     #
	#     # if type == 511:
	#     #     #asset['InitialAmount'] = multitrans_live_record['initialprice511']
	#     #     asset['RecurringAmount'] = multitrans_live_record['recurringprice511']
	#     #     asset['PurchPeriod'] = multitrans_live_record['recurringlength511']
	#     # elif type == 505:
	#     #     asset['PurchTotal'] = 0.00
	#     #     asset['InitialAmount'] = 0.00
	#     #     #asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen']) +  timedelta(days=merchantbillconfig['RebillLen'])
	#     #
	#     # purchtype_recurring = [501, 505, 506, 507, 511]
	#     # if multitrans_base_record['Authorized'] == 1:
	#     #     transdate = (datetime.now().date())
	#     #     if type in (purchtype_recurring):
	#     #         asset['PurchStatus'] = 801
	#     #         asset['StatusDate'] = current_date
	#     #         asset['PurchDate'] = current_date
	#     #         if type == 511:
	#     #             asset['NextDate'] = current_date + timedelta(days=multitrans_live_record['initiallength511'])
	#     #             asset['ExpiredDate'] = current_date + timedelta(days=multitrans_live_record['initiallength511'])
	#     #         elif type == 505:
	#     #             asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen']) + timedelta(days=merchantbillconfig['RebillLen'])
	#     #         else:
	#     #             asset['NextDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen'])
	#     #             asset['ExpiredDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen'])
	#     #
	#     #         asset['CancelDate'] = None
	#     #         asset['ConvDate'] = None
	#     #         asset['LastDate'] = None
	#     #     else:
	#     #         asset['PurchStatus'] = 804
	#     #         if type in [503, 510]:
	#     #             asset['StatusDate'] = current_date
	#     #             asset['PurchDate'] = current_date
	#     #             asset['NextDate'] = None
	#     #             asset['ExpiredDate'] = current_date
	#     #             asset['CancelDate'] = current_date
	#     #             asset['ConvDate'] = current_date
	#     #             asset['LastDate'] = current_date
	#     #         elif type == 502:
	#     #             asset['PurchDate'] = current_date
	#     #             asset['NextDate'] = None
	#     #             asset['ExpiredDate'] = current_date + timedelta(days=merchantbillconfig['InitialLen'])
	#     #             asset['CancelDate'] = current_date
	#     #             asset['ConvDate'] = current_date
	#     #             asset['LastDate'] = current_date
	#     #     asset['LastResult'] = None
	#     #     asset['Purchases'] = 1
	#     #
	#     # else:
	#     #     assets['PurchStatus'] = 806
	#     #     assets['LastResult'] = 'Declined'
	#     #     assets['PurchTotal'] = 0
	#     #     assets['Purchases'] = 0
	#     #     asset['StatusDate'] = current_date
	#     #     asset['PurchDate'] = current_date
	#     #     asset['NextDate'] = None
	#     #     asset['ExpiredDate'] = current_date
	#     #     asset['CancelDate'] = current_date
	#     #     asset['ConvDate'] = current_date
	#     #     asset['LastDate'] = current_date

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


def asset_compare(asset_base_record):
	differences = {}
	purchaseid = asset_base_record['PurchaseID']
	asset_live_record = dbs.asset_full_record(purchaseid)[0]
	for key in asset_base_record:
		live_value = asset_live_record[key]
		base_value = asset_base_record[key]
		asset_dates = ['StatusDate', 'PurchDate', 'NextDate', 'ExpiredDate', 'CancelDate', 'ConvDate', 'LastDate']
		if key in asset_dates and asset_live_record[key] != None:
			live_value = asset_live_record[key].date()

		if base_value != live_value:
			# print(f" Key:{key}   miss: Base:{base_value} Live:{live_value}")
			# differences[key] = f" Key:{key}   miss: Base:{base_value} Live:{live_value}"
			differences[key] = f"Base:{base_value} => Live:{live_value}"

	if len(differences) == 0:
		print(colored(f" Asset Record Compared => Pass  | PurchaseID:{purchaseid} ", 'green'))
	else:
		print(colored(f"********************* Asset MissMatch ****************", 'red'))
		for k, v in differences.items():
			print(k, v)
	return differences
