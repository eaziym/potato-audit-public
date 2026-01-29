# SGX Announcement Fetcher Setup Guide

This guide will help you set up the SGX announcement fetching module on a fresh PC.

## Prerequisites

1. **Python 3.7 or higher**
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - macOS: `brew install python3` or download from python.org
   - Linux: `sudo apt-get install python3 python3-pip`

2. **Google Chrome Browser**
   - Download and install from [google.com/chrome](https://www.google.com/chrome/)

3. **Git** (optional, for cloning the repository)

## Installation Steps

### 1. Create Project Directory

```bash
mkdir sgx-announcements
cd sgx-announcements
```

### 2. Copy Required Files

You need these files from the repository:
- `src/GetSGXAnnouncement_Today.py` - Main fetching script
- `src/emailANN.py` - Email sending functionality
- `requirements.txt` - Python dependencies (or create it manually)

### 3. Install Python Dependencies

Create a `requirements.txt` file with the following content:

```txt
selenium==4.15.2
webdriver-manager==4.0.1
openpyxl==3.1.2
```

Then install:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install selenium webdriver-manager openpyxl
```

### 4. Create Company List File

Create a CSV file named `companies.csv` with your target companies:

```csv
company
DBS Group Holdings Ltd
United Overseas Bank Ltd
Oversea-Chinese Banking Corp
Singapore Airlines Ltd
```

### 5. Configure Email Settings (Optional)

If you want to send emails, edit `emailANN.py`:

```python
sender_email = "your-email@company.com"  # Your email
sender_password = "your-app-password"     # Your email app password
recipients = ["recipient1@company.com", "recipient2@company.com"]
```

**Important:** Use app-specific passwords, not your actual email password!
- Outlook/Office365: [Create app password](https://support.microsoft.com/en-us/account-billing/manage-app-passwords-for-two-step-verification-d6dc8c6d-4bf7-4851-ad95-6d07799387e9)
- Gmail: [Create app password](https://support.google.com/accounts/answer/185833)

### 6. Create Main Script

Create a file named `fetch_and_email.py`:

```python
import csv
from GetSGXAnnouncement_Today import fetch_announcements_for_companies
from emailANN import emailANN

# Read companies from file
companies = []
with open('companies.csv', 'r') as f:
    reader = csv.DictReader(f)
    companies = [row['company'] for row in reader]

# Fetch announcements
print("Fetching announcements...")
announcements = fetch_announcements_for_companies(companies)

# Save to CSV
output_file = 'announcements_output.csv'
with open(output_file, 'w', newline='') as f:
    if announcements:
        writer = csv.DictWriter(f, fieldnames=['date', 'company', 'title', 'link'])
        writer.writeheader()
        writer.writerows(announcements)
        print(f"Saved {len(announcements)} announcements to {output_file}")
    else:
        print("No announcements found")

# Send email (optional)
if announcements:
    print("Sending email...")
    emailANN(output_file)
    print("Email sent!")
```

## Running the Script

### Basic Usage (Fetch Only)

```bash
python fetch_and_email.py
```

### Without Email (Comment out email section)

Edit `fetch_and_email.py` and comment out the email section:

```python
# Send email (optional)
# if announcements:
#     print("Sending email...")
#     emailANN(output_file)
#     print("Email sent!")
```

## Scheduling Automated Runs

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\fetch_and_email.py`
   - Start in: `C:\path\to\sgx-announcements`

### macOS/Linux (Cron)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/sgx-announcements && python3 fetch_and_email.py >> logs.txt 2>&1
```

For Monday 9 AM only (to fetch Friday's announcements):
```bash
0 9 * * 1 cd /path/to/sgx-announcements && python3 fetch_and_email.py >> logs.txt 2>&1
```

## Troubleshooting

### ChromeDriver Issues

**Error: "Can not connect to the Service"**

The script should handle this automatically, but if issues persist:

**macOS:**
```bash
# Remove quarantine attribute
xattr -cr ~/.wdm/drivers/chromedriver/
```

**Windows:**
- Make sure Chrome browser is installed
- Run as Administrator if permission issues occur

**Linux:**
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### Email Issues

- Verify sender email and app password
- Check SMTP server settings (default: Office365)
- For Gmail, change SMTP to: `smtp.gmail.com` (port 587)

### No Announcements Found

- Verify company names match exactly with SGX website
- Check if running on a weekend (script fetches previous working day)
- Verify SGX website is accessible

## Output

The script creates:
- `announcements_output.csv` - CSV file with all announcements
- Console output showing progress and results

## Working Day Logic

The script automatically fetches from the **previous working day**:
- **Monday**: Fetches Friday's announcements
- **Tuesday-Friday**: Fetches previous day's announcements
- **Weekend**: Fetches Friday's announcements

## Project Structure

```
sgx-announcements/
├── GetSGXAnnouncement_Today.py  # Main fetcher
├── emailANN.py                   # Email sender
├── fetch_and_email.py            # Main script
├── companies.csv                 # Company list
├── announcements_output.csv      # Output file
└── requirements.txt              # Dependencies
```

## Support

For issues or questions:
1. Check Chrome browser is updated
2. Verify Python version: `python --version`
3. Reinstall dependencies: `pip install --upgrade -r requirements.txt`
4. Check SGX website structure hasn't changed
