from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from datetime import datetime

def fetch_announcements_for_companies(companies):
    announcements = []
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    for company in companies:
        try:
            # Strip the company name of any whitespace
            company = company.strip()
            today = datetime.today().strftime('%Y%m%d')
            sgx_url = f'https://www.sgx.com/securities/company-announcements?value={company}&type=company&from={today}&to={today}&page=1&pagesize=50'
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
                announcements.append({'date': today, 'company': company, 'title': 'No announcements today.', 'link': ''})
            else:
                # Extract data if present
                rows = driver.find_elements(By.CSS_SELECTOR, "table.website-content-table tbody tr")
                for row in rows:
                    date = today
                    link_element = row.find_element(By.CSS_SELECTOR, "a.website-link")
                    title = link_element.text
                    link = link_element.get_attribute('href')
                    announcements.append({'date': date, 'company': company, 'title': title, 'link': link})
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Exception occurred for {company}: {e}")
            announcements.append({'date': today, 'company': company, 'title': 'Error retrieving announcements.', 'link': ''})

    driver.quit()
    return announcements

