# potato-audit
 Auto-fetch announcements and semi-auto invoice data extraction!

How to Set up?
1. pip install -r requirements.txt
2. Download Node.js binaries at https://nodejs.org/en/download/prebuilt-binaries/current
3. Extract the file and create a new folder with whatever name we want.
4. Copy and paste node.exe, npm.cmd, and node_modules into the folder in step 3.
5. Go to Envrionment Variables and add new PATH that points to the directory of the fold in step 3.
6. Download poppler at https://github.com/oschwartz10612/poppler-windows/releases/
7. Extract the file and go to Library\bin
8. Copy and paste the path 'C:\Users\YOU\Release-24.02.0-0\poppler-24.02.0\Library\bin' to process_invoice_file.py
9. Download Tesseract installer at https://github.com/UB-Mannheim/tesseract/wiki 
10. Follow the wizard for installation and then copy the path
	'C:\Users\YOU\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    to process_invoice_file.py
11. Download and install wkhtmltopdf at https://wkhtmltopdf.org/downloads.html
12. Copy and paste the path pointing to 'C:\Users\YOU\wkhtmltopdf\bin\wkhtmltopdf.exe' to GetSGX_Announcement.py
13. May need to install chrome webdriver at https://googlechromelabs.github.io/chrome-for-testing/#stable
14. Go to Powershell and cd to potato-audit directory and run 
	npm start
15. Go app.py and run it to enable Flask
16. Enjoy!
