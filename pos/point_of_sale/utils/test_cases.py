import random
import decimal
import time
from datetime import datetime
from xml.etree.ElementTree import fromstring
import requests
import traceback
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import options
import yaml

db_agent = DBActions()
start_time = datetime.now()
print(f"Test Cases are generated based on | Merchant: 'EU,US | 3DS Configuration | Scope | Cardinal Test Cases | Processor | CollectUserInfo | PricePoint Type |")
print("________________________________________________________________________________________________________________________________________________________")
print()
cnt_tc = 0
cnt = 0  # transactions
available_languages = ['EN']  # ,'ES', "PT", "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]
eu_currencies = ['USD']  # , "AUD", "CAD", "CHF", "DKK", "EUR", "GBP", "HKD", "JPY", "NOK", "SEK"]
currencies = ['USD']
packages = [800, 900, 900, 901, 902, 903, 800, 801, 802, 803, 192137, 192261, 192195, 192059, 192204, 192138, 192282, 192196, 999, 99,192317]
random_cards = ['4000000000001000', '4000000000001018', '4000000000001026', '4000000000001034', '4000000000001042', '4000000000001059', '4000000000001067',
                '4000000000001075', '4000000000001083', '4000000000001091', '4000000000001109', '4000000000001117', '4000000000001125', '4000000000001133',
                '5432768030017007', '4916280519180429']


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
	try:
		d = config.test_data
		processor_name = {
			26: 'PAYVISIONWE',
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
			aproved_declined = False
		elif d['3ds'] == False and d['scope'] == False:
			msg = 'This Transaction should be Aproved | Merchant not in scope and not configured |'
			aproved_declined = True
		elif int(d['cc']) in cardinal_aprove_cards:
			msg = 'This Transaction should be Aproved'
			if d['cc'] == '4000000000001000': cardinal_case = "Test Case 1: Successful Frictionless Authentication"
			if d['cc'] == '4000000000001091': cardinal_case = "Test Case 10: Successful Step Up Authentication"
			if d['cc'] == '4000000000001026': cardinal_case = "Test Case 3: Attempts Stand-In Frictionless Authentication"
			aproved_declined = True
		elif d['card_type'] == 'Prepaid':
			msg = 'This Transaction should be Aproved'
			aproved_declined = True
		elif int(d['cc']) in cardinal_decline_cards:
			if config.test_data['scope']:
				msg = 'This Transaction should be Declined'
			else:
				msg = "This Transaction can be Aproved or Declined | If CardinalResultActions = 1181 -Aprove | If CardinalResultActions = 1182 - Decline  "
			if d['cc'] == '4000000000001018': cardinal_case = "Test Case 2: Failed Frictionless Authentication"
			if d['cc'] == '4000000000001034': cardinal_case = "Test Case 4: Unavailable Frictionless Authentication from the Issuer"
			if d['cc'] == '4000000000001042': cardinal_case = "Test Case 5: Rejected Frictionless Authentication by the Issuer"
			if d['cc'] == '4000000000001059': cardinal_case = "Test Case 6: Authentication Not Available on Lookup"
			if d['cc'] == '4000000000001067': cardinal_case = "Test Case 7: Error on Lookup"
			if d['cc'] == '4000000000001075': cardinal_case = "Test Case 8: Timeout on cmpi_lookup Transaction"
			if d['cc'] == '4000000000001083': cardinal_case = "Test Case 9: Bypassed Authentication"
			if d['cc'] == '4000000000001109': cardinal_case = "Test Case 11: Failed Step Up Authentication"
			if d['cc'] == '4000000000001117': cardinal_case = "Test Case 12: Step Up Authentication is Unavailable"
			if d['cc'] == '4000000000001125': cardinal_case = "Test Case 13: Error on Authentication"
			if d['cc'] == '4000000000001133': cardinal_case = "Test Case 14: Step Up Authentication with Merchant Bypass"
			purch_tatus = 806
		else:
			msg = "This Transaction should be Declined", 'red'" - | Note: Can be aproved based on the settings in CardinalResultActions if ResultAction = 1181'"
			purch_tatus = 806
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

		tc_str = f"{d['Merchant']}{d['3ds']}{d['card_type']}{d['Type']}{cardinal_case}" # {d['Type']}
		postbacks_decline = ''
		if not tc_str in config.test_cases:
			sc = '-' * 136 + 'Start'
			er = f"Expected Results :" + ('_' * 140)
			end_c = '_' * 158 + 'end_Test_Case_Scenario'
			if aproved_declined == False and postbacks:
				postbacks_decline = postbacks.replace('1 ,', '').replace(' 2,', '')
			if d['card_type'] == 'Prepaid':
				tmp = f"_______________Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Assets:      | PurchStatus: {purch_tatus} | PurchType: {d['Type']} | Processor: {processor_name[d['processor']]} | UserName: {username} | Password: {password} | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Email:       | PointOfSaleEmailQueue should have | EmailType: 981 | in the que with Status: 863 (Complete)\n" \
				      f"_______________PostBacks:   | PostBackNotifications should have: | {postbacks} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________3DS:         | Cardinal3dsRequests should not have any record for this transaction\n"
			elif 'If CardinalResultActions = 1181' in msg:
				tmp = f"If Declined  :\n_______________ Multitranse: | AuthCode: 'C300' or 'C200' | Autorized: 0 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl} |\n" \
				      f"_______________ Assets:      | PurchStatus: 806 | PurchType: {d['Type']} | LastResult: Declined | UserName: {username} | Password: {password} | Purchases: 0 | RefURL: {checkrefurl} |\n" \
				      f"_______________ Email:       | PointOfSaleEmailQueue should not have email for this transaction | PostBacks are only transactionals |\n" \
				      f"_______________ PostBacks:   | PostBackNotifications should have: | {postbacks_decline} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"If Aproved   :\n_______________ Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl} |\n" \
				      f"_______________ Assets:      | PurchStatus: {purch_tatus} | PurchType: {d['Type']} | Processor: {processor_name[d['processor']]} | UserName: {username} | Password: {password} | RefVariables: {checkrefs} | RefURL: {checkrefurl} |\n" \
				      f"_______________ Email:       | PointOfSaleEmailQueue should have | EmailType: 981 | in the que with Status: 863 (Complete)\n" \
				      f"_______________ PostBacks:   | PostBackNotifications should have: | {postbacks} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________ 3DS:         | {cardinal_check}\n"
			elif 'Declined' in msg:
				tmp = f"_______________Multitranse: | AuthCode: 'C300' or 'C200' | Autorized: 0 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
				      f"_______________Assets:      | PurchStatus: 806 | PurchType: {d['Type']} | LastResult: Declined | UserName: {username} | Password: {password} | Purchases: 0 | RefURL: {checkrefurl}\n" \
				      f"_______________Email:       | PointOfSaleEmailQueue should not have email for this transaction | PostBacks are only transactionals |\n" \
				      f"_______________PostBacks:   | PostBackNotifications should have: | {postbacks_decline} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)\n" \
				      f"_______________3DS:         | {cardinal_check}\n"

			else:
				tmp = f"_______________Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}\n" \
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
			config.test_cases[tc_str] = final_str

	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass


