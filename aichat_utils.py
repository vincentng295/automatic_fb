import json  # For handling JSON data
import shlex  # For parsing shell-like syntax
import pyotp  # For generating TOTP (Time-based One-Time Passwords)
from selenium.webdriver.support.ui import WebDriverWait  # For waiting for elements in Selenium

def get_header_prompt(day_and_time, myname, ai_prompt, who_chatted, self_facebook_info, facebook_info):
    return f"""
I am creating a chat bot / message response model and using your reply as a response. 

Pretending that you are me: {myname}
{ai_prompt}
Here is json information about you "{myname}" on Facebook:
{json.dumps(self_facebook_info, ensure_ascii=False, indent=2)}

Currently, it is {day_and_time}, you receives a message from "{who_chatted}".
Here is json information about "{who_chatted}":
{json.dumps(facebook_info, ensure_ascii=False, indent=2)}
"""

def escape_string(input_string):
    """
    Escapes special characters in a string, including replacing newlines with \\n.
    :param input_string: The string to be escaped.
    :return: The escaped string.
    """
    escaped_string = input_string.replace("\\", "\\\\")  # Escape backslashes
    escaped_string = escaped_string.replace("\n", "\\n")  # Escape newlines
    escaped_string = escaped_string.replace("\t", "\\t")  # Escape tabs (optional)
    escaped_string = escaped_string.replace("\"", "\\\"")  # Escape double quotes
    escaped_string = escaped_string.replace("\'", "\\\'")  # Escape single quotes
    return escaped_string

emoji_to_shortcut = [
    {"emoji": "👍", "shortcut": "(y)"},
    {"emoji": "😇", "shortcut": "O:)"},
    {"emoji": "😈", "shortcut": "3:)"},
    {"emoji": "❤️", "shortcut": "<3"},
    {"emoji": "😞", "shortcut": ":("},
    {"emoji": "☹️", "shortcut": ":["},
    {"emoji": "😊", "shortcut": "^_^"},
    {"emoji": "😕", "shortcut": "o.O"},
    {"emoji": "😲", "shortcut": ":O"},
    {"emoji": "😘", "shortcut": ":*"},
    {"emoji": "😢", "shortcut": ":'("},
    {"emoji": "😎", "shortcut": "8-)"},
    {"emoji": "😆", "shortcut": ":v"},
    {"emoji": "😸", "shortcut": ":3"},
    {"emoji": "😁", "shortcut": ":-D"},
    {"emoji": "🐧", "shortcut": "<(\")"},
    {"emoji": "😠", "shortcut": ">:("},
    {"emoji": "😜", "shortcut": ":P"},
    {"emoji": "😮", "shortcut": ">:O"},
    {"emoji": "😕", "shortcut": ":/"},
    {"emoji": "🤖", "shortcut": ":|]"},
    {"emoji": "🦈", "shortcut": "(^^^)"},
    {"emoji": "😑", "shortcut": "-_-"},
    {"emoji": "💩", "shortcut": ":poop:"},
    {"emoji": "😭", "shortcut": "T_T"},
]

# Create a dictionary for quick lookup
emoji_dict = {item["emoji"]: item["shortcut"] for item in emoji_to_shortcut}

def replace_emoji_with_shortcut(text):
    # Use regex to find all emojis and replace them
    for emoji, shortcut in emoji_dict.items():
        text = text.replace(emoji, shortcut)
    return text

def wait_for_load(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def remove_non_bmp_characters(input_string):
    return ''.join(c for c in input_string if ord(c) <= 0xFFFF)
    
def inject_reload(driver, timedelay = 300000):
    # Insert JavaScript to reload the page after 5 minutes (300,000 ms)
    reload_script = """
            if (typeof window.reloadScheduled === 'undefined') {
                window.reloadScheduled = true;
                setTimeout(function() {
                    location.reload();
                }, arguments[0]);
            }
    """
    driver.execute_script(reload_script, timedelay)

def find_and_get_text(parent, find_by, find_selector):
    try:
        return parent.find_element(find_by, find_selector).text
    except Exception:
        return None

def find_and_get_list_text(parent, find_by, find_selector):
    myList = []
    try:
        for element in parent.find_elements(find_by, find_selector):
            try:
                myList.append(element.text)
            except Exception:
                pass
    except Exception:
        pass
    return myList

def switch_to_mobile_view(driver):
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36"
    })

def switch_to_desktop_view(driver):
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    })

def is_cmd(text):
    return text == "/cmd" or text.startswith("/cmd ")

# Define functions to be called
import pyotp
def totp_cmd(secret):
    return pyotp.TOTP(secret).now()

# Dictionary mapping arg1 to functions
func = {
    "totp": totp_cmd,
}

def parse_and_execute(command):
    # Parse the command
    args = shlex.split(command)
    
    # Check if the command starts with /cmd
    if len(args) < 3 or args[0] != "/cmd":
        return "Invalid command format. Use: /cmd arg1 arg2"
    
    # Extract arg1 and arg2
    arg1, arg2 = args[1], args[2]
    
    # Check if arg1 is in func and execute
    if arg1 in func:
        try:
            return func[arg1](arg2)
        except Exception as e:
            return f"Error while executing function: {e}"
    else:
        return f"Unknown command: {arg1}"