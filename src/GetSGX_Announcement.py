def fetch_SGX_announcements(company, year, target_dir):

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import NoSuchElementException  # Ensure this is imported
    import time
    import os
    import pdfkit
    import re
    from datetime import datetime

    # Path to the wkhtmltopdf executable
    wkhtmltopdf_PATH = r'/usr/local/bin/wkhtmltopdf'

    # Function to wait for the download to complete and return the path of the downloaded file
    def wait_for_download_complete(download_dir, timeout=60):
        start_time = time.time()
        initial_files = set(os.listdir(download_dir))
        while True:
            time.sleep(5)  # Short delay to allow file to appear
            current_files = set(os.listdir(download_dir))
            new_files = current_files - initial_files
            if new_files:
                return os.path.join(download_dir, new_files.pop())  # Return the new file path
            if time.time() - start_time > timeout:
                raise Exception("Download timed out")

    # Function to rename the downloaded file with datetime prepended
    def rename_downloaded_file(filepath, date_time):
        directory, filename = os.path.split(filepath)
        # Convert date_time to a safe format for filenames
        safe_date_time = datetime.strptime(date_time, "%d %b %Y %I:%M %p").strftime("%Y%m%d_%H%M")
        new_filename = f"{safe_date_time}_{filename}"
        new_filepath = os.path.join(directory, new_filename)
        os.rename(filepath, new_filepath)
        return new_filepath

    # The URL for announcements
    sgx_url = f'https://www.sgx.com/securities/company-announcements?value={company}&type=company&from={str(year)}0101&page=1&pagesize=50'

    # The directory where you want to download the files
    download_dir = target_dir

    # Initialize the WebDriver session with download directory preferences
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'plugins.always_open_pdf_externally': True,
    })


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the SGX announcements page for OEL (HOLDINGS) LIMITED
    driver.get(sgx_url)

    # Wait for 5 seconds
    time.sleep(5)

    detail_page_urls = []

    # Wait for the user to manually solve the CAPTCHA
    print("Please solve the CAPTCHA...")
    # Wait for the tbody inside the table to become visible
    WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.website-content-table tbody tr")))


    rows = driver.find_elements(By.CSS_SELECTOR, "table.website-content-table tbody tr")

    # Loop over the rows to find the links
    for row in rows:
        try:
            # Within each row, select the fourth <td> element to get the link
            link = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(4) a")
            url = link.get_attribute('href')
            detail_page_urls.append(url)
            print('Retrieving: ' + url)  # Print the href attribute of the link
        except Exception as e:
            print("An error occurred while trying to find the link:", e)





    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_PATH)


    # # Function to parse and format date and time from the table
    # def format_datetime_from_table(date_time_str):
    #     # Assuming the format in the table is like "18 Jan 2024 06:44 PM"
    #     dt = datetime.datetime.strptime(date_time_str, "%d %b %Y %I:%M %p")
    #     return dt.strftime("%Y%m%d-%H%M")

    # Function to sanitize filenames
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', "-", filename)

    # Find the table rows
    table_rows = driver.find_elements(By.CSS_SELECTOR, "table.website-content-table tbody tr")
    announcement_details = []

    # Extract date and time from each row and the URL of the announcement
    for row in table_rows:
        date_time = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(1)").text
        detail_url = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(4) a").get_attribute('href')
        announcement_details.append((date_time, detail_url))


    # For each detail page URL retrieved (assuming detail_page_urls is a list of URLs)
    for date_time, detail_url in announcement_details:
        # Navigate to the detail page
        driver.get(detail_url)
        
        # Try to find a PDF link in the attachments section
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".announcement-attachment-list"))
            )
            # # Find all the download links within the attachments section
            # download_links = driver.find_elements(By.CSS_SELECTOR, ".announcement-attachment-list a")
        
            # Find the attachment list element
            attachment_list = driver.find_elements(By.CSS_SELECTOR, ".announcement-attachment-list")

            # Check if there are any <a> tags (attachments) inside the list
            download_links = attachment_list[0].find_elements(By.TAG_NAME, "a") if attachment_list else []

            if download_links:
                for link in download_links:
                    href = link.get_attribute('href')
                    if href:
                        # This might be a relative URL; if so, you need to concatenate with base URL
                        driver.get(href)  # Navigate to each href to trigger the download
                        print('Downloading: ' + href)  # or process the href as needed
                        # Wait for the download to complete and get the downloaded file path
                        downloaded_file_path = wait_for_download_complete(download_dir)
                        # Rename the downloaded file with datetime prepended
                        new_file_path = rename_downloaded_file(downloaded_file_path, date_time)
                        print(f"File downloaded and renamed to: {new_file_path}")
                        time.sleep(5)  # Wait for the download to start

            else:
                # If no links are found, throw a NoSuchElementException
                raise NoSuchElementException("No download links found in the attachments section.")
        except NoSuchElementException:
            # Get the title of the announcement from the page
            # Extract the title for the PDF filename
            print('No PDF found. Downloading Webpage...')
            page_title = driver.title 
            print('Original Title: ' + page_title)
            sanitized_title = sanitize_filename(page_title)
            print('Sanitized Title: ' + sanitized_title)
            safe_date_time = datetime.strptime(date_time, "%d %b %Y %I:%M %p").strftime("%Y%m%d_%H%M")

            # Define the output filename with the page title
            output_filename = os.path.join(download_dir, f"{safe_date_time}_{sanitized_title}.pdf")
            # filename = f"{safe_date_time}_{sanitized_title}.pdf"
            
            pdfkit.from_url(detail_url, output_filename, configuration=config)

            # import subprocess
            # # Change to the desired directory
            # os.chdir(download_dir)
            # command = [wkhtmltopdf_PATH, detail_url, filename]  # No extra quotes needed here
            # try:
            #     subprocess.run(command, check=True)
            # except subprocess.CalledProcessError as e:
            #     print(f"Command execution failed: {e}")

            print('Downloading: ' + output_filename)
            time.sleep(5)  # Wait for the print-to-PDF to complete
        except Exception as e:
            print(f"An error occurred: {e}")

    # Close the driver
    driver.quit()