# for item in config.test_cases:
# 	print(config.test_cases[item])
# 	d0 = 3

# ==================================================================================================> Begining of the script
merchantid = 27001
# packageid = 901
# pricepoints = db_agent.pricepoint_list(merchantid)

for packageid in packages:
	config.test_data['packageid'] = packageid
	pricepoints = db_agent.get_pricepoints()
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
					if config.test_data['Merchant'] == 'EU':
						currencies = eu_currencies
					else:
						currencies = ['USD']
					config.test_data['dmc'] = dmc
					joinlink()
					scenario()
					cnt += 1
					# cnt_tc +=1
					k = 3
				except Exception as ex:
					traceback.print_exc()
					print(f"Exception {Exception} ")
					pass

# print(cnt_tc)
print(len(config.test_cases))


keys = 	config.test_cases.keys()
for item in sorted(keys):
	print(config.test_cases[item])
print()






# web.browser_quit()
end_time = datetime.now()
print('Full test Duration: {}'.format(end_time - start_time))
file_name = (format(end_time - start_time).split('.')[0] + ".yaml").replace(':', '-')
filename = f"C:/segpay_qa_automation/pos/point_of_sale\\tests\\test_run_{file_name}"
with open(filename, 'w') as f:
	data = yaml.dump(config.test_cases, f)

print(f"Total number of transaction : {cnt}")
print()
print()
