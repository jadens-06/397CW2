#=== NOTE === for each line that begins "### TODO- ", do not remove the line

from more_itertools import first, last
from robocorp.tasks import task
from robocorp import browser

### TODO-01
import re
import json
import os
import shutil
from datetime import datetime

# Global variables
page = ""
acc_no = ""

# Constants
url = "https://com397bankdemo.z16.web.core.windows.net/#/login"

### TODO-02
zip_code_re = r"^\d{5}(?:-\d{4})?$"

# Locators
bank_manager_login_button = "//html/body/div/div/div[2]/div/div[1]/div[2]/button"
add_customer_button = "//html/body/div/div/div[2]/div/div[1]/button[1]"
add_customer_form_first_name = "//html/body/div/div/div[2]/div/div[2]/div/div/form/div[1]/input"
add_customer_form_last_name = "//html/body/div/div/div[2]/div/div[2]/div/div/form/div[2]/input"
add_customer_form_zip_code = "//html/body/div/div/div[2]/div/div[2]/div/div/form/div[3]/input"
add_customer_form_submit = "//html/body/div/div/div[2]/div/div[2]/div/div/form/button"

### TODO-03
open_account_button = "//html/body/div/div/div[2]/div/div[1]/button[2]"
open_account_customer_select = "//html/body/div/div/div[2]/div/div[2]/div/div/select[1]"
open_account_currency_select = "//html/body/div/div/div[2]/div/div[2]/div/div/select[2]"
open_account_process = "//html/body/div/div/div[2]/div/div[2]/div/div/button"

### TODO-04
customers_button = "//html/body/div/div/div[2]/div/div[1]/button[3]"
customer_list_table = "//html/body/div/div/div[2]/div/div[2]/div/table"


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
    # Create agreements directory if it doesn't exist
    if not os.path.exists("agreements"):
        os.makedirs("agreements")
    
    ### TODO-05
    # set up customer_file
    with open("new-customers.json", "r", encoding="UTF-8") as customer_file:
        customers = json.load(customer_file)
    
    ### TODO-06
    for customer in customers:
        # split each customer record into individual fields (variables)
        fn = customer["first_name"]
        ln = customer["last_name"]
        pc = customer["zip_code"]
        cn = customer["currency"]
        add_customer(fn, ln, pc, cn)
        open_account(fn, ln, cn)

def add_customer(fn, ln, pc, cn):
    print(f"Adding customer {fn} {ln}")
    global page
    page.locator(add_customer_button).click()

    # Check post code
    valid_zip_code = re.match(zip_code_re, pc)

    if (valid_zip_code):
        ### TODO-07
        page.locator(add_customer_form_first_name).fill(fn)
        page.locator(add_customer_form_last_name).fill(ln)
        page.locator(add_customer_form_zip_code).fill(pc)
        page.locator(add_customer_form_submit).click()
        # Wait for the dialog to appear and handle it before returning
        dialog = page.wait_for_event("dialog")
        dialog.accept()
    else:
        ### TODO-08
        print(f"Invalid zip code: {pc}. Skipping customer {fn} {ln}")

def open_account(fn, ln, cn):
    global page
    global acc_no   # <-- MUST be before you assign to acc_no

    # Click "Open Account" button
    page.locator(open_account_button).click(force=True)

    # Select customer and currency
    page.locator(open_account_customer_select).select_option(f"{fn} {ln}")
    page.locator(open_account_currency_select).select_option(cn)

    # Submit the form
    page.locator(open_account_process).click()

    # --- Handle alert + extract account number ---
    dialog = page.wait_for_event("dialog")
    alert_text = dialog.message
    dialog.accept()

    acc_no = re.search(r"\d+", alert_text).group()

    # --- Create CREDIT agreement ---
    credit_filename = f"agreements/{ln}-{fn}-{acc_no}-credit-agreement.txt"
    with open(credit_filename, "w") as f:
        f.write(f"Business Terms and Conditions for account: {acc_no}")

    # --- FX agreement (GBP or Rupee only) ---
    if cn in ["GBP", "Rupee"]:
        fx_filename = f"agreements/{ln}-{fn}-{acc_no}-FX-agreement.txt"
        with open(fx_filename, "w") as f:
            f.write(f"Foreign Exchange Terms and Conditions for account: {acc_no}")


def zip_agreement_documents():
    ### TODO-11
    credit_filename = f"agreements/{last}-{first}-{acc_no}-credit-agreement.txt"
    with open(credit_filename, "w") as f:
        f.write(f"Business Terms and Conditions for account: {acc_no}")

    
def generate_report():
    global page
    page.locator(customers_button).click()
    ### TODO-12
    page.wait_for_timeout(2000)
    table_content = page.locator(customer_list_table).text_content()
    
    report_fn = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_fn, "w", encoding="UTF-8") as report_file:
        report_file.write("Bank Manager Customer Report\n")
        report_file.write("="*50 + "\n")
        report_file.write(table_content)
    
    print(f"Report generated: {report_fn}")

# Alert box handler functions
def handle_alert(dialog):
    dialog.accept()        

def handle_alert_acc(dialog):
    global page
    global acc_no
    acc_no = ""

    ### TODO-09
    dialog_text = dialog.message
    if "Account id" in dialog_text or "account" in dialog_text.lower():
        words = dialog_text.split()
        for word in words:
            if word.isdigit() and len(word) > 4:
                acc_no = word
                break
    
    dialog.accept()
    page.locator(open_account_button).click()
