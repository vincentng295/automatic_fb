from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
import json
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import re
import urllib
import time
import os
import sys
from fb_getcookies import get_fb_cookies, check_cookies_
from fbparser import get_facebook_id
from pickle_utils import *
from github_utils import get_file, upload_file
from cryptography.fernet import Fernet

sys.stdout.reconfigure(encoding='utf-8')

tds_token = os.getenv("TDS_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Pass GitHub Token
GITHUB_REPO = os.getenv("GITHUB_REPO")   # Pass the repository (owner/repo)
STORAGE_BRANCE = os.getenv("STORAGE_BRANCE")
PASSWORD = os.getenv("PASSWORD")
encrypt_key = generate_fernet_key(PASSWORD)
filename="traodoisub_fbconfig.json"

if tds_token == None or tds_token == "":
    raise Exception("TDS_TOKEN is not setup")


login_list = []

driver_list = {}

def quit_nocare(driver):
    try:
        driver.quit()
    except Exception:
        pass

def wait_for_load(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    
def convert_facebook_url(url):
    """
    Converts a Facebook post URL of the format facebook.com/*/posts/* to the embed URL format.

    Args:
        url (str): The original Facebook URL.

    Returns:
        str: The converted embed URL if the input matches, otherwise the original URL.
    """
    # Check if the URL matches the format facebook.com/*/posts/*
    if (("facebook.com" in url and "/posts/" in url) or "facebook.com/permalink.php" in url) and ("&comment_id=" not in url and "?comment_id=" not in url):
        try:

            # Construct the new embed URL
            embed_base = "https://www.facebook.com/plugins/post.php"
            encoded_href = urllib.parse.quote(url)

            embed_url = f"{embed_base}?href={encoded_href}&show_text=true&width=500"
            return embed_url
        except Exception as e:
            print(f"Error converting URL: {e}")
            return url
    else:
        # Return the original URL if it doesn't match the required pattern
        return url

def switch_to_mobile_view(driver):
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36"
    })

def switch_to_desktop_view(driver):
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    })

# Get the path to the event payload file
event_path = os.getenv('GITHUB_EVENT_PATH', "")
login_list_env = ""
loop_count = 999
sec_delay = 100
if event_path != "":
    # Read the event data from the file
    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            # Extract the inputs from the event payload
            # Example for workflow_dispatch input
            inputs_data = event_data.get('inputs', {})
            login_list_env = inputs_data.get("json", "")
            loop_count = int(inputs_data.get("count", "999"))
            sec_delay = int(inputs_data.get("delay", "100"))
    except Exception:
        pass

if login_list_env != "":
    with open(filename, "w") as f:
        f.write(login_list_env)
else:
    try:
        if STORAGE_BRANCE is not None and STORAGE_BRANCE != "":
            # Download the encrypted file
            print(f"Đang khôi phục thông tin đăng nhập từ branch: {STORAGE_BRANCE}")
            get_file(GITHUB_TOKEN, GITHUB_REPO, filename + ".enc", STORAGE_BRANCE, filename + ".enc")
            print("Đang giải mã tập tin...")
            decrypt_file(filename + ".enc", filename, encrypt_key)
            print("Đã giải mã file thành công!")
    except Exception as e:
        print(e)

try:
    # Set Chrome options
    chrome_options = Options()
    prefs = {
        "profile.default_content_setting_values.notifications": 1  # 1 allows notifications, 2 blocks
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")  # Enable advanced headless mode
    chrome_options.add_argument("--disable-gpu")   # Disable GPU acceleration for compatibility
    chrome_options.add_argument(f"window-size={1920*2},{1080*2}")  # Set custom window size
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox') 
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--force-device-scale-factor=0.5")
    
    try:
        f = open(filename, "r")
    except FileNotFoundError:
        raise Exception(f"{filename} file not found")
    else:
        print(f"Đang tải dữ liệu từ file: {filename}")
        login_list = json.load(f)
        login_list_tmp = []

        print("Kiểm tra tài khoản Facebook")
        for info in login_list:
            username = info["username"]
            password = info["password"]
            otp_secret = info["otp_sec"]
            alt_account = info["alt"]
            print(f"Đăng nhập username={username} password=*** otp_secret=*** alt={alt_account}")
            cookies = check_cookies_(info.get("cookies"))
            if cookies == None:
                cookies = get_fb_cookies(username, password, otp_secret, int(alt_account))
            if cookies == None:
                continue
            
            info['cookies'] = cookies
        time.sleep(10)
        print("Thiết lập chạy auto Facebook")
        for info in login_list:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://www.facebook.com")
            if type(info.get('cookies')) == list:
                for cookie in info['cookies']:
                    driver.add_cookie(cookie)
            print("Khôi phục cookies:", info['username'], info.get("alt","0"))
            driver.get("https://www.facebook.com/profile.php")
            wait_for_load(driver)
            if driver.current_url.startswith("https://www.facebook.com/checkpoint/"):
                print(f"Acc đã bị die, dính checkpoint")
                quit_nocare(driver)
                continue
            try:
                info['fb_id'] = get_facebook_id(driver.current_url)
                print(f"[{driver.current_url}] ID là {info['fb_id']}")
            except Exception as e:
                print(e)
                quit_nocare(driver)
                continue
            driver_list[info['fb_id']] = driver
            login_list_tmp.append(info)
        f = open(filename, "w")
        login_list = login_list_tmp
        login_list_tmp = None
        json.dump(login_list, f, indent=4)
        f.close() 
    
    print("Tất cả đã tải thành công")
    
    try:
        if STORAGE_BRANCE is not None and STORAGE_BRANCE != "":
            print("Đang mã hóa tập tin trước khi tải lên...")
            encrypt_file(filename, filename + ".enc", encrypt_key)
            print("Mã hóa thành công!")
            # Upload the file onto repo
            upload_file(GITHUB_TOKEN, GITHUB_REPO, filename + ".enc", STORAGE_BRANCE)
            print(f"Đã tải tệp lên branch: {STORAGE_BRANCE}")
    except Exception as e:
        print(e)

    def do_fb_job(driver, fields, s_delay, jtype="LIKE"):
    
        button_selector = {
            "facebook_follow" : [
                {
                    "by" : By.CSS_SELECTOR, 
                    "selector" : "div[aria-label='Theo dõi']"
                }
            ],
            
            "facebook_page" : [
                {
                    "by" : By.CSS_SELECTOR, 
                    "selector" : "div[aria-label='Thích']"
                }
            ],
            
            "facebook_reaction" : [
                {
                    "by" : By.CSS_SELECTOR, 
                    "selector" : 'div[aria-label$="like, double tap and hold for more reactions"]'
                },
                
                {
                    "by" : By.CSS_SELECTOR, 
                    "selector" : "div[aria-label='Thích']"
                }
            ],
            
            "facebook_reactioncmt" : [
                {
                    "by" : By.CSS_SELECTOR, 
                    "selector" : "div[aria-label^='Thích']"
                },
                
                {
                    "by" : By.CSS_SELECTOR, 
                    "selector" : 'div[class="xi81zsa x1ypdohk x1rg5ohu x117nqv4 x1n2onr6 xt0b8zv"]'
                }
            ],
            
            "facebook_share" : [
                {
                    "by" : By.CSS_SELECTOR,
                    "selector" : 'div[class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k x150jy0e x1e558r4 xjkvuk6 x1iorvi4"]'
                },
                
                {
                    "by" : By.XPATH, 
                    "selector" : '//span[contains(text(), "Chia sẻ")]'
                }
            ]
        }
        
        button = None
        
        is_really_reaction_comment = False
    
    
        # https://traodoisub.com/api/?fields={{fields}}&access_token={{TDS_token}}&type={{type}}
        url = "https://traodoisub.com/api/?fields=" + fields + "&access_token=" + tds_token
        
        if fields == "facebook_reaction" or fields == "facebook_reactioncmt":
            url += "&type=" + jtype
        
        #print(url)
        
        # Send an HTTP GET request to the URL
        print(f"Đang lấy danh sách nhiệm vụ cho {fields}...")
        response = requests.get(url)
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Parse the JSON content
        json_data = response.json()
        
        # Check if the response contains an "error" field
        if "error" in json_data:
            print(f"Lỗi: {json_data['error']}")
            if "countdown" in json_data:
                print(f"Thử lại sau: {json_data['countdown']} seconds")
                return json_data['countdown']
            return 10
        else:
            # Access and process the 'data' field
            data_list = json_data.get("data", [])
            print(data_list)
            for item in data_list:
                print(f"ID: {item.get('id')}, Code: {item.get('code')}, Type: {item.get('type')}")
                job_url = "https://www.facebook.com/" + item.get('id')
                coin_url = "https://traodoisub.com/api/coin/?type=" + fields + "&id=" + item.get('code') + "&access_token=" + tds_token
                
                if fields == "facebook_share":
                    job_url = "https://www.facebook.com/sharer/sharer.php?u=" + job_url
                try:
                    switch_to_desktop_view(driver)
                    print(f"Truy cập [{job_url}]")
                    driver.get(job_url)
                    wait_for_load(driver)
                    new_job_url = convert_facebook_url(driver.current_url)
                    is_really_reaction_comment = (fields == "facebook_reactioncmt" and ("&comment_id=" in driver.current_url or "?comment_id=" in driver.current_url))
                    if (driver.current_url != new_job_url):
                        switch_to_mobile_view(driver)
                        driver.refresh()
                        wait_for_load(driver)
                        time.sleep(3)
                    
                    button_selector_to_find = button_selector[fields]
                    if fields == "facebook_reactioncmt" and is_really_reaction_comment == False:
                        button_selector_to_find = button_selector["facebook_reaction"]
                    
                    for it in button_selector_to_find:
                        try:
                            print(f"Tìm nút: ({it['by']}, {it['selector']})...")
                            button = driver.find_element(it['by'], it['selector'])
                            break
                        except NoSuchElementException:
                            button = None
                        
                    if button == None and fields == "facebook_follow": 
                        try:
                            print(f"Tìm nút: ({By.XPATH}, //span[contains(text(), 'Theo dõi')])...")
                            button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Xem lựa chọn']")
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            button = driver.find_element(By.XPATH, '//span[contains(text(), "Theo dõi")]')

                        except NoSuchElementException:
                            button = None
                        
                    
                    if button == None:
                        print("Không thể tìm nút để nhấn")
                        time.sleep(10)
                        continue
                    
                    print("Tiến hành nhấn vào nút")
                    driver.execute_script("arguments[0].click();", button)

                    time.sleep(2)
                    switch_to_desktop_view(driver)
                    
                    
                    if fields == "facebook_follow" or fields == "facebook_page":
                        cache_url = "https://traodoisub.com/api/coin/?type=" + fields + "_cache&id=" + item.get('code') + "&access_token=" + tds_token # dành cho facebook_follow and facebook_page
                        #print(f"Gửi yêu cầu [{cache_url}]")
 
                        # Send an HTTP GET request to the URL
                        cache_res = requests.get(cache_url)
                        
                        # Raise an exception if the request was unsuccessful
                        cache_res.raise_for_status()
                        
                        # Parse the JSON content
                        res_json_data = cache_res.json()
                        print(res_json_data)
                        
                    
                    # Send an HTTP GET request to the URL
                    #print(f"Gửi yêu cầu [{coin_url}]")
                    coin_res = requests.get(coin_url)
                        
                    # Parse the JSON content
                    res_json_data = coin_res.json()
                    print(res_json_data)
                    
                except NoSuchWindowException:
                    break   
                except Exception as e:
                    print(f"Lỗi xảy ra: {e}, bỏ nhiệm vụ này")
                    continue

                print(f"Trì hoãn {s_delay} giây...")
                time.sleep(s_delay)   
        
        return 0
    
    for _n in range(loop_count):
        for fb_id, driver in driver_list.items():
            try:
                print("Chuyển sang:", fb_id)
                
                # https://traodoisub.com/api/?fields=run&id={{idfb}}&access_token={{TDS_token}}
                setup_url = "https://traodoisub.com/api/?fields=run&id=" + fb_id + "&access_token=" + tds_token
                
                # Send an HTTP GET request to the URL
                res = requests.get(setup_url)
                
                # Raise an exception if the request was unsuccessful
                res.raise_for_status()
                
                # Parse the JSON content
                json_data = res.json()
                print(json_data)
                
                if "success" in json_data and json_data['success'] == 200: 
                    #time.sleep(do_fb_job(driver, "facebook_share", sec_delay))
                    #time.sleep(do_fb_job(driver, "facebook_reactioncmt", sec_delay))
                    time.sleep(do_fb_job(driver, "facebook_page", sec_delay))
                    time.sleep(do_fb_job(driver, "facebook_follow", sec_delay))
                    #time.sleep(do_fb_job(driver, "facebook_reaction", sec_delay))
            except Exception as e:
                print(f"Lỗi xảy ra: {e}")
        

finally:
    for fb_id, driver in driver_list.items():
        print(f"Đang đóng {fb_id}")
        quit_nocare(driver)
