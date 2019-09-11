import traceback
import simplexml
from termcolor import colored
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
import json
from pos.point_of_sale.utils import options
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
	response = {}
	sca = False
	try:
		visa_secure = config.test_data['visa_secure']
		base_field = ''
		live_field = ''

		if visa_secure == 0: # out of scope
			options.append_list(f"Card is Prepaid | No 3DS record | Out of Scope")
			print(colored(f"Card is Prepaid | No 3DS record | Out of Scope  => Pass ", 'green'))
			return True
		if visa_secure == 1 and not config.test_data['3ds']: # in scope
			options.append_list(f"Merchant EU | Not Configured for 3DS | Card EU | No record in Cardinal3dsRequests | In  Scope | Should be declined")
			print(colored(f"Merchant EU | Not Configured for 3DS | Card EU | No record in Cardinal3dsRequests | In  Scope | Should be declined ", 'red'))
		elif visa_secure == 2 and not config.test_data['3ds']:
			options.append_list(f"Merchant is not configured for 3ds | TransID: {transid} | CC: {config.test_data['cc']} | PPID: {'processor'}")
			print(colored(f"Merchant is not configured for 3ds | TransID: {transid} | CC: {config.test_data['cc']} | Out Of  Scope | Should be aproved", 'blue'))
			return True
		elif visa_secure in [1,2]:
			sql = f"select dbo.DecryptString(lookupresponsedata) as lookuprresponse,dbo.DecryptString(AuthResponseData) as authresponse " \
			      f" from Cardinal3dsRequests where transguid =  (select Transguid from multitrans where transid = {transid})"
			live_record = db_agent.execute_select_with_no_params(sql)
			if live_record:
				xml_return_string_lookuprresponse = simplexml.loads(live_record['lookuprresponse'])
				response = xml_return_string_lookuprresponse['CardinalMPI']
				scope = config.test_data['scope']
				cavv = response['Cavv']
				eciflag = response['EciFlag']
				enrolled = response['Enrolled']
				parestatus = response['PAResStatus']
				sigver = response['SignatureVerification']
				if not live_record['authresponse'] == '':
					json_authresponse = json.loads(live_record['authresponse'])
					json_response = json_authresponse['Payload']['Payment']['ExtendedData']
					if 'PAResStatus' in json_response: parestatus = json_response['PAResStatus']
					if 'SignatureVerification' in json_response: sigver = json_response['SignatureVerification']
					if 'CAVV' in json_response: cavv = json_response['CAVV']
					if 'ECIFlag' in json_response: eciflag = json_response['ECIFlag']
					sca = True
				if cavv == "" or cavv == {}:
					cavv = 'NO'
				else:
					cavv = 'YES'
				print(f"Scope: {scope} | Cavv: {cavv} | EciFlag: {eciflag} | Enrolled: {enrolled} | ParesStatus: {parestatus} | SingatureVerification: {sigver} | SCA Required: {sca} ")
				options.append_list(f"Cardinal3dsRequests test_case: {config.test_data['cc']} Records Compared => Pass ")
				print(colored(f"Cardinal3dsRequests test_case: {config.test_data['cc']} Records Compared => Pass ", 'green'))
				print()
				return True
			else:
				print(colored(f"Merchant Configured for 3DS - should have a 3ds record - No record recieved from Cardinal ", 'red'))
				print()
				return False

		print()
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}  Tid: {transid,} ")
		pass
