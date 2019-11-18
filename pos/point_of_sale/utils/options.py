import random
import string
from pos.point_of_sale.utils import constants
from pos.point_of_sale.config import config
import traceback
import simplexml
from termcolor import colored
from pos.point_of_sale.db_functions.dbactions import DBActions
import pymssql
from pos.point_of_sale.config import config
import json
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

def randomString(stringLength=10):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))

def refurl():
	tmpurl = randomString(270)
	refurl = '&refurl=wwww.regressesion.com/'  # + tmpurl
	return refurl

def collect_userinfo():
	collectinfo = [0, 1, 2]
	selected_option = ''
	try:
		selected_option = random.choice(collectinfo)
		return selected_option
	except Exception as ex:
		traceback.print_exc()
		return False

def get_error_from_log():
	connection = pymssql.connect(config.server, "SPStaff", 'Toccata200e', "aspnetdb")
	cur = connection.cursor(as_dict=True)
	cur.execute(constants.GET_ERRORS_FROM_THE_LOG)
	response = cur.fetchall()
	if not response:
		print(colored(f"No errors in the SegPayLogs in last 1 minute", 'blue', attrs=['bold', 'underline', 'dark']))
		connection.close()
		return None
	else:
		for line in response:
			print(f"ID: {response['Id']} Meage: {response['Message']}")
		print(colored(f"Errors in the SegPayLogs in last 1 minute:", 'red', attrs=['bold', 'underline', 'dark']))
		connection.close()

def joinlink_param():
	extra_param = '&merchantpartnerid=rgvalitor&foreignid=validmember1&natssess=djslkafq3rf0i3wmefk34q434'
	extra_param2 = "&x-auth-link=https://www.cnn.com&x-auth-text=you%20are%20approved&x-decl-link=https://www.trump.com&x-decl-text=you%20lose"
	extra_param3 = extra_param + extra_param2
	extra_param4 = ''
	prm = [extra_param, extra_param2, extra_param3, extra_param4]
	param = random.choice(prm)
	return param

def ref_variables():
	refs = f"&ref1={randomString(5)}&ref2={randomString(4)}&ref3={randomString(5)}&ref4={randomString(4)}" \
		   f"&ref5={randomString(5)}&ref6={randomString(4)}&ref7={randomString(5)}&ref8={randomString(4)}" \
		   f"&ref9={randomString(5)}&ref10={randomString(4)}"
	
	ref1 = f"&ref1={randomString(5)}&ref2={randomString(4)}"
	ref2 = f"&ref9={randomString(5)}&ref10={randomString(4)}"
	ref3 = f"&ref5={randomString(5)}&ref6={randomString(4)}&ref7={randomString(5)}&ref8={randomString(4)}"
	ref4 = f"&ref9={randomString(5)}"
	ref5 = f"&ref3={randomString(5)}&ref7={randomString(4)}"
	ref6 = ''
	refs = random.choice([refs, ref1, ref2, ref3, ref4, ref5, ref6])
	return refs

def joinlink_xbill():
	x_billname = "&x-billname=QA+Segpay"
	x_billemail = "&x-billemail=qateam@segpay.com"
	x_billaddr = "&x-billaddr=123+Segpay+Street"
	x_billcity = "&x-billcity=Philladelphia"
	x_billstate = "&x-billstate=PA"
	x_billzip = "&x-billzip=19116"
	x_billcntry = "&x-billcntry=US"
	x_many = x_billname + x_billemail
	x_bill_all = x_billaddr + x_billcity + x_billstate + x_billzip + x_billcntry
	x_bill_empty = ""
	x_bill_addr_state = x_billaddr + x_billstate
	x_bill_many = x_billaddr + x_billcity + x_billcntry
	x_bill_all1 = x_billname + x_billemail + x_billaddr + x_billcity + x_billstate + x_billzip + x_billcntry
	x_bill_list = [x_many, x_bill_all, x_bill_empty, x_bill_addr_state, x_bill_many, x_bill_all1]
	x_bill = random.choice(x_bill_list)
	return x_bill

def clear_data_for_merchant(merchantid):
	pricepoints = []
	try:
		merchant_us_or_eu = db_agent.merchant_us_or_eu(merchantid)
		if not merchant_us_or_eu['MerchantCountry'] == 'US': merchant_us_or_eu['MerchantCountry'] = 'EU'
		config.test_data['merchant_us_or_eu'] = merchant_us_or_eu['MerchantCountry']
		config.test_data['merchantid'] = merchantid
		config.oc_tokens = {}
		config.transaction_records = []
		if config.pricepoints_options == 'type':
			pricepoints = db_agent.pricepoint_type(merchantid, [511, 501, 506])  # ,505
		elif config.pricepoints_options == 'list':
			pricepoints = db_agent.pricepoint_list(merchantid)
		else:
			pricepoints = config.merchant_data[merchant_us_or_eu['MerchantCountry']][0]
		return pricepoints
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass

