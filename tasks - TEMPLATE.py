#=== NOTE === for each line that begins "### TODO- ", do not remove the line

from robocorp.tasks import task
from robocorp import browser

### TODO-01
import re
...

# Global variables
page = ""
acc_no = ""

# Constants
url = "https://com397bankdemo.z16.web.core.windows.net/#/login"

### TODO-02
zip_code_re = ...

# Locators
bank_manager_login_button = "//html/body/div/div/div[2]/div/div[1]/div[2]/button"
add_customer_button = "//html/body/div/div/div[2]/div/div[1]/button[1]"
add_customer_form_first_name = "//html/body/div/div/div[2]/div/div[2]/div/div/form/div[1]/input"
add_customer_form_last_name = "//html/body/div/div/div[2]/div/div[2]/div/div/form/div[2]/input"
add_customer_form_zip_code = "//html/body/div/div/div[2]/div/div[2]/div/div/form/div[3]/input"
add_customer_form_submit = "//html/body/div/div/div[2]/div/div[2]/div/div/form/button"

### TODO-03
open_account_button = ...
open_account_customer_select = ...
open_account_currency_select = ...
open_account_process = ...

### TODO-04
customers_button = ...
customer_list_table = ...


@task
def onboard_new_customers():
    bank_manager_login()
    onboard_customers()
    zip_agreement_documents()
    generate_report()

def bank_manager_login():
    browser.configure(
        slowmo=1,
        headless=False,
        browser_engine = "firefox"
    )
    browser.goto(url)
    global page
    page = browser.page()
    
    # Click "Bank Manager Login" Button
    page.locator(bank_manager_login_button).click()
    # page = browser.page()

def onboard_customers():
    ### TODO-05
    # set up customer_file
    # with open(
    
    ### TODO-06
        count = 0
        for customer in customer_file:
            # Eat header line
            ...
             
            # split each customer record into individual fields (variables)
            ...

def add_customer(fn, ln, pc, cn):
    print(f"Adding customer {fn} {ln}")
    global page
    page.locator(add_customer_button).click()

    # Check post code
    valid_zip_code = re.match(zip_code_re, pc)

    if (valid_zip_code):
        ### TODO-07
        ...
    else:
        ### TODO-08
        ...

def open_account(fn, ln, cn):
    global page
    # Click "Open Account" button
    page.locator(open_account_button).click(force=True)
    # select from list by label
    page.locator(open_account_customer_select).select_option(f"{fn} {ln}")
    page.locator(open_account_currency_select).select_option(cn)
    page.locator(open_account_process).click()

    global acc_no
    page.on("dialog", handle_alert_acc) # setting acc_no

    credit_agreement_fn = fn+"_"+ln+"_"+acc_no+"_credit_agreement.txt"
    with open(f"agreements/{credit_agreement_fn}", "w", encoding="UTF-8") as credit_agreement_file:
        credit_agreement_file.write(f"Business Terms and Conditions for account: {acc_no}\n")

    if cn == "Pound" or cn == "Rupee":
        ### TODO-10
        ...

def zip_agreement_documents():
    ### TODO-11
    ...
    
def generate_report():
    global page
    page.locator(customers_button).click()
    ### TODO-12

# Alert box handler functions
def handle_alert(dialog):
    dialog.accept()        

def handle_alert_acc(dialog):
    global page
    global acc_no
    acc_no = ""

    ### TODO-09
    ...

    page.locator(open_account_button).click()
