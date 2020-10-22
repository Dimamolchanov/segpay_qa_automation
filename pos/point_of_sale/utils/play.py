from playwright import sync_playwright


with sync_playwright() as p:
    #p.chromium.launch(headless=False)
    browser = p.firefox.launch(headless=False)
    page = browser.newPage()
    page.goto('https://qas2.segpay.com/billing/poset.cgi?x-eticketid=900:27072')
    page.type("input[id=FirstNameInput]", "Yan")
    page.type("input[id=LastNameInput]", "Test")

    
    
    page.type("input[id=CreditCardInputNumeric]", "4444333322221111")
    page.selectOption('select#CCExpMonthDDL', '05')
    page.selectOption('select#CCExpYearDDL', '2023')
    page.type("input[id=CVVInputNumeric]", "444")
    page.type("input[id=EMailInput]", "1@2.com")
    page.type("input[id=ZipInput]", "33063")
    page.type("input[id=UserNameInput]", "q123456")
    page.type("input[id=PasswordInput]", "qew123456")
    page.check('input[name=x-xsale1-accept]')

    
    
    #handle = page.evaluate('input[id=CreditCardInputNumeric]').textContent
    
    handle = page.querySelector("input[id=CreditCardInputNumeric]").textContent()
    
    print(handle.textContent ())
    page.dispatchEvent('button[id=SecurePurchaseButton]', 'click')
    #page.click("button[id=SecurePurchaseButton]")
    # page.waitForSelector("text=microsoft/Playwright")

    browser.close()