def collectuserinfo(cluf):
	try:
		if cluf == 0:
			Ocoriginaluserinfo = 1
		elif cluf == 1:
			Ocoriginaluserinfo = 2
	except Exception as ex:
		traceback.print_exc()
		pass

def oc_tokens(merchant):
	if merchant == 'EU':
		octoken = 200062198
	elif merchant == 'US':
		octoken = 200062808
	return octoken

def pricepoints_options(pricepoints_options, merchantid):
	pricepoints = []
	if pricepoints_options == 'single':
		pricepoints = [100120]
	elif pricepoints_options == 'type':
		pricepoints = db_agent.pricepoint_type(merchantid, [501, 502, 503, 504, 505, 506, 510, 511])
	elif pricepoints_options == 'list':
		pricepoints = db_agent.pricepoint_list(merchantid)
	return pricepoints

def approved_cards():
	approved_cards = ['4000000000001000', '4000000000001091']
	try:
		dmc = random.choice(approved_cards)
		return dmc
	except Exception as ex:
		traceback.print_exc()
		return False

def decline_cards():
	approved_cards = ['4000000000001000', '4000000000001091']
	try:
		dmc = random.choice(approved_cards)
		return dmc
	except Exception as ex:
		traceback.print_exc()
		return False

def string_after(value, a):
	# Find and validate first part.
	pos_a = value.rfind(a)
	if pos_a == -1: return ""
	# Returns chars after the found string.
	adjusted_pos_a = pos_a + len(a)
	if adjusted_pos_a >= len(value): return ""
	return value[adjusted_pos_a:]

def is_3DS(merchantid, packageid):
	try:
		is_merchant_configured = db_agent.execute_select_two_parameters(constants.GET_DATA_FROM_3D_SECURE_CONFIG, merchantid, packageid)
		return is_merchant_configured
	except Exception as ex:
		traceback.print_exc()
		pass

def is_EU(merchantid):
	try:
		is_eu_merchant = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MERCHANT_EXTENSION, merchantid)['VISARegion']
		return is_eu_merchant
	except Exception as ex:
		traceback.print_exc()
		pass

def random_dmc():
	dmc = ''
	currencies = ['USD', "AUD", "CAD", "CHF"]  # , "DKK", "EUR", "GBP", "NOK", 'RUB', "ILS", "INR", 'CZK']  # "HKD", "JPY", , "SEK"
	try:
		dmc = random.choice(currencies)
		return dmc
	except Exception as ex:
		traceback.print_exc()
		return False

def random_lang():
	available_languages = ['EN', 'ES', "PT", "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]
	try:
		lang = random.choice(available_languages)
		return lang
	except Exception as ex:
		traceback.print_exc()
		return False

def is_visa_secure():
	is_card_eu = False
	result = ''
	card_type = 'US'
	config.test_data['scope'] = False
	try:
		is_merchant_configured = db_agent.execute_select_two_parameters(constants.GET_DATA_FROM_3D_SECURE_CONFIG, config.test_data['MerchantID'], config.test_data['PackageID'])
		is_eu_merchant = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MERCHANT_EXTENSION, config.test_data['MerchantID'])['VISARegion']
		
		if is_merchant_configured:
			config.test_data['3ds'] = True
		else:
			config.test_data['3ds'] = False
		if is_eu_merchant == 1:
			config.test_data['Merchant'] = 'EU'
		else:
			config.test_data['Merchant'] = 'US'
		
		cc_card = config.test_data['cc']  # '4444333322221111' #
		cc_bin = cc_card[0:9]
		is_card = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_GLOBALBINDETAILS, cc_bin)
		eu_countries = ['BE', 'BG', 'BL', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GF', 'GG', 'GI', 'GP', 'GR', 'HR', 'HU', 'IE', 'IM', 'IS', 'IT', 'JE', 'LI', 'LT',
						'LU', 'LV', 'MF', 'MQ', 'MT']
		if is_card and is_card['IssCountry'] in eu_countries:
			is_card_eu = True
			card_type = 'EU'
		if is_card and is_card['PrePaid'] == 'Y':  # out of scope
			card_type = 'Prepaid'
			result = 0  # no 3ds
		elif config.test_data['Merchant'] == 'EU' and is_card_eu:  # Merchant EU, card is EU, not configured for 3ds in Scope decline  IN SCOPE
			result = 1  # 3ds psd2
			config.test_data['scope'] = True
		# elif config.test_data['Merchant'] == 'EU' and is_card_eu and is_merchant_configured:  # Merchant EU, card is EU, configured for 3ds
		# 	result = 2  # 3ds psd2
		# 	config.test_data['scope'] = True
		# elif is_merchant_configured:  # Any merchant configured but not in scope
		# 	result = 3  # 3ds psd2
		# config.test_data['scope'] = True
		else:
			result = 2  # Merchant not EU not in scope
		config.test_data['card_type'] = card_type
		return result
	except Exception as ex:
		traceback.print_exc()
		# print(f"{Exception}")
		pass

