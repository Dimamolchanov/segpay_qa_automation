from pos.point_of_sale import config
import splinter
import random, decimal, string
from pos.point_of_sale.db_functions import dbs
from splinter import Browser
from faker import Faker
from faker.providers import internet
import subprocess
from selenium import webdriver
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XML, fromstring, tostring
import simplexml
import requests
import copy
from pos.point_of_sale.features import options

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--window-position=-1400,0")
fake = Faker()

br = Browser(driver_name='chrome', options=chrome_options)


def navigate_to_url(url):
	retry_flag = True
	retry_count = 0
	while retry_flag and retry_count < 30:
		try:
			br.visit(url)
			assert (br.url == url)
			retry_flag = False
			return True

		except:
			print("Retry after 1 sec navigating to url")
			retry_count = retry_count + 1
			time.sleep(1)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------ 1click POS and WS
def one_click(option, eticket, pricepoint_type, multitrans_base_record, email,url_options, selected_options):
	transguid = ''
	multitrans_oneclick_record = copy.deepcopy(multitrans_base_record)
	token = multitrans_base_record['PurchaseID']
	username = fake.user_name() + str(random.randint(333, 999))
	password = fake.user_name() + str(random.randint(333, 999))

	if option == 'pos':
		if pricepoint_type == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			multitrans_oneclick_record['TransAmount'] = dynamic_price
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			url = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={token}" + selected_options
		elif pricepoint_type == 511:
			pricingguid = dbs.get_pricingguid(multitrans_base_record['MerchantID'], pricepoint_type)[0]
			url = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={token}" + selected_options
		else:
			url = f"{config.url}{eticket}&octoken={token}" + url_options
		print(url)

		page_loaded = navigate_to_url(url)
		if page_loaded == False:
			return None
		else:
			if br.is_element_present_by_id('TransGUID', wait_time=10):
				transguid = br.find_by_id('TransGUID').value
				transguid = subprocess.run(
					['C:\segpay\pos\point_of_sale\/transguid\TransGuidDecoderApp.exe', transguid, '-l'],
					stdout=subprocess.PIPE)
				transguid = transguid.stdout.decode('utf-8')
			else:
				print("Transguid not Found ")
				return None
			paypage_lnaguage = br.find_by_id('LanguageDDL').select(selected_options[1])
			time.sleep(2)
			br.find_by_id('EMailInput').fill(email)
			if br.find_by_id('UserNameInput'):
				br.find_by_id('UserNameInput').fill(username)
			if br.find_by_id('PasswordInput'):
				br.find_by_id('PasswordInput').fill(password)
			br.find_by_id('SecurePurchaseButton').click()

			oneclick_record = dbs.multitrans_full_record('', transguid, '')
			full_record = oneclick_record[0]

			if pricepoint_type in [501, 506, 511]:
				multitrans_oneclick_record['TransSource'] = 121
			else:
				multitrans_oneclick_record['TransSource'] = 123
			multitrans_oneclick_record['TransType'] = 1011
			multitrans_oneclick_record['TransStatus'] = 186
			multitrans_oneclick_record['PurchaseID'] = full_record['PurchaseID']
			multitrans_oneclick_record['TransID'] = full_record['TransID']
			multitrans_oneclick_record['TRANSGUID'] = transguid
			multitrans_oneclick_record['RelatedTransID'] = multitrans_base_record['TransID']
			print(f"OneClick POS => Eticket: {eticket} | Type: {pricepoint_type} | Processor: {multitrans_base_record['Processor']} "
			      f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")

			return multitrans_oneclick_record, oneclick_record




	elif option == 'ws':
		if pricepoint_type == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			multitrans_oneclick_record['TransAmount'] = dynamic_price
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			url = f"{config.urlws}{eticket}&amount={dynamic_price}" \
				      f"&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={token}" + selected_options + '&DMCURRENCY=JPY'
		elif pricepoint_type == 511:
			pricingguid = dbs.get_pricingguid(multitrans_base_record['MerchantID'], pricepoint_type)[0]
			url = f"{config.urlws}{eticket}" \
				      f"&DynamicPricingID={pricingguid['PricingGuid']}&octoken={token}" + selected_options

		else:
			url = f"{config.urlws}{eticket}&octoken={token}" + url_options
		print(url)

		resp = requests.get(url)
		xml_return_string = simplexml.loads(resp.content)
		transid = int(xml_return_string['TransReturn']['TransID'])
		oneclick_record = dbs.multitrans_full_record(transid, '', '')
		full_record = oneclick_record[0]

		if pricepoint_type in [501, 506, 511]:
			multitrans_oneclick_record['TransSource'] = 121
		else:
			multitrans_oneclick_record['TransSource'] = 123
		multitrans_oneclick_record['TransType'] = 1011
		multitrans_oneclick_record['TransStatus'] = 186
		multitrans_oneclick_record['PurchaseID'] = full_record['PurchaseID']
		multitrans_oneclick_record['TransID'] = transid
		multitrans_oneclick_record['TRANSGUID'] = full_record['TRANSGUID']
		multitrans_oneclick_record['RelatedTransID'] = multitrans_base_record['TransID']
		print(f"OneClick WS => Eticket: {eticket} | Type: {pricepoint_type} | Processor: {multitrans_base_record['Processor']} "
		      f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")

		return multitrans_oneclick_record, oneclick_record # #

#------------------------------------------------------------------------------------------------------------------------------------------------------------------ Instant Conversion POS and WS
def instant_conversion(option, eticket, pricepoint_type, multitrans_base_record, email, selected_options, merchantbillconfig):
	transguid = ''
	url = ''
	multitrans_ic_record = copy.deepcopy(multitrans_base_record)
	token = multitrans_base_record['TRANSGUID']
	username = fake.user_name() + str(random.randint(333, 999))
	password = fake.user_name() + str(random.randint(333, 999))

	if option == 'pos':

		url = f"{config.urlic}{token}" + selected_options
		print(url)

		page_loaded = navigate_to_url(url)
		if page_loaded == False:
			return None
		else:
			if br.is_element_present_by_id('TransGUID', wait_time=10):
				transguid = br.find_by_id('TransGUID').value
				transguid = subprocess.run(
					['C:\segpay\pos\point_of_sale\/transguid\TransGuidDecoderApp.exe', transguid, '-l'],
					stdout=subprocess.PIPE)
				transguid = transguid.stdout.decode('utf-8')
			else:
				print("Transguid not Found ")
				return None
			br.find_by_id('EMailInput').fill(email)
			# if br.find_by_id('UserNameInput'):
			#     br.find_by_id('UserNameInput').fill(username)
			# if br.find_by_id('PasswordInput'):
			#     br.find_by_id('PasswordInput').fill(password)
			br.find_by_id('SecurePurchaseButton').click()

			ic_record = dbs.multitrans_full_record('', transguid, '')
			full_record = ic_record[0]
			multitrans_ic_record['TransSource'] = 122
			multitrans_ic_record['TransType'] = 108
			multitrans_ic_record['TransStatus'] = 186
			multitrans_ic_record['PurchaseID'] = full_record['PurchaseID']
			multitrans_ic_record['TransID'] = full_record['TransID']
			multitrans_ic_record['TRANSGUID'] = transguid
			multitrans_ic_record['RelatedTransID'] = multitrans_base_record['TransID']
			multitrans_ic_record['TransAmount'] = merchantbillconfig['RebillPrice']
			exchange_rate = 1
			if merchantbillconfig['Currency'] == multitrans_base_record['MerchantCurrency']:
				exchange_rate = 1
			else:
				exchange_rate = dbs.exc_rate(multitrans_base_record['MerchantCurrency'], merchantbillconfig['Currency'])
				if multitrans_base_record['MerchantCurrency'] != 'JPY':
					exchange_rate = round(exchange_rate, 2)
			multitrans_ic_record['ExchRate'] = exchange_rate
			markup = round(merchantbillconfig['RebillPrice'] * exchange_rate, 2)
			multitrans_ic_record['Markup'] = markup
			print(f"InstantConversion POS => Eticket: {eticket} | Type: {pricepoint_type} | Processor: {multitrans_base_record['Processor']} "
			      f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")

			return multitrans_ic_record, ic_record

	# if pricepoint_type == 511:
	#     data_from_paypage['initialprice511'] = pricingguid['InitialPrice']
	#     data_from_paypage['initiallength511'] = pricingguid['InitialLength']
	#     data_from_paypage['recurringlength511'] = pricingguid['RecurringLength']
	#     data_from_paypage['recurringprice511'] = pricingguid['RecurringPrice']
	# elif pricepoint_type == 510:
	#     data_from_paypage['initialprice510'] = dynamic_price

	elif option == 'ws':
		if pricepoint_type == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			multitrans_ic_record['TransAmount'] = dynamic_price
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			url = f"https://stgsvc.segpay.com/OneClickSales.asmx/SalesService?eticketid={eticket}&amount={dynamic_price}" \
				      f"&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={token}" + selected_options
		elif pricepoint_type == 511:
			pricingguid = dbs.get_pricingguid(multitrans_base_record['MerchantID'], pricepoint_type)[0]
			url = f"https://stgsvc.segpay.com/OneClickSales.asmx/SalesService?eticketid={eticket}" \
				      f"&DynamicPricingID={pricingguid['PricingGuid']}&octoken={token}" + selected_options

		else:
			url = f"{config.urlicws}{token}" + selected_options
		print(url)

		resp = requests.get(url)
		xml_return_string = simplexml.loads(resp.content)
		transid = int(xml_return_string['TransReturn']['TransID'])
		oneclick_record = dbs.multitrans_full_record(transid, '', '')
		full_record = oneclick_record[0]

		if pricepoint_type in [501, 506, 511]:
			multitrans_ic_record['TransSource'] = 121
		else:
			multitrans_ic_record['TransSource'] = 123
		multitrans_ic_record['TransType'] = 1011
		multitrans_ic_record['TransStatus'] = 186
		multitrans_ic_record['PurchaseID'] = full_record['PurchaseID']
		multitrans_ic_record['TransID'] = transid
		multitrans_ic_record['TRANSGUID'] = full_record['TRANSGUID']
		multitrans_ic_record['RelatedTransID'] = multitrans_base_record['TransID']
		print(f"OneClick WS => Eticket: {eticket} | Type: {pricepoint_type} | Processor: {multitrans_base_record['Processor']} "
		      f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")

		return multitrans_ic_record, oneclick_record


def FillDefault(url, selected_options):
	page_loaded = navigate_to_url(url)
	if page_loaded == False:
		return None
	#email = 'qateam@segpay.com'  # fake.email()
	email =fake.email()
	email = email.replace(email.split("@",1)[1],"yopmail.com")
	print(email)
	if br.is_element_present_by_id('TransGUID', wait_time=10):
		transguid = br.find_by_id('TransGUID').value
		# print(transguid)
		transguid = subprocess.run(['C:\segpay\pos\point_of_sale\/transguid\TransGuidDecoderApp.exe', transguid, '-l'],
		                           stdout=subprocess.PIPE)
		transguid = transguid.stdout.decode('utf-8')
	# print (transguid)
	else:
		print("Transguid not Found ")
		return None

	# C:\segpay\pos\point_of_sale\transguid\TransGuidDecoderApp.exe
	cc = 4444333322221111 # 4444333322221111
	transbin = int(str(cc)[:6])
	card_encrypted = dbs.encrypt_card(cc)
	month = ['01', '02', '03', '04']
	expiration_date = random.choice(month)
	year = ['21', '22', '23', '24']
	year = f"20{random.choice(year)}"
	cvv = random.randint(111, 999)
	cvv = str(cvv)
	firstname = fake.first_name()
	lastname = fake.last_name()
	zip = random.randint(11111, 99999)
	email_encrypt = dbs.encrypt_email(email)
	username = fake.user_name() + str(random.randint(333, 999))
	password = fake.user_name() + str(random.randint(333, 999))

	data_from_paypage = {'transguid': transguid,
	                     'cc': cc,
	                     'expiration_date': expiration_date,
	                     'year': year,
	                     'cvv': cvv,
	                     'firstname': firstname,
	                     'lastname': lastname,
	                     'email_encrypt': email_encrypt,
	                     'email': email,
	                     'username': username,
	                     'password': password,
	                     'zip': str(zip),
	                     'card_encrypted': card_encrypted,
	                     'transbin': transbin
	                     }

	# print(transguid)
	merchant_currency = br.find_by_id('CurrencyDDL').select(selected_options[0])
	paypage_lnaguage = br.find_by_id('LanguageDDL').select(selected_options[1])
	time.sleep(2)
	if config.enviroment == 'stage':
		br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
	elif config.enviroment == 'qa':
		br.find_by_id('CreditCardInput').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
	elif config.enviroment == 'stage2':
		br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput

	br.find_by_id('CCExpMonthDDL').select(expiration_date)
	br.find_by_id('CCExpYearDDL').select(year)
	if config.enviroment == 'stage':
		br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
	elif config.enviroment == 'qa':
		br.find_by_id('CVVInput').fill(cvv)  # new CVVInputNumeric old CVVInput
	elif config.enviroment == 'stage2':
		br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
	br.find_by_id('FirstNameInput').fill(firstname)
	br.find_by_id('LastNameInput').fill(lastname)
	br.find_by_id('ZipInput').fill(zip)
	# br.find_by_id('CountryDDL').fill('999')
	br.find_by_id('EMailInput').fill(email)
	if br.find_by_id('UserNameInput'):
		br.find_by_id('UserNameInput').fill(username)
	if br.find_by_id('PasswordInput'):
		br.find_by_id('PasswordInput').fill(password)

	merchant_country = br.find_by_id('CountryDDL').value

	data_from_paypage['merchant_currency'] = br.find_by_id('CurrencyDDL').value
	data_from_paypage['paypage_lnaguage'] = br.find_by_id('LanguageDDL').value
	data_from_paypage['merchant_country'] = merchant_country
	br.find_by_id('SecurePurchaseButton').click()
	return data_from_paypage


def create_transaction(pricepoint_type, eticket, selected_options, enviroment, merchantid, url_options, processor):
	#url = ''
	joinlink = ''
	pricingguid = {}
	dynamic_price = ''
	try:
		if pricepoint_type == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			print(hash_url)
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			joinlink = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST{url_options}"
		elif pricepoint_type == 511:
			pricingguid = dbs.get_pricingguid(merchantid, pricepoint_type)[0]
			joinlink = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}{url_options}"  # PricingGuid, InitialPrice
		else:
			joinlink = config.url + eticket + url_options

		print(joinlink)

		data_from_paypage = FillDefault(joinlink, selected_options)  # fill the page and return what was populated
		transguid = data_from_paypage['transguid']
		full_record = dbs.multitrans_full_record('', transguid, '')  # transid_purchaseid = dbs.multitrans_val(transguid)
		data_from_paypage['PurchaseID'] = full_record[0]['PurchaseID']
		data_from_paypage['TransID'] = full_record[0]['TransID']
		if pricepoint_type == 511:
			data_from_paypage['initialprice511'] = pricingguid['InitialPrice']
			data_from_paypage['initiallength511'] = pricingguid['InitialLength']
			data_from_paypage['recurringlength511'] = pricingguid['RecurringLength']
			data_from_paypage['recurringprice511'] = pricingguid['RecurringPrice']
		elif pricepoint_type == 510:
			data_from_paypage['initialprice510'] = dynamic_price

		processor_name = {
			26: 'PAYVISIONWE',
			42: 'ROCKETGATEISO',
			57: 'SPCATISO',
			44: 'PAYVISIONPRIVMS',
			65: 'SPKAISO1'
		}
		data_from_paypage['processor'] = processor_name[processor]
		data_from_paypage['full_record'] = full_record

		print(f"New SignUp => Mid: {merchantid} | Eticket: {eticket} | Type: {pricepoint_type} | Processor: {data_from_paypage['processor']} |"
		      f" DMC: {data_from_paypage['merchant_currency']} | Lnaguage: {data_from_paypage['paypage_lnaguage']}")

		return data_from_paypage
	except Exception as ex:
		print(ex)
		print(f"Module web Function: create_transaction(pricepoint_type, eticket, selected_options, enviroment, merchantid, url_options, processor)")

def browser_quit():
	br.quit()
