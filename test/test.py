import splinter


from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://seleniumhq.org/')

















from splinter import Browser



browser = Browser()


browser.visit('http://google.com')
browser.fill('q', 'splinter - python acceptance testing for web applications')
button = browser.find_by_name('btnG')
button.click()
if browser.is_text_present('splinter.readthedocs.io'):
    print ("Yes, the official website was found!")
else:
    print("No, it wasn't found... We need to improve our SEO techniques")
browser.quit()