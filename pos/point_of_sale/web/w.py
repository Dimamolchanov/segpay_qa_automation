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
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
db_agent = DBActions()



class FillPayPage:

	def __init__(self):
		self.path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'transguid\\TransGuidDecoderApp.exe')
		self.chrome_options = webdriver.ChromeOptions()
		self.chrome_options.add_argument("--window-position=-1400,0")
		chrome_options = webdriver.ChromeOptions()
		self.chrome_options.add_argument("--window-position=-1400,0")
		self.fake = Faker()
		#self.br = Browser(driver_name='chrome', options=chrome_options)

		self.br = webdriver.Chrome()
		self.br.set_window_position(-1400, 0)

	# def start_browser(self):
	# 	chrome_options = webdriver.ChromeOptions()
	# 	chrome_options.add_argument("--window-position=-1400,0")
	# 	chrome_options = webdriver.ChromeOptions()
	# 	self.br = Browser(driver_name='chrome', options=chrome_options)
	def is_element_present(self, how, what):
		try:
			self.br.find_element(by=how, value=what)
		except NoSuchElementException:
			return False
		return True

	def navigate_to_url(self,url):
		retry_flag = True
		retry_count = 0
		while retry_flag and retry_count < 30:
			try:
				self.br.get(url)
				assert (self.br.current_url == url)
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
			if self.is_element_present(By.ID,'TransGUID'):
				transguid = self.br.find_element_by_id('TransGUID').get_attribute('value')
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
			if self.br.find_element_by_id('CurrencyDDL'):
				merchant_currency = Select(self.br.find_element_by_id('CurrencyDDL')).select_by_value(test_case['dmc'])
				tmp = self.br.find_element_by_id('LanguageDDL')

			paypage_lnaguage = Select(tmp).select_by_value(test_case['lang'])

			if not test_case['lang'] == 'EN':
				time.sleep(2)
			self.br.find_element_by_id('CreditCardInputNumeric').send_keys(cc)  # CreditCardInputNumeric  older CreditCardInput
			# if config.enviroment == 'qa':
			# 	self.br.find_by_id('CreditCardInput').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
			# else:
			# 	self.br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
			self.br.find_element_by_id('CVVInputNumeric').send_keys(cvv)  # new CVVInputNumeric old CVVInput
			# if config.enviroment == 'qa':
			# 	self.br.find_by_id('CVVInput').fill(cvv)  # new CVVInputNumeric old CVVInput
			# else:
			# 	self.br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
			while self.br.execute_script("return jQuery.active == 0") != True:
				time.sleep(1)
			firstname = self.fake.first_name()
			lastname = self.fake.first_name()

			Select(self.br.find_element_by_id('CCExpMonthDDL')).select_by_value('01')

			self.br.find_element_by_id('CCExpYearDDL').send_keys('2023')
			self.br.find_element_by_id('FirstNameInput').send_keys(firstname)
			self.br.find_element_by_id('LastNameInput').send_keys(lastname)
			# br.find_option_by_text('Florida').first.click()
			self.br.find_element_by_id('ZipInput').send_keys(test_case['zip'])
			# br.find_by_id('CountryDDL').fill('999')
			self.br.find_element_by_id('EMailInput').send_keys(email)

			if self.is_element_present(By.ID, 'UserNameInput'):
				self.br.find_element_by_id('UserNameInput').send_keys(self.fake.user_name() + str(random.randint(333, 999)))
			if self.is_element_present(By.ID, 'PasswordInput'):
				self.br.find_element_by_id('PasswordInput').send_keys(self.fake.user_name() + str(random.randint(333, 999)))
			merchant_country = self.br.find_element_by_id('CountryDDL').get_attribute('value')
			test_case['merchant_country'] = merchant_country
			test_case['expiration_date'] = '01'
			test_case['year'] = '2023'
			test_case['firstname'] = firstname
			test_case['lastname'] = lastname
			test_case['merchant_currency'] = test_case['dmc']
			test_case['paypage_lnaguage'] = self.br.find_element_by_id('LanguageDDL').get_attribute('value')
			while self.br.execute_script("return jQuery.active == 0") != True:
				time.sleep(1)
			self.br.find_element_by_id('SecurePurchaseButton').click()
			time.sleep((2))
		except Exception as ex:
			traceback.print_exc()

			print(ex)
			pass
		try:

			if self.is_element_present(By.NAME, 'Cardinal-CCA-IFrame'):
				iframe = self.br.find_element_by_name('Cardinal-CCA-IFrame')
				self.br.switch_to.frame(iframe)
				if self.is_element_present(By.NAME, 'challengeDataEntry'):
					iframe.find_element_by_name('challengeDataEntry').send_keys('1234')
					iframe.find_element_by_name('SUBMIT').click()
				elif self.is_element_present(By.NAME, 'authWindow'):
					auth = iframe.find_element_by_name('Cardinal-CCA-IFrame')
					auth.find_element_by_id('password').send_keys('test')
					auth.find_element_by_name('UsernamePasswordEntry').click()
				else:
					pass


			#iframe = br.find_element_by_css_selector("iframe[title='paypal_buttons']")

			#
			# self.br
			# if self.br.get_iframe('Cardinal-CCA-IFrame'):
			# 	with self.br.get_iframe('Cardinal-CCA-IFrame') as iframe:
			# 		if iframe.find_by_name('challengeDataEntry'):
			# 			iframe.find_by_name('challengeDataEntry').fill('1234')
			# 			iframe.find_by_value('SUBMIT').click()
			# 		elif iframe.get_iframe('authWindow'):
			# 			with iframe.get_iframe('authWindow') as auth:
			# 				auth.find_by_id('password').fill('test')
			# 				auth.find_by_name('UsernamePasswordEntry').click()
			# 		else:
			# 			pass
		except NoSuchFrameException:
			pass
		except Exception as ex:
			traceback.print_exc()
			print(ex)
		return test_case


	def __del__(self):
		self.br.quit()