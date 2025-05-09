from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path
import sys
import time

short_wait = 1

# Set up project output folder as download directory
project_root = Path(__file__).resolve().parent.parent
output_dir = str(project_root / "output")
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Set headless Chrome options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

prefs = {
    "download.default_directory": output_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# Create headless driver
driver = webdriver.Chrome(options=options)

def open_website():
    driver.get("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")
    driver.implicitly_wait(short_wait)

def select_something(XPATH_dropdown_list, XPATH_list_item):
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, XPATH_dropdown_list))
    )
    dropdown.click()

    list_item = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, XPATH_list_item))
    )
    list_item.click()

    # NEW: Wait for dropdown to collapse
    time.sleep(0.5)

def click_something(xpath, max_retries=3, wait_between_retries=1):
    """
    Attempts to find and click an element safely, handling click interception issues.
    
    Args:
        xpath (str): The xpath of the element you want to click.
        max_retries (int): Number of times to retry on failure.
        wait_between_retries (float): Wait time between retries in seconds.
    """
    for attempt in range(max_retries):
        try:
            # Always freshly find element
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            return  # Click successful
        except ElementClickInterceptedException:
            print(f"⚡ Click intercepted. Attempt {attempt+1}/{max_retries}. Retrying...")

            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                ActionChains(driver).move_to_element(element).pause(0.2).click(element).perform()
                return
            except Exception as e:
                print(f"⚠️ Still failed after scrolling: {e}")

            time.sleep(wait_between_retries)

        except StaleElementReferenceException:
            print(f"❌ Element is stale. Attempt {attempt+1}/{max_retries}. Retrying...")
            time.sleep(wait_between_retries)

    raise Exception(f"Failed to click the element at xpath {xpath} after {max_retries} retries.")


def E2W(two_wheeler_nt_path, two_wheeler_t_path):
    click_something(two_wheeler_nt_path)
    print("Log: 2W NT selected")
    sys.stdout.flush()
    click_something(two_wheeler_t_path)
    print("Log: 2W T selected")
    sys.stdout.flush()

def E3W(three_wheeler_nt_path, three_wheeler_t_path):
    click_something(three_wheeler_nt_path)
    print("Log: 3W NT selected")
    sys.stdout.flush()
    click_something(three_wheeler_t_path)
    print("Log: 3W T selected")
    sys.stdout.flush()

def en_date(list_of_dates, meta_year):
    match meta_year:
        case "2024" | "2028":
            feb_day = 29
        case _:
            feb_day = 28
    dates = {
        "JAN": f"01-31",
        "FEB": f"02-{feb_day}",
        "MAR": "03-31",
        "APR": "04-30",
        "MAY": "05-31",
        "JUN": "06-30",
        "JUL": "07-31",
        "AUG": "08-31",
        "SEP": "09-30",
        "OCT": "10-31",
        "NOV": "11-30",
        "DEC": "12-31"
    }
    list_of_dates_f = []
    for month in list_of_dates:
        month = month.strip().upper()
        if month in dates:
            dated = dates[month]
            list_of_dates_f.append(f"{meta_year}-{dated}")
        else:
            print(f"Warning: Unknown month '{month}' found. Skipping.")
            sys.stdout.flush()
    return list_of_dates_f

def return_header(rows, trim, year):
    if not rows or len(rows) < 4:
        print("Warning: Not enough rows to extract header. Returning default header.")
        sys.stdout.flush()
        return ["State", "RTO", "Variant", "OEM", "Total"]

    raw_months = rows[3][2:]
    raw_months = [m for m in raw_months if m and m.strip() != '']
    
    month_dates = en_date(raw_months, year)
    header = ["State", "RTO", "Variant", "OEM"] + month_dates + ["Total"]
    return header

def return_row(list_of_rows, serial_number, trim, var_ph, rto_ph, state_ph):
    try:
        row_data = list_of_rows[3 + serial_number]
    except IndexError:
        print(f"Warning: Row {3 + serial_number} is out of range. Skipping.")
        sys.stdout.flush()
        return None

    if not row_data or all((cell is None or cell.strip() == '') for cell in row_data):
        print(f"Warning: Empty or invalid row at index {3 + serial_number}. Skipping.")
        sys.stdout.flush()
        return None

    row = row_data[1:]
    maker = row[0].strip() if row[0] else "Unknown Maker"
    month_values_raw = row[2:]
    
    month_values = []
    for val in month_values_raw:
        val = val.strip() if isinstance(val, str) else val
        try:
            month_values.append(int(val))
        except (ValueError, TypeError):
            month_values.append(0)

    total = sum(month_values)
    final_row = [state_ph, rto_ph, var_ph, maker] + month_values + [total]
    return final_row
