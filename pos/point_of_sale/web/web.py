import random
import decimal
from splinter import Browser
from faker import Faker
import subprocess
from selenium import webdriver
import time
from datetime import datetime
from xml.etree.ElementTree import fromstring
import simplexml
import requests
import copy
import traceback
import os
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.bep import bep
from selenium.common.exceptions import *
from pos.point_of_sale.utils import constants
from pos.point_of_sale.utils import options
from termcolor import colored

db_agent = DBActions()



chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-position=-1400,0")

fake = Faker()

# def start_browser():
br = Browser(driver_name='chrome', options=chrome_options)

path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'transguid\\TransGuidDecoderApp.exe')


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
			retry_count = retry_count + 1
			time.sleep(1)

def one_click_pos(eticket,octoken,currency_lang,url_options):
	oneclick_record = None
	dynamic_price = 9999
	pricingguid = ''
	try:
		# eticket = config.test_data['eticket']
		ppid = eticket.split(':')
		multitrans_oneclick_record = {}
		sql = "select * from MerchantBillConfig where BillConfigID = {}"
		mbconfig = db_agent.execute_select_one_parameter(sql, ppid[1])
		pricepoint_type = mbconfig['Type']
		merchantid = mbconfig['MerchantID']
		username = 'UserName' + str(random.randint(333, 999))
		password = 'Password' + str(random.randint(333, 999))

		if pricepoint_type == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			url = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}" + url_options
		elif pricepoint_type == 511:
			pricingguid = db_agent.get_pricingguid(merchantid, pricepoint_type)[0]
			url = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
		else:
			url = f"{config.url}{eticket}&octoken={octoken}" + url_options

		print(url)
		config.logging.info(url)

		page_loaded = navigate_to_url(url)
		if page_loaded == False:
			return None
		else:
			if br.is_element_present_by_id('TransGUID', wait_time=10):
				transguid = br.find_by_id('TransGUID').value
				transguid = subprocess.run(
					['C:\\segpay_qa_automation\\pos\\point_of_sale\\transguid\\TransGuidDecoderApp.exe', transguid, '-l'],

					stdout=subprocess.PIPE)
				transguid = transguid.stdout.decode('utf-8')
			else:
				print("Transguid not Found ")
				return None
			if currency_lang[1] != 'EN':
				paypage_lnaguage = br.find_by_id('LanguageDDL').select(currency_lang[1])
				time.sleep(2)
			br.find_by_id('CVVInputNumeric').fill('333')
			if br.find_by_id('UserNameInput'):
				br.find_by_id('UserNameInput').fill(username)
			if br.find_by_id('PasswordInput'):
				br.find_by_id('PasswordInput').fill(password)
			while br.execute_script("return jQuery.active == 0") != True:
				time.sleep(1)
			br.find_by_id('SecurePurchaseButton').click()
			time.sleep((2))
			try:
				if br.get_iframe('Cardinal-CCA-IFrame'):
					with br.get_iframe('Cardinal-CCA-IFrame') as iframe:
						if iframe.find_by_name('challengeDataEntry'):
							iframe.find_by_name('challengeDataEntry').fill('1234')
							iframe.find_by_value('SUBMIT').click()
						elif iframe.get_iframe('authWindow'):
							with iframe.get_iframe('authWindow') as auth:
								auth.find_by_id('password').fill('test')
								auth.find_by_name('UsernamePasswordEntry').click()
						else:
							pass
			except NoSuchFrameException:
				pass
			except Exception as ex:
				traceback.print_exc()
				print(ex)
				config.logging.info(ex)

			cnt = 0
			while oneclick_record == None and cnt < 15:
				cnt += 1
				time.sleep(1)
				sql = "select * from multitrans where TransGuid = '{}'"
				oneclick_record = db_agent.execute_select_one_parameter(sql, transguid)

			if pricepoint_type == 511:
				oneclick_record['511'] = pricingguid
			elif pricepoint_type == 510:
				oneclick_record['510'] = dynamic_price
			token_type = config.oc_tokens[octoken]
			card = db_agent.execute_select_one_parameter(constants.GET_PAYMENTACCT_FROM_ASSET, octoken)
			visa_secure = options.is_visa_secure()

			if visa_secure == 0:
				print(colored(f"OneClick |  Prepaid card  | Short Form | CC_Card: {card['cc']}  | POS ", 'white', 'on_blue', attrs=['bold']))
				config.logging.info(colored(f"OneClick |  Prepaid card  | Short Form ", 'blue'))
			elif visa_secure == 1:
				print(colored(f"OneClick |  3DS configured - Not in Scope  for PSD2 | Short Form | CC_Card: {card['cc']}  | POS ", 'white', 'on_blue', attrs=['bold']))
				config.logging.info(colored(f"OneClick |  3DS configured - Not in Scope  for PSD2 | Short Form | CC_Card: {card['cc']}  | POS", 'blue'))
			elif visa_secure == 2:
				print(colored(f"OneClick |  3DS not configured | In Scope  for PSD2 | Short Form | CC_Card: {card['cc']}  | POS ", 'white', 'on_blue', attrs=['bold']))
				config.logging.info(colored(f"OneClick |  3DS not configured | In Scope  for PSD2 | Short Form | CC_Card: {card['cc']}  | POS ", 'blue', attrs=['bold']))  # will decline
			elif visa_secure == 3:
				print(colored(f"OneClick |  3DS not configured | Not in Scope  for PSD2 | Short Form | CC_Card: {card['cc']}  | POS ", 'white', 'on_blue', attrs=['bold']))
				config.logging.info(colored(f"OneClick |  3DS not configured | Not in Scope  for PSD2 | Short Form | CC_Card: {card['cc']}  | POS ", 'blue'))
			elif visa_secure == 4:
				print(colored(f"OneClick |  3DS  configured |  in Scope  for PSD2 | Extended Form | CC_Card: {card['cc']}  | POS ", 'white', 'on_blue', attrs=['bold']))
				config.logging.info(colored(f"OneClick |  3DS  configured |  in Scope  for PSD2 | Extended Form | CC_Card: {card['cc']}  | POS", 'blue'))

			print(f"OneClick POS => Eticket: {eticket}  | Processor: {oneclick_record['Processor']} "
			      f"| DMC: {currency_lang[0]} | Lnaguage: {currency_lang[1]} | Type: {pricepoint_type} TokenType: {token_type} ")
			print(f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}")
			config.logging.info(f"OneClick POS => Eticket: {eticket}  | Processor: {oneclick_record['Processor']} "
			                    f"| DMC: {currency_lang[0]} | Lnaguage: {currency_lang[1]} | Type: {pricepoint_type} TokenType: {token_type}")
			config.logging.info(f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}")
			config.logging.info('')

	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}  Eticket: {eticket}  ")
		config.logging.info(f"{Exception}  Eticket: {eticket}  ")
		pass

	return oneclick_record  # , pricepoint_type

