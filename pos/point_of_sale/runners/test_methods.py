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
from pos.point_of_sale.utils import report
#from pos.point_of_sale.runners import run_package

db_agent = DBActions()


br = web.Signup()
def sign_up_trans_web():  # Yan
	pass_fail = False

	current_transaction_record = {}
	aprove_or_decline = None
	if config.test_data['Merchant'] == 'EU':
		currencies = config.test_data['eu_available_currencies']
	else:
		currencies = config.test_data['us_available_currencies']
	for selected_language in config.available_languages:
		# dmc_currencies = []
		config.test_data['lang'] = selected_language
		for dmc in currencies:
			config.test_data['dmc'] = dmc
			config.cnt = config.cnt + 1
			try:
				selected_options = [dmc, selected_language]
				url_options = options.ref_variables() + options.refurl() + config.template
				config.test_data['url_options'] = url_options
				options.joinlink()
				report.scenario()

				current_transaction_record = br.create_transaction(config.test_data['Type'],
																	config.test_data['eticket'], selected_options,
																	config.test_data['MerchantID'], url_options,
																	config.test_data['processor'])

				#current_transaction_record = web.create_transaction(config.test_data['Type'], config.test_data['eticket'], selected_options, config.test_data['MerchantID'], url_options, config.test_data['processor'])
				config.test_data['transaction_to_check'] = current_transaction_record
				aprove_or_decline = options.aprove_decline(current_transaction_record['TransID'])
				print(colored(f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}", 'yellow'))
				config.test_case['actual'] = [f"PurchaseID: {config.test_data['PurchaseID']} | TransId:{config.test_data['TransID']} | TransGuid: {config.test_data['transguid']}"]
				if current_transaction_record['full_record']['Authorized']:
					tmp = current_transaction_record['full_record']
					config.oc_tokens[tmp['PurchaseID']] = [config.test_data['Type'], tmp['MerchantCurrency'], tmp['Language']]
					result = current_transaction_record['full_record']
					tmpstr = f"Transaction Aproved : AuthCode:{result['AuthCode']}"
					print(colored(tmpstr, 'cyan', attrs=['bold']))

				else:
					result = current_transaction_record['full_record']
					tmpstr = f"Transaction DECLINED : AuthCode:{result['AuthCode']}"
					print(colored(tmpstr, 'red', attrs=['bold']))

				pass_fail = TransActionService.verify_signup_transaction(current_transaction_record)
				if pass_fail:
					pf = "Scenario completed: All Passed"
					print(colored(f"Scenario completed: All Passed", 'green', attrs=['bold', 'underline', 'dark']))
				else:
					print(colored(f"Scenario had some issues: Failed | Re-Check Manually |", 'red', attrs=['bold', 'underline', 'dark']))
					pf = "Scenario had some issues: Failed | Re-Check Manually |"

				options.append_list(tmpstr)
				options.append_list(pf)
				options.append_list('_____Finished Scenario_______')

				config.test_cases[config.test_data['TransID']] = config.test_case
				config.test_case = {}

				print(colored("___________________________________________________________Finished Scenario_______________________________________________________________________________________________________", 'grey', 'on_yellow', attrs=['bold', 'dark']))
				print()
				print()
			except Exception as ex:
				traceback.print_exc()
				print(f"{Exception}")
				pass

	return current_transaction_record


def signup_oc(oc_type, eticket, test_data):  # Yan  # refactor
	result = True
	one_click_record = {}
	for current_transaction_id in config.transaction_records:
		try:
			config.test_case = {}
			print("\n======================================|       OneClick     |======================================\n")
			pricepoint = current_transaction_id['full_record']['BillConfigID']
			config.test_data = TransActionService.prepare_data1(pricepoint, current_transaction_id['full_record']['PackageID'], 1)
			selected_options = [current_transaction_id['merchant_currency'], current_transaction_id['paypage_lnaguage']]
			eticket = config.test_data['eticket']
			octoken = current_transaction_id['PurchaseID']
			url_options = options.ref_variables() + options.refurl() + config.template
			config.test_data['url_options'] = url_options
			config.test_case['one_click_pos'] = f"One Click Started - Eticket: {eticket}"
			config.test_case['actual'] = f"One Click Results - Eticket: {eticket}"

			if oc_type == 'pos':
				one_click_record = br.one_click_pos(eticket, octoken, selected_options, url_options)
			elif oc_type == 'ws':
				one_click_record = web.one_click_services(eticket, octoken, selected_options, url_options)

			aprove_or_decline = options.aprove_decline(one_click_record['TransID'])
			if one_click_record == None:
				print("Delay Capture")
			elif one_click_record['Authorized']:
				result &= TransActionService.verify_oc_transaction(octoken, eticket, one_click_record, url_options, selected_options)
			else:
				print(colored(f"OneClick Transaction DECLINED : AuthCode:{one_click_record['AuthCode']}", 'red', attrs=['bold']))
				print()
			config.test_cases[one_click_record['TransID']] = config.test_case
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
				config.test_case = {}
				print("\n======================================|       OneClick     |======================================\n")
				config.logging.info("\n======================================|       OneClick     |======================================\n")
				config.logging.info('')
				pricepoint = current_transaction_id['full_record']['BillConfigID']
				config.test_data = TransActionService.prepare_data1(pricepoint, current_transaction_id['full_record']['PackageID'], 1)
				eticket = config.test_data['eticket']
				selected_options = [config.oc_tokens[token][1], config.oc_tokens[token][2]]
				octoken = token
				url_options = options.ref_variables() + options.refurl() + config.template
				config.test_data['url_options'] = url_options
				config.test_case['one_click_pos'] = f"One Click Started - Eticket: {eticket}"
				config.test_case['actual'] = f"One Click Results - Eticket: {eticket}"
				if oc_type == 'pos':
					one_click_record = br.one_click_pos(eticket, octoken, selected_options, url_options)
					# aprove_or_decline = options.aprove_decline(one_click_record['TransID'])
					if one_click_record == None:
						config.test_data['1click_not_found'] = eticket
					else:
						if not one_click_record['Authorized']:
							print(colored(f"Transaction DECLINED : AuthCode:{one_click_record['AuthCode']} ", 'red', attrs=['bold']))
							print("---------------------------------------")
						result &= TransActionService.verify_oc_transaction(octoken, eticket, one_click_record, url_options, selected_options)
						config.test_cases[one_click_record['TransID']] = config.test_case

				elif oc_type == 'ws':
					one_click_record = web.one_click_services(eticket, octoken, selected_options, config.test_data['url_options'])



			except Exception as ex:
				traceback.print_exc()
				print(f"{Exception}  ")
				config.logging.info(f"{Exception}  ")
				pass
	return result


def verify_refunds():  # Yan
	# refunds = config.refunds[1]
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
