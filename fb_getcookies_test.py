from fb_getcookies import get_fb_cookies, check_cookies, parse_cookies
import os
import sys
import json
import time
from pickle_utils import *
from github_utils import *
from cryptography.fernet import Fernet

sys.stdout.reconfigure(encoding='utf-8')

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Pass GitHub Token
GITHUB_REPO = os.getenv("GITHUB_REPO")   # Pass the repository (owner/repo)
STORAGE_BRANCE = os.getenv("STORAGE_BRANCE")
PASSWORD = os.getenv("PASSWORD")
encrypt_key = generate_fernet_key(PASSWORD)

f_login_info = "logininfo.json"
f_intro_txt = "setup/introduction.txt"
f_rules_txt = "setup/rules.txt"

cookies_text = None

if os.getenv("USE_ENV_SETUP") == "true":

    # Get the path to the event payload file
    event_path = os.getenv('GITHUB_EVENT_PATH')

    # Read the event data from the file
    with open(event_path, 'r') as f:
        event_data = json.load(f)

    # Extract the inputs from the event payload
    # Example for workflow_dispatch input
    login_info = event_data.get('inputs', {})

    cookies_text = login_info.get("cookies_text", None)
    login_info["cookies_text"] = None

    with open(f_login_info, "w") as f:
        json.dump(login_info, f)
else:
    if STORAGE_BRANCE is not None and STORAGE_BRANCE != "":
        try:
            # Download the encrypted file
            print(f"Đang khôi phục thông tin đăng nhập từ branch: {STORAGE_BRANCE}")
            get_file(GITHUB_TOKEN, GITHUB_REPO, f_login_info + ".enc", STORAGE_BRANCE, f_login_info + ".enc")
            print("Đang giải mã tập tin...")
            decrypt_file(f_login_info + ".enc", f_login_info, encrypt_key)
            print("Đã giải mã file thành công!")
        except Exception as e:
            print(e)

    with open(f_login_info, "r") as f:
        login_info = json.load(f)

ai_prompt = login_info.get("ai_prompt", None)
if ai_prompt is not None and ai_prompt != "":
    with open(f_intro_txt, "w", encoding='utf-8') as f: # What kind of person will AI simulate?
        f.write(ai_prompt)

if STORAGE_BRANCE is not None and STORAGE_BRANCE != "":
    for filename in [ f_intro_txt, f_rules_txt ]:
        try:
            get_file(GITHUB_TOKEN, GITHUB_REPO, filename, STORAGE_BRANCE, filename)
        except Exception:
            # Else using default one
            upload_file(GITHUB_TOKEN, GITHUB_REPO, filename, STORAGE_BRANCE, filename)

username = login_info["username"]
password = login_info["password"]
otp_secret = login_info.get("otp_secret", "")
alt_account = login_info.get("alt_account", "0")

if alt_account == None or alt_account == "":
    alt_account = 0
else:
    alt_account = int(alt_account)

filename = "cookies.json"
try:
    if cookies_text is not None:
        with open(filename, "w") as cookies_file:
            json.dump(parse_cookies(cookies_text), cookies_file)
    elif STORAGE_BRANCE is not None and STORAGE_BRANCE != "":
        # Download the encrypted file
        print(f"Đang khôi phục cookies từ branch: {STORAGE_BRANCE}")
        get_file(GITHUB_TOKEN, GITHUB_REPO, filename + ".enc", STORAGE_BRANCE, filename + ".enc")
        print("Đang giải mã tập tin...")
        decrypt_file(filename + ".enc", filename, encrypt_key)
        print("Đã giải mã file thành công!")
except Exception as e:
    print(e)

cookies = check_cookies(filename)

for i in range(5):
    if cookies == None:
        cookies = get_fb_cookies(username, password, otp_secret, alt_account)
    if cookies == None:
        time.sleep(5)
        continue
    break

if cookies == None:
    raise Exception("Login facebook failed")

with open(filename, "w") as cookies_file:
    json.dump(cookies, cookies_file)

try:
    if STORAGE_BRANCE is not None and STORAGE_BRANCE != "":
        # Encrypt file with encrypt key
        print("Đang mã hóa tập tin trước khi tải lên...")
        encrypt_file(filename, filename + ".enc", encrypt_key)
        encrypt_file(f_login_info, f_login_info + ".enc", encrypt_key)
        print("Mã hóa thành công!")
        # Upload the file onto repo
        upload_file(GITHUB_TOKEN, GITHUB_REPO, filename + ".enc", STORAGE_BRANCE)
        upload_file(GITHUB_TOKEN, GITHUB_REPO, f_login_info + ".enc", STORAGE_BRANCE)
        print(f"Đã tải tệp lên branch: {STORAGE_BRANCE}")
except Exception as e:
    print(e)