def one_click_services(eticket,octoken,currency_lang,url_options):
	oneclick_record = None ; dynamic_price = 9999 ; pricingguid = ''


	try:
		ppid = eticket.split(':')
		multitrans_oneclick_record = {}
		sql = "select * from MerchantBillConfig where BillConfigID = {}"
		mbconfig = db_agent.execute_select_one_parameter(sql, ppid[1])
		pricepoint_type = mbconfig['Type']
		merchantid = mbconfig['MerchantID']
		if pricepoint_type == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			url = f"{config.urlws}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}" + url_options
		elif pricepoint_type == 511:
			pricingguid = db_agent.get_pricingguid(merchantid, pricepoint_type)[0]
			url = f"{config.urlws}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
		else:
			url = f"{config.urlws}{eticket}&octoken={octoken}" + url_options
		print(url)
		resp = requests.get(url)
		xml_return_string = simplexml.loads(resp.content)
		transid = int(xml_return_string['TransReturn']['TransID'])
		# oneclick_record = db_agent.multitrans_full_record(transid, '', '')
		# full_record = oneclick_record[0]

		cnt = 0
		while oneclick_record == None and cnt < 15:
			cnt += 1
			time.sleep(1)
			sql = "select * from multitrans where TransID = '{}'"
			oneclick_record = db_agent.execute_select_one_parameter(sql, transid)

		if pricepoint_type == 511:
			oneclick_record['511'] = pricingguid
		elif pricepoint_type == 510:
			oneclick_record['510'] = dynamic_price
		print(f"OneClick Web Services => Eticket: {eticket}  | Processor: {oneclick_record['Processor']} "
		      f"| DMC: {currency_lang[0]} | Lnaguage: {currency_lang[1]} | Type: {pricepoint_type}")
		print(f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}")
		return oneclick_record




	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}  Eticket: {eticket} Module => one_click_services ")
		pass
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------ 1click POS and WS
def one_click(option, eticket, pricepoint_type, multitrans_base_record, email, url_options, selected_options):
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
			url = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={token}" + url_options
		elif pricepoint_type == 511:
			pricingguid = db_agent.get_pricingguid(multitrans_base_record['MerchantID'], pricepoint_type)[0]
			url = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={token}" + url_options
		else:
			url = f"{config.url}{eticket}&octoken={token}" + url_options
		print(url)

		page_loaded = navigate_to_url(url)
		if page_loaded == False:
			return None
		else:
			if br.is_element_present_by_id('TransGUID', wait_time=10):
				transguid = br.find_by_id('TransGUID').value
				transguid = subprocess.run([path, transguid, '-l'],

					stdout=subprocess.PIPE)
				transguid = transguid.stdout.decode('utf-8')
			else:
				print("Transguid not Found ")
				return None
			paypage_lnaguage = br.find_by_id('LanguageDDL').select(selected_options[1])
			time.sleep(2)
			if br.find_by_id('EMailInput'):
			    br.find_by_id('EMailInput').fill(email)
			br.find_by_id('CVVInputNumeric').fill('123')
			#br.find_by_id('EMailInput').fill(email)
			br.find_by_id('CVVInputNumeric').fill('333')
			if br.find_by_id('UserNameInput'):
				br.find_by_id('UserNameInput').fill(username)
			if br.find_by_id('PasswordInput'):
				br.find_by_id('PasswordInput').fill(password)
			br.find_by_id('SecurePurchaseButton').click()
			while br.execute_script("return jQuery.active == 0") != True:
				time.sleep(1)
			if br.get_iframe('Cardinal-CCA-IFrame'):
			    with br.get_iframe('Cardinal-CCA-IFrame') as iframe:
				    with iframe.get_iframe('authWindow') as auth:
					    auth.find_by_id('password').fill('test')
					    auth.find_by_name('UsernamePasswordEntry').click()

			oneclick_record = db_agent.multitrans_full_record('', transguid, '')
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
				      f"&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={token}" + url_options  # + '&DMCURRENCY=JPY'
		elif pricepoint_type == 511:
			pricingguid = db_agent.get_pricingguid(multitrans_base_record['MerchantID'], pricepoint_type)[0]
			url = f"{config.urlws}{eticket}" \
				      f"&DynamicPricingID={pricingguid['PricingGuid']}&octoken={token}" + url_options

		else:
			url = f"{config.urlws}{eticket}&octoken={token}" + url_options
		print(url)

		resp = requests.get(url)
		xml_return_string = simplexml.loads(resp.content)
		transid = int(xml_return_string['TransReturn']['TransID'])
		oneclick_record = db_agent.multitrans_full_record(transid, '', '')
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

		return multitrans_oneclick_record, oneclick_record  # #


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------ Instant Conversion POS and WS
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
				transguid = subprocess.run([path, transguid, '-l'], stdout=subprocess.PIPE)
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

			ic_record = db_agent.multitrans_full_record('', transguid, '')
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
				exchange_rate = db_agent.exc_rate(multitrans_base_record['MerchantCurrency'], merchantbillconfig['Currency'])
				if multitrans_base_record['MerchantCurrency'] != 'JPY':
					exchange_rate = round(exchange_rate, 2)
			multitrans_ic_record['ExchRate'] = exchange_rate
			markup = round(merchantbillconfig['RebillPrice'] * exchange_rate, 2)
			multitrans_ic_record['Markup'] = markup
			print(f"InstantConversion POS => Eticket: {eticket} | Type: {pricepoint_type} | Processor: {multitrans_base_record['Processor']} "
			      f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")

			return multitrans_ic_record, ic_record

	elif option == 'ws':
		url = f"{config.urlicws}{token}" + selected_options
		print(url)
		resp = requests.get(url)
		xml_return_string = simplexml.loads(resp.content)
		transid = int(xml_return_string['TransReturn']['TransID'])
		oneclick_record = db_agent.multitrans_full_record(transid, '', '')
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


def FillDefault(url, selected_options, merchantid, packageid):
	page_loaded = navigate_to_url(url)
	if page_loaded == False:
		return None
	email = 'qateam@segpay.com'  # fake.email()
	config.test_data['cc'] = '4000000000001026'# '5432768030017007'#'4444333322221111' for decline 4000000000001133
	visa_secure = options.is_visa_secure()
	if visa_secure == 0:
		print(colored(f"Email: {email}   |  Prepaid card  | Short Form | Card {config.test_data['cc']} ", 'yellow','on_grey', attrs=['blink']))
		config.logging.info(colored(f"Email: {email}   |  Prepaid card  | Short Form ", 'blue'))
	elif visa_secure == 1:
		print(colored(f"Email: {email}   |  3DS configured - Not in Scope  for PSD2 | Short Form | Card {config.test_data['cc']} ", 'yellow','on_grey', attrs=['blink']))
		config.logging.info(colored(f"Email: {email}   |  3DS configured - Not in Scope  for PSD2 | Short Form | Card {config.test_data['cc']}", 'blue'))
	elif visa_secure== 2:
		print(colored(f"Email: {email}   |  3DS not configured | In Scope  for PSD2 | Short Form | Card {config.test_data['cc']} ", 'yellow','on_grey', attrs=['blink']))
		config.logging.info(colored(f"Email: {email}   |  3DS not configured | In Scope  for PSD2 | Short Form | Card {config.test_data['cc']} ", 'blue', attrs=['bold']))  # will decline
	elif visa_secure== 3:
		print(colored(f"Email: {email}   |  3DS not configured | Not in Scope  for PSD2 | Short Form | Card {config.test_data['cc']} ", 'yellow','on_grey', attrs=['blink']))
		config.logging.info(colored(f"Email: {email}   |  3DS not configured | Not in Scope  for PSD2 | Short Form | Card {config.test_data['cc']} ", 'blue'))
	elif visa_secure== 4:
		print(colored(f"Email: {email}   |  3DS  configured |  in Scope  for PSD2 | Extended Form | Card {config.test_data['cc']} ", 'yellow','on_grey', attrs=['blink']))
		config.logging.info(colored(f"Email: {email}   |  3DS  configured |  in Scope  for PSD2 | Extended Form | Card {config.test_data['cc']}", 'blue'))
	config.test_data['visa_secure'] = visa_secure
	if br.is_element_present_by_id('TransGUID', wait_time=10):
		transguid = br.find_by_id('TransGUID').value
		transguid = subprocess.run([path, transguid, '-l'], stdout=subprocess.PIPE)
		transguid = transguid.stdout.decode('utf-8')
	else:
		print("Transguid not Found ")
		return None
	sql = f"select top 1 * from [MerchantCC3DSecureConfig] where merchantid = {merchantid} and segpayprocessorid = " \
		f"(select top 1 ProcessorID from ProcessorPoolsDetail where CardType = 'VISA' " \
		f"and  ppid = ( select  PrefProcessorID from package where packageid = {packageid}))"
	#visa_secure = db_agent.execute_select_two_parameters(sql, merchantid, packageid)
	#config.test_data['cc'] = random.choice(config.random_cards)
	cc = config.test_data['cc']
	transbin = int(str(cc)[:6])
	card_encrypted = db_agent.encrypt_card(cc)
	if not db_agent.execute_select_one_parameter(constants.FRAUD_CARD_CHECK, card_encrypted):
		db_agent.execute_insert(constants.FRAUD_CARD_INSERT, card_encrypted)
	month = ['01', '02', '03', '04']
	expiration_date = random.choice(month)
	year = ['21', '22', '23', '24']
	year = f"20{random.choice(year)}"
	cvv = str(random.randint(111, 999))
	firstname = fake.first_name()
	lastname = fake.last_name()
	zip = random.randint(11111, 99999)
	email_encrypt = db_agent.encrypt_email(email)
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
	elif config.enviroment == 'stage3':
		br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
	while br.execute_script("return jQuery.active == 0") != True:
		time.sleep(1)
	br.find_by_id('CCExpMonthDDL').select(expiration_date)
	br.find_by_id('CCExpYearDDL').select(year)
	if config.enviroment == 'stage':
		br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
	elif config.enviroment == 'qa':
		br.find_by_id('CVVInput').fill(cvv)  # new CVVInputNumeric old CVVInput
	elif config.enviroment == 'stage2':
		br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
	elif config.enviroment == 'stage3':
		br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
	br.find_by_id('FirstNameInput').fill(firstname)
	br.find_by_id('LastNameInput').fill(lastname)

	#br.find_option_by_text('Florida').first.click()
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
	while br.execute_script("return jQuery.active == 0") != True:
		time.sleep(1)

	if not visa_secure == 4:
		if br.find_by_id('PhoneNumberInput').__getattr__('visible'):
			print('Form SHould be short eeeeeeeeeeeeeeee')

	br.find_by_id('SecurePurchaseButton').click()

	time.sleep((2))
	try:
		if br.get_iframe('Cardinal-CCA-IFrame'):
			with br.get_iframe('Cardinal-CCA-IFrame') as iframe:
				if iframe.find_by_name('challengeDataEntry'):
					iframe.find_by_name('challengeDataEntry').fill('1234')
					iframe.find_by_value('SUBMIT').click()
				elif iframe.get_iframe('authWindow'):
					with iframe.get_iframe('authWindow') as auth:
						auth.find_by_id('password').fill('test')
						auth.find_by_name('UsernamePasswordEntry').click()
				else:
					pass
	except NoSuchFrameException:
		pass
	except Exception as ex:
		traceback.print_exc()
		print(ex)
		config.logging.info(ex)
		config.logging.info('')
	return data_from_paypage


def create_transaction(pricepoint_type, eticket, selected_options, merchantid, url_options, processor):
	# url = ''
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
			pricingguid = db_agent.get_pricingguid(merchantid, pricepoint_type)[0]
			joinlink = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}{url_options}"  # PricingGuid, InitialPrice
		else:
			joinlink = config.url + eticket + url_options

		print(joinlink)
		config.logging.info(joinlink)
		data_from_paypage = FillDefault(joinlink, selected_options, merchantid, config.packageid)  # fill the page and return what was populated
		transguid = data_from_paypage['transguid']
		sql = "select * from multitrans where TransGuid = '{}'"
		full_record = db_agent.execute_select_one_with_wait(sql, transguid)
		#print(full_record['PurchaseID'])
		data_from_paypage['PurchaseID'] = full_record['PurchaseID']
		data_from_paypage['TransID'] = full_record['TransID']
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
		      f" DMC: {data_from_paypage['merchant_currency']} | Lnaguage: {data_from_paypage['paypage_lnaguage']} Card: {config.test_data['cc']}")
		print(f"PurchaseID: {data_from_paypage['PurchaseID']} | TransID: {data_from_paypage['TransID']} | TransGuid: {data_from_paypage['transguid']}")
		config.logging.info(f"New SignUp => Mid: {merchantid} | Eticket: {eticket} | Type: {pricepoint_type} | Processor: {data_from_paypage['processor']} |"
		      f" DMC: {data_from_paypage['merchant_currency']} | Lnaguage: {data_from_paypage['paypage_lnaguage']} Card: {config.test_data['cc']}")
		config.logging.info(f"PurchaseID: {data_from_paypage['PurchaseID']} | TransID: {data_from_paypage['TransID']} | TransGuid: {data_from_paypage['transguid']}")
		return data_from_paypage
	except Exception as ex:
		print(ex)
		config.logging.info(ex)
		traceback.print_exc()
		print(f"Module web Function: create_transaction(pricepoint_type, eticket, selected_options, enviroment, merchantid, url_options, processor)")
		config.logging.info(f"Module web Function: create_transaction(pricepoint_type, eticket, selected_options, enviroment, merchantid, url_options, processor)")


