import random
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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

db_agent = DBActions()


fake = Faker()

class Signup:
    
    def __init__(self):
        self.path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                 'transguid\\TransGuidDecoderApp.exe')
        self.fake = Faker()
        self.br = Browser(driver_name='chrome')
        self.br.driver.set_window_position(-1400, 0)
    
    def get_transguid(self):
        transguid = ''
        try:
            if self.br.is_element_present_by_id('TransGUID', wait_time=10):
                transguid = self.br.find_by_id('TransGUID').value
                transguid = subprocess.run([self.path, transguid, '-l'], stdout=subprocess.PIPE)
                config.test_data['transguid'] = transguid.stdout.decode('utf-8')
                print(config.test_data['transguid'])
            else:
                print("Transguid not Found ")
                return None
        except Exception as ex:
            traceback.print_exc()
    
    def change_language(self):
        if not config.test_data['lang_from'] == 'u':
            if not config.test_data['lang'] == 'EN':
                try:
                    paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(config.test_data['lang'])
                    time.sleep(1)
                    self.wait_for_ajax(self.br)
                except Exception as ex:
                    traceback.print_exc()
                    pass
    
    def change_currency(self):
        if not (config.test_data['dmc_from'] == 'u' or config.test_data['merchant'] == 'US'):
            if self.br.driver.find_element_by_id('CurrencyDDL'):
                merchant_currency = self.br.find_by_id('CurrencyDDL').select(config.test_data['dmc'])
        
        
        
    
    
    
    def user_password(self):
        try:
            if config.test_data['userinfo'] == 1:
                if self.br.driver.find_element_by_id('UserNameInput'):
                    self.br.find_by_id('UserNameInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
                if self.br.driver.find_element_by_id('PasswordInput'):
                    self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
            elif config.test_data['userinfo'] == 2:
                if self.br.driver.find_element_by_id('PasswordInput'):
                    self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
            if self.br.driver.find_element_by_id('CurrencyDDL'):
                merchant_currency = self.br.find_by_id('CurrencyDDL').select(config.test_data['dmc'])
        except NoSuchElementException:
            pass
        except Exception as ex:
            traceback.print_exc()
            pass
    
    def cc_payment(self):
        try:
            if config.test_data['payment'] == 'CC':
                self.br.find_by_id('CreditCardInputNumeric').fill(config.test_data['cc'])  # CreditCardInputNumeric  older CreditCardInput
                self.br.find_by_id('CVVInputNumeric').fill(str(random.randint(111, 999)))  # new CVVInputNumeric old CVVInput
                self.wait_for_ajax(self.br)
                self.br.find_by_id('CCExpMonthDDL').select('01')
                self.br.find_by_id('CCExpYearDDL').select('2023')
                self.br.find_by_id('FirstNameInput').fill(config.test_data['firstname'])
                self.br.find_by_id('LastNameInput').fill(config.test_data['lastname'])
                self.br.find_by_id('ZipInput').fill('33333')
                self.br.find_by_id('EMailInput').fill(config.test_data['email'])
                #self.wait_for_ajax(self.br)
                time.sleep(1)
                self.br.find_by_id('SecurePurchaseButton').click()
                self.wait_for_ajax(self.br)
                time.sleep(2)
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
                    elif self.br.get_iframe('IFrame3DS'):
                        with self.br.get_iframe('IFrame3DS') as iframe:
                            iframe.find_by_name('continue').click()
                            while self.br.execute_script("return jQuery.active == 0") != True:
                                time.sleep(1)
                            time.sleep(1)
                
                except NoSuchFrameException:
                    pass
                except NoSuchElementException:
                    pass
                except Exception as ex:
                    traceback.print_exc()
        
        except Exception as ex:
            traceback.print_exc()
            pass
    
    def paypal_payment(self):
        elem = ''
        print(
                'PayPal----- payment *********************************************************************************************')
        self.br.find_by_css("input[name='paymentoption'][value='1301']")[0].click()
        time.sleep(1)
        id = self.br.find_by_tag("iframe")[1]['id']
        with self.br.get_iframe(id) as iframe:
            iframe.find_by_id("buttons-container").first.click()
        self.br.windows.current = self.br.windows[1]
        #self.br.driver.set_window_position(-1400, 0)
        self.spin(self.br)
        if self.wait_for_title:
            if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
        if self.br.title == 'Log in to your PayPal account':  # Log in to your PayPal account
            if self.br.find_by_id("email").first:
                while self.br.find_by_id("email").first.visible == False:
                    time.sleep(1)
                self.br.find_by_id("email").first.fill(
                        'yan@segpay.com')  # ('CCREJECT-REFUSED@paypal.com') #('yan@segpay.com')
                # br.find_by_id("btnNext").first.click()
                elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "btnNext")))
                elem.click()
                self.check_title(self.br)
            if self.br.find_by_id("password").first:
                while self.br.find_by_id("password").first.visible == False:  # password
                    time.sleep(1)
                self.br.find_by_id("password").first.fill('Karapuz2')  # ('PayPal2016')
                elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "btnLogin")))
                elem.click()
            self.spin(self.br)
            time.sleep(2)

        while self.br.title != 'PayPal Checkout - Choose a way to pay':
            time.sleep(1)
            if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
        if self.br.title == 'PayPal Checkout - Choose a way to pay':
            try:
                if self.is_element_present(By.ID, 'button'):
                    elem = WebDriverWait(self.br.driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "button")))
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
                if self.is_element_present(By.ID, 'button'):
                    elem = WebDriverWait(self.br.driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "button")))
                elif self.is_element_present(By.ID, 'fiSubmitButton'):
                    elem = WebDriverWait(self.br.driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "fiSubmitButton")))
                elif self.is_element_present(By.CLASS_NAME, ".buttons.reviewButton"):
                    elem = WebDriverWait(self.br.driver, 10).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, ".buttons.reviewButton")))

                elif self.is_element_present(By.ID, 'consentButton'):
                    elem = self.br.find_by_id("consentButton")
                    #self.br.find_by_id("consentButton").click()
                elem.click()
                self.spin(self.br)
                cnt = 0
                self.br.windows.current = self.br.windows[0]
                time.sleep(1)
                while self.br.url != 'https://stgs2.segpay.com/PayPage/Receipt' and cnt < 10:
                    time.sleep(1)
                    cnt += 1
                    
                    
                
                # br.find_by_value('Agree & Pay').click()
                #print(self.br.title)
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
        



    def paypal_paymentoc(self):
        elem = ''

        id = self.br.find_by_tag("iframe")[1]['id']
        with self.br.get_iframe(id) as iframe:
            iframe.find_by_id("buttons-container").first.click()
        self.br.windows.current = self.br.windows[1]
        #self.br.driver.set_window_position(-1400, 0)
        self.spin(self.br)
        if self.wait_for_title:
            if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
        if self.br.title == 'Log in to your PayPal account':  # Log in to your PayPal account
            if self.br.find_by_id("email").first:
                while self.br.find_by_id("email").first.visible == False:
                    time.sleep(1)
                self.br.find_by_id("email").first.fill(
                    'yan@segpay.com')  # ('CCREJECT-REFUSED@paypal.com') #('yan@segpay.com')
                # br.find_by_id("btnNext").first.click()
                elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "btnNext")))
                elem.click()
                self.check_title(self.br)
            if self.br.find_by_id("password").first:
                while self.br.find_by_id("password").first.visible == False:  # password
                    time.sleep(1)
                self.br.find_by_id("password").first.fill('Karapuz2')  # ('PayPal2016')
                elem = WebDriverWait(self.br.driver, 10).until(EC.element_to_be_clickable((By.ID, "btnLogin")))
                elem.click()
            self.spin(self.br)
            time.sleep(2)

        while self.br.title != 'PayPal Checkout - Choose a way to pay':
            time.sleep(1)
            if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
        if self.br.title == 'PayPal Checkout - Choose a way to pay':
            try:
                if self.is_element_present(By.ID, 'button'):
                    elem = WebDriverWait(self.br.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "button")))
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
                if self.is_element_present(By.ID, 'consentButton'):
                    self.br.find_by_id("consentButton").click()
                    self.spin(self.br)
                    cnt  = 0
                    self.br.windows.current = self.br.windows[0]
                    #self.br.driver.switchTo().parentFrame()
                    #self.br.driver.switchTo().defaultContent();
                    
                    
                    while self.br.url != 'https://stgs2.segpay.com/PayPage/Receipt' and cnt < 10:
                        time.sleep(1)
                        cnt +=1
                time.sleep(1)
                    
            except ElementClickInterceptedException:
                time.sleep(2)  # Sometimes the pop-up takes time to load
                elem.click()
            except Exception as e:
                pass
        # while self.br.title != 'PayPal Checkout - Review your payment':
        #     time.sleep(1)
        #     if self.check_title(self.br) == False: raise ValueError('Wrong Frame')
        # if self.br.title == 'PayPal Checkout - Review your payment':
        #     try:
        #         if self.is_element_present(By.ID, 'button'):
        #             elem = WebDriverWait(self.br.driver, 10).until(
        #                 EC.element_to_be_clickable((By.ID, "button")))
        #         elif self.is_element_present(By.ID, 'fiSubmitButton'):
        #             elem = WebDriverWait(self.br.driver, 10).until(
        #                 EC.element_to_be_clickable((By.ID, "fiSubmitButton")))
        #         elif self.is_element_present(By.CLASS_NAME, ".buttons.reviewButton"):
        #             elem = WebDriverWait(self.br.driver, 10).until(
        #                 EC.element_to_be_clickable((By.CLASS_NAME, ".buttons.reviewButton")))
        #         elem.click()
        #         time.sleep(1)
        #         # br.find_by_value('Agree & Pay').click()
        #         print(self.br.title)
        #     except ElementClickInterceptedException:
        #         time.sleep(2)  # Sometimes the pop-up takes time to load
        #         elem.click()
        #     try:
        #         while self.br.title == 'PayPal Checkout - Review your payment':
        #             time.sleep(1)
        #     except NoSuchWindowException:
        #         self.br.windows.current = self.br.windows[0]
        #         pass
        #     except Exception as e:
        #         pass
        # try:
        #     while self.br.find_by_id("SubmitSpinner").visible:
        #         time.sleep(1)
        # except Exception as e:
        #     pass
    def create_signup(self):  # Used by Recurring
        current_transaction_record = None
        try:
            if self.navigate_to_url(config.test_data['link']) == False:
                return None
            self.change_language()
            self.get_transguid()
            self.change_currency()
            self.user_password()
            config.test_data['merchant_country'] = self.br.find_by_id('CountryDDL').value
            config.test_data['card_encrypted'] = db_agent.encrypt_card(config.test_data['cc'])
            if not db_agent.execute_select_one_parameter(constants.FRAUD_CARD_CHECK, config.test_data['card_encrypted']):
                db_agent.execute_insert(constants.FRAUD_CARD_INSERT, config.test_data['card_encrypted'])
            email = 'qateam@segpay.com'
            config.test_data['email_encrypt'] = db_agent.encrypt_email(email) #email = # fake.email()
            config.test_data['transbin'] = int(str(config.test_data['cc'])[:6])
            config.test_data['email'] = email
            config.test_data['zip'] = '33333'
            config.test_data['expiration_date'] = '01'
            config.test_data['year'] = '2023'
            config.test_data['firstname'] = self.fake.first_name()
            config.test_data['lastname'] = self.fake.first_name()
            config.test_data['merchant_currency'] = config.test_data['dmc']
            config.test_data['paypage_lnaguage'] = self.br.find_by_id('LanguageDDL').value
            self.wait_for_ajax(self.br)
            if config.test_data['payment'] == 'CC':
                self.cc_payment()
            elif config.test_data['payment'] == 'Paypal':
                self.paypal_payment()
        except Exception as ex:
            traceback.print_exc()
        pass
        try:
            cnt = 0
            sql = "select * from multitrans where TransGuid = '{}'"
            current_transaction_record = db_agent.execute_select_one_with_wait(sql, config.test_data['transguid'])
            return current_transaction_record
        except Exception as ex:
            traceback.print_exc()
            pass
    
    def navigate_to_url(self, url):
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
    
    def wait_for_ajax(self, driver):
        wait = WebDriverWait(self, driver, 15)
        try:
            wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            print('waiting')
        except Exception as e:
            pass
    
    def check_title(self, driver):
        title = self.br.title
        if title == 'Secure Checkout':
            window = self.br.windows[1]
            window.close()
            self.br.windows.current = self.br.windows[0]
            time.sleep(1)
            return False
        return True
    
    def wait_for_title(self, br):
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
    
    def spin(self, driver):
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
    
    def oc_pos(self):  # Currently in use by recurring
        oneclick_record = None
        dynamic_price = 9999
        pricingguid = ''
        d = config.test_data
        if config.test_data['Type'] == 505:
            print("___________________Delay Capture One Click is not allowed_____________")
            print()
            return None
        
        try:
            page_loaded = self.navigate_to_url(d['link'])
            if page_loaded == False:
                return None
            else:
                self.change_language()
                self.get_transguid()
                self.change_currency()
                self.user_password()
                if config.test_data['payment'] == 'CC':
                    self.br.find_by_id('CVVInputNumeric').fill('333')
                    self.br.find_by_id('SecurePurchaseButton').click()
                elif config.test_data['payment'] == 'Paypal':
                    if self.br.find_by_id('EMailInput').first.visible:
                        self.br.find_by_id('EMailInput').fill(config.test_data['octoken_email'])
                        self.br.find_by_id('SecurePurchaseButton').click()
                        time.sleep(2)
                    else:
                        self.paypal_paymentoc()
                        # id = self.br.find_by_tag("iframe")[1]['id']
                        # with self.br.get_iframe(id) as iframe:
                        #     iframe.find_by_id("buttons-container").first.click()


               
                cnt = 0
                while oneclick_record == None and cnt < 15:
                    cnt += 1
                    time.sleep(1)
                    sql = "select * from multitrans where TransGuid = '{}'"
                    oneclick_record = db_agent.execute_select_one_parameter(sql, config.test_data['transguid'])
                
                if oneclick_record:
                    if config.test_data['Type'] == 511:
                        oneclick_record['511'] = pricingguid
                    elif config.test_data['Type'] == 510:
                        oneclick_record['510'] = dynamic_price
                    sql = "Select PurchType from assets where purchaseid = {}"
                    token_type = db_agent.execute_select_one_parameter(sql, d['octoken'])['PurchType']
                    card = db_agent.execute_select_one_parameter(constants.GET_PAYMENTACCT_FROM_ASSET, d['octoken'])
                    config.test_case['actual'] = [
                        f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}"]
                    
                    config.test_case['oneclick_record_pos'] = oneclick_record
                else:
                    print("OneClickPOS record  error, record has not been created")
        except Exception as ex:
            traceback.print_exc()
            pass
        
        return oneclick_record  # , pricepoint_type
    
    def oc_ws(self):
        oneclick_record = None
        d = config.test_data
        if config.test_data['Type'] == 505:
            print("___________________Delay Capture One Click is not allowed_____________")
            print()
            return None
        multitrans_oneclick_record = {}
        sql = "select * from MerchantBillConfig where BillConfigID = {}"
        mbconfig = db_agent.execute_select_one_parameter(sql, d['pricepoint'])
        pricepoint_type = d['pp_type']
        merchantid = d['MerchantID']
        try:
            resp = requests.get(d['link'])
            xml_return_string = simplexml.loads(resp.content)
            transid = int(xml_return_string['TransReturn']['TransID'])
            cnt = 0
            while oneclick_record == None and cnt < 15:
                cnt += 1
                time.sleep(1)
                sql = "select * from multitrans where TransID = '{}'"
                oneclick_record = db_agent.execute_select_one_parameter(sql, transid)
            # print(f"OneClick Web Services => Eticket: {d['eticket']}  | Processor: {oneclick_record['Processor']} "
            #       f"| DMC: {d['dmc']} | Lnaguage: {d['lang']} | Type: {pricepoint_type}")
            # print(
            #         f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}")
            return oneclick_record
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}  Eticket: {d['eticket']} Module => one_click_services ")
            pass
    
    def close(self):
        self.br.quit()
        