def aprove_decline(transid):
	aprove_or_decline = False
	result_type = 0
	cardinal_result = {}
	in_or_aout_scope = 0
	try:
		if config.test_data['visa_secure'] in [1, 2]:
			if config.test_data['Type'] == 505:
				sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authresponse " \
					  f" from Cardinal3dsRequests where transguid =  (select Transguid from multitrans where transid = {transid} and TransSource = 122 )"
			else:
				sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authresponse " \
					  f" from Cardinal3dsRequests where transguid =  (select Transguid from multitrans where transid = {transid})"
			
			live_record_3ds = db_agent.execute_select_with_no_params(sql)
			if live_record_3ds:
				xml_return_string_lookuprresponse = simplexml.loads(live_record_3ds['lookuprresponse'])
				response = xml_return_string_lookuprresponse['CardinalMPI']
				if 'Cavv' in response:
					if response['Cavv'] == {} or response['Cavv'] == '':
						response['Cavv'] = None
					else:
						response['Cavv'] = response['Cavv']
				else:
					response['Cavv'] = None
				if 'PAResStatus' in response:
					if response['PAResStatus'] == {} or response['PAResStatus'] == '':
						response['PAResStatus'] = None
					else:
						response['PAResStatus'] = response['PAResStatus']
				else:
					response['PAResStatus'] = None
				
				if 'EciFlag' in response:
					if response['EciFlag'] == {} or response['EciFlag'] == '':
						response['EciFlag'] = None
					else:
						response['EciFlag'] = response['EciFlag']
				else:
					response['EciFlag'] = None
				if 'SignatureVerification' in response:
					if response['SignatureVerification'] == {} or response['SignatureVerification'] == '':
						response['SignatureVerification'] = None
					else:
						response['SignatureVerification'] = response['SignatureVerification']
				else:
					response['SignatureVerification'] = None
				
				if not live_record_3ds['authresponse'] == '':
					json_authresponse = json.loads(live_record_3ds['authresponse'])
					auth_response = {**json_authresponse['Payload'],
									 **json_authresponse['Payload']['Payment']['ExtendedData']}
					
					if 'ECIFlag' in auth_response:
						if auth_response['ECIFlag'] == {} or auth_response['ECIFlag'] == '':
							response['EciFlag'] = None
						else:
							response['EciFlag'] = auth_response['ECIFlag']
					else:
						response['EciFlag'] = None
					if 'CAVV' in auth_response:
						if auth_response['CAVV'] == {} or auth_response['CAVV'] == '':
							response['Cavv'] = None
						else:
							response['Cavv'] = auth_response['CAVV']
					else:
						response['Cavv'] = None
					if 'PAResStatus' in auth_response:
						if auth_response['PAResStatus'] == {} or auth_response['PAResStatus'] == '':
							response['PAResStatus'] = None
						else:
							response['PAResStatus'] = auth_response['PAResStatus']
					else:
						response['PAResStatus'] = None
					if 'SignatureVerification' in auth_response:
						if auth_response['SignatureVerification'] == {} or auth_response['SignatureVerification'] == '':
							response['SignatureVerification'] = None
						else:
							response['SignatureVerification'] = auth_response['SignatureVerification']
					else:
						response['SignatureVerification'] = None
				
				if config.test_data['visa_secure'] == 1:
					# msg = "In Scope |PSD2 Required|"
					in_or_aout_scope = 1171
					if response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'Y' and response[
						'SignatureVerification'] == 'Y':
						# 1151	Successful Authentication
						result_type = 1151
					# aprove_or_decline = True
					elif response['Cavv'] and response['EciFlag'] == '06' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'A' and response[
						'SignatureVerification'] == 'Y':
						# 1152	Authentication Attempted
						result_type = 1152
					# aprove_or_decline = True
					else:
						result_type = 999
				
				elif config.test_data['visa_secure'] == 2:
					in_or_aout_scope = 1172
					if response['Cavv'] == None and response['EciFlag'] == '07' and 'PAResStatus' == None:
						# 1158	Failed Authentication
						result_type = 1158
					elif response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] in ['Y', 'A'] and response[
						'SignatureVerification'] == 'N':
						# Signature Verification Failure
						result_type = 1157
					# print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
					elif response['Cavv'] == None and response['EciFlag'] == '07' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'N' and response[
						'SignatureVerification'] == 'Y':
						# Failed Authentication
						result_type = 1159
					# print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
					elif response['Cavv'] == None and response['EciFlag'] == '06' and response['Enrolled'] == 'N' and response['PAResStatus'] == None and response[
						'SignatureVerification'] == None:
						# Non-Enrolled Card/Non-participating bank
						result_type = 1153
					elif response['Cavv'] == None and response['EciFlag'] == '07' and response['Enrolled'] == 'U' and response['PAResStatus'] == None and response[
						'SignatureVerification'] == None:
						# 1154	Authentication Unavailable
						result_type = 1154
					elif response['Cavv'] == None and response['EciFlag'] == '07' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'U' and response[
						'SignatureVerification'] in ['Y', 'N']:
						# 1155	Authentication Unavailable at Issuer
						result_type = 1155
					elif response['Cavv'] == None and response['EciFlag'] == '07' and response['Enrolled'] == 'B' and response['PAResStatus'] == None and response[
						'SignatureVerification'] == None:
						# 1156	Authentication Bypassed
						result_type = 1156
					elif response['Cavv'] == None and response['EciFlag'] == None and response['Enrolled'] == 'Y' and response['PAResStatus'] == None and response[
						'SignatureVerification'] == None:
						# 1158	Authentication Error
						result_type = 1158
					elif response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'Y' and response[
						'SignatureVerification'] == 'Y':
						# 1151	Successful Authentication
						result_type = 1151
					# aprove_or_decline = True
					elif response['Cavv'] and response['EciFlag'] == '06' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'A' and response[
						'SignatureVerification'] == 'Y':
						# 1152	Authentication Attempted
						result_type = 1152
					else:
						aprove_or_decline = False
			
			if result_type == 999:
				msg = "In Scope |PSD2 Required|"
				aprove_or_decline = False
			# print(colored(f"This Transaction should be declined |{msg}|  <----------------", 'red', attrs=['bold']))
			else:
				final_action = db_agent.cardinal_actions(result_type, in_or_aout_scope)
				if in_or_aout_scope == 1171:
					msg = "In Scope |PSD2 Required|"
				else:
					msg = "Out of Scope |PSD2 NOT Required|"
				if final_action:
					if final_action['ResultAction'] == 1181:
						aprove_or_decline = True
					# print(colored(f"This Transaction should be aproved |{msg}|  <---------------- | ResultType: {result_type} | ResultAction: 1181 | ", 'grey', attrs=['bold']))
					elif final_action['ResultAction'] == 1182:
						aprove_or_decline = False
				# print(colored(f"This Transaction should be declined |{msg}|  <---------------- | ResultType: {result_type} | ResultAction: 1182 | ", 'red', attrs=['bold']))
				else:
					aprove_or_decline = True
		# print(colored(f"This Transaction should be aproved |{msg}|  <---------------- | {msg}", 'grey', attrs=['bold']))
		elif config.test_data['visa_secure'] == 0:
			aprove_or_decline = True
		# print(colored(f"This Transaction should be aproved |Prepaid Card|  <---------------- | ", 'grey', attrs=['bold']))
		config.test_data['aprove_or_decline'] = aprove_or_decline
		return aprove_or_decline
	except Exception as ex:
		traceback.print_exc()
		# print(f"{Exception}")
		pass