def reactivate(transids):
	transguids = {}
	reactivated = []
	asset_reactivated = {}
	mt_reactivated = {}
	not_reactivated = []


	tid = ''
	reactivate_tids = bep.get_data_before_action(transids, 'reactivation')
	sql = "Select TransGuid from Multitrans where TransID = {} "  # and TransType in ( 101,1011)
	try:
		for tid in reactivate_tids[1]:
			try:
				pid = reactivate_tids[1][tid]['PurchaseID']
				purch_type = reactivate_tids[0][pid]['PurchType']

				if purch_type in [501,506,505,511]:
					transguid = reactivate_tids[1][tid]['TRANSGUID']
					reactivate_record = reactivate_tids[1][tid]
					#pid = reactivate_tids[1][tid]['PurchaseID']

					config.test_data['zip'] = '33063'
					config.test_data['firstname'] = fake.first_name()
					config.test_data['lastname'] = fake.last_name()
					cc = config.test_data['cc'] # 4444333322221111
					config.test_data['month'] = '02'
					config.test_data['year'] = '2025'
					config.test_data['cvv'] = '888'
					joinlink = f"{config.reactivation_url}{transguid}&sprs=mp"
					tasks_type_status = db_agent.tasks_table(tid)
					db_agent.update_package(reactivate_record['PackageID'], reactivate_record['MerchantID'], reactivate_record['BillConfigID'])
					navigate_to_url(joinlink)
					time.sleep(1)





					if 'This subscription is not eligible for reactivation.' in br.html:
						not_reactivated.append(f"This subscription is not eligible for reactivation => {transguid} | PurchaseID : {reactivate_record['PurchaseID']} | Type:{reactivate_tids[0][reactivate_record['PurchaseID']]['PurchType']} "
						                       f"| DMC: {reactivate_record['MerchantCurrency']} | RefundType: {tasks_type_status[0]} | TransType: {reactivate_record['TransType']}")
					else:
						if tasks_type_status[0] == 841:
							br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
							time.sleep(2)
							br.find_by_id('ZipInput').fill(config.test_data['zip'])
							br.find_by_id('FirstNameInput').fill(config.test_data['firstname'])
							br.find_by_id('LastNameInput').fill(config.test_data['lastname'] )
							br.find_by_id('CCExpMonthDDL').select(config.test_data['month'])
							br.find_by_id('CCExpYearDDL').select(config.test_data['year'])
							br.find_by_id('CVVInputNumeric').fill(config.test_data['cvv'])
							while br.execute_script("return jQuery.active == 0") != True:
								time.sleep(1)
							time.sleep(1)
							br.find_by_id('SecurePurchaseButton').click()
							time.sleep(2)
							try:
								if br.get_iframe('Cardinal-CCA-IFrame'):
									with br.get_iframe('Cardinal-CCA-IFrame') as iframe:
										if iframe.find_by_name('challengeDataEntry'):
											iframe.find_by_name('challengeDataEntry').fill('1234')
											iframe.find_by_value('SUBMIT').click()
										elif iframe.get_iframe('authWindow'):
											with iframe.get_iframe('authWindow') as auth:
												auth.find_by_id('password').fill('test')
												auth.find_by_name('UsernamePasswordEntry').click()
										else:
											pass
							except NoSuchFrameException:
								pass
							except Exception as ex:
								traceback.print_exc()
								print(ex)
								config.logging.info(ex)
							cnt = 0 ; reactivation_complete = None
							while reactivation_complete == None and cnt < 10:
								cnt += 1
								sql = "Select * from multitrans where PurchaseID = {} and TransSource = 127"
								reactivation_complete = db_agent.execute_select_one_parameter(sql, pid)
								time.sleep(1)
							if reactivation_complete == None:
								print(f"******* Warning => transaction with TransID: {tid} is not Reactiavted - Check Manually ! *******")
								config.logging.info(f"******* Warning => transaction with TransID: {tid} is not Reactiavted - Check Manually ! *******")
								raise Exception('norecord')
							else:
								time.sleep(1)
								reactivated.append(f"Subscription has been reactivated => {transguid} | PurchaseID : {reactivate_record['PurchaseID']} | Type:{reactivate_tids[0][reactivate_record['PurchaseID']]['PurchType']} "
								                   f"| DMC: {reactivate_record['MerchantCurrency']} | RefundType: {tasks_type_status[0]} | TransType: {reactivate_record['TransType']}")
						else:
							br.find_by_id('SecurePurchaseButton').click()
							time.sleep(1)
							reactivated.append(f"Subscription has been reactivated => {transguid} | PurchaseID : {reactivate_record['PurchaseID']} | Type:{reactivate_tids[0][reactivate_record['PurchaseID']]['PurchType']} "
							                   f"| DMC: {reactivate_record['MerchantCurrency']} | RefundType: {tasks_type_status[0]} | TransType: {reactivate_record['TransType']}")
						mt_reactivated[tid] = reactivate_tids[1]
						asset_reactivated[reactivate_record['PurchaseID']] = reactivate_tids[0]
			except Exception as ex:
				print(f"{Exception}  Tid: {tid,}  ")
				config.logging.info(ex)
				traceback.print_exc()
				pass

		print()

		if len(not_reactivated) > 0:
			print("*================================>   Subscriptions are not eligible for reactivation  <================================*")
			for i in not_reactivated:
				print(i)
				config.logging.info(i)
			print()
			config.logging.info('')
		print("*================================>   Subscriptions have been  reactivated      <================================*")
		for i in reactivated:
			print(i)
			config.logging.info(i)
		print()
		config.logging.info('')
		config.asset_reactivated = asset_reactivated
		config.mt_reactivated = mt_reactivated
		return asset_reactivated, mt_reactivated
	except Exception as ex:
		print(f"{Exception}  Tid: {tid,}  ")
		config.logging.info(f"{Exception}  Tid: {tid,}  ")
		traceback.print_exc()
		pass