# br = Browser(driver_name='chrome', options=chrome_options)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------ Instant Conversion POS and WS


# # ==========================================================================================================================BEP
# def rebill(pids):
# 	rebill_dates = {}
# 	before_rebill = {}
# 	# REFACTOR SQL:
# 	sql = "Select * from Assets where PurchaseID = {}"
# 	for pid in pids:
# 		# REFACTOR SQL:
# 		temp = db_agent.execute_select_one_parameter(sql, pid)
# 		# print(temp)
# 		before_rebill[pid] = temp
# 		temp = datetime.date(temp['NextDate'])
# 		if temp not in rebill_dates:
# 			rebill_dates[temp] = 1
# 	print("Starting Rebill")
# 	start_time = datetime.now()
# 	for rebill_date in rebill_dates:
# 		rebill_url = config.rebill_url + str(rebill_date) + '%2023:59:59'
# 		print(rebill_url)
# 		# br.driver.set_page_load_timeout(600)
# 		br.visit(rebill_url)
# 		while br.url != rebill_url:
# 			time.sleep(1)
# 		time.sleep(1)
# 	print("Finished Rebill")
# 	end_time = datetime.now()
# 	print('Duration: {}'.format(end_time - start_time))
# 	if 'Rebills processing is done.' in br.html:
# 		return ['RebillsFinished', before_rebill]
# 	else:
# 		return ['Rebill=>SomethingWrong', before_rebill]
#
#
# def captures(capture_date):
# 	captures_url = config.captures_url + str(capture_date)
# 	print("Starting Captures")
# 	start_time = datetime.now()
# 	br.visit(captures_url)
# 	print(captures_url)
# 	while br.url != captures_url:
# 		time.sleep(1)
# 	time.sleep(1)
# 	end_time = datetime.now()
# 	print('Duration: {}'.format(end_time - start_time))
# 	print("End Captures")
# 	if 'Final working set:' in br.html:
# 		return 'CapturesFinished'
# 	else:
# 		return 'Captures=>SomethingWrong'
#
#
# def refund():
# 	print("Starting Refund")
# 	start_time = datetime.now()
# 	br.visit(config.refund_url)
# 	print(config.refund_url)
# 	while br.url != config.refund_url:
# 		time.sleep(1)
# 	end_time = datetime.now()
# 	time.sleep(1)
# 	print('Duration: {}'.format(end_time - start_time))
# 	print("End Refund")
# 	if 'Application finished.' in br.html:
# 		return 'RefundFinished'
# 	else:
# 		return 'Refund=>SomethingWrong'
#
#
# def browser_quit():
# 	br.quit()
