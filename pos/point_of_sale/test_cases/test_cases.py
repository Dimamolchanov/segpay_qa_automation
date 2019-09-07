import random
import decimal
from pos.point_of_sale.utils import constants
import time
from datetime import datetime
from xml.etree.ElementTree import fromstring
import requests
from pos.point_of_sale.web import w
from termcolor import colored
from pos.point_of_sale.config import config
from pos.point_of_sale.utils import options
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import psd2
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.verifications import postback_service
from pos.point_of_sale.verifications import emails
# from pos.point_of_sale.runners import test_methods
import traceback
import random
import yaml

db_agent = DBActions()
start_time = datetime.now()
print(f"Test Cases are generated based on | Merchant: 'EU,US | 3DS Configuration | Scope | Cardinal Test Cases | Processor | CollectUserInfo | PricePoint Type |")
print("________________________________________________________________________________________________________________________________________________________")
print()


def load_test_cases(filename):
	# filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\test_cases.yaml"
	with open(filename) as f:
		test_cases_all = yaml.load(f, Loader=yaml.FullLoader)
		return test_cases_all


# for item in config.test_cases:
# 	print(config.test_cases[item][0])


def joinlink():
	pricingguid = {}
	joinlink = ''
	dynamic_price = ''
	d = config.test_data
	url_options = options.ref_variables() + options.refurl() + config.template
	config.test_data['url_options'] = url_options
	try:
		if d['Type'] == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			# print(hash_url)
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			joinlink = f"{config.url}{d['eticket']}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST{d['url_options']}"
		elif d['Type'] == 511:
			pricingguid = db_agent.get_pricingguid(d['MerchantID'], d['Type'])[0]
			joinlink = f"{config.url}{d['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}{d['url_options']}"  # PricingGuid, InitialPrice
		else:
			joinlink = config.url + d['eticket'] + url_options
		config.test_data['link'] = joinlink
		if d['Type'] == 511:
			config.test_data['initialprice511'] = pricingguid['InitialPrice']
			config.test_data['initiallength511'] = pricingguid['InitialLength']
			config.test_data['recurringlength511'] = pricingguid['RecurringLength']
			config.test_data['recurringprice511'] = pricingguid['RecurringPrice']
		elif d['Type'] == 510:
			config.test_data['initialprice510'] = dynamic_price


	except Exception as ex:
		traceback.print_exc()
		print(f"Function joinglink \n {Exception}")
		pass


def verify_signup_transaction(transaction_to_check):
	multitrans_base_record = mt.build_multitrans()
	asset_base_record = asset.build_asset_signup(multitrans_base_record, transaction_to_check)
	differences_multitrans = mt.multitrans_compare(multitrans_base_record, transaction_to_check['full_record'])
	differences_asset = asset.asset_compare(asset_base_record)
	if transaction_to_check['full_record']['Authorized'] == 1:
		check_email = emails.check_email_que(config.test_data['Type'], multitrans_base_record, 'signup')
		config.test_data['aproved_transids'] = transaction_to_check['TransID']
	if config.test_data['Type'] == 505:
		sql = "Select TransID from Multitrans where purchaseid = {} and TransSource = 121"
		tid = db_agent.execute_select_one_parameter(sql,config.test_data['PurchaseID'])['TransID']
		differences_postback = postback_service.verify_postback_url("SignUp", config.test_data['PackageID'], tid)
	else:
		differences_postback = postback_service.verify_postback_url("SignUp", config.test_data['PackageID'], transaction_to_check['TransID'])
	differences_3ds = psd2.cardinal3dsrequests(transaction_to_check['TransID'])
	config.transids.append(transaction_to_check['TransID'])
	config.transaction_records.append(transaction_to_check)
	decline_aprove = True
	if not config.test_data['full_record']['Authorized'] == config.test_data['aprove_or_decline']:
		decline_aprove = False
	if not differences_multitrans and not differences_asset and not differences_postback and decline_aprove:  # and not differences_3ds:
		return True
	else:
		return False