# ==========================================================================================================================BEP
def rebill(pids):
	rebill_dates = {}
	before_rebill = {}
	# REFACTOR SQL:
	sql = "Select * from Assets where PurchaseID = {}"
	for pid in pids:
		# REFACTOR SQL:
		temp = db_agent.execute_select_one_parameter(sql, pid)
		# print(temp)
		before_rebill[pid] = temp
		temp = datetime.date(temp['NextDate'])
		if temp not in rebill_dates:
			rebill_dates[temp] = 1
	print("Starting Rebill")
	start_time = datetime.now()
	for rebill_date in rebill_dates:
		rebill_url = config.rebill_url + str(rebill_date) + '%2023:59:59'
		print(rebill_url)
		# br.driver.set_page_load_timeout(600)
		br.visit(rebill_url)
		while br.url != rebill_url:
			time.sleep(1)
		time.sleep(1)
	print("Finished Rebill")
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))
	if 'Rebills processing is done.' in br.html:
		return ['RebillsFinished', before_rebill]
	else:
		return ['Rebill=>SomethingWrong', before_rebill]


def captures(capture_date):
	captures_url = config.captures_url + str(capture_date)
	print("Starting Captures")
	start_time = datetime.now()
	br.visit(captures_url)
	print(captures_url)
	while br.url != captures_url:
		time.sleep(1)
	time.sleep(1)
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))
	print("End Captures")
	if 'Final working set:' in br.html:
		return 'CapturesFinished'
	else:
		return 'Captures=>SomethingWrong'


def refund():
	print("Starting Refund")
	start_time = datetime.now()
	br.visit(config.refund_url)
	print(config.refund_url)
	while br.url != config.refund_url:
		time.sleep(1)
	end_time = datetime.now()
	time.sleep(1)
	print('Duration: {}'.format(end_time - start_time))
	print("End Refund")
	if 'Application finished.' in br.html:
		return 'RefundFinished'
	else:
		return 'Refund=>SomethingWrong'


def browser_quit():
	br.quit()
