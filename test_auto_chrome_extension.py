from selenium import webdriver
from selenium.webdriver.common.by import By

profile_path = r"C:\Users\mauri\AppData\Local\Google\Chrome\User Data\Profile 4"
options = webdriver.ChromeOptions()

# 设置权限参数可以在 Chrome 浏览器中打开指定的扩展程序并访问其选项页
options.add_argument("--disable-extensions-except=")
options.add_argument("--load-extension=/path/to/extension")

options.add_argument("user-data-dir=" + profile_path)
options.add_extension(r'C:\Users\mauri\AppData\Local\Google\Chrome\User Data\Default\Extensions\opcgpfmipidbgpenhmajoajpbobppdil\23.4.4.0_2')
driver = webdriver.Chrome(options=options)
driver.get('https://www.google.com')

# 打开一个新标签页
driver.execute_script("window.open('chrome-extension://opcgpfmipidbgpenhmajoajpbobppdil/')")
# 切换到新标签页
driver.switch_to.window(driver.window_handles[-1])
# 执行 JavaScript 代码打开选项页
driver.execute_script("window.open('chrome-extension://opcgpfmipidbgpenhmajoajpbobppdil/options.html')")
