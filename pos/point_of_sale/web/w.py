import random
from splinter import Browser
from faker import Faker
import subprocess
import time
import traceback
import os
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions
from selenium.common.exceptions import *
from pos.point_of_sale.utils import constants
from selenium import webdriver
import random
from splinter import Browser
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import subprocess
import time
import traceback
import os
from selenium.common.exceptions import *

db_agent = DBActions()



class FillPayPage:

	def __init__(self):
		self.path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'transguid\\TransGuidDecoderApp.exe')
		self.chrome_options = webdriver.ChromeOptions()
		self.chrome_options.add_argument("--window-position=-1400,0")
		chrome_options = webdriver.ChromeOptions()
		# self.chrome_options.add_argument("--window-position=-1400,0")
		self.fake = Faker()
		self.br = Browser(driver_name='chrome', options=chrome_options)
		self.br.driver.set_window_position(-1400, 0)
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

	def wait_for_ajax(self,driver):
		wait = WebDriverWait(self,driver, 15)
		try:
			wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
			wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
			print('waiting')
		except Exception as e:
			pass

	def check_title(self,driver):
		title = self.br.title
		if title == 'Secure Checkout':
			window = self.br.windows[1]
			window.close()
			self.br.windows.current = self.br.windows[0]
			time.sleep(1)
			return False
		return True

	def wait_for_title(self,br):
		cnt = 0
		while cnt < 15:
			title = self.br.title
			if title == 'Log in to your PayPal account' or title == 'PayPal Checkout - Choose a way to pay':
				return True
			time.sleep(1)
			cnt += 1
			print(cnt)

		self.check_title(br)
		return False
	def spin(self,driver):
		try:
			while self.br.find_by_id("preloaderSpinner").visible:
				time.sleep(1)
		except Exception as e:
			pass
	def is_element_present(self, how, what):
		try:
			self.br.driver.find_element(by=how, value=what)
		except NoSuchElementException:
			return False
		return True


	def FillDefault(self,test_case,payment):
		elem = ''
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
			if self.br.find_by_id('UserNameInput'):
				self.br.find_by_id('UserNameInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
			if self.br.find_by_id('PasswordInput'):
				self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
			if self.br.find_by_id('CurrencyDDL'):
				merchant_currency = self.br.find_by_id('CurrencyDDL').select(test_case['dmc'])
			paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(test_case['lang'])
			if not test_case['lang'] == 'EN':
				time.sleep(2)
			merchant_country = self.br.find_by_id('CountryDDL').value
			cc = test_case['cc']
			card_encrypted = db_agent.encrypt_card(cc)
			if not db_agent.execute_select_one_parameter(constants.FRAUD_CARD_CHECK, card_encrypted):
				db_agent.execute_insert(constants.FRAUD_CARD_INSERT, card_encrypted)
			cvv = str(random.randint(111, 999))
			firstname = self.fake.first_name()
			lastname = self.fake.first_name()
			email_encrypt = db_agent.encrypt_email(email)
			test_case['card_encrypted'] = card_encrypted
			test_case['transbin'] = int(str(cc)[:6])
			test_case['transguid'] = transguid
			test_case['email'] = email
			test_case['zip'] = '33333'
			test_case['email_encrypt'] = email_encrypt
			test_case['merchant_country'] = merchant_country
			test_case['expiration_date'] = '01'
			test_case['year'] = '2023'
			test_case['firstname'] = firstname
			test_case['lastname'] = lastname
			test_case['merchant_currency'] = test_case['dmc']
			test_case['paypage_lnaguage'] = self.br.find_by_id('LanguageDDL').value

			self.wait_for_ajax(self.br)
			# while self.br.execute_script("return jQuery.active == 0") != True:
			# 	time.sleep(1)

			if payment == 'cc':
				self.br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
				self.br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
				while self.br.execute_script("return jQuery.active == 0") != True:
					time.sleep(1)
				self.br.find_by_id('CCExpMonthDDL').select('01')
				self.br.find_by_id('CCExpYearDDL').select('2023')
				self.br.find_by_id('FirstNameInput').fill(firstname)
				self.br.find_by_id('LastNameInput').fill(lastname)
				# br.find_option_by_text('Florida').first.click()
				self.br.find_by_id('ZipInput').fill(test_case['zip'])
				# br.find_by_id('CountryDDL').fill('999')
				self.br.find_by_id('EMailInput').fill(email)
				# while self.br.execute_script("return jQuery.active == 0") != True:
				# 	time.sleep(1)
				self.wait_for_ajax(self.br)
				self.br.find_by_id('SecurePurchaseButton').click()
				time.sleep((2))
				print('Credit Card payment *********************************************************************************************')
			elif payment == 'pp':
				print(
					'PayPal----- payment *********************************************************************************************')
				self.br.find_by_css("input[name='paymentoption'][value='1301']")[0].click()
				time.sleep(1)
				id = self.br.find_by_tag("iframe")[1]['id']
				with self.br.get_iframe(id) as iframe:
					iframe.find_by_id("buttons-container").first.click()
				self.br.windows.current = self.br.windows[1]
				self.br.driver.set_window_position(-1400, 0)
				# 222222222222222222222222222222222222222222222222222222222222222222222
				self.spin(self.br)
				if self.wait_for_title:
					if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
				# while br.title != 'Log in to your PayPal account' or br.title != 'PayPal Checkout - Choose a way to pay':
				#     time.sleep(1)
				if self.br.title == 'Log in to your PayPal account':  # Log in to your PayPal account
					if self.br.find_by_id("email").first:
						while self.br.find_by_id("email").first.visible == False:
							time.sleep(1)
						self.br.find_by_id("email").first.fill('yan@segpay.com') #('CCREJECT-REFUSED@paypal.com') #('yan@segpay.com')
						# br.find_by_id("btnNext").first.click()
						elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "btnNext")))
						elem.click()
						self.check_title(self.br)
					if self.br.find_by_id("password").first:
						while self.br.find_by_id("password").first.visible == False: # password
							time.sleep(1)
						self.br.find_by_id("password").first.fill('Karapuz2')#('PayPal2016')
						elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "btnLogin")))
						elem.click()
					# br.find_by_id("btnLogin").first.click()
					self.spin(self.br)
					time.sleep(2)

				while self.br.title != 'PayPal Checkout - Choose a way to pay':
					time.sleep(1)
					if self.check_title(self.br) == False: raise ValueError('Wrong Frame')

				# if check_title(br) == False  : raise ValueError('Wrong Frame')
				if self.br.title == 'PayPal Checkout - Choose a way to pay':
					try:
						if self.is_element_present( By.ID, 'button'):
							elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "button")))
						elif self.is_element_present(By.ID, 'fiSubmitButton'):
							elem = WebDriverWait(self.br.driver, 10).until(
								EC.element_to_be_clickable((By.ID, "fiSubmitButton")))
						elif self.is_element_present(By.CLASS_NAME, ".buttons.reviewButton"):
							elem = WebDriverWait(self.br.driver, 10).until(
								EC.element_to_be_clickable((By.CLASS_NAME, ".buttons.reviewButton")))
						self.spin(self.br)
						elem.click()
						self.spin(self.br)
						time.sleep(1)
					except ElementClickInterceptedException:
						time.sleep(2)  # Sometimes the pop-up takes time to load
						elem.click()

				while self.br.title != 'PayPal Checkout - Review your payment':
					time.sleep(1)
					if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
				if self.br.title == 'PayPal Checkout - Review your payment':
					try:
						if self.is_element_present( By.ID, 'button'):
							elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "button")))
						elif self.is_element_present( By.ID, 'fiSubmitButton'):
							elem = WebDriverWait(self.br.driver, 10).until(
								EC.element_to_be_clickable((By.ID, "fiSubmitButton")))
						elif self.is_element_present( By.CLASS_NAME, ".buttons.reviewButton"):
							elem = WebDriverWait(self.br.driver, 10).until(
								EC.element_to_be_clickable((By.CLASS_NAME, ".buttons.reviewButton")))
						elem.click()
						time.sleep(1)
						# br.find_by_value('Agree & Pay').click()
						print(self.br.title)
					except ElementClickInterceptedException:
						time.sleep(2)  # Sometimes the pop-up takes time to load
						elem.click()
					try:
						while self.br.title == 'PayPal Checkout - Review your payment':
							time.sleep(1)
					except NoSuchWindowException:
						self.br.windows.current = self.br.windows[0]
						pass
					except Exception as e:
						pass
				try:
					while self.br.find_by_id("SubmitSpinner").visible:
						time.sleep(1)
				except Exception as e:
					pass


		except Exception as ex:
			traceback.print_exc()
		print(f"Exception {Exception} ")
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