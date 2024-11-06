from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import pandas as pd
import fitz  # PyMuPDF
import re
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException  # Ensure this is imported
import pdfkit



wkhtmltopdf_PATH = r'C:\Users\jason\OneDrive\Desktop\NUS Y3S2\wkhtmltopdf\wkhtmltopdf\bin\wkhtmltopdf.exe'

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "-", filename)

# Function to wait for the download to complete and return the path of the downloaded file
def wait_for_download_complete(download_dir, timeout=60):
    start_time = time.time()
    initial_files = set(os.listdir(download_dir))
    while True:
        time.sleep(3)  # Short delay to allow file to appear
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

def fetch_and_process_annual_reports(download_dir):
    # Initialize WebDriver
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_dir,
             "download.prompt_for_download": False,
             "plugins.always_open_pdf_externally": True}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Navigate to the SGX announcements page
    sgx_url = 'https://www.sgx.com/securities/company-announcements?ANNC=ANNC30&page=1&pagesize=100'
    driver.get(sgx_url)
    time.sleep(5)  # Wait for the page to load

    # Wait for the user to manually solve the CAPTCHA
    print("Please solve the CAPTCHA...")
    # Wait for the tbody inside the table to become visible
    WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.website-content-table tbody tr")))



    
    # Find the table rows
    table_rows = driver.find_elements(By.CSS_SELECTOR, "table.website-content-table tbody tr")
    announcement_details = []

    # Extract date and time from each row and the URL of the announcement
    for row in table_rows:
        date_time = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(1)").text
        detail_url = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(4) a").get_attribute('href')
        announcement_details.append((date_time, detail_url))


    downloaded_pdfs = []  # Initialize the list to keep track of downloaded PDF paths

    # Download the first 3 PDFs (for demonstration purposes)
    announcement_details = announcement_details[:3]
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

                        downloaded_pdfs.append(new_file_path)  # Add the new file path to the list

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
            
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_PATH)

            pdfkit.from_url(detail_url, output_filename, configuration=config)

            print('Downloading: ' + output_filename)
            time.sleep(5)  # Wait for the print-to-PDF to complete
        except Exception as e:
            print(f"An error occurred: {e}")

    # Close the driver
    driver.quit()

    """Processes downloaded PDFs to extract 'Key Audit Matters' from all pages that contain the phrase."""
    key_audit_matters_records = []

    # Iterate through all PDF files in the download directory
    for filename in os.listdir(download_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(download_dir, filename)
            try:
                doc = fitz.open(pdf_path)
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text("text")
                    if "key audit matters" in text.lower():
                        key_audit_matters_records.append({
                            "PDF Name": filename,
                            "Page Number": page_num,
                            "Key Audit Matters": text,
                            "File Link": f'=HYPERLINK(".\\{filename}")'  # Excel hyperlink formula
                        })
            except Exception as e:
                print(f"Error processing {filename}: {e}")


    # Write results to an Excel file
    df = pd.DataFrame(key_audit_matters_records)
    output_path = os.path.join(download_dir, "Key_Audit_Matters.xlsx")
    df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"Processed {len(key_audit_matters_records)} 'Key Audit Matters' entries into {output_path}")
