# Email Sorting Agent

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automated Gmail inbox organizer that categorizes emails using Selenium WebDriver. Perfect for managing financial statements (Zerodha), shopping receipts, meeting invites, and urgent communications.

## Features

- ✅ Automatic labeling of unread emails
- 🔍 Smart keyword-based categorization
- 🔄 Stale element recovery system
- 📧 Supports Gmail's modern interface
- 📁 Multiple category configurations
- 📸 Automatic error screenshots for debugging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/email-sorting-agent.git
cd email-sorting-agent
```
2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```
3. Install dependencies:
```bash
selenium==4.13.0
python-dotenv==1.0.0
webdriver-manager==4.0.1
```
4. Create .env file:
```bash
GMAIL_EMAIL=your@gmail.com
GMAIL_PASSWORD=yourpassword
```

## Usage
Run the script:

```bash
python main.py
```

**The script will:**

- Open Chrome browser and log into Gmail

- Scan unread emails

- Apply labels based on content

- Provide detailed console logs