def scenario():
	descr = ''
	form = 'Short'
	checkrefs = None
	checkrefurl = None
	aproved_declined = False
	username = ''
	password = ''
	postbacks = ''
	cardinal_case = 'Not a Cardinal Test_Case'
	in_scope = False
	config.test_case = {}
	test_cases_local = {}
	cardinal_tc = -1
	try:
		d = config.test_data
		processor_name = {
			26: 'PAYVISIONWE',
			22: 'ROCKETGATE',
			42: 'ROCKETGATEISO',
			57: 'SPCATISO',
			44: 'PAYVISIONPRIVMS',
			65: 'SPKAISO1',
			74: 'SPHBIPSP'
		}
		config.test_data['processor_name'] = processor_name[d['processor']]
		if d['visa_secure'] == 2:
			form = 'Extended'
		if d['Type'] == 501:
			descr = 'Recurring'
			m4 = 1
		elif d['Type'] == 502:
			descr = 'One Time'
			m4 = 2
		elif d['Type'] == 503:
			descr = 'Digital Purchase'
			m4 = 3
		elif d['Type'] == 505:
			descr = 'Delayed Capture'
			m4 = 4
		elif d['Type'] == 506:
			descr = 'Instant Conversion'
		elif d['Type'] == 510:
			descr = 'Dynamic Pricing'
			m4 = 5
		elif d['Type'] == 511:
			descr = 'Dynamic Recurring'
			m4 = 6
		cardinal_aprove_cards = [4000000000001000, 4000000000001091, 4000000000001026]  # 4000000000001026
		cardinal_decline_cards = [4000000000001018, 4000000000001125, 4000000000001133, 4000000000001034, 4000000000001042, 4000000000001059, 4000000000001067, 4000000000001075, 4000000000001083, 4000000000001109, 4000000000001117]

		if d['3ds'] == False and d['scope']:
			msg = 'This Transaction should be Declined | C300:Merchant is not configured for Cardinal |'
			cardinal_case = "Not a Cardinal Case | 3ds Not Configured | in Scope"
			cardinal_tc = 29
			aproved_declined = False
		elif d['3ds'] == False and d['scope'] == False:
			msg = 'This Transaction should be Aproved | Merchant not in scope and not configured |'
			cardinal_case = "Not a Cardinal Case | 3ds Not Configured | Not in Scope"
			cardinal_tc = 30
			aproved_declined = True
		elif int(d['cc']) in cardinal_aprove_cards:
			msg = 'This Transaction should be Aproved'
			if d['cc'] == '4000000000001000':
				cardinal_case = "Test Case 1: Successful Frictionless Authentication"
				cardinal_tc = 15
			if d['cc'] == '4000000000001091':
				cardinal_case = "Test Case 10: Successful Step Up Authentication"
				cardinal_tc = 16
			if d['cc'] == '4000000000001026':
				cardinal_case = "Test Case 3: Attempts Stand-In Frictionless Authentication"
				cardinal_tc = 17
			aproved_declined = True
		elif d['card_type'] == 'Prepaid':
			msg = 'This Transaction should be Aproved'
			cardinal_case = "Prepaid Card"
			cardinal_tc = 31
			aproved_declined = True
		elif int(d['cc']) in cardinal_decline_cards:
			if config.test_data['scope']:
				msg = 'This Transaction should be Declined'
			else:
				msg = "This Transaction can be Aproved or Declined | If CardinalResultActions = 1181 -Aprove | If CardinalResultActions = 1182 - Decline  "
			if d['cc'] == '4000000000001018':
				cardinal_case = "Test Case 2: Failed Frictionless Authentication"
				cardinal_tc = 18
			if d['cc'] == '4000000000001034':
				cardinal_case = "Test Case 4: Unavailable Frictionless Authentication from the Issuer"
				cardinal_tc = 19
			if d['cc'] == '4000000000001042':
				cardinal_case = "Test Case 5: Rejected Frictionless Authentication by the Issuer"
				cardinal_tc = 20
			if d['cc'] == '4000000000001059':
				cardinal_case = "Test Case 6: Authentication Not Available on Lookup"
				cardinal_tc = 21
			if d['cc'] == '4000000000001067':
				cardinal_case = "Test Case 7: Error on Lookup"
				cardinal_tc = 22
			if d['cc'] == '4000000000001075':
				cardinal_case = "Test Case 8: Timeout on cmpi_lookup Transaction"
				cardinal_tc = 23
			if d['cc'] == '4000000000001083':
				cardinal_case = "Test Case 9: Bypassed Authentication"
				cardinal_tc = 24
			if d['cc'] == '4000000000001109':
				cardinal_case = "Test Case 11: Failed Step Up Authentication"
				cardinal_tc = 25
			if d['cc'] == '4000000000001117':
				cardinal_case = "Test Case 12: Step Up Authentication is Unavailable"
				cardinal_tc = 26
			if d['cc'] == '4000000000001125':
				cardinal_case = "Test Case 13: Error on Authentication"
				cardinal_tc = 27
			if d['cc'] == '4000000000001133':
				cardinal_case = "Test Case 14: Step Up Authentication with Merchant Bypass"
				cardinal_tc = 28
			purch_tatus = 806
		else:
			msg = "This Transaction should be Declined", 'red'" - | Note: Can be aproved based on the settings in CardinalResultActions if ResultAction = 1181'"
			cardinal_case = "Unknown at the moment"
			cardinal_tc = 32
			purch_tatus = 806

		# if cardinal_tc == -1:
		# 	print('stop')
		if 'ref' in d['url_options']: checkrefs = True
		if 'refurl' in d['url_options']: checkrefurl = True
		if aproved_declined:
			if d['Type'] in [501, 506, 507, 511]:
				purch_tatus = 801
			else:
				purch_tatus = 804
		else:
			purch_tatus = 806
		if d['CollectUserInfo'] == 0:
			username = True
			password = False
			if d['PostBackID']: postbacks = " 5's"
		elif d['CollectUserInfo'] == 1:
			username = True
			password = True
			if d['PostBackID']: postbacks = "1 , 2, 5's"
		elif d['CollectUserInfo'] == 2:
			username = 'Should be the Email'
			password = True
			if d['PostBackID']: postbacks = "1 , 2, 5's"

		if d['3ds'] and (d['cc'] in str(cardinal_aprove_cards) or d['cc'] in str(cardinal_decline_cards)):
			cardinal_check = f"Cardinal3dsRequests should have a response from Cardinal for {cardinal_case}"
		else:
			cardinal_check = f"Cardinal3dsRequests should have the response from Cardinal"

		in_scope = config.test_data['scope']
		# ===================================================================================================================================================
		if d['Merchant'] == 'EU': m = 1  # else: m = 2
		if d['Merchant'] == 'US': m = 2
		if d['3ds']: d3 = 3
		if d['3ds'] == False: d3 = 4
		if d['card_type'] == 'EU': c = 5
		if d['card_type'] == 'US': c = 6
		if d['card_type'] == 'Prepaid': c = 7
		if d['Type'] == 501: t = 8
		if d['Type'] == 502: t = 9
		if d['Type'] == 503: t = 10
		if d['Type'] == 505: t = 11
		if d['Type'] == 506: t = 12
		if d['Type'] == 510: t = 13
		if d['Type'] == 511: t = 14

		tc_str = f"{m}{d3}{c}{t}{cardinal_tc}"  # {d['Type']}
		# print(cardinal_tc)

		# tc_str = f"{d['Merchant']}{d['3ds']}{d['card_type']}{d['Type']}{cardinal_case}"  # {d['Type']}
		postbacks_decline = ''
		if not tc_str in config.test_cases:
			sc = '-' * 136 + 'Start'
			er = f"Expected Results :" + ('_' * 140)
			end_c = '_' * 158 + 'end_Test_Case_Scenario'
			if aproved_declined == False and postbacks:
				postbacks_decline = postbacks.replace('1 ,', '').replace(' 2,', '')
			if d['card_type'] == 'Prepaid':
				tmp = f"PayPage:_______Form should be: {form} | {msg}\n" \
				      f"_______________Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Assets:      | PurchStatus: {purch_tatus} | PurchType: {d['Type']} | Processor: {processor_name[d['processor']]} | UserName: {username} | Password: {password} | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Email:       | PointOfSaleEmailQueue should have | EmailType: 981 | in the que with Status: 863 (Complete)\n" \
				      f"_______________PostBacks:   | PostBackNotifications should have: | {postbacks} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________3DS:         | Cardinal3dsRequests should not have any record for this transaction\n"
			elif 'If CardinalResultActions = 1181' in msg:
				tmp = f"PayPage:________Form should be: {form} | {msg}\n" \
				      f"If Declined  :\n_______________ Multitranse: | AuthCode: 'C300' or 'C200' | Autorized: 0 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl} |\n" \
				      f"_______________ Assets:      | PurchStatus: 806 | PurchType: {d['Type']} | LastResult: Declined | UserName: {username} | Password: {password} | Purchases: 0 | RefURL: {checkrefurl} |\n" \
				      f"_______________ Email:       | PointOfSaleEmailQueue should not have email for this transaction | PostBacks are only transactionals |\n" \
				      f"_______________ PostBacks:   | PostBackNotifications should have: | {postbacks_decline} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"If Aproved   :\n_______________ Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl} |\n" \
				      f"_______________ Assets:      | PurchStatus: {purch_tatus} | PurchType: {d['Type']} | Processor: {processor_name[d['processor']]} | UserName: {username} | Password: {password} | RefVariables: {checkrefs} | RefURL: {checkrefurl} |\n" \
				      f"_______________ Email:       | PointOfSaleEmailQueue should have | EmailType: 981 | in the que with Status: 863 (Complete)\n" \
				      f"_______________ PostBacks:   | PostBackNotifications should have: | {postbacks} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________ 3DS:         | {cardinal_check}\n"
			elif 'Declined' in msg:
				tmp = f"PayPage:_______Form should be: {form} | {msg}\n" \
				      f"_______________Multitranse: | AuthCode: 'C300' or 'C200' | Autorized: 0 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Assets:      | PurchStatus: 806 | PurchType: {d['Type']} | LastResult: Declined | UserName: {username} | Password: {password} | Purchases: 0 | RefURL: {checkrefurl}\n" \
				      f"_______________Email:       | PointOfSaleEmailQueue should not have email for this transaction | PostBacks are only transactionals |\n" \
				      f"_______________PostBacks:   | PostBackNotifications should have: | {postbacks_decline} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________3DS:         | {cardinal_check}\n"
			else:
				tmp = f"PayPage:_______Form should be: {form} | {msg}\n" \
				      f"_______________Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Assets:      | PurchStatus: {purch_tatus} | PurchType: {d['Type']} | Processor: {processor_name[d['processor']]} | UserName: {username} | Password: {password} | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Email:       | PointOfSaleEmailQueue should have | EmailType: 981 | in the que with Status: 863 (Complete)\n" \
				      f"_______________PostBacks:   | PostBackNotifications should have: | {postbacks} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________3DS:         | {cardinal_check}\n"
			final_str = f"Test Case Scenario:\n{sc}\n--SignUp Transaction | Merchant: {d['Merchant']} | 3DS Configured: {d['3ds']}  | Card: {d['card_type']} | Card # {d['cc']} |\n" \
			            f"--In Scope: {in_scope}  | Cardinal - {cardinal_case} |\n" \
			            f"--PricePoint Type: {d['Type']} - {descr}  | DMC: {d['dmc']} | Language: {d['lang']} | Processor PoolID: {d['processor']} |\n" \
			            f"--DMCStatus = {d['DMCStatus']} | CollectUserInfo: {d['CollectUserInfo']}\n\n" \
			            f"Prerequisite:\n-----------------\n--MerhcantID: {d['MerchantID']} | Card: {d['cc']} | Eticket: {d['eticket']} | Template: {d['PayPageTemplate']} | \n" \
			            f"--Link: {d['link']}\n\n{er}\n\n{tmp}\n" \
			            f"{end_c}\n\n\n"
			config.test_cases[tc_str] = [final_str, config.test_data]
			if not tc_str in test_cases_all:
				descr = f" Merchant: {d['Merchant']} | 3DS Configured: {d['3ds']}  | Card: {d['card_type']} | In Scope: {in_scope}  | Cardinal - {cardinal_case} "
				# print(cardinal_tc)
				# print( f"{tc_str} | {descr}")
				test_cases_all[tc_str] = [final_str, config.test_data, descr]
			# es = transaction(config.test_cases)

			# return tc_str,[final_str, config.test_data]

			s = 3
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass


def transaction(test_cases):
	br = w.FillPayPage()
	failed_test_cases = []
	passed_test_cases = {}
	try:
		for item in config.test_cases:
			try:
				config.test_case = {}
				print(config.test_cases[item][0])
				current_transaction_record = {}
				test_case = test_cases[item][1]
				br.FillDefault(test_case)
				sql = "select * from multitrans where TransGuid = '{}'"
				full_record = db_agent.execute_select_one_with_wait(sql, test_case['transguid'])
				test_case['PurchaseID'] = full_record['PurchaseID']
				test_case['TransID'] = full_record['TransID']
				if test_case['Type'] == 505:
					sql = "Select * from Multitrans where purchaseid = {} and TransSource = 122"
					tmp = db_agent.execute_select_one_with_wait(sql, test_case['PurchaseID'])
					if tmp: full_record = tmp

				test_case['full_record'] = full_record
				config.test_data = test_case
				current_transaction_record = test_case
				config.test_data['transaction_to_check'] = current_transaction_record
				aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
				print()
				print(f"TestCase: {item} | Description: {test_cases_all[item][2]}")
				print(colored("___________________________________________________________Actual Results_______________________________________________________________________________________________________", 'grey', 'on_yellow', attrs=['bold', 'dark']))
				print(colored(f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}", 'yellow'))
				config.test_case['actual'] = [f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}"]
				if current_transaction_record['full_record']['Authorized']:
					tmp = current_transaction_record['full_record']
					config.oc_tokens[tmp['PurchaseID']] = [config.test_data['Type'], tmp['MerchantCurrency'], tmp['Language']]
					result = current_transaction_record['full_record']
					tmpstr = f"Transaction Aproved : AuthCode:{result['AuthCode']}"
					print(colored(tmpstr, 'cyan', attrs=['bold']))
				else:
					result = current_transaction_record['full_record']
					tmpstr = f"Transaction DECLINED : AuthCode:{result['AuthCode']}"
					print(colored(tmpstr, 'red', attrs=['bold']))

				pass_fail = verify_signup_transaction(current_transaction_record)
				if pass_fail:
					passed_test_cases[item] = test_cases_all[item][2]
					print(colored(f"Scenario completed: All Passed", 'green', attrs=['bold', 'underline', 'dark']))
					print(colored("________________________________________________________Verification Completed_______________________________________________________________________________________________________", 'grey', 'on_yellow', attrs=['bold', 'dark']))
				else:
					failed_test_cases.append(item)
					print(colored(f"Scenario had some issues: Failed | Re-Check Manually |", 'red', attrs=['bold', 'underline', 'dark']))

					print(colored(f"________________________________________________________Verification Completed | Test_Case: {item} => FAILED__________________________________________________________________________________", 'white', 'on_grey', attrs=['bold', 'dark']))
				print()
				print()
				z = 3
			except Exception as ex:
				traceback.print_exc()
				print(f"{Exception}")
				pass

		filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\failed_test_cases.yaml"
		with open(filename, 'w') as f:
			data = yaml.dump(failed_test_cases, f)
		return passed_test_cases
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass


def create_test_cases():
	cnt = 0  # transactions
	available_languages = ['EN']  # ,'ES', "PT", "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]
	eu_currencies = ['USD', "AUD", "CAD", "CHF", "DKK", "EUR", "GBP", "HKD", "JPY", "NOK", "SEK"]
	currencies = ''  # ['USD']

	packages =  [803, 900, 901, 902, 903, 800, 801, 802, 803, 192137, 192261, 192195, 192059, 192204, 192138, 192282, 192196, 999, 99, 192317]
	random_cards = ['4000000000001000', '4000000000001018', '4000000000001026', '4000000000001034', '4000000000001042', '4000000000001059', '4000000000001067',
	                '4000000000001075', '4000000000001083', '4000000000001091', '4000000000001109', '4000000000001117', '4000000000001125', '4000000000001133',
	                '5432768030017007', '4916280519180429']
	for packageid in packages:
		config.test_data['packageid'] = packageid
		sql = "Select MerchantID from package where packageid = {}"
		merchantid = db_agent.execute_select_one_parameter(sql, packageid)['MerchantID']
		pricepoints = db_agent.get_pricepoints()
		is_eu_merchant = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MERCHANT_EXTENSION, merchantid)['VISARegion']
		if is_eu_merchant == 1:
			currencies = eu_currencies
		else:
			currencies = ['USD']
		for pricepoint in pricepoints:
			for selected_language in config.available_languages:
				for dmc in currencies:
					try:
						cnt += 1
						config.test_data = {}
						config.test_data['cc'] = random.choice(random_cards)
						config.test_data['lang'] = selected_language
						config.test_data['packageid'] = packageid
						config.test_data = {**config.test_data, **config.initial_data}
						merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
						config.test_data = {**config.test_data, **merchantbillconfig}
						package = db_agent.package(packageid)
						config.test_data['processor'] = package
						config.test_data = {**config.test_data, **package}
						eticket = str(packageid) + ':' + str(pricepoint)
						config.test_data['eticket'] = eticket
						config.test_data['url_options'] = options.ref_variables() + options.refurl() + config.template
						config.test_data['visa_secure'] = options.is_visa_secure()
						config.test_data['processor'] = config.test_data['PrefProcessorID']
						config.test_data['dmc'] = dmc
						joinlink()
						scenario()
						# tmp  = scenario()
						# test_cases_local[tmp[0]] = tmp[1]
						# cnt_tc +=1
						k = 3
					except Exception as ex:
						traceback.print_exc()
						print(f"Exception {Exception} ")
						pass


#test_cases_all = {}
# create_test_cases()

failed = True
filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\test_cases.yaml"
test_cases_all = load_test_cases(filename)
if failed:
	filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\failed_test_cases.yaml"
	test_cases_failed = load_test_cases(filename)
	for item in test_cases_failed:
		if item in test_cases_all:
			config.test_cases[item] = test_cases_all[item]
else:
	create_test_cases()
	# filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\test_cases.yaml"
	with open(filename, 'w') as f:
		data = yaml.dump(test_cases_all, f)



res = transaction(config.test_cases)
# oneclick =  test_methods.signup_oc_all,('pos', config.test_data['eticket'], config.test_data)
print(len(config.test_cases))

# web.browser_quit()
end_time = datetime.now()
print('Full test Duration: {}'.format(end_time - start_time))
# file_name = (format(end_time - start_time).split('.')[0] + ".yaml").replace(':', '-')
# filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\test_run_{file_name}"
# filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\test_cases.yaml"
# with open(filename, 'w') as f:
# 	data = yaml.dump(test_cases_all, f)
