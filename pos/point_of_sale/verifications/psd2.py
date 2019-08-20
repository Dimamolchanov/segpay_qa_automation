import traceback
import simplexml
from termcolor import colored
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
import json

db_agent = DBActions()


def cardinal3dsrequests(transid):  # card
	live_record = {}
	psd2_completed_mt = []
	card = {}
	failed = {}
	sql = ''
	pid = 0
	psd2_failed = []
	item = ''
	try:
		visa_secure = config.test_data['visa_secure']
		base_field = ''
		live_field = ''
		sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authresponse " \
		      f" from Cardinal3dsRequests where transguid =  (select Transguid from multitrans where transid = {transid})"
		if visa_secure == 1:
			live_record = db_agent.execute_select_with_no_params(sql)
			if live_record == None:
				print(colored(f"Merchant Configured for 3DS not in scope  => No record found | TransID: {transid} | CC: {config.test_data['cc']} | PPID: {config.test_data['package'][0]['PrefProcessorID']}", 'blue'))
			else:
				print(colored(f"Response received from Cardinal - Not a cardinal test case card {config.test_data['cc']}  => Pass ", 'green'))
		elif visa_secure == 4:
			if config.test_data['cc'] in config.cards_3ds:
				card = config.cards_3ds[config.test_data['cc']]
				try:
					if 'card' in card:
						del card['card']
						del card['cmpi_authenticate response']
				except Exception as ex:
					traceback.print_exc()
					print(f"Card is not in the dictionary")
					print(f"{Exception}")
					pass

				live_record = db_agent.execute_select_with_no_params(sql)
				if live_record == None:
					print(colored(f"No record recieved from Cardinal - In Scope", 'red'))
					print()
				else:
					if not live_record['authresponse'] == '':
						json_authresponse = json.loads(live_record['authresponse'])
						# auth_response = json_authresponse['Payload']['Payment']['ExtendedData']
						auth_response = {**json_authresponse['Payload'], **json_authresponse['Payload']['Payment']['ExtendedData']}
						for item in card:
							try:
								if item == 'cPAResStatus':
									base_field = card[item]
									live_field = auth_response['PAResStatus']
								elif item == 'cSignatureVerification':
									base_field = card[item]
									live_field = auth_response['SignatureVerification']
								elif item == 'cCavv':
									base_field = 'value'
									live_field = auth_response['CAVV']
									if live_field != '':
										live_field = 'value'
								elif item == 'cEciFlag':
									base_field = card[item]
									live_field = auth_response['ECIFlag']
								elif item == 'cErrorNo':
									base_field = card[item]
									live_field = auth_response['ErrorNumber']
								elif item == 'cErrorDesc':
									base_field = card[item]
									live_field = auth_response['ErrorDescription']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
									if base_field == '<blank>' or base_field == '':
										base_field = {}
								if base_field != live_field:
									failed[item] = f"{base_field}split{live_field} | SCA Required |"

							except Exception as ex:
								traceback.print_exc()
								failed[item] = f"{base_field} split | Expected_Field is missing from Auth_response | SCA Required"
								# print(f"Expected_Field: | {item[1:]} | is missing from Auth_response")
								# print()
								pass

					xml_return_string_lookuprresponse = simplexml.loads(live_record['lookuprresponse'])
					response = xml_return_string_lookuprresponse['CardinalMPI']
					for item in card:
						try:
							if item[0] != 'c':
								if item == 'Enrolled':
									base_field = card[item]
									live_field = response['Enrolled']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
								elif item == 'PAResStatus':
									base_field = card[item]
									live_field = response['PAResStatus']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
								elif item == 'SignatureVerification':
									base_field = card[item]
									live_field = response['SignatureVerification']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
								elif item == 'Cavv':
									if card[item] == '':
										base_field = {}
										live_field = response['Cavv']
								elif item == 'EciFlag':
									base_field = card[item]
									live_field = response['EciFlag']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
								elif item == 'ACSUrl':
									base_field = card[item]
									live_field = response['ACSUrl']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
									elif base_field == '<value>':
										base_field = 'https://0merchantacsstag.cardinalcommerce.com/MerchantACSWeb/creq.jsp'
								elif item == 'Payload':
									base_field = card[item]
									live_field = response['Payload']
									if base_field == '<blank>' or base_field == '':
										base_field = {}
									elif base_field == '<value>':
										base_field = live_field
								elif item == 'ErrorNo':
									base_field = card[item]
									live_field = response['ErrorNo']
								elif item == 'ErrorDesc':
									base_field = card[item]
									live_field = response['ErrorDesc']
									if base_field == '<blank>' or base_field == '':
										base_field = {}

								if base_field != live_field:
									failed[item] = f"{base_field}split{live_field}"
						except Exception as ex:
							traceback.print_exc()
							failed[item] = f"{base_field} split | Expected_Field is missing from CardinalMPI |"
							# print(f"Expected_Field: | {item} | is missing from CardinalMPI")
							print()
							pass

			else:
				live_record = db_agent.execute_select_with_no_params(sql)
				if live_record == None:
					print(colored(f"Merchant Configured for PSD2 => No record found | TransID: {transid} | CC: {config.test_data['cc']} | PPID: {config.test_data['package'][0]['PrefProcessorID']}", 'blue'))
					print()
				else:
					print(colored(f"Response received from Cardinal - Not a cardinal test case card {config.test_data['cc']}  => Pass ", 'green'))

			if len(failed) > 0:
				print()
				print(colored(f"********************* 3DS verification MissMatch *********************", 'red'))
				for item in failed:
					tmp = failed[item].split('split')
					print(f"Field : {item} =>  Expected BaseField: {tmp[0]}  | Actual : {tmp[1]}  ")
				print()
			if len(failed) == 0 and live_record:
				print(colored(f"Cardinal3dsRequests test_case: {config.test_data['cc']} Records Compared => Pass ", 'green'))
				print()
			return failed
		print()
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}  Tid: {transid,} ")
		pass
