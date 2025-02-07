from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fb_getcookies import __chrome_driver__
import time

try:
    for opt in [
        (None, True, False),
        (None, True, True),
        (None, False, False),
        (None, False, True),
    ]:
        driver = __chrome_driver__(*opt)
        driver.get("https://deviceandbrowserinfo.com/are_you_a_bot")
        wait = WebDriverWait(driver, 20)

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)
        resultsBotTest = driver.find_element(By.ID, "resultsBotTest").text
        resultsBotTestDetails = driver.find_element(By.ID, "resultsBotTestDetails").text
        print("resultsBotTest:", resultsBotTest)
        print("resultsBotTestDetails:", resultsBotTestDetails)
        driver.quit()
    
except Exception as e:
    print(e)
finally:
    driver.quit()
