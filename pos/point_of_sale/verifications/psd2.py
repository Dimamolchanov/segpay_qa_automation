import traceback
import simplexml
from termcolor import colored
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions

db_agent = DBActions()


def cardinal3dsrequests(transid): # card
	live_record = {}; psd2_completed_mt = []; card = {} ;failed = {} ;sql = '' ; pid = 0 ;psd2_failed = []
	item = ''

	try:
		visa_secure = config.test_data['visa_secure']
		sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authreponse " \
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
					print("No record found")
				else:
					xml_return_string = simplexml.loads(live_record['lookuprresponse'])
					response = xml_return_string['CardinalMPI']

					try:
						for item in card:
							base_field = card[item]
							if base_field == '':
								base_field = {}
							live_field = response[item]
							if item == 'Cavv':
								if live_field == '':
									print("Cavv Field field is empty")
								else:
									base_field = live_field
							# elif item == 'ACSUrl' and base_field == '':
							#     base_field = {}
							#
							# elif item == 'Payload' and base_field == '':
							#     base_field = {}
							# elif item == 'ErrorDesc' and base_field == '':
							#     base_field = {}

							if base_field != live_field:
								print(f"Field : {item} BaseField: {base_field}  => Live_Field : {live_field}  ")
								failed[transid][item] = f"Field : {item} BaseField: {base_field}  => Live_Field : {live_field} "
						if len(failed) == 0:
							print(colored(f"Cardinal3dsRequests test_case: {config.test_data['cc']} Records Compared => Pass ", 'green'))
						return failed

					except Exception as ex:
						traceback.print_exc()
						print(f"3DS verification MissMatch")
						print(f"{Exception}  Field: {item,} ")
						pass
			else:
				live_record = db_agent.execute_select_with_no_params(sql)
				if live_record == None:
					print(colored(f"Merchant Configured for PSD2 => No record found | TransID: {transid} | CC: {config.test_data['cc']} | PPID: {config.test_data['package'][0]['PrefProcessorID']}", 'blue'))
				else:
					print(colored(f"Response received from Cardinal - Not a cardinal test case card {config.test_data['cc']}  => Pass ", 'green'))

		print()
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}  Tid: {transid,} ")
		pass
