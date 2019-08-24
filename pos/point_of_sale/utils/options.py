import random
import string
from pos.point_of_sale.utils import constants
from pos.point_of_sale.config import config
import traceback
import simplexml
from termcolor import colored
from pos.point_of_sale.db_functions.dbactions import DBActions
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
	refurl = '&refurl=wwww.test.com/' + tmpurl
	return refurl


def ref_variables():
	refs = f"&ref1={randomString(5)}&ref2={randomString(4)}&ref3={randomString(5)}&ref4={randomString(4)}" \
	       f"&ref5={randomString(5)}&ref6={randomString(4)}&ref7={randomString(5)}&ref8={randomString(4)}" \
	       f"&ref9={randomString(5)}&ref10={randomString(4)}"
	return refs


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


def pricepoints_options(pricepoints_options, merchantid):
	pricepoints = []
	if pricepoints_options == 'single':
		pricepoints = [100120]
	elif pricepoints_options == 'type':
		pricepoints = db_agent.pricepoint_type(merchantid, [501, 502, 503, 504, 505, 506, 510, 511])
	elif pricepoints_options == 'list':
		pricepoints = db_agent.pricepoint_list(merchantid)
	return pricepoints


def string_after(value, a):
	# Find and validate first part.
	pos_a = value.rfind(a)
	if pos_a == -1: return ""
	# Returns chars after the found string.
	adjusted_pos_a = pos_a + len(a)
	if adjusted_pos_a >= len(value): return ""
	return value[adjusted_pos_a:]


