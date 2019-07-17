import config
import random, decimal, string
import string
from features import options
from verifications import asset
from verifications import emails
from verifications import mts as mt
from termcolor import colored
from db_functions import dbs
from web import web
import requests

pricepoints = []
report = {}
# ==================================================================> Configuration
#config.enviroment = 'stage'
enviroment=config.enviroment
#27001
merchants = [20004]
#99
packageid = 99
processors = [26]
pricepoints_options = 'single'
# ==================================================================> Options
refurl = options.refurl()
ref_variables = options.ref_variables()
template = ''  # '&template=defaultnopaypal'
url_options = ref_variables + refurl + template

available_currencies = ['CAD']#, 'USD', 'CHF',  "CAD"] #, "CHF",  "EUR", "GBP", "HKD", "JPY", "NOK", "SEK"] # "DKK",
available_languages = ['EN']#, "PT", "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]
selected_currency = random.choice(available_currencies)
selected_language = random.choice(available_languages)
selected_options = [selected_currency, selected_language]
one_click_pos = True
one_click_ws = True
instant_coversion_pos = True
instant_coversion_ws = True
single_use_promo = False

# ==================================================================> for 511 and 510
pricingguid = {}
pricepoint_type = 0
dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))

# ==================================================================================================> Begining of the script
for merchantid in merchants:
	try:
		if pricepoints_options == 'single':
			pricepoints = [27011]
		elif pricepoints_options == 'type':
			pricepoints = dbs.pricepoint_type(merchantid, [501, 502, 503, 504, 505, 506, 510, 511])
		elif pricepoints_options == 'list':
			pricepoints = dbs.pricepoint_list(merchantid)
		for pricepoint in pricepoints:

			try:

				eticket = str(packageid) + ':' + str(pricepoint)
				# ========================================================================> preparing package processor
				merchantbillconfig = dbs.merchantbillconfig(pricepoint)
				if one_click_pos or one_click_ws:
					dbs.update_merchantbillconfig_oneclick(pricepoint, 1)  # enabling 1click if its not enabled

				if single_use_promo:
					dbs.update_pp_singleuse_promo(pricepoint, 1, 1)
				else:
					dbs.update_pp_singleuse_promo(pricepoint, 1, 0)  # feature 1 is single use promo
				pricepoint_type = merchantbillconfig[0]['Type']
				package = dbs.package(packageid)
				dbs.update_processor(processors[0], packageid)
				dbs.update_package(packageid, merchantid, pricepoint)

				transaction_record = web.create_transaction(pricepoint_type, eticket, selected_options, enviroment,
				                                            merchantid, url_options, 26)
				multitrans_base_record = mt.build_multitrans(merchantbillconfig[0], package[0], transaction_record,
				                                             url_options)
				differences_multitrans = mt.multitrans_compare(multitrans_base_record,
				                                               transaction_record['full_record'])

				asset_base_record = asset.build_asset_signup(merchantbillconfig[0], multitrans_base_record,
				                                             transaction_record)
				differences_asset = asset.asset_compare(asset_base_record)

				check_email_differences = emails.check_email_que(pricepoint_type, multitrans_base_record, 'signup')
				print('*********************SignUp Transaction Verification Complete*********************')
				print()

				if pricepoint_type in [501, 502, 503, 504, 506, 510, 511] and one_click_pos:
					one_click_pos_record = web.one_click('pos', eticket, pricepoint_type, multitrans_base_record,
					                                     transaction_record['email'], url_options,selected_options)
					differences_oneclick_pos = mt.multitrans_compare(one_click_pos_record[0], one_click_pos_record[1])
					asset_base_record_onelick = asset.asset_oneclick(merchantbillconfig[0], asset_base_record,
					                                                 one_click_pos_record[1])
					differences_asset = asset.asset_compare(asset_base_record_onelick)
					check_email = emails.check_email_que(pricepoint_type, multitrans_base_record, 'signup')
					report['pos' + str(eticket)] = [differences_multitrans, differences_asset, check_email]
					print('*********************OneClick POS Transaction Verification Complete*********************')
					print()
				if pricepoint_type in [501, 502, 503, 504, 506, 510, 511] and one_click_ws:
					one_click_ws_record = web.one_click('ws', eticket, pricepoint_type, multitrans_base_record,
					                                    transaction_record['email'], url_options,selected_options)
					differences_oneclick_ws = mt.multitrans_compare(one_click_ws_record[0], one_click_ws_record[1])
					asset_base_record_onelick = asset.asset_oneclick(merchantbillconfig[0], asset_base_record,
					                                                 one_click_ws_record[1])
					differences_asset = asset.asset_compare(asset_base_record_onelick)
					check_email = emails.check_email_que(pricepoint_type, one_click_ws_record[0], 'signup')
					report['ws' + str(eticket)] = [differences_multitrans, differences_asset, check_email]
					print('*********************OneClick WS Transaction Verification Complete*********************')
					print()
				report[eticket] = [differences_multitrans, differences_asset, check_email_differences]

				if pricepoint_type == 506 and instant_coversion_pos:
					ic_pos_record = web.instant_conversion('pos', eticket, pricepoint_type, multitrans_base_record,
					                                       transaction_record['email'], url_options,
					                                       merchantbillconfig[0])
					differences_ic_pos = mt.multitrans_compare(ic_pos_record[0], ic_pos_record[1])
					asset_ic_record = asset.asset_instant_conversion(merchantbillconfig[0], asset_base_record,
					                                                 ic_pos_record[1])
					differences_asset = asset.asset_compare(asset_ic_record)
					check_email = emails.check_email_que(pricepoint_type, ic_pos_record[1][0], 'signup')
					report['pos' + str(eticket)] = [differences_ic_pos, differences_asset, check_email]
					print('*********************Instant Conversion Transaction Verification Complete*********************')
					print()



			except Exception as ex:
				print(ex)



	except Exception as ex:
		print(ex)
web.browser_quit()
