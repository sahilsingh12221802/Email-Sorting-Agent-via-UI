import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
from dotenv import load_dotenv

load_dotenv()

class EmailSorter:
    def __init__(self):
        self.email = os.getenv('GMAIL_EMAIL')
        self.password = os.getenv('GMAIL_PASSWORD')
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # More specific categories to avoid false positives
        self.categories = {
            'finance': ['statement', 'equity', 'account', 'transaction', 'settlement', 'zerodha'],
            'shopping': ['amazon', 'order', 'delivery', 'shipment', 'receipt'],
            'meeting': ['meeting', 'calendar', 'invite', 'appointment'],
            'urgent': ['urgent', 'important', 'immediate', 'action required']
        }
    
    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
    
    def wait_for_login_success(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Inbox"))
            )
            return True
        except:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="button"][gh="cm"]'))
                )
                return True
            except:
                return False
    
    def handle_verification(self):
        try:
            verify_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                    "//*[contains(text(), 'Verify') or contains(text(), 'Confirm') or contains(text(), 'Security')]"))
            )
            
            print("\n🔐 Manual Verification Required!")
            print("1. Complete verification in browser")
            print("2. Wait until you see your Gmail inbox")
            input("3. Press Enter here AFTER you're logged in...")
            
            return self.wait_for_login_success()
        except:
            return False
    
    def login(self):
        try:
            self.driver.get("https://mail.google.com")
            
            email_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']"))
            )
            self.human_type(email_field, self.email)
            email_field.send_keys(Keys.RETURN)
            
            if self.handle_verification():
                return True
            
            password_field = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
            )
            self.human_type(password_field, self.password)
            password_field.send_keys(Keys.RETURN)
            
            if self.wait_for_login_success():
                return True
                
            if self.handle_verification():
                return True
                
            return False
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def get_email_subject(self, email_element):
        """More robust way to get email subject"""
        try:
            return WebDriverWait(email_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[class="bog"]'))
            ).text.lower()
        except:
            return ""
    
    def process_emails(self):
        print("\n📨 Processing emails...")
        
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'tr[role="row"][class*="zA"]'))
            )
            time.sleep(2)  # Additional stabilization
        except Exception as e:
            print(f"Failed to load emails: {str(e)}")
            self.driver.save_screenshot('email_load_error.png')
            return
        
        # Get fresh references to email elements
        email_elements = self.driver.find_elements(By.CSS_SELECTOR, 'tr[role="row"][class*="zA"]')
        print(f"Found {len(email_elements)} unread emails")
        
        processed = 0
        for i in range(min(20, len(email_elements))):  # Limit to first 20
            try:
                # Refresh elements periodically
                if i > 0 and i % 5 == 0:
                    email_elements = self.driver.find_elements(By.CSS_SELECTOR, 'tr[role="row"][class*="zA"]')
                
                email = email_elements[i]
                subject = self.get_email_subject(email)
                if not subject:
                    continue
                
                labeled = False
                for category, keywords in self.categories.items():
                    if any(keyword in subject for keyword in keywords):
                        print(f"ℹ️ Matching '{category}' for: {subject[:50]}...")
                        if self.label_email(email, subject, category):
                            processed += 1
                            labeled = True
                            break
                
                if not labeled:
                    print(f"⏩ No match: {subject[:50]}...")
                    
            except Exception as e:
                print(f"⚠️ Error processing email {i}: {str(e)}")
                continue
        
        print(f"\n✅ Successfully processed {processed} emails")

    def label_email(self, email_element, subject, label):
        """More reliable email labeling with better error handling"""
        try:
            # Scroll to element with smooth behavior
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                email_element
            )
            time.sleep(1)
            
            # Click using ActionChains for better reliability
            ActionChains(self.driver).move_to_element(email_element).pause(0.5).click().perform()
            
            # Wait for email to fully load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="More actions"]'))
            )
            time.sleep(1)
            
            # Click label button
            label_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label^="Label"]'))
            )
            label_btn.click()
            time.sleep(0.5)
            
            # Select label
            label_xpath = f'//div[@role="menuitem"]//div[contains(text(), "{label}")]'
            label_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, label_xpath))
            )
            label_option.click()
            
            print(f"🏷️ Labeled '{subject[:50]}...' as {label}")
            
            # Return to inbox more reliably
            for _ in range(3):
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'a[href="#inbox"]').click()
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'tr[role="row"]'))
                    )
                    break
                except:
                    self.driver.back()
                    time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to label '{subject[:50]}...': {str(e)}")
            self.driver.save_screenshot('label_error.png')
            
            # Try to return to inbox
            try:
                self.driver.find_element(By.CSS_SELECTOR, 'a[href="#inbox"]').click()
            except:
                try:
                    self.driver.back()
                except:
                    pass
            
            return False
    
    def run(self):
        try:
            if self.login():
                for attempt in range(3):
                    try:
                        print(f"\nAttempt {attempt + 1} of 3")
                        self.process_emails()
                        break
                    except Exception as e:
                        print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                        if attempt < 2:
                            print("Retrying after 5 seconds...")
                            time.sleep(5)
                            self.driver.refresh()
            else:
                print("\n❌ Login failed. Solutions:")
                print("1. Use App Password (for 2FA accounts)")
                print("2. Check .env file credentials")
                print("3. Try manual login first in Chrome")
        finally:
            self.driver.quit()
            print("\n🏁 Script completed")

if __name__ == "__main__":
    print("🚀 Starting Email Sorter...")
    sorter = EmailSorter()
    sorter.run()