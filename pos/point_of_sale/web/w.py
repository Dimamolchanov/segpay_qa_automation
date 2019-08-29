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



class FillPayPage:

	def __init__(self):
		self.path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'transguid\\TransGuidDecoderApp.exe')
		self.chrome_options = webdriver.ChromeOptions()
		self.chrome_options.add_argument("--window-position=-1400,0")
		chrome_options = webdriver.ChromeOptions()
		self.chrome_options.add_argument("--window-position=-1400,0")
		self.fake = Faker()
		self.br = Browser(driver_name='chrome', options=chrome_options)
	# def start_browser(self):
	# 	chrome_options = webdriver.ChromeOptions()
	# 	chrome_options.add_argument("--window-position=-1400,0")
	# 	chrome_options = webdriver.ChromeOptions()
	# 	self.br = Browser(driver_name='chrome', options=chrome_options)


	def navigate_to_url(self,url):
		retry_flag = True
		retry_count = 0
		while retry_flag and retry_count < 30:
			try:
				self.br.visit(url)
				assert (self.br.url == url)
				retry_flag = False
				return True

			except:
				retry_count = retry_count + 1
				time.sleep(1)
	def FillDefault(self,test_case):
		page_loaded = self.navigate_to_url(test_case['link'])
		transguid = ''
		if page_loaded == False:
			return None
		email = 'qateam@segpay.com'  # fake.email()
		try:
			if self.br.is_element_present_by_id('TransGUID', wait_time=10):
				transguid = self.br.find_by_id('TransGUID').value
				transguid = subprocess.run([self.path, transguid, '-l'], stdout=subprocess.PIPE)
				transguid = transguid.stdout.decode('utf-8')
			else:
				print("Transguid not Found ")
				return None
			cc = test_case['cc']
			card_encrypted = db_agent.encrypt_card(cc)
			if not db_agent.execute_select_one_parameter(constants.FRAUD_CARD_CHECK, card_encrypted):
				db_agent.execute_insert(constants.FRAUD_CARD_INSERT, card_encrypted)
			cvv = str(random.randint(111, 999))
			email_encrypt = db_agent.encrypt_email(email)
			test_case['card_encrypted'] = card_encrypted
			test_case['transbin'] = int(str(cc)[:6])
			test_case['transguid'] = transguid
			test_case['email'] = email
			test_case['zip'] = '33333'
			test_case['email_encrypt'] = email_encrypt
			if self.br.find_by_id('CurrencyDDL'):
				merchant_currency = self.br.find_by_id('CurrencyDDL').select(test_case['dmc'])
			paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(test_case['lang'])
			# while br.execute_script("return jQuery.active == 0") != True:
			# time.sleep(1)
			if not test_case['lang'] == 'EN':
				time.sleep(2)
			if config.enviroment == 'qa':
				self.br.find_by_id('CreditCardInput').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
			else:
				self.br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
			if config.enviroment == 'qa':
				self.br.find_by_id('CVVInput').fill(cvv)  # new CVVInputNumeric old CVVInput
			else:
				self.br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
			while self.br.execute_script("return jQuery.active == 0") != True:
				time.sleep(1)
			firstname = self.fake.first_name()
			lastname = self.fake.first_name()
			self.br.find_by_id('CCExpMonthDDL').select('01')
			self.br.find_by_id('CCExpYearDDL').select('2023')
			self.br.find_by_id('FirstNameInput').fill(firstname)
			self.br.find_by_id('LastNameInput').fill(lastname)
			# br.find_option_by_text('Florida').first.click()
			self.br.find_by_id('ZipInput').fill(test_case['zip'])
			# br.find_by_id('CountryDDL').fill('999')
			self.br.find_by_id('EMailInput').fill(email)
			if self.br.find_by_id('UserNameInput'):
				self.br.find_by_id('UserNameInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
			if self.br.find_by_id('PasswordInput'):
				self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
			merchant_country = self.br.find_by_id('CountryDDL').value
			test_case['merchant_country'] = merchant_country
			test_case['expiration_date'] = '01'
			test_case['year'] = '2023'
			test_case['firstname'] = firstname
			test_case['lastname'] = lastname
			test_case['merchant_currency'] = test_case['dmc']
			test_case['paypage_lnaguage'] = self.br.find_by_id('LanguageDDL').value
			while self.br.execute_script("return jQuery.active == 0") != True:
				time.sleep(1)
			self.br.find_by_id('SecurePurchaseButton').click()
			time.sleep((2))
		except Exception as ex:
			traceback.print_exc()

			print(ex)
			pass
		try:
			if self.br.get_iframe('Cardinal-CCA-IFrame'):
				with self.br.get_iframe('Cardinal-CCA-IFrame') as iframe:
					if iframe.find_by_name('challengeDataEntry'):
						iframe.find_by_name('challengeDataEntry').fill('1234')
						iframe.find_by_value('SUBMIT').click()
					elif iframe.get_iframe('authWindow'):
						with iframe.get_iframe('authWindow') as auth:
							auth.find_by_id('password').fill('test')
							auth.find_by_name('UsernamePasswordEntry').click()
					else:
						pass
		except NoSuchFrameException:
			pass
		except Exception as ex:
			traceback.print_exc()
			print(ex)
		return test_case


	def __del__(self):
		self.br.quit()