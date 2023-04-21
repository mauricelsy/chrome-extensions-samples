import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# 打开Google指定账户profile
profile_path = r"C:\Users\mauri\AppData\Local\Google\Chrome\User Data\Profile 4"
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=" + profile_path)
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com/")

# 检测Discord指定账户登录状态，如果未登录进行自动登录操作
driver.get("https://discord.com/login")
time.sleep(5) # 等待页面加载完成
if driver.current_url == "https://discord.com/login":
    email = driver.find_element(By.NAME, "email")
    password = driver.find_element(By.NAME, "password")
    email.send_keys("pekoe.bit@gmail.com")
    password.send_keys("uxy_vyp0ctd7bxn0KCA")
    password.submit()

# 登录Discord进入指定频道板块
time.sleep(5) # 等待页面加载完成
driver.get("https://discord.com/channels/916379725201563759/1037811694564560966") # Sui - testnet-faucet
# driver.get("https://discord.com/channels/896185694857343026/915212611962929192") # Lit Protocol - gm
# 等待页面加载完成
wait = WebDriverWait(driver, 10)
message_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'textAreaSlate')]/div/div[@role='textbox']")))

# 以指定的随机时间间隔，发送一条指定内容的信息
messages = ["!faucet 0x3fb797b4d1112382a0e111cc46fd9cce2e61e83c17deb9e32b6e57cef225de70"]
while True:
    message = random.choice(messages)
        
    message_box.click()
    message_box.send_keys(message)
    message_box.send_keys(Keys.ENTER)
    sleep_time = random.randint(7200, 9000) # 等待指定秒数的随机时间
    print("wait", sleep_time, "s to send the next message")
    time.sleep(sleep_time) 