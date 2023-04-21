import requests
import json
import time
import random

# 设置时间间隔范围（秒）
min_interval = 3600  # 1小时
max_interval = 10800  # 3小时

# 设置请求数据
url = 'https://faucet.testnet.sui.io/gas'
headers = {
    'Content-Type': 'application/json'
}
data = {
    "FixedAmountRequest": {
        "recipient": "0x0586022c92f8ab3d58bf54cbff9be3c9127303575379f335eefc905a92cd78e5"
    }
}

def send_gas():
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json())

# 首次执行
send_gas()

# 执行定时任务
while True:
    interval = random.randint(min_interval, max_interval)
    print(f"下次请求将在{interval/3600:.1f}小时后执行")
    time.sleep(interval)
    send_gas()