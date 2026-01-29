from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import stat
import platform

from datetime import datetime
from datetime import timedelta

def get_previous_working_day():
    """Get the previous working day (skips weekends)"""
    today = datetime.today()
    # Monday = 0, Sunday = 6
    if today.weekday() == 0:  # Monday
        # Go back 3 days to Friday
        return today - timedelta(days=3)
    elif today.weekday() == 6:  # Sunday
        # Go back 2 days to Friday
        return today - timedelta(days=2)
    else:
        # Go back 1 day for any other day
        return today - timedelta(days=1)

def fetch_announcements_for_companies(companies):
    announcements = []
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Install and make ChromeDriver executable
    driver_path = ChromeDriverManager().install()
    os.chmod(driver_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
    
    # Remove quarantine attribute on macOS only
    if platform.system() == 'Darwin':  # Darwin is macOS
        try:
            os.system(f'xattr -cr "{os.path.dirname(driver_path)}"')
        except:
            pass
    
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    
    for company in companies:
        try:
            # Strip the company name of any whitespace
            company = company.strip()
            previous_working_day = get_previous_working_day()
            yesterday = previous_working_day.strftime('%Y%m%d')
            sgx_url = f'https://www.sgx.com/securities/company-announcements?value={company}&type=company&from={yesterday}&to={yesterday}&page=1&pagesize=50'
            driver.get(sgx_url)
            print(f"Extracting data for {company}")

            # Wait for either the no data icon to be visible or the data table to have rows
            no_data_icon_condition = EC.visibility_of_element_located((By.CSS_SELECTOR, "div.sgx-loader--error-empty-icon"))
            data_table_condition = EC.visibility_of_element_located((By.CSS_SELECTOR, "table.website-content-table tbody tr"))

            # Use any_of to wait for any of the conditions
            WebDriverWait(driver, 120).until(EC.any_of(no_data_icon_condition, data_table_condition))

            # Check if the no data icon is visible
            if driver.find_elements(By.CSS_SELECTOR, "div.sgx-loader--error-empty-icon"):
                print(f"No data to display for {company}")
                announcements.append({'date': yesterday, 'company': company, 'title': 'No announcements today.', 'link': ''})
            else:
                # Extract data if present
                rows = driver.find_elements(By.CSS_SELECTOR, "table.website-content-table tbody tr")
                for row in rows:
                    date = yesterday
                    link_element = row.find_element(By.CSS_SELECTOR, "a.website-link")
                    title = link_element.text
                    link = link_element.get_attribute('href')
                    announcements.append({'date': date, 'company': company, 'title': title, 'link': link})
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Exception occurred for {company}: {e}")
            announcements.append({'date': yesterday, 'company': company, 'title': 'Error retrieving announcements.', 'link': ''})

    driver.quit()
    return announcements

