import os
import pandas as pd
import fitz  # PyMuPDF
from datetime import datetime

def process_pdfs_and_generate_excel(download_dir):
    # Assuming all PDFs in the directory should be processed
    pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
    
    df = pd.DataFrame()  # Initialize the DataFrame

    def truncate_to_excel_limit(text, percentage=0.8):
        max_excel_chars = 32767
        limit = int(max_excel_chars * percentage)
        return text[:limit] if len(text) > limit else text


    for i, pdf_file in enumerate(sorted(pdf_files), start=1):
        pdf_path = os.path.join(download_dir, pdf_file)
        # Extract text from PDF
        text = ""
        with fitz.open(pdf_path) as pdf:
            try:
                # Extract text from all pages for text documents
                for page in pdf:
                    text += page.get_text()
                # Truncate the text to fit into Excel's character limit if necessary
                text = truncate_to_excel_limit(text)
                
            # If the PDF is an image or slides, skip it and fill the text with the file name except the date and time
            except RuntimeError:
                print(f"Skipping {pdf_file} as it is not a text-based PDF")
                text = pdf_file.split('_', 2)[2].replace('.pdf', '')
                continue  # Skip the rest of the code in the loop and continue with the next PDF
            except Exception as e:
                print(f"Error extracting text from {pdf_file}: {e}")
                continue
        

        
        # Extract datetime from filename
        datetime_split = pdf_file.split('_', 2)[0:2]
        datetime_str = '_'.join(datetime_split)
        # Convert the sortable datetime string back to the original format if necessary
        date_time_obj = datetime.strptime(datetime_str, "%Y%m%d_%H%M")
        readable_date_str = date_time_obj.strftime("%d %b %Y %I:%M %p")

        # Update DataFrame creation to include the actual datetime
        file_info = pd.DataFrame({
            'Date': [readable_date_str],  # Use the converted datetime
            'Ref': [f'E513-{i}'],  # Adjust if necessary
            'Category': [pdf_file.split('_', 2)[2].replace('.pdf', '')],  # Adjusted to extract category correctly
            'Details': [text],
            'FS Impact/AWP': ['']
        })

        df = pd.concat([df, file_info], ignore_index=True)
    
    # Define the Excel file path
    excel_path = os.path.join(download_dir, 'Extracted_Announcements.xlsx')
    # Save the DataFrame to an Excel file
    df.to_excel(excel_path, index=False)
    
    return excel_path