def is_visa_secure():
	is_card_eu = False
	result = ''
	card_type = 'US'
	try:
		is_merchant_configured = db_agent.execute_select_two_parameters(constants.GET_DATA_FROM_3D_SECURE_CONFIG, config.test_data['MerchantID'], config.test_data['PackageID'])
		is_eu_merchant = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MERCHANT_EXTENSION, config.merchants[0])['VISARegion']

		if is_merchant_configured: config.test_data['3ds'] = True
		if is_eu_merchant:
			config.test_data['Merchant'] = 'EU'
		else:
			config.test_data['Merchant'] = 'US'

		cc_card = config.test_data['cc']
		cc_bin = cc_card[0:9]
		is_card = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_GLOBALBINDETAILS, cc_bin)
		eu_countries = ['BE', 'BG', 'BL', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GF', 'GG', 'GI', 'GP', 'GR', 'HR', 'HU', 'IE', 'IM', 'IS', 'IT', 'JE', 'LI', 'LT', 'LU', 'LV', 'MF', 'MQ', 'MT']
		if is_card and is_card['IssCountry'] in eu_countries:
			is_card_eu = True
			card_type = 'EU'
		if is_card and is_card['PrePaid'] == 'Y':
			card_type= 'Prepaid'
			result =  0  # no 3ds

		elif is_merchant_configured and not is_card_eu:
			result = 1  # 3ds but no psd
		elif not is_merchant_configured and is_card_eu:
			result = 2  # will be decline in scope
		elif not is_merchant_configured and not is_card_eu:
			result = 3  # no 3ds no psd2
		elif is_merchant_configured and is_card_eu:
			result = 4  # 3ds psd2
		config.test_data['card_type'] = card_type
		return result
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass


def aprove_decline(transid):
	aprove_or_decline = None
	result_type = 0
	cardinal_result = {}
	in_or_aout_scope = 0
	try:
		if config.test_data['visa_secure'] in [1, 3, 4, 5]:
			sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authresponse " \
			      f" from Cardinal3dsRequests where transguid =  (select Transguid from multitrans where transid = {transid})"
			live_record_3ds = db_agent.execute_select_with_no_params(sql)
			if live_record_3ds:
				xml_return_string_lookuprresponse = simplexml.loads(live_record_3ds['lookuprresponse'])
				response = xml_return_string_lookuprresponse['CardinalMPI']
				if not live_record_3ds['authresponse'] == '':
					json_authresponse = json.loads(live_record_3ds['authresponse'])
					auth_response = {**json_authresponse['Payload'],
					                 **json_authresponse['Payload']['Payment']['ExtendedData']}

					if 'ECIFlag' in auth_response:
						response['EciFlag'] = auth_response['ECIFlag']
					if 'CAVV' in auth_response:
						response['Cavv'] = auth_response['CAVV']
					if 'PAResStatus' in auth_response:
						response['PAResStatus'] = auth_response['PAResStatus']
					if 'SignatureVerification' in auth_response:
						response['SignatureVerification'] = auth_response['SignatureVerification']
				if config.test_data['visa_secure'] == 4:
					in_or_aout_scope = 1171
					if response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'Y' and response['SignatureVerification'] == 'Y':
						# 1151	Successful Authentication
						result_type = 1151
					elif response['Cavv'] and response['EciFlag'] == '06' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'A' and response['SignatureVerification'] == 'Y':
						# 1152	Authentication Attempted
						result_type = 1152
					else:
						result_type = 999
				elif config.test_data['visa_secure'] in [1, 3, 5]:
					in_or_aout_scope = 1172
					if not 'Cavv' in response and response['EciFlag'] == '07' and not 'PAResStatus' in response:
						# 1158	Failed Authentication
						result_type = 1158
					elif response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] in ['Y', 'A'] and response['SignatureVerification'] == 'N':
						# Signature Verification Failure
						result_type = 1157
						print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
					elif not 'Cavv' in response and response['EciFlag'] == '07' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'N' and response['SignatureVerification'] == 'Y':
						# Failed Authentication
						result_type = 1159
						print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
					elif response['Cavv'] == {} and response['EciFlag'] == '06' and response['Enrolled'] == 'N' and not 'PAResStatus' in response and not 'SignatureVerification' in response:
						# Non-Enrolled Card/Non-participating bank
						result_type = 1153
					elif response['Cavv'] == {} and response['EciFlag'] == '07' and response['Enrolled'] == 'U' and not 'PAResStatus' == {} and not 'SignatureVerification' == {}:
						# 1154	Authentication Unavailable
						result_type = 1154
					elif response['Cavv'] == {} and response['EciFlag'] == '07' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'U' and response['SignatureVerification'] in ['Y', 'N']:
						# 1155	Authentication Unavailable at Issuer
						result_type = 1155
					elif response['Cavv'] == {} and response['EciFlag'] == '07' and response['Enrolled'] == 'B' and not 'PAResStatus' in response and not 'SignatureVerification' in response:
						# 1156	Authentication Bypassed
						result_type = 1156
					elif response['Cavv'] == {} and not 'EciFlag' in response and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'Error' and not 'SignatureVerification' in response:
						# 1158	Authentication Error
						result_type = 1158

			if result_type == 999:
				msg = "In Scope |PSD2 Required|"
				aprove_or_decline = False
				print(colored(f"This Transaction should be declined |{msg}|  <----------------", 'red', attrs=['bold']))
			else:
				final_action = db_agent.cardinal_actions(result_type, in_or_aout_scope)
				if in_or_aout_scope == 1171:
					msg = "In Scope |PSD2 Required|"
				else:
					msg = "Out of Scope |PSD2 NOT Required|"
				if final_action:
					if final_action['ResultAction'] == 1181:
						aprove_or_decline = True
						print(colored(f"This Transaction should be aproved |{msg}|  <---------------- | ResultType: {result_type} | ResultAction: 1181 | ", 'grey', attrs=['bold']))
					elif final_action['ResultAction'] == 1182:
						aprove_or_decline = False
						print(colored(f"This Transaction should be declined |{msg}|  <---------------- | ResultType: {result_type} | ResultAction: 1182 | ", 'red', attrs=['bold']))
		elif config.test_data['visa_secure'] == 0:
			aprove_or_decline = True
			print(colored(f"This Transaction should be aproved |Prepaid Card|  <---------------- | ", 'grey', attrs=['bold']))

		config.test_data['aprove_or_decline'] = aprove_or_decline
		return aprove_or_decline
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass


def joinlink():
	pricingguid = {}
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
			joinlink = config.url + d['eticket'] + d['url_options']
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
