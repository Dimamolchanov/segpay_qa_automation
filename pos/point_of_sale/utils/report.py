import traceback
from datetime import datetime
from functools import partial
from pos.point_of_sale.bep import bep
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.runners import test_methods
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web
from pos.point_of_sale.utils import options
from termcolor import colored
from datetime import datetime
from datetime import timedelta


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
		if d['visa_secure'] == 4:
			form = 'Extended'
		if d['Type'] == 501:
			descr = 'Recurring'
		elif d['Type'] == 502:
			descr = 'One Time'
		elif d['Type'] == 503:
			descr = 'Digital Purchase'
		elif d['Type'] == 505:
			descr = 'Delayed Capture'
		elif d['Type'] == 506:
			descr = 'Instant Conversion'
		elif d['Type'] == 510:
			descr = 'Dynamic Pricing'
		elif d['Type'] == 511:
			descr = 'Dynamic Recurring'
		cardinal_aprove_cards = [4000000000001000, 4000000000001091, 4000000000001026]  # 4000000000001026
		cardinal_decline_cards = [4000000000001018, 4000000000001125, 4000000000001133, 4000000000001034, 4000000000001042, 4000000000001059, 4000000000001067, 4000000000001075, 4000000000001083, 4000000000001109, 4000000000001117]

		if d['3ds'] == False:
			msg = colored('This Transaction should be Aproved', 'geen')
			aproved_declined = True
		elif int(d['cc']) in cardinal_aprove_cards:
			msg = colored('This Transaction should be Aproved', 'green')
			if d['cc'] == '4000000000001000': cardinal_case = "Test Case 1: Successful Frictionless Authentication"
			if d['cc'] == '4000000000001091': cardinal_case = "Test Case 10: Successful Step Up Authentication"
			if d['cc'] == '4000000000001026': cardinal_case = "Test Case 3: Attempts Stand-In Frictionless Authentication"
			aproved_declined = True
		elif d['card_type'] == 'Prepaid':
			msg = colored('This Transaction should be Aproved', 'green')

			aproved_declined = True
		elif int(d['cc']) in cardinal_decline_cards:
			msg = colored("This Transaction should be Declined", 'red')
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
			msg = colored("This Transaction should be Declined", 'red') + " - | Note: Can be aproved based on the settings in CardinalResultActions if ResultAction = 1181'"
			# msg = 'This Transaction should be Declined - | Note: Can be aproved based on the settings in CardinalResultActions if ResultAction = 1181'
			purch_tatus = 806
		if 'ref' in d['url_options']:
			checkrefs = True
		if 'refurl' in d['url_options']:
			checkrefurl = True
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

		if d['3ds'] and (d['cc'] in cardinal_aprove_cards or d['cc'] in cardinal_decline_cards):
			cardinal_check = f"Cardinal3dsRequests should have a response from Cardinal for {cardinal_case}"
		else:
			cardinal_check = f"Cardinal3dsRequests should have the response from Cardinal"

		tmp = colored('Scenario:', 'blue', attrs=['bold'])
		print(colored(tmp, 'blue', attrs=['underline']))
		print("___________________________________________________________________________________________________________________________________________________________________________________")
		tr_type = colored("SignUp Transaction", 'blue')
		tmp = colored(cardinal_case, 'yellow')
		print(f"{tr_type} | Merchant: {d['Merchant']} | 3DS Configured: {d['3ds']}  | Card: {d['card_type']} | In Scope: {'True'}  | Cardinal - {tmp} ")
		print(f"PricePoint Type: {d['BillConfigID']} - {descr}  | DMC: {d['dmc']} | Language: {d['lang']} | Processor PoolID: {d['processor']} |DMCStatus = {d['DMCStatus']} | CollectUserInfo: {d['CollectUserInfo']}                                ")
		print("___________________________________________________________________________________________________________________________________________________________________________________")
		print()
		tmp = colored('Prerequisite:', 'magenta', attrs=['bold'])
		print(colored(tmp, 'magenta', attrs=['underline']))
		print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
		print(f"MerhcantID: {d['MerchantID']} | Card: {d['cc']} | Eticket: {d['eticket']} | Template: {d['PayPageTemplate']} | Link: {d['link']}  ")
		# print('------------------------------------------------------------------------------------------------------------------------------------------------')
		print()
		tmp = colored('Expected Results:', 'green', attrs=['bold'])
		print(colored(tmp, 'green', attrs=['underline']))
		print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
		print(f"PayPage:     | Form should be: {form} | {msg}")
		print(f"Multitranse: | AuthCode: 'OK:0' | TxStatus: 2 | TransSource: 121 | TransStatus: 184 | TransType: 101 | RefVariables: {checkrefs} | RefURL: {checkrefurl}                                                                                 ")
		print(f"Assets:      | PurchStatus: {purch_tatus} | PurchType: {d['Type']} | Processor: {processor_name[d['processor']]} | UserName: {username} | Password: {password} | RefVariables: {checkrefs} | RefURL: {checkrefurl}                ")
		print(f"Email:       | PointOfSaleEmailQueue should have | EmailType: 981 | in the que with Status: 863 (Complete)")
		print(f"PostBacks:   | PostBackNotifications should have: | {postbacks} PostBacks Type   with | PostResults: Ok | with Status: 863 (Complete)")
		print(f"3DS:         | {cardinal_check}")

		print()
		print()
		tmp = colored('Actual Results:', 'magenta', attrs=['bold'])
		print(colored(tmp, 'green', attrs=['underline']))
		print("___________________________________________________________________________________________________________________________________________________________________________________")
	except Exception as ex:
		traceback.print_exc()
		print(f"{Exception}")
		pass
