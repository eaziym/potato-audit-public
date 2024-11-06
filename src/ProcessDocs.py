import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from pytesseract import Output
from PIL import Image
from pdf2image import convert_from_path
import os


TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
POPPLER_PATH = r'C:\Users\jason\OneDrive\Desktop\NUS Y3S2\Release-24.02.0-0\poppler-24.02.0\Library\bin'
DPI = 250

def process_docs_and_generate_excel(upload_dir, download_dir):
    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
    image_files = [f for f in os.listdir(upload_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    df = pd.DataFrame()  # Initialize the DataFrame

    def truncate_to_excel_limit(text, percentage=0.8):
        max_excel_chars = 32767
        limit = int(max_excel_chars * percentage)
        return text[:limit] if len(text) > limit else text

    for i, pdf_file in enumerate(sorted(pdf_files), start=1):
        pdf_path = os.path.join(upload_dir, pdf_file)
        text = ""
        
        # Open the PDF file with PyMuPDF
        with fitz.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf):
                # Try to extract text
                page_text = page.get_text()
                if page_text.strip():  # If there's text on the page
                    text += page_text
                else:  # If no text is found, it's likely an image-based PDF
                    # Convert the PDF page to an image
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    # Use pytesseract to do OCR on the image
                    page_text = pytesseract.image_to_string(img, lang='eng', output_type=Output.STRING)
                    text += page_text

                # Truncate the text to fit into Excel's character limit if necessary
                text = truncate_to_excel_limit(text)

        # Create a DataFrame for the extracted text
        file_info = pd.DataFrame({'Details': [text]})
        df = pd.concat([df, file_info], ignore_index=True)

    for i, image_file in enumerate(sorted(image_files), start=i+1):
        image_path = os.path.join(upload_dir, image_file)
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='eng', output_type=Output.STRING)
        
        # Truncate the text to fit into Excel's character limit if necessary
        text = truncate_to_excel_limit(text)
        
        # Create a DataFrame for the extracted text
        file_info = pd.DataFrame({'Details': [text]})
        df = pd.concat([df, file_info], ignore_index=True)
    
    # Save the DataFrame to an Excel file
    excel_path = os.path.join(download_dir, 'Extracted_Texts.xlsx')
    df.to_excel(excel_path, index=False)
    
    return excel_path