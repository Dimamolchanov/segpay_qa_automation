import random
import string
from pos.point_of_sale.utils import constants
from pos.point_of_sale.config import config
import traceback
import simplexml
from termcolor import colored
from pos.point_of_sale.db_functions.dbactions import DBActions
import json

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


#
# ref1 = randomString(4)
# ref2 = randomString(4)
# ref3 = randomString(5)
# ref4 = randomString(6)
# ref5 = randomString(4)
# ref6 = randomString(4)
# ref7 = randomString(4)
# ref8 = randomString(2)
# ref9 = randomString(11)
# ref10 = randomString(8)
# return ref1,ref4


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
	try:
		is_merchant_configured = db_agent.execute_select_two_parameters(constants.GET_DATA_FROM_3D_SECURE_CONFIG, config.merchants[0], config.packageid)
		is_eu_merchant = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_MERCHANT_EXTENSION, config.merchants[0])['VISARegion']
		cc_card = config.test_data['cc']
		cc_bin = cc_card[0:9]
		is_card = db_agent.execute_select_one_parameter(constants.GET_DATA_FROM_GLOBALBINDETAILS, cc_bin)
		eu_countries = ['BE', 'BG', 'BL', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GF', 'GG', 'GI', 'GP', 'GR', 'HR', 'HU', 'IE', 'IM', 'IS', 'IT', 'JE', 'LI', 'LT', 'LU', 'LV', 'MF', 'MQ', 'MT']
		if is_card and is_card['IssCountry'] in eu_countries:
			is_card_eu = True
		if is_card and is_card['PrePaid'] == 'Y':
			return 0  # no 3ds
		elif is_merchant_configured and not is_card_eu:
			return 1  # 3ds but no psd
		elif not is_merchant_configured and is_card_eu:
			return 2  # will be decline in scope
		elif not is_merchant_configured and not is_card_eu:
			return 3  # no 3ds no psd2
		elif is_merchant_configured and is_card_eu:
			return 4  # 3ds psd2

	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass


def aprove_decline(transid):
	aprove_or_decline = None
	try:
		if config.test_data['visa_secure'] in [3,4]:
			sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authresponse " \
			      f" from Cardinal3dsRequests where transguid =  (select Transguid from multitrans where transid = {transid})"
			live_record_3ds = db_agent.execute_select_with_no_params(sql)
			if live_record_3ds:
				if not live_record_3ds['authresponse'] == '':
					json_authresponse = json.loads(live_record_3ds['authresponse'])
					auth_response = {**json_authresponse['Payload'],
					                 **json_authresponse['Payload']['Payment']['ExtendedData']}
					xml_return_string_lookuprresponse = simplexml.loads(live_record_3ds['lookuprresponse'])
					response = xml_return_string_lookuprresponse['CardinalMPI']
					if config.test_data['visa_secure'] == 4:
						if response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'Y' and response['SignatureVerification'] == 'Y':
							print(colored(f"This Transaction should be aproved |PSD2 Required|", 'grey', attrs=['bold']))
							aprove_or_decline = True
						elif response['Cavv'] and response['EciFlag'] == '06' and response['Enrolled'] == 'Y' and response['PAResStatus'] == 'A' and response['SignatureVerification'] == 'Y':
							print(colored(f"This Transaction should be aproved |PSD2 Required|", 'grey', attrs=['bold']))
							aprove_or_decline = True
						else:
							print(colored(f"This Transaction should be declined|PSD2 Required|", 'white', 'on_grey', attrs=['bold']))
							aprove_or_decline = False
					elif config.test_data['visa_secure'] == 3:
						override_settings = 'db'
						if response['Cavv'] and response['EciFlag'] == '05' and response['Enrolled'] == 'Y' and response['PAResStatus'] in ['Y', 'A'] and response['SignatureVerification'] == 'N':
							print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
						elif response['Cavv'] and response['EciFlag'] == '07' and response['Enrolled'] == 'Y' and response['PAResStatus'] in ['Y', 'A'] and response['SignatureVerification'] == 'Y':
							print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
						# work in it
						elif response['Cavv'] and response['EciFlag'] == '07' and response['Enrolled'] == 'Y' and response['PAResStatus'] in ['Y', 'A'] and response['SignatureVerification'] == 'Y':
							if override_settings == 1:
								print(colored(f"This Transaction should be aproved|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))
							elif override_settings == 0 :
								print(colored(f"This Transaction should be declined|PSD2 not Required|", 'white', 'on_grey', attrs=['bold']))








		config.test_data['aprove_or_decline'] = aprove_or_decline
		return aprove_or_decline





	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass
