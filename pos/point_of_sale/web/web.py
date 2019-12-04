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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

db_agent = DBActions()

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--window-position=-1000,0")

fake = Faker()

# path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'transguid\\TransGuidDecoderApp.exe')
class Signup:
    
    def __init__(self):
        self.path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                 'transguid\\TransGuidDecoderApp.exe')
        self.fake = Faker()
        self.br = Browser(driver_name='chrome')
        self.br.driver.set_window_position(-1400, 0)
    
    def create_signup(self):  # Used by Recurring
        data_from_paypage = {}
        elem = ''
        tc = config.test_data
        joinlink = tc['link']
        page_loaded = self.navigate_to_url(joinlink)
        current_transaction_record = None
        transguid = ''
        
        if page_loaded == False:
            return None
        email = 'qateam@segpay.com'  # fake.email()
        
        try:
            if not tc['lang'] == 'EN':
                try:
                    paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(tc['lang'])
                    time.sleep(1)
                    self.wait_for_ajax(self.br)
                except Exception as ex:
                    traceback.print_exc()
                    pass
            try:
                if self.br.is_element_present_by_id('TransGUID', wait_time=10):
                    transguid = self.br.find_by_id('TransGUID').value
                    transguid = subprocess.run([self.path, transguid, '-l'], stdout=subprocess.PIPE)
                    transguid = transguid.stdout.decode('utf-8')
                else:
                    print("Transguid not Found ")
                    return None
            except Exception as ex:
                traceback.print_exc()
            
            try:
                if config.test_data['userinfo'] == 1:
                    if self.br.driver.find_element_by_id('UserNameInput'):
                        self.br.find_by_id('UserNameInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
                    if self.br.driver.find_element_by_id('PasswordInput'):
                        self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
                elif config.test_data['userinfo'] == 1:
                    if self.br.driver.find_element_by_id('PasswordInput'):
                        self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
                if self.br.driver.find_element_by_id('CurrencyDDL'):
                    merchant_currency = self.br.find_by_id('CurrencyDDL').select(tc['dmc'])
            except NoSuchElementException:
                pass
            except Exception as ex:
                traceback.print_exc()
                pass
            
            try:
                merchant_country = self.br.find_by_id('CountryDDL').value
                cc = tc['cc']
                card_encrypted = db_agent.encrypt_card(cc)
                if not db_agent.execute_select_one_parameter(constants.FRAUD_CARD_CHECK, card_encrypted):
                    db_agent.execute_insert(constants.FRAUD_CARD_INSERT, card_encrypted)
                cvv = str(random.randint(111, 999))
                firstname = self.fake.first_name()
                lastname = self.fake.first_name()
                email_encrypt = db_agent.encrypt_email(email)
                tc['card_encrypted'] = card_encrypted
                tc['transbin'] = int(str(cc)[:6])
                tc['transguid'] = transguid
                tc['email'] = email
                tc['zip'] = '33333'
                tc['email_encrypt'] = email_encrypt
                tc['merchant_country'] = merchant_country
                tc['expiration_date'] = '01'
                tc['year'] = '2023'
                tc['firstname'] = firstname
                tc['lastname'] = lastname
                tc['merchant_currency'] = tc['dmc']
                tc['paypage_lnaguage'] = self.br.find_by_id('LanguageDDL').value
                self.wait_for_ajax(self.br)
            except Exception as ex:
                traceback.print_exc()
                pass
            if config.test_data['payment'] == 'CC':
                self.br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
                self.br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
                self.wait_for_ajax(self.br)
                self.br.find_by_id('CCExpMonthDDL').select('01')
                self.br.find_by_id('CCExpYearDDL').select('2023')
                self.br.find_by_id('FirstNameInput').fill(firstname)
                self.br.find_by_id('LastNameInput').fill(lastname)
                self.br.find_by_id('ZipInput').fill('33333')
                self.br.find_by_id('EMailInput').fill(email)
                self.wait_for_ajax(self.br)
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
            
            elif config.test_data['payment'] == 'pp':
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
        pass
        try:
            cnt = 0
            sql = "select * from multitrans where TransGuid = '{}'"
            
            current_transaction_record = db_agent.execute_select_one_with_wait(sql, transguid)
            return current_transaction_record
            # if current_transaction_record:
            #     tc['PurchaseID'] = full_record['PurchaseID']
            #     tc['TransID'] = full_record['TransID']
            #     tc['full_record'] = full_record
            #     tc['record_to_check'] = current_transaction_record
            #     config.test_data = tc
            #     return tc
        
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
    
    def signup(self, selected_options, merchantid, url_options, processor):  # Currently in use by Yan
        joinlink = config.test_data['link']
        full_record = {}
        try:
            data_from_paypage = self.fill_default(joinlink, selected_options, merchantid, config.test_data[
                'PackageID'])  # fill the page and return what was populated
            if data_from_paypage:
                transguid = data_from_paypage['transguid']
                sql = "select * from multitrans where TransGuid = '{}'"
                full_record = db_agent.execute_select_one_with_wait(sql, transguid)
                if full_record:
                    data_from_paypage['PurchaseID'] = full_record['PurchaseID']
                    data_from_paypage['TransID'] = full_record['TransID']
                    data_from_paypage['full_record'] = full_record
                    config.test_data = {**config.test_data, **data_from_paypage}
                    return data_from_paypage
            else:
                return False
        except Exception as ex:
            traceback.print_exc()
    
    def create_transaction(self, pricepoint_type, eticket, selected_options, merchantid, url_options, processor):
        joinlink = config.test_data['link']
        full_record = {}
        try:
            data_from_paypage = self.fill_default(joinlink, selected_options, merchantid, config.test_data[
                'PackageID'])  # fill the page and return what was populated
            if data_from_paypage:
                transguid = data_from_paypage['transguid']
                sql = "select * from multitrans where TransGuid = '{}'"
                full_record = db_agent.execute_select_one_with_wait(sql, transguid)
                if full_record:
                    data_from_paypage['PurchaseID'] = full_record['PurchaseID']
                    data_from_paypage['TransID'] = full_record['TransID']
                    data_from_paypage['full_record'] = full_record
                    config.test_data = {**config.test_data, **data_from_paypage}
                    return data_from_paypage
            else:
                return False
        except Exception as ex:
            traceback.print_exc()
    
    def fill_default(self, joinlink, selected_options, merchantid, packageid):
        data_from_paypage = {}
        elem = ''
        test_case = config.test_data
        page_loaded = self.navigate_to_url(joinlink)
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
            paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(test_case['lang'])
            if not test_case['lang'] == 'EN':
                while self.br.execute_script("return jQuery.active == 0") != True:
                    time.sleep(1)
                # time.sleep(2)
            if self.br.find_by_id('UserNameInput'):
                self.br.find_by_id('UserNameInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
            if self.br.find_by_id('PasswordInput'):
                self.br.find_by_id('PasswordInput').fill(self.fake.user_name() + str(random.randint(333, 999)))
            if self.br.find_by_id('CurrencyDDL'):
                merchant_currency = self.br.find_by_id('CurrencyDDL').select(test_case['dmc'])
            
            merchant_country = self.br.find_by_id('CountryDDL').value
            cc = test_case['cc']
            card_encrypted = db_agent.encrypt_card(cc)
            if not db_agent.execute_select_one_parameter(constants.FRAUD_CARD_CHECK, card_encrypted):
                db_agent.execute_insert(constants.FRAUD_CARD_INSERT, card_encrypted)
            cvv = str(random.randint(111, 999))
            firstname = self.fake.first_name()
            lastname = self.fake.first_name()
            email_encrypt = db_agent.encrypt_email(email)
            data_from_paypage['card_encrypted'] = card_encrypted
            data_from_paypage['transbin'] = int(str(cc)[:6])
            data_from_paypage['transguid'] = transguid
            data_from_paypage['email'] = email
            data_from_paypage['zip'] = '33333'
            data_from_paypage['email_encrypt'] = email_encrypt
            data_from_paypage['merchant_country'] = merchant_country
            data_from_paypage['expiration_date'] = '01'
            data_from_paypage['year'] = '2023'
            data_from_paypage['firstname'] = firstname
            data_from_paypage['lastname'] = lastname
            data_from_paypage['merchant_currency'] = test_case['dmc']
            data_from_paypage['paypage_lnaguage'] = self.br.find_by_id('LanguageDDL').value
            self.wait_for_ajax(self.br)
            if config.test_data['payment'] == 'cc':
                # print(
                #     'Credit Card payment')
                self.br.find_by_id('CreditCardInputNumeric').fill(cc)  # CreditCardInputNumeric  older CreditCardInput
                self.br.find_by_id('CVVInputNumeric').fill(cvv)  # new CVVInputNumeric old CVVInput
                while self.br.execute_script("return jQuery.active == 0") != True:
                    time.sleep(1)
                self.br.find_by_id('CCExpMonthDDL').select('01')
                self.br.find_by_id('CCExpYearDDL').select('2023')
                self.br.find_by_id('FirstNameInput').fill(firstname)
                self.br.find_by_id('LastNameInput').fill(lastname)
                self.br.find_by_id('ZipInput').fill('33333')
                self.br.find_by_id('EMailInput').fill(email)
                self.wait_for_ajax(self.br)
                self.br.find_by_id('SecurePurchaseButton').click()
                # time.sleep(1)
                while self.br.execute_script("return jQuery.active == 0") != True:
                    time.sleep(1)
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
                return data_from_paypage
            elif config.test_data['payment'] == 'pp':
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
        pass
    
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
            multitrans_oneclick_record = {}
            sql = "select * from MerchantBillConfig where BillConfigID = {}"
            mbconfig = db_agent.execute_select_one_parameter(sql, d['pricepoint'])
            pricepoint_type = d['pp_type']
            merchantid = d['MerchantID']
            username = 'UserName' + str(random.randint(333, 999))
            password = 'Password' + str(random.randint(333, 999))
            page_loaded = self.navigate_to_url(d['link'])
            if page_loaded == False:
                return None
            else:
                if self.br.is_element_present_by_id('TransGUID', wait_time=10):
                    transguid = self.br.find_by_id('TransGUID').value
                    transguid = subprocess.run(
                            ['C:\\segpay_qa_automation\\pos\\point_of_sale\\transguid\\TransGuidDecoderApp.exe', transguid,
                             '-l'],
                            stdout=subprocess.PIPE)
                    transguid = transguid.stdout.decode('utf-8')
                else:
                    print("Transguid not Found ")
                    return None
                    # time.sleep(2)
                if d['lang'] != 'EN':
                    paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(d['lang'])
                    # time.sleep(2)
                    while self.br.execute_script("return jQuery.active == 0") != True:
                        time.sleep(1)
                if d['dmc'] != 'USD':
                    try:
                        dmc = self.br.find_by_id('CurrencyDDL').select(d['dmc'])
                        while self.br.execute_script("return jQuery.active == 0") != True:
                            time.sleep(1)
                    except Exception as ex:
                        traceback.print_exc()
                        pass
                
                self.br.find_by_id('CVVInputNumeric').fill('333')
                if self.br.find_by_id('UserNameInput'):
                    self.br.find_by_id('UserNameInput').fill(username)
                if self.br.find_by_id('PasswordInput'):
                    self.br.find_by_id('PasswordInput').fill(password)
                while self.br.execute_script("return jQuery.active == 0") != True:
                    time.sleep(1)
                self.br.find_by_id('SecurePurchaseButton').click()
                # time.sleep(1)
                while self.br.execute_script("return jQuery.active == 0") != True:
                    time.sleep(1)
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
                    config.logging.info(ex)
                
                cnt = 0
                while oneclick_record == None and cnt < 15:
                    cnt += 1
                    time.sleep(1)
                    sql = "select * from multitrans where TransGuid = '{}'"
                    oneclick_record = db_agent.execute_select_one_parameter(sql, transguid)
                
                if pricepoint_type == 511:
                    oneclick_record['511'] = pricingguid
                elif pricepoint_type == 510:
                    oneclick_record['510'] = dynamic_price
                sql = "Select PurchType from assets where purchaseid = {}"
                token_type = db_agent.execute_select_one_parameter(sql, d['octoken'])['PurchType']
                # 3333333333333333333333333token_type = config.oc_tokens[octoken]
                card = db_agent.execute_select_one_parameter(constants.GET_PAYMENTACCT_FROM_ASSET, d['octoken'])
            config.test_case['actual'] = [
                f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}"]

            config.test_case['oneclick_record_pos'] = oneclick_record
        except Exception as ex:
            traceback.print_exc()
            pass
        
        return oneclick_record  # , pricepoint_type
    
    def instant_conversion(self, option, signup_record):
        transguid = ''
        url = ''
        full_record = {}
        multitrans_base_record = signup_record['full_record']
        multitrans_ic_record = copy.deepcopy(multitrans_base_record)
        token = multitrans_base_record['TRANSGUID']
        username = fake.user_name() + str(random.randint(333, 999))
        password = fake.user_name() + str(random.randint(333, 999))
        try:
            if option == 'pos':
                url = config.test_data['link']
                page_loaded = self.navigate_to_url(url)
                if page_loaded == False:
                    return None
                else:
                    if self.br.is_element_present_by_id('TransGUID', wait_time=10):
                        transguid = self.br.find_by_id('TransGUID').value
                        transguid = subprocess.run(
                                ['C:\\segpay_qa_automation\\pos\\point_of_sale\\transguid\\TransGuidDecoderApp.exe', transguid,
                                 '-l'],
                                stdout=subprocess.PIPE)
                        transguid = transguid.stdout.decode('utf-8')
                    else:
                        print("Transguid not Found ")
                        return None
                    self.br.find_by_id('EMailInput').fill(signup_record['email'])
                    self.br.find_by_id('SecurePurchaseButton').click()
                    full_record = db_agent.multitrans_full_record('', transguid, '')[0]
            elif option == 'ws':
                resp = requests.get(config.test_data['link'])
                xml_return_string = simplexml.loads(resp.content)
                transid = int(xml_return_string['TransReturn']['TransID'])
                full_record = db_agent.multitrans_full_record(transid, '', '')[0]
            
            if full_record:
                config.test_data['PurchaseID'] = full_record['PurchaseID']
                config.test_data['TransID'] = full_record['TransID']
                config.test_data['full_record'] = full_record
                
                # full_record = ic_record[0]
                multitrans_ic_record['TransSource'] = 122
                multitrans_ic_record['TransType'] = 108
                multitrans_ic_record['TransStatus'] = 186
                multitrans_ic_record['PurchaseID'] = full_record['PurchaseID']
                multitrans_ic_record['TransID'] = full_record['TransID']
                multitrans_ic_record['TRANSGUID'] = transguid
                multitrans_ic_record['RelatedTransID'] = multitrans_base_record['TransID']
                multitrans_ic_record['TransAmount'] = config.test_data['RebillPrice']
                exchange_rate = 1
                if config.test_data['Currency'] == multitrans_base_record['MerchantCurrency']:
                    exchange_rate = 1
                else:
                    exchange_rate = db_agent.exc_rate(multitrans_base_record['MerchantCurrency'], config.test_data['Currency'])
                    if multitrans_base_record['MerchantCurrency'] != 'JPY':
                        exchange_rate = round(exchange_rate, 2)
                multitrans_ic_record['ExchRate'] = exchange_rate
                markup = round(config.test_data['RebillPrice'] * exchange_rate, 2)
                multitrans_ic_record['Markup'] = markup
                print(
                        f"InstantConversion POS Conversion => PurchaseID: {full_record['PurchaseID']} | TransID: {full_record['TransID']} | Type: 507 | Processor: {multitrans_base_record['Processor']} "
                        f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")
                
                return multitrans_ic_record, full_record
            else:
                return False
        except Exception as ex:
            traceback.print_exc()
            pass
        #     elif option == 'ws':
        #
        #         resp = requests.get(config.test_data['link'])
        #         xml_return_string = simplexml.loads(resp.content)
        #         transid = int(xml_return_string['TransReturn']['TransID'])
        #         oneclick_record = db_agent.multitrans_full_record(transid, '', '')
        #         full_record = oneclick_record[0]
        #
        #         multitrans_ic_record['TransSource'] = 123
        #         multitrans_ic_record['TransType'] = 1011
        #         multitrans_ic_record['TransStatus'] = 186
        #         multitrans_ic_record['PurchaseID'] = full_record['PurchaseID']
        #         multitrans_ic_record['TransID'] = transid
        #         multitrans_ic_record['TRANSGUID'] = full_record['TRANSGUID']
        #         multitrans_ic_record['RelatedTransID'] = multitrans_base_record['TransID']
        #         print(f"OneClick WS => Eticket: {config.test_data['eticket']} | Type: 507 | Processor: {multitrans_base_record['Processor']} "
        #               f"| DMC: {multitrans_base_record['MerchantCurrency']} | Lnaguage: {multitrans_base_record['Language']}")
        #
        #         return multitrans_ic_record, oneclick_record
        #
        #
        # except Exception as ex:
        #     traceback.print_exc()
        #     pass
    
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
    
    def one_click_pos(self, eticket, octoken, currency_lang, url_options):
        oneclick_record = None
        dynamic_price = 9999
        pricingguid = ''
        if config.test_data['Type'] == 505:
            print("___________________Delay Capture One Click is not allowed_____________")
            print()
            return None
        
        try:
            ppid = eticket.split(':')
            multitrans_oneclick_record = {}
            sql = "select * from MerchantBillConfig where BillConfigID = {}"
            mbconfig = db_agent.execute_select_one_parameter(sql, ppid[1])
            pricepoint_type = mbconfig['Type']
            merchantid = mbconfig['MerchantID']
            username = 'UserName' + str(random.randint(333, 999))
            password = 'Password' + str(random.randint(333, 999))
            
            if pricepoint_type == 510:
                dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
                hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
                resp = requests.get(hash_url)
                dynamic_hash = fromstring(resp.text).text
                url = f"{config.url}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}" + url_options
            elif pricepoint_type == 511:
                pricingguid = db_agent.get_pricingguid(merchantid, pricepoint_type)[0]
                url = f"{config.url}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
            else:
                url = f"{config.url}{eticket}&octoken={octoken}" + url_options
            
            print(url)
            # config.logging.info(url)
            page_loaded = self.navigate_to_url(url)
            if page_loaded == False:
                return None
            else:
                if self.br.is_element_present_by_id('TransGUID', wait_time=10):
                    transguid = self.br.find_by_id('TransGUID').value
                    transguid = subprocess.run(
                            ['C:\\segpay_qa_automation\\pos\\point_of_sale\\transguid\\TransGuidDecoderApp.exe', transguid,
                             '-l'],
                            stdout=subprocess.PIPE)
                    transguid = transguid.stdout.decode('utf-8')
                else:
                    print("Transguid not Found ")
                    return None
                if currency_lang[1] != 'EN':
                    paypage_lnaguage = self.br.find_by_id('LanguageDDL').select(currency_lang[1])
                    time.sleep(2)
                self.br.find_by_id('CVVInputNumeric').fill('333')
                if self.br.find_by_id('UserNameInput'):
                    self.br.find_by_id('UserNameInput').fill(username)
                if self.br.find_by_id('PasswordInput'):
                    self.br.find_by_id('PasswordInput').fill(password)
                while self.br.execute_script("return jQuery.active == 0") != True:
                    time.sleep(1)
                self.br.find_by_id('SecurePurchaseButton').click()
                time.sleep((2))
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
                    config.logging.info(ex)
                
                cnt = 0
                while oneclick_record == None and cnt < 15:
                    cnt += 1
                    time.sleep(1)
                    sql = "select * from multitrans where TransGuid = '{}'"
                    oneclick_record = db_agent.execute_select_one_parameter(sql, transguid)
                
                if pricepoint_type == 511:
                    oneclick_record['511'] = pricingguid
                elif pricepoint_type == 510:
                    oneclick_record['510'] = dynamic_price
                token_type = config.oc_tokens[octoken]
                card = db_agent.execute_select_one_parameter(constants.GET_PAYMENTACCT_FROM_ASSET, octoken)
                config.test_data['cc'] = card['cc']
            try:
                merchant_us_or_eu = db_agent.merchant_us_or_eu(merchantid)
                merchant_us_or_eu = merchant_us_or_eu['MerchantCountry']
                visa_secure = options.is_visa_secure()
                if merchant_us_or_eu == 'US':
                    if visa_secure in [1, 4]:
                        config.test_data['visa_secure'] = 5  # Configured for 3ds
                        print(colored(f"US Merchant 3DS configured - Not in Scope  | Card {config.test_data['cc']} ",
                                      'yellow', 'on_grey', attrs=['blink']))
                    else:
                        config.test_data['visa_secure'] = 6  # not configured at 3ds
                        print(colored(f"US Merchant 3DS not configured - Not in Scope | Card {config.test_data['cc']} ",
                                      'yellow', 'on_grey', attrs=['blink']))
                else:
                    if visa_secure == 0:
                        print(
                                colored(f"EU Merchant  Prepaid card  | Card {config.test_data['cc']} ", 'yellow', 'on_grey',
                                        attrs=['blink']))
                        config.logging.info(colored(f" Prepaid card  | Short Form ", 'blue'))
                    elif visa_secure == 1:
                        print(colored(
                                f"EU Merchant 3DS configured - Not in Scope  for PSD2 | Card {config.test_data['cc']} ",
                                'yellow', 'on_grey', attrs=['blink']))
                        config.logging.info(
                                colored(f" 3DS configured - Not in Scope  for PSD2 | Card {config.test_data['cc']}",
                                        'blue'))
                    elif visa_secure == 2:
                        print(colored(
                                f"EU Merchant 3DS not configured | In Scope  for PSD2 | Card {config.test_data['cc']} ",
                                'yellow', 'on_grey', attrs=['blink']))
                        config.logging.info(
                                colored(f" 3DS not configured | In Scope  for PSD2 | Card {config.test_data['cc']} ",
                                        'blue', attrs=['bold']))  # will decline
                    elif visa_secure == 3:
                        print(colored(
                                f"EU Merchant 3DS not configured | Not in Scope  for PSD2 | Card {config.test_data['cc']} ",
                                'yellow', 'on_grey', attrs=['blink']))
                        config.logging.info(
                                colored(f" 3DS not configured | Not in Scope  for PSD2 | Card {config.test_data['cc']} ",
                                        'blue'))
                    elif visa_secure == 4:
                        print(colored(
                                f"EU Merchant 3DS  configured |  in Scope  for PSD2 | Extended Form | Card {config.test_data['cc']} ",
                                'yellow', 'on_grey', attrs=['blink']))
                        config.logging.info(colored(
                                f" 3DS  configured |  in Scope  for PSD2 | Extended Form | Card {config.test_data['cc']}",
                                'blue'))
                    config.test_data['visa_secure'] = visa_secure
            except Exception as ex:
                traceback.print_exc()
                print(f"{Exception}")
                pass
            
            config.test_case['actual'] = [
                f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}"]
            print(f"OneClick POS => Eticket: {eticket}  | Processor: {oneclick_record['Processor']} "
                  f"| Lnaguage: {currency_lang[1]} | Type: {pricepoint_type} TokenType: {token_type} ")
            print(
                    f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}")
        
        except Exception as ex:
            traceback.print_exc()
            print(f"{Exception}  Eticket: {eticket}  ")
            config.logging.info(f"{Exception}  Eticket: {eticket}  ")
            pass
        
        return oneclick_record  # , pricepoint_type
    
    def reactivate(self, transids):
        transguids = {}
        reactivated = []
        asset_reactivated = {}
        mt_reactivated = {}
        not_reactivated = []
        
        tid = ''
        reactivate_tids = bep.get_data_before_action(transids, 'reactivation')
        sql = "Select TransGuid from Multitrans where TransID = {} "  # and TransType in ( 101,1011)
        try:
            for tid in reactivate_tids[1]:
                try:
                    pid = reactivate_tids[1][tid]['PurchaseID']
                    purch_type = reactivate_tids[0][pid]['PurchType']
                    
                    if purch_type in [501, 506, 505, 511]:
                        transguid = reactivate_tids[1][tid]['TRANSGUID']
                        reactivate_record = reactivate_tids[1][tid]
                        # pid = reactivate_tids[1][tid]['PurchaseID']
                        config.test_data['zip'] = '33063'
                        config.test_data['firstname'] = fake.first_name()
                        config.test_data['lastname'] = fake.last_name()
                        cc = config.test_data['cc']  # 4444333322221111
                        config.test_data['month'] = '02'
                        config.test_data['year'] = '2025'
                        config.test_data['cvv'] = '888'
                        joinlink = f"{config.reactivation_url}{transguid}&sprs=mp"
                        tasks_type_status = db_agent.tasks_table(tid)
                        db_agent.update_package(reactivate_record['PackageID'], reactivate_record['MerchantID'],
                                                reactivate_record['BillConfigID'])
                        self.navigate_to_url(joinlink)
                        time.sleep(1)
                        
                        if 'This subscription is not eligible for reactivation.' in self.br.html:
                            not_reactivated.append(
                                    f"This subscription is not eligible for reactivation => {transguid} | PurchaseID : {reactivate_record['PurchaseID']} | Type:{reactivate_tids[0][reactivate_record['PurchaseID']]['PurchType']} "
                                    f"| DMC: {reactivate_record['MerchantCurrency']} | RefundType: {tasks_type_status[0]} | TransType: {reactivate_record['TransType']}")
                        else:
                            if tasks_type_status[0] == 841:
                                self.br.find_by_id('CreditCardInputNumeric').fill(
                                        cc)  # CreditCardInputNumeric  older CreditCardInput
                                time.sleep(2)
                                self.br.find_by_id('ZipInput').fill(config.test_data['zip'])
                                self.br.find_by_id('FirstNameInput').fill(config.test_data['firstname'])
                                self.br.find_by_id('LastNameInput').fill(config.test_data['lastname'])
                                self.br.find_by_id('CCExpMonthDDL').select(config.test_data['month'])
                                self.br.find_by_id('CCExpYearDDL').select(config.test_data['year'])
                                self.br.find_by_id('CVVInputNumeric').fill(config.test_data['cvv'])
                                while self.br.execute_script("return jQuery.active == 0") != True:
                                    time.sleep(1)
                                time.sleep(1)
                                self.br.find_by_id('SecurePurchaseButton').click()
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
                                except NoSuchFrameException:
                                    pass
                                except Exception as ex:
                                    traceback.print_exc()
                                    print(ex)
                                    config.logging.info(ex)
                                cnt = 0;
                                reactivation_complete = None
                                while reactivation_complete == None and cnt < 10:
                                    cnt += 1
                                    sql = "Select * from multitrans where PurchaseID = {} and TransSource = 127"
                                    reactivation_complete = db_agent.execute_select_one_parameter(sql, pid)
                                    time.sleep(1)
                                if reactivation_complete == None:
                                    print(
                                            f"******* Warning => transaction with TransID: {tid} is not Reactiavted - Check Manually ! *******")
                                    config.logging.info(
                                            f"******* Warning => transaction with TransID: {tid} is not Reactiavted - Check Manually ! *******")
                                    raise Exception('norecord')
                                else:
                                    time.sleep(1)
                                    reactivated.append(
                                            f"Subscription has been reactivated => {transguid} | PurchaseID : {reactivate_record['PurchaseID']} | Type:{reactivate_tids[0][reactivate_record['PurchaseID']]['PurchType']} "
                                            f"| DMC: {reactivate_record['MerchantCurrency']} | RefundType: {tasks_type_status[0]} | TransType: {reactivate_record['TransType']}")
                            else:
                                self.br.find_by_id('SecurePurchaseButton').click()
                                time.sleep(1)
                                reactivated.append(
                                        f"Subscription has been reactivated => {transguid} | PurchaseID : {reactivate_record['PurchaseID']} | Type:{reactivate_tids[0][reactivate_record['PurchaseID']]['PurchType']} "
                                        f"| DMC: {reactivate_record['MerchantCurrency']} | RefundType: {tasks_type_status[0]} | TransType: {reactivate_record['TransType']}")
                            mt_reactivated[tid] = reactivate_tids[1]
                            asset_reactivated[reactivate_record['PurchaseID']] = reactivate_tids[0]
                except Exception as ex:
                    print(f"{Exception}  Tid: {tid,}  ")
                    config.logging.info(ex)
                    traceback.print_exc()
                    pass
            
            print()
            
            if len(not_reactivated) > 0:
                print(
                        "*================================>   Subscriptions are not eligible for reactivation  <================================*")
                for i in not_reactivated:
                    print(i)
                    config.logging.info(i)
                print()
                config.logging.info('')
            print(
                    "*================================>   Subscriptions have been  reactivated      <================================*")
            for i in reactivated:
                print(i)
                config.logging.info(i)
            print()
            config.logging.info('')
            config.asset_reactivated = asset_reactivated
            config.mt_reactivated = mt_reactivated
            return asset_reactivated, mt_reactivated
        except Exception as ex:
            print(f"{Exception}  Tid: {tid,}  ")
            config.logging.info(f"{Exception}  Tid: {tid,}  ")
            traceback.print_exc()
            pass
    
    def __del__(self):
        # self.br.quit()
        z = 3

# br = Browser(driver_name='chrome', options=chrome_options)
def one_click_services(eticket, octoken, currency_lang, url_options):
    oneclick_record = None;
    dynamic_price = 9999;
    pricingguid = ''
    
    try:
        ppid = eticket.split(':')
        multitrans_oneclick_record = {}
        sql = "select * from MerchantBillConfig where BillConfigID = {}"
        mbconfig = db_agent.execute_select_one_parameter(sql, ppid[1])
        pricepoint_type = mbconfig['Type']
        merchantid = mbconfig['MerchantID']
        if pricepoint_type == 510:
            dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
            hash_url = f"https://srs.segpay.com/PricingHash/PricingHash.svc/GetDynamicTrans?value={dynamic_price}"
            resp = requests.get(hash_url)
            dynamic_hash = fromstring(resp.text).text
            url = f"{config.urlws}{eticket}&amount={dynamic_price}&dynamictrans={dynamic_hash}&dynamicdesc=QA+TEST&octoken={octoken}" + url_options
        elif pricepoint_type == 511:
            pricingguid = db_agent.get_pricingguid(merchantid, pricepoint_type)[0]
            url = f"{config.urlws}{eticket}&DynamicPricingID={pricingguid['PricingGuid']}&octoken={octoken}" + url_options
        else:
            url = f"{config.urlws}{eticket}&octoken={octoken}" + url_options
        print(url)
        resp = requests.get(url)
        xml_return_string = simplexml.loads(resp.content)
        transid = int(xml_return_string['TransReturn']['TransID'])
        # oneclick_record = db_agent.multitrans_full_record(transid, '', '')
        # full_record = oneclick_record[0]
        cnt = 0
        while oneclick_record == None and cnt < 15:
            cnt += 1
            time.sleep(1)
            sql = "select * from multitrans where TransID = '{}'"
            oneclick_record = db_agent.execute_select_one_parameter(sql, transid)
        
        if pricepoint_type == 511:
            oneclick_record['511'] = pricingguid
        elif pricepoint_type == 510:
            oneclick_record['510'] = dynamic_price
        print(f"OneClick Web Services => Eticket: {eticket}  | Processor: {oneclick_record['Processor']} "
              f"| DMC: {currency_lang[0]} | Lnaguage: {currency_lang[1]} | Type: {pricepoint_type}")
        print(
                f"PurchaseID: {oneclick_record['PurchaseID']} | TransID: {oneclick_record['TransID']} | TransGuid: {oneclick_record['TRANSGUID']}")
        return oneclick_record
    
    
    
    
    except Exception as ex:
        traceback.print_exc()
        print(f"{Exception}  Eticket: {eticket} Module => one_click_services ")
        pass
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