def joinlink():
	pricingguid = {}
	extra_param = '&x-billname=QA+Segpay&x-billemail=qateam%40segpay.com&x-billaddr=123+Segpay+Street&x-billcity=Las+Vegas&x-billstate=ND&x-billzip=33063&x-billcntry=US&merchantpartnerid=rgvalitor&foreignid=validmember1&natssess=djslkafq3rf0i3wmefk34q434'
	joinlink = ''
	dynamic_price = ''
	d = config.test_data
	try:
		if d['Type'] == 510:
			dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
			hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
			print(hash_url)
			resp = requests.get(hash_url)
			dynamic_hash = fromstring(resp.text).text
			joinlink = f"{config.url}{d['eticket']}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST{d['url_options']}"
		elif d['Type'] == 511:
			pricingguid = db_agent.get_pricingguid(d['MerchantID'], d['Type'])[0]
			joinlink = f"{config.url}{d['eticket']}&DynamicPricingID={pricingguid['PricingGuid']}{d['url_options']}"  # PricingGuid, InitialPrice
		else:
			joinlink = config.url + d['eticket'] + d['url_options'] + extra_param
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

def append_list(msg):
	try:
		current_list = config.test_case['actual']
		current_list.append(msg)
		config.test_case['actual'] = current_list
	except Exception as ex:
		# traceback.print_exc()
		# print(f"{Exception}  Options.append_list")
		pass
