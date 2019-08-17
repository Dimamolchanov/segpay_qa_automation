import traceback
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import options
from pos.point_of_sale.web import web
from pos.point_of_sale.verifications import postback_service
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.verifications import asset
from termcolor import colored

db_agent = DBActions()


def sign_up_trans_web1(test_data):  # Yan
	test_data = config.test_data  # refactor needs
	current_transaction_record = {}
	for selected_language in config.available_languages:
		for dmc in config.available_currencies:
			try:
				selected_options = [dmc, selected_language]
				url_options = options.ref_variables() + options.refurl() + config.template
				config.test_data['url_options'] = url_options
				print("======================================| SignUp Transaction |======================================\n")
				config.logging.info('print("======================================| SignUp Transaction |======================================\n")')
				current_transaction_record = web.create_transaction(test_data['pricepoint_type'], test_data['eticket'], selected_options, config.merchants[0], url_options, config.processors[0])
				if current_transaction_record['full_record']['Authorized']:
					config.oc_tokens[current_transaction_record['full_record']['PurchaseID']] = config.test_data['pricepoint_type']
					TransActionService.verify_signup_transaction(current_transaction_record)
				else:
					result = current_transaction_record['full_record']
					print(colored(f"Transaction DECLINED : AuthCode:{result['AuthCode']} ",'red',attrs=['bold']))
					print()
			except Exception as ex:
				traceback.print_exc()
				print(f"{Exception}")
				config.logging.info(f"{Exception} ")
				pass

	return current_transaction_record
def signup_oc(oc_type, eticket, test_data):  # Yan  # refactor
	result = True
	one_click_record = {}
	for current_transaction_id in config.transaction_records:
		try:
			print("\n======================================|       OneClick     |======================================\n")
			pricepoint = current_transaction_id['full_record']['BillConfigID']
			config.test_data = TransActionService.prepare_data(pricepoint, 1)
			selected_options = [current_transaction_id['merchant_currency'], current_transaction_id['paypage_lnaguage']]
			eticket = config.test_data['eticket']
			octoken = current_transaction_id['PurchaseID']
			if oc_type == 'pos':
				one_click_record = web.one_click_pos(eticket, octoken, selected_options, config.test_data['url_options'])
			elif oc_type == 'ws':
				one_click_record = web.one_click_services(eticket, octoken, selected_options, config.test_data['url_options'])
			if one_click_record['Authorized']:
				result &= TransActionService.verify_oc_transaction(octoken, eticket, one_click_record, config.test_data['url_options'], selected_options)
			else:
				print(colored(f"OneClick Transaction DECLINED : AuthCode:{one_click_record['AuthCode']}",'red', attrs=['bold']))
				print()
		except Exception as ex:
			traceback.print_exc()
			print(f"{Exception}  ")
			pass
	return result
def signup_oc_all(oc_type, eticket, test_data):  # Yan  # refactor
	result = True
	one_click_record = {}
	octokens = config.oc_tokens.keys()
	for current_transaction_id in config.transaction_records:
		for token in octokens:
			try:
				print("\n======================================|       OneClick     |======================================\n")
				config.logging.info("\n======================================|       OneClick     |======================================\n")
				config.logging.info('')
				pricepoint = current_transaction_id['full_record']['BillConfigID']
				config.test_data = TransActionService.prepare_data(pricepoint, 1)
				selected_options = [current_transaction_id['merchant_currency'], current_transaction_id['paypage_lnaguage']]
				eticket = config.test_data['eticket']
				octoken = token
				if oc_type == 'pos':
					one_click_record = web.one_click_pos(eticket, octoken, selected_options, config.test_data['url_options'])
				elif oc_type == 'ws':
					one_click_record = web.one_click_services(eticket, octoken, selected_options, config.test_data['url_options'])
				result &= TransActionService.verify_oc_transaction(octoken, eticket, one_click_record, config.test_data['url_options'], selected_options)
			except Exception as ex:
				traceback.print_exc()
				print(f"{Exception}  ")
				config.logging.info(f"{Exception}  ")
				pass
	return result
def verify_refunds():  # Yan
	#refunds = config.refunds[1]
	sql = ''
	pid = 0
	rkeys = config.refunds[1]
	differences_mt_refunds = mt.multitrans_check_refunds()
	differences_asset_refunds = asset.asseets_check_refunds()
	for tid in rkeys:
		try:
			sql = "Select * from multitrans where TransID = {}"
			record_data = db_agent.execute_select_one_parameter(sql, tid)
			if record_data['TransStatus'] == 182:
				sql = "Select * from multitrans where PurchaseID = {} and TransType = 107 and RelatedTransID = {}"
			else:
				sql = "Select * from multitrans where PurchaseID = {} and TransType = 102 and RelatedTransID = {}"
			live_record = db_agent.execute_select_two_parameters(sql, record_data['PurchaseID'], tid)
			differences_postback = postback_service.verify_postback_url("refund", config.packageid, live_record['TransID'])
		except Exception as ex:
			traceback.print_exc()
			print(f"{Exception} ")
			config.logging.info(f"{Exception}")
			pass
	pass

	if not differences_mt_refunds and not differences_asset_refunds:
		return True
	else:
		return False
