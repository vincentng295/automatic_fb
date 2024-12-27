from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import random
from urllib.parse import urlparse

cwd = os.getcwd()

import pyotp
def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

def __chrome_driver__(scoped_dir = None):
    # Set Chrome options
    chrome_options = Options()
    prefs = {
        "profile.default_content_setting_values.popups": 2,  # Block popups
        "profile.default_content_setting_values.notifications": 1  # 1 allows notifications, 2 blocks
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")  # Enable advanced headless mode
    chrome_options.add_argument("--disable-gpu")   # Disable GPU acceleration for compatibility
    chrome_options.add_argument("window-size=1920,1080")  # Set custom window size
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox') 
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--lang=en')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("disable-infobars")
    if scoped_dir != None and scoped_dir != "":
        chrome_options.add_argument(f"--user-data-dir={scoped_dir}")
    return webdriver.Chrome(options=chrome_options)


def check_cookies_(cookies):
    if cookies == None:
        return None
    try:
        scoped_dir = os.getenv("SCPDIR")
        driver = __chrome_driver__(scoped_dir)

        driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})
        driver.get("https://www.facebook.com")
        driver.delete_all_cookies()
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Đã khôi phục cookies")
        driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": False})
        
        driver.get("https://facebook.com/profile.php")
        
        wait = WebDriverWait(driver, 20)

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        parsed_url = urlparse(driver.current_url)
        base_url_with_path = parsed_url.netloc + parsed_url.path.rstrip("/")
        if base_url_with_path == "www.facebook.com" or base_url_with_path == "www.facebook.com/login":
            driver.delete_all_cookies()
            return None
        cookies = driver.get_cookies()
        print("Đăng nhập thành công:", driver.current_url)
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()
    return cookies


def check_cookies(filename=None):
    try:
        cookies = None
        if filename:
            with open(filename, "r") as f:
                cookies = json.load(f)
        return check_cookies_(cookies)
    except Exception as e:
        print(f"Error loading cookies from file: {e}")
        return None

def get_fb_cookies(username, password, otp_secret = None, alt_account = 0, finally_stop = False):
    cookies = None
    try:
        scoped_dir = os.getenv("SCPDIR")
        driver = __chrome_driver__(scoped_dir)

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        actions = ActionChains(driver)
        
        wait = WebDriverWait(driver, 20)
        
        def find_element_when_clickable(by, selector):
            return wait.until(EC.element_to_be_clickable((by, selector)))
        
        def find_element_when_clickable_in_list(elemlist):
            for btn_select in elemlist:
                try:
                    return find_element_when_clickable(btn_select[0], btn_select[1])
                    break
                except Exception:
                    continue
            return None

        driver.get("https://www.facebook.com/login")
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(0.5)

        email_input = find_element_when_clickable(By.NAME, "email")
        password_input = find_element_when_clickable(By.NAME, "pass")
        actions.move_to_element(email_input).click().perform()
        time.sleep(random.randint(3,6))
        actions.move_to_element(email_input).send_keys(username).perform()
        actions.move_to_element(password_input).click().perform()
        time.sleep(random.randint(3,6))
        actions.move_to_element(password_input).send_keys(password).perform()
        
        time.sleep(random.randint(3,6))
        button = find_element_when_clickable_in_list([
            (By.CSS_SELECTOR, 'button[id="loginbutton"]'),
            (By.CSS_SELECTOR, 'button[type="submit"]')
        ])
        actions.move_to_element(button).click().perform()
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)
        parsed_url = urlparse(driver.current_url)
        base_url_with_path = parsed_url.netloc + parsed_url.path.rstrip("/")
        
        if base_url_with_path.startswith("www.facebook.com/two_step_verification/"):
            other_veri_btn = find_element_when_clickable_in_list([
                (By.CSS_SELECTOR, 'div[class="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3"]'),
                (By.XPATH, '//span[contains(text(), "Thử cách khác")]'),
                (By.XPATH, '//span[contains(text(), "Try another way")]')
                ])
            actions.move_to_element(other_veri_btn).click().perform() # Click other verification method
            time.sleep(random.randint(5,8))
            other_veri_btn = find_element_when_clickable_in_list([
                (By.XPATH, '//div[contains(text(), "Ứng dụng xác thực")]'),
                (By.XPATH, '//div[contains(text(), "Authentication app")]')
                ])
            actions.move_to_element(other_veri_btn).click().perform() # Click App Auth method
            time.sleep(random.randint(5,8))
            other_veri_btn = find_element_when_clickable_in_list([
                (By.XPATH, '//span[contains(text(), "Tiếp tục")]'),
                (By.XPATH, '//span[contains(text(), "Continue")]')
                ])
            actions.move_to_element(other_veri_btn).click().perform() # Click Continue
            time.sleep(random.randint(5,8))
            other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'input[type="text"]')
            actions.move_to_element(other_veri_btn).click().perform() # Click on input code
            time.sleep(random.randint(5,8))
            actions.move_to_element(other_veri_btn).send_keys(generate_otp(otp_secret)).perform() # Type in code on input
            time.sleep(random.randint(5,8))
            other_veri_btn = find_element_when_clickable_in_list([
                (By.CSS_SELECTOR, 'div[class="x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xtvsq51 xi112ho x17zwfj4 x585lrc x1403ito x1fq8qgq x1ghtduv x1oktzhs"]'),
                (By.XPATH, '//span[contains(text(), "Tiếp tục")]'),
                (By.XPATH, '//span[contains(text(), "Continue")]')
                ])
            actions.move_to_element(other_veri_btn).click().perform() # Click Confirmed

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)
        parsed_url = urlparse(driver.current_url)
        base_url_with_path = parsed_url.netloc + parsed_url.path.rstrip("/")
        
        if base_url_with_path == "www.facebook.com/two_factor/remember_browser":
            button = find_element_when_clickable_in_list([
                (By.CSS_SELECTOR, 'div[class="x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xtvsq51 xi112ho x17zwfj4 x585lrc x1403ito x1fq8qgq x1ghtduv x1oktzhs"]')
            ])
            if button != None:
                actions.move_to_element(button).click().perform()
                time.sleep(5)

        driver.get("https://www.facebook.com/profile.php")

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        if alt_account > 0:
            accounts_btn = find_element_when_clickable(By.CSS_SELECTOR, 'image[style="height:40px;width:40px"]')
            actions.move_to_element(accounts_btn).click().perform() # Click on accounts setting
            time.sleep(1)
            account_list_panel = find_element_when_clickable(By.CSS_SELECTOR, 'div[role="list"][class="html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd"]')
            account_list_btns = account_list_panel.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            if alt_account <= len(account_list_btns):
                actions.move_to_element(account_list_btns[alt_account -1]).click().perform()
                time.sleep(3)

        driver.get("https://www.facebook.com/profile.php")

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)
        parsed_url = urlparse(driver.current_url)
        base_url_with_path = parsed_url.netloc + parsed_url.path.rstrip("/")
        if base_url_with_path == "www.facebook.com" or base_url_with_path == "www.facebook.com/login":
            raise Exception("Lỗi đăng nhập")

        if finally_stop:
            input("Press Enter to extract the cookies")
        cookies = driver.get_cookies()
        print("Đăng nhập thành công:", driver.current_url)
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()
        
    return cookies
