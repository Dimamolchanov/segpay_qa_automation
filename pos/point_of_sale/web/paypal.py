import random
from faker import Faker
import time
import traceback
import os
from pos.point_of_sale.db_functions.dbactions import DBActions
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import subprocess
from selenium.webdriver.support.ui import Select
from pos.point_of_sale.utils import constants

db_agent = DBActions()


class PayPal:

    def __init__(self):
        self.path = os.path.join((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                 'transguid\\TransGuidDecoderApp.exe')
        self.fake = Faker()
        self.br = webdriver.Chrome()
        self.br.set_window_position(-1400, 0)

    def is_element_present(self, how, what):
        try:
            self.br.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def wait_for_ajax(self, driver):
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            pass

    def fill_paypal(self, test_case):
        cnt = 0
        page_loaded = self.br.get(test_case['link'])
        transguid = ''
        if page_loaded == False:
            return None
        email = 'qateam@segpay.com'  # fake.email()
        try:
            if self.is_element_present(By.ID, 'TransGUID'):
                transguid = self.br.find_element_by_id('TransGUID').get_attribute('value')
                transguid = subprocess.run([self.path, transguid, '-l'], stdout=subprocess.PIPE)
                transguid = transguid.stdout.decode('utf-8')
            else:
                print("Transguid not Found ")
                return None
        except Exception as ex:
            traceback.print_exc()
            print(f"Exception {Exception} ")

        try:
            window_before = self.br.window_handles[0]

            if self.is_element_present(By.ID, 'UserNameInput'):
                self.br.find_element_by_id('UserNameInput').send_keys("test" + str(random.randint(333, 999)))
            if self.is_element_present(By.ID, 'PasswordInput'):
                self.br.find_element_by_id('PasswordInput').send_keys("test" + str(random.randint(333, 999)))
            self.br.find_elements_by_css_selector("input[name='paymentoption'][value='1301']")[0].click()

            iframe = self.br.find_element_by_css_selector("iframe[title='paypal_buttons']")
            firstname = self.fake.first_name()
            lastname = self.fake.first_name()
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
            merchant_country = self.br.find_element_by_id('CountryDDL').get_attribute('value')
            test_case['merchant_country'] = merchant_country
            test_case['expiration_date'] = '01'
            test_case['year'] = '2023'
            test_case['firstname'] = firstname
            test_case['lastname'] = lastname
            test_case['merchant_currency'] = test_case['dmc']
            test_case['paypage_lnaguage'] = self.br.find_element_by_id('LanguageDDL').get_attribute('value')

            while self.br.find_element_by_css_selector("iframe[title='paypal_buttons']") == False:
                time.sleep(1)
            self.br.switch_to.frame(iframe)
            while self.wait_for_ajax(self.br) == False:
                # page_loaded = page_has_loaded(br)
                print('jquery')
                time.sleep(1)
            wait = WebDriverWait(self.br, 10)
            elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button']")))
            elem.click()
            time.sleep(2)
            window_after = self.br.window_handles[1]
            self.br.switch_to.window(window_after)
            self.br.set_window_position(-1400, 0)

            while self.wait_for_ajax(self.br) == False:
                # page_loaded = page_has_loaded(br)
                time.sleep(1)

            try:
                if self.is_element_present(By.ID, 'email'):
                    email = WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.ID, "email")))
                    email.send_keys("yan@segpay.com")
            except NoSuchElementException:
                print("No email field")
                pass
            try:
                if self.is_element_present(By.NAME, "btnNext"):
                    self.br.find_element_by_name("btnNext").click()
            except NoSuchElementException:
                print("no button continue")
                pass
            try:
                if self.is_element_present(By.ID, "password"):
                    passw = WebDriverWait(self.br, 15).until(EC.visibility_of_element_located((By.ID, "password")))
                    passw.send_keys("Karapuz2")
            except NoSuchElementException:
                print("no button continue")
                pass
            try:
                if self.is_element_present(By.NAME, "btnLogin"):
                    self.br.find_element_by_name("btnLogin").click()
            except NoSuchElementException:
                print("no button continue")
                pass
            cc_selection = WebDriverWait(self.br, 20).until(EC.visibility_of_element_located((By.NAME, "selectedFI")))

            while self.br.page_source.find("Cancel and return to test facilitator's Test Store") == False:
                time.sleep(1)

            try:
                time.sleep(2)
                # elem = br.find_element_by_id("preloaderSpinner")
                # while elem.is_displayed():
                #     time.sleep(1)
                #     print('spinner')
                if self.is_element_present(By.CSS_SELECTOR, ".btn.full.confirmButton.continueButton"):
                    ready_to_click = WebDriverWait(self.br, 100).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.full.confirmButton.continueButton")))
                    ready_to_click.click()
                    # br.find_element_by_css_selector(".btn.full.confirmButton.continueButton").click()
                elif self.is_element_present(By.ID, "fiSubmitButton"):
                    ready_to_click = WebDriverWait(self.br, 100).until(
                        EC.element_to_be_clickable((By.ID, "fiSubmitButton")))
                    ready_to_click.click()
                    # br.find_element_by_id("fiSubmitButton").click()
            except NoSuchElementException:
                print("No element found .btn.full.confirmButton.continueButton")
                pass

            try:
                time.sleep(2)
                if self.is_element_present(By.ID, "confirmButtonTop"):
                    ready_to_click = WebDriverWait(self.br, 100).until(
                        EC.element_to_be_clickable((By.ID, "confirmButtonTop")))
                    ready_to_click.click()
                    # br.find_element_by_id("confirmButtonTop").click()
                elif self.is_element_present(By.ID, "consentButton"):
                    ready_to_click = WebDriverWait(self.br, 100).until(
                        EC.element_to_be_clickable((By.ID, "consentButton")))
                    ready_to_click.click()
                    # br.find_element_by_id("consentButton").click()
            except NoSuchElementException:
                print("crap")
                pass

            self.br.switch_to.window(window_before)
            while self.br.current_url != "https://stgs2.segpay.com/PayPage/Receipt" and cnt < 10:
                cnt += 1
                time.sleep(1)
            z = 3
            cnt = 0
        except Exception as ex:
            traceback.print_exc()
            print(f"Exception {Exception} ")
            pass
            # br.quit()
        return test_case

    def __del__(self):
        self.br.quit()
