#=== NOTE === for each line that begins "### TODO- ", do not remove the line

from robocorp.tasks import task
from robocorp import browser

### TODO-01
import re
import json
import os
import shutil
import zipfile
from datetime import datetime

# Global variables
page = ""
acc_no = ""

# Constants
url = "https://com397bankdemo.z16.web.core.windows.net/#/login"
output_dir = "output"
agreements_dir = "agreements"

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
def onboard_customers():
    os.makedirs(agreements_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    with open("new-customers.json", "r", encoding="UTF-8") as customer_file:
        customers = json.load(customer_file)

    ### TODO-06
    for customer in customers:
        fn = customer["first_name"]
        ln = customer["last_name"]
        pc = customer["zip_code"]
        cn = customer["currency"]

        add_customer(fn, ln, pc, cn)

    return True

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
    # Create agreements and output directories if they don't exist
    os.makedirs(agreements_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    ### TODO-05
    with open("new-customers.json", "r", encoding="UTF-8") as customer_file:
        customers = json.load(customer_file)
    
    # Read the last processed index
    state_file = os.path.join(output_dir, "last_processed_index.txt")
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            last_index = int(f.read().strip())
    else:
        last_index = -1
    
    # Process the next customer
    next_index = last_index + 1
    if next_index < len(customers):
        customer = customers[next_index]
        fn = customer["first_name"]
        ln = customer["last_name"]
        pc = customer["zip_code"]
        cn = customer["currency"]
        add_customer(fn, ln, pc, cn)
        
        # Update the state file
        with open(state_file, "w") as f:
            f.write(str(next_index))
        print(f"Processed customer {next_index + 1}/{len(customers)}: {fn} {ln}")
        return False  # Not all processed yet
    else:
        print("All customers have been processed.")
        return True  # All processed


def add_customer(fn, ln, pc, cn):
    print(f"Adding customer {fn} {ln}")
    global page
    page.locator(add_customer_button).click()

    # Check post code
    valid_zip_code = re.match(zip_code_re, pc)

    if valid_zip_code:
        page.locator(add_customer_form_first_name).fill(fn)
        page.locator(add_customer_form_last_name).fill(ln)
        page.locator(add_customer_form_zip_code).fill(pc)
        page.locator(add_customer_form_submit).click()

    dialog = page.wait_for_event("dialog")
    dialog.accept()

    print(f"Customer {fn} {ln} added successfully")
    page.wait_for_timeout(1000)

    

# Alert box handler functions
def handle_alert(dialog):
    dialog.accept()


def handle_alert_acc(dialog):
    global acc_no
    acc_no = ""

    ### TODO-09
    dialog_text = dialog.message
    match = re.search(r"\b(\d{5,})\b", dialog_text)
    if match:
        acc_no = match.group(1)
    else:
        print(f"Warning: could not extract account number from alert: {dialog_text}")

    dialog.accept()


def open_account(fn, ln, cn):
    global page
    global acc_no

    page.locator(open_account_button).click()

    # Select customer
    full_name = f"{fn} {ln}"
    page.locator(open_account_customer_select).select_option(label=full_name)

    # Select currency
    page.locator(open_account_currency_select).select_option(label=cn)

    # Handle alert to capture account number
    page.once("dialog", handle_alert_acc)

    # Click process
    page.locator(open_account_process).click()

    page.wait_for_timeout(1000)

    print(f"Account opened for {fn} {ln}, Account No: {acc_no}")

    create_agreements(fn, ln, cn, acc_no)


def create_agreements(fn, ln, cn, acc_no):
    # Credit agreement
    credit_filename = f"{ln}-{fn}-{acc_no}-credit-agreement.txt"
    credit_path = os.path.join(agreements_dir, credit_filename)

    with open(credit_path, "w") as f:
        f.write(f"Business Terms and Conditions for account: {acc_no}")

    # FX agreement if needed
    if cn in ["GBP", "Rupee"]:
        fx_filename = f"{ln}-{fn}-{acc_no}-FX-agreement.txt"
        fx_path = os.path.join(agreements_dir, fx_filename)

        with open(fx_path, "w") as f:
            f.write(f"Foreign Exchange Terms and Conditions for account: {acc_no}")

    zip_filename = f"agreements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(agreements_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                archive_name = os.path.relpath(file_path, agreements_dir)
                zipf.write(file_path, arcname=archive_name)

    os.makedirs(output_dir, exist_ok=True)
    output_zip_path = os.path.join(output_dir, zip_filename)
    shutil.copy2(zip_path, output_zip_path)

    print(f"Archived agreement documents to {zip_path} and copied to {output_zip_path}")


def generate_report():
    global page
    page.locator(customers_button).click()
    ### TODO-12
    page.wait_for_timeout(2000)
    report_path = os.path.join(output_dir, f"customer_table_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.locator(customer_list_table).screenshot(path=report_path)
    print(f"Report screenshot saved to {report_path}")
