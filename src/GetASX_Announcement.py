def fetch_ASX_announcements(company, year, target_dir):

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    import os
    from datetime import datetime
    import re
 

    # Function to wait for a new PDF to be downloaded
    def wait_for_new_pdf(download_dir, previous_files, timeout=300):
        start_time = time.time()
        while True:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - previous_files
            new_pdfs = {f for f in new_files if f.endswith('.pdf')}
            if new_pdfs:
                latest_file = max(new_pdfs, key=lambda x: os.path.getctime(os.path.join(download_dir, x)))
                return latest_file
            elif time.time() - start_time > timeout:
                raise TimeoutError("No new PDF file appeared within the timeout period.")
            time.sleep(3)  # Check every second


    # The URL you provided
    url = 'https://www.asx.com.au/asx/v2/statistics/announcements.do'

    # company = 'PAM'
    # year = '2023'

    # The directory where you want to download the files
    download_dir = target_dir

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Perform a GET request to the ASX announcements page
    driver.get(f"{url}?by=asxCode&asxCode={company}&timeframe=Y&year={year}")

    # Wait for the user to manually solve the CAPTCHA
    print("Please solve the CAPTCHA...")
    # Wait for the tbody inside the table to become visible
    WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table > tbody")))


    announcements = []

    # After CAPTCHA is solved and the table's body is visible, you can interact with it
    tbody = driver.find_element(By.CSS_SELECTOR, 'table > tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')

    for row in rows:
        # Initialize a dictionary to store the details of this particular announcement
        announcement = {}
        # Extract the date and time from the first <td> tag
        date_str = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(1)").text
        time_str = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(1) > span").text
        announcement['date_str'] = f"{date_str}"
        announcement['time_str'] = f"{time_str}"

        # Extract the headline and PDF link from the link within the third <td> tag
        link = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(3) > a")
        announcement['headline'] = link.text
        announcement['pdf_url'] = link.get_attribute('href')

        # Append the announcement dictionary to the list of all announcements
        announcements.append(announcement)





    def clean_headline(headline):
        # Remove unwanted characters like '\r', '\n', '\t'
        cleaned = ' '.join(headline.split())
        
        # Use regex to remove trailing digits and page information
        cleaned = re.sub(r'(\d+)(\s*pages.*)?$', '', cleaned, flags=re.IGNORECASE).strip()

        return cleaned

    def clean_date(date_str, time_str):
        # Convert date and time into a single datetime object
        dt = datetime.strptime(f"{date_str[:10]} {time_str}", "%d/%m/%Y %I:%M %p")
        # Format it to match the SGX file format
        return dt.strftime("%Y%m%d_%H%M")

    # Assuming `announcements` is your list of dictionaries
    for announcement in announcements:
        announcement['date_time'] = clean_date(announcement['date_str'], announcement['time_str'])
        announcement['headline'] = clean_headline(announcement['headline'])

    # Print first 5 announcements
    for announcement in announcements[:5]:
        print(announcement)



    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
    })

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # To click the "Agree and proceed" button for the first announcement ONLY
    i = 0

    # Iterate over the announcements
    for announcement in announcements:
        previous_files = set(os.listdir(download_dir))

        # Get the date and time of the announcement
        date_time = announcement['date_time']

        # Initialize the WebDriver session
        driver.get(announcement['pdf_url'])
        print('Opening URL: ' + announcement['pdf_url'])

        # Only click the "Agree and proceed" button for the first announcement; skip for the rest
        if i == 0:
            # Click the "Agree and proceed" button if it appears
            try:
                agree_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Agree and proceed']")))
                agree_button.click()
                print("Clicked 'Agree and proceed' for the file.")
            except:
                print("No 'Agree and proceed' button to click, or already clicked for previous files.")

        i += 1

        try:
            # Wait for the download to complete and get the downloaded file

            downloaded_file = wait_for_new_pdf(download_dir, previous_files)

            print(f"Downloaded file: {downloaded_file}")
        except Exception as e:
            print(f"Error waiting for download to complete: {e}")


        # Rename the downloaded file with datetime prepended
        try:
            sanitized_headline = re.sub(r'[\\/*?:"<>|]', "-", announcement['headline'])
            new_file_name = f"{date_time}_{sanitized_headline}.pdf"
            new_file_path = os.path.join(download_dir, new_file_name)
            os.rename(os.path.join(download_dir, downloaded_file), new_file_path)
            print(f"File renamed to: {new_file_path}")
        except Exception as e:
            print(f"Error renaming file: {e}")

    

    # Close the WebDriver session
    driver.quit()
