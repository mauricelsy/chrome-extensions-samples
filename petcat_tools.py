import sys

sys.path.append("../toolbox")

import config_thread
import string_tools
import okx_tools

import requests, json, random
from datetime import datetime
import time

# import portalocker

HUGE_NUMBER = (
    115792089237316195423570985008687907853269984665640564039457584007913129639935
)


# 获取谷歌表格配置信息
def get_config(sheetname, worksheet, key):
    sheet_name = sheetname
    worksheet_name = worksheet
    creds = "../gCloud/pet-cats-09f0e10784ea.json"

    thread = config_thread.ConfigThread(
        creds, "read", sheet_name, worksheet_name, key=key
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    config_result = thread.result
    if config_result:
        return config_result.get(key)


def get_api_key(app, username):
    return get_config("api-key", username, app)


# print(json.loads(get_api_key("okx", "mauricelsy@gmail.com")))
# # 返回字符串需要处理判断是否json序列化


# 获取谷歌表格abi记录
def get_abi_gs(address, chain):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Contracts"

    # 获取谷歌表格公链名称（参数chain可能以id形式传递）
    worksheet_name = "chain"
    thread = config_thread.ConfigThread(
        creds, "read", sheet_name, worksheet_name, key=chain
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    config_result = thread.result
    if config_result.get(chain):  # 如果有匹配项
        chain = config_result.get(chain)

    worksheet_name = "contract"
    abi = []

    thread = config_thread.ConfigThread(
        creds, "readln", sheet_name, worksheet_name, key=address
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    config_result = thread.result
    match_result = [
        record
        for record in config_result
        if "Contract" in record
        and "Chain" in record
        and record["Contract"].lower() == address.lower()
        and record["Chain"] == chain
    ]
    if match_result:
        if match_result[0].get("Proxy"):
            abi = get_abi_gs(match_result[0].get("Proxy"), chain)
        else:
            abi = match_result[0].get("ABI")
    return abi


# 写入谷歌表格交易日志
def tx_journal_gs(tx_journal):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "tx_journal"
    worksheet_name = "Sheet1"
    tx_journal_list = []
    for id, journal in tx_journal.items():
        tx_journal_list.append(list({"id": id, **journal}.values()))

    thread = config_thread.ConfigThread(
        creds, "write-rows", sheet_name, worksheet_name, value=tx_journal_list
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    return True


def get_group_accounts(group_no):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Groups"
    worksheet_name = f"Group{group_no}"

    thread = config_thread.ConfigThread(creds, "read", sheet_name, worksheet_name)
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    return thread.result


def get_assignment(group_no, status="active"):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Tasks"
    worksheet_name = "assignment"

    thread = config_thread.ConfigThread(creds, "readln", sheet_name, worksheet_name)
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    if thread.result:
        return {
            d["hashID"]: {
                "mission": d["missionID"],
                "name": d["missionName"],
                "params": json.loads(d["Params"]),  # 添加判断处理非json标准格式输入
                "status": d["Status"],
                "deadline": d["Deadline"],
            }
            for d in thread.result
            if d["hashID"]
            and d["missionID"]
            and d["Params"]
            and group_no == d["Group"]
            and d["Status"] in status
        }
    else:
        return {}


def update_assignment(id, account_list):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Tasks"
    worksheet_name = "assignment"

    status_list = []
    group_status_completed = True
    group_status_processing = False
    group_status_paused = False
    group_status_expired = False
    for account, assignments in account_list.items():
        assignment = assignments.get(id)
        if assignment:
            status = assignment["status"]
            if status != "completed":
                group_status_completed = False
            if status == "processing":
                group_status_processing = True
            if status == "paused":
                group_status_paused = True
            if status == "expired":
                group_status_expired = True
        else:
            status = ""
        status_list.append(f"{status} - {account}")

    # 更新所有地址状态
    thread = config_thread.ConfigThread(
        creds,
        "write-column",
        sheet_name,
        worksheet_name,
        key=id,
        value=status_list,
        col_start=10,
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    # 更新当前任务状态
    if group_status_completed:
        group_status_new = "completed"
    else:
        group_status_new = ""
        if group_status_processing:
            group_status_new = "processing"
        if group_status_paused:
            group_status_new = "paused"
        if group_status_expired:
            group_status_new = "expired"

    if group_status_new:
        thread = config_thread.ConfigThread(
            creds,
            "write-column",
            sheet_name,
            worksheet_name,
            key=id,
            value=[group_status_new],
            col_start=7,
        )
        time.sleep(1)
        thread.start()
        thread.join()
        time.sleep(1)


def get_job(mission_id):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Tasks"
    worksheet_name = "mission"

    thread = config_thread.ConfigThread(
        creds, "readln", sheet_name, worksheet_name, mission_id
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    if thread.result:
        job_list = {
            d["jobID"]: {
                "seq": d["Seq"],
                "task": d["Task"],
                "params": json.loads(d["Params"]),  # 添加判断处理非json标准格式输入
            }
            for d in thread.result
            if isinstance(d["Seq"], int) and d["Seq"] >= 0 and d["jobID"]
        }

        # def sort_key(item):
        #     return item["seq"], random.random()

        # sorted_task = sorted(task_list, key=sort_key)

        return job_list
    else:
        return {}


def get_task(task_id=None):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Tasks"
    worksheet_name = "task"

    thread = config_thread.ConfigThread(
        creds, "readln", sheet_name, worksheet_name, task_id
    )
    time.sleep(1)
    thread.start()
    thread.join()
    time.sleep(1)
    if thread.result:
        if task_id:
            return {
                d["Task"]: json.loads(d["Params"])
                for d in thread.result
                if d["taskID"] == task_id
            }
        else:
            return {d["Task"]: json.loads(d["Params"]) for d in thread.result}


def get_job_ordered(job_list):
    # 随机排序
    sorted_keys = sorted(
        job_list.keys(), key=lambda k: (job_list[k]["seq"], random.random())
    )
    return sorted_keys


def get_cex_address(exchange, address=None):
    creds = "../gCloud/pet-cats-09f0e10784ea.json"
    sheet_name = "Exchanges"
    worksheet_name = "deposit"

    thread = config_thread.ConfigThread(
        creds, "readln", sheet_name, worksheet_name, address
    )
    thread.start()
    thread.join()
    time.sleep(2)
    if thread.result:
        return {
            d["wallet"]: d[exchange]
            for d in thread.result
            if "wallet" in d and exchange in d and d["wallet"] and d[exchange]
        }
    else:
        return {}


# 测试代码
# address = "0x90a6D85d98B696B8c9f3b8c26998DfF03229F691"
# print(get_cex_address("okx").get(address))


# 字典键随机输出（数组）
def get_shuffled(dict):
    keys = list(dict.keys())
    random.shuffle(keys)
    return keys


def get_random_number(start, end, precision=None):
    def determine_precision(start, end):
        start_str = str(start)
        end_str = str(end)

        start_decimals = len(start_str.split(".")[-1]) if "." in start_str else 0
        end_decimals = len(end_str.split(".")[-1]) if "." in end_str else 0

        return max(start_decimals, end_decimals)

    if isinstance(start, int) and isinstance(end, int):
        # 如果都是整数，返回整数随机数
        number = random.randint(start, end)
    else:
        # number = random.uniform(start, end)
        precision = (
            precision if precision is not None else determine_precision(start, end)
        )
        # 小数随机数精度由输入值确定（比输入值的精度多一位）
        number = round(random.uniform(start, end), precision + 1)

    return number


def send_request(url, method="GET", data=None, headers=None):
    if method == "GET":
        response = requests.get(url, params=data, headers=headers)
    elif method == "POST":
        if headers and headers.get("Content-Type") == "application/json":
            json_data = json.dumps(data)
            response = requests.post(url, data=json_data, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
    else:
        raise ValueError("Invalid HTTP method specified.")

    # 检查请求是否成功
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        response.raise_for_status()  # 抛出异常以指示请求失败


# # 测试代码 for send_request
# url = "https://across.to/api/suggested-fees"
# params = {
#     "token": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
#     "destinationChainId": 10,
#     "originChainId": 42161,
#     "amount": 1000000000000000,
#     "skipAmountLimit": "true",
# }
# response_text = send_request(url, method="GET", data=params)
# print(response_text)


def get_token_address(symbol, chain):
    token_list = [
        {
            "Symbol": "WETH",
            "Chain": "arb",
            "Address": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        }
    ]
    # 创建索引
    index = {(item["Symbol"], item["Chain"]): item["Address"] for item in token_list}

    address = index.get((symbol, chain))
    return address


def get_chain_info(chain_symbol):
    chain_list = [
        {"Symbol": "arb", "Name": "Arbitrum", "ID": 42161},
        {"Symbol": "op", "Name": "Optimism", "ID": 10},
    ]
    return [item for item in chain_list if item["Symbol"] == chain_symbol]


def get_tx_info(chain, tx_receipt):
    status = tx_receipt["status"]
    gas_used = tx_receipt["gasUsed"]
    gas_price = tx_receipt["effectiveGasPrice"]
    gas_price_info = f"gas price: {round(gas_price/1e9,2)} gwei"
    # print(f"status:{status} gas used:{gas_used}")

    tx_fee = 0
    tx_fee_info = ""

    if chain == "eth":
        tx_fee = gas_price * gas_used / 1e18
        tx_fee_info = f"tx fee: {tx_fee:.6f} eth"
        # print(f"gas price: {round(gas_price/1e9,2)} gwei")
        # print(f"tx fee: {round(tx_fee,6):.6f} eth")

    if chain == "matic":
        tx_fee = gas_price * gas_used / 1e18
        tx_fee_info = f"tx fee: {tx_fee:.6f} matic"
        # print(f"gas price: {round(gas_price/1e9,2)} gwei")
        # print(f"tx fee: {round(tx_fee,6):.6f} matic")

    if chain == "op":
        l1fee = int(tx_receipt["l1Fee"], 16)
        l1GasPrice = int(tx_receipt["l1GasPrice"], 16)
        l1GasUsed = int(tx_receipt["l1GasUsed"], 16)
        l1FeeScalar = float(tx_receipt["l1FeeScalar"])
        # print(
        #     f"l1fee:{l1fee}, l1GasPrice:{l1GasPrice}, l1GasUsed:{l1GasUsed}, l1FeeScalar:{l1FeeScalar}"
        # )
        l1fee_calculated = l1GasPrice * l1GasUsed * l1FeeScalar / 1e18
        l2fee = gas_price * gas_used / 1e18
        tx_fee = l1fee_calculated + l2fee
        L1pct = round(l1fee_calculated / tx_fee, 2)
        tx_fee_info = f"tx fee: {tx_fee:.6f} eth, L1 {L1pct:.0%}"
        # print(f"tx fee: {round(tx_fee,6):.6f} eth, L1: {L1pct:.0%}")

    if chain == "arb":
        gasUsedForL1 = int(tx_receipt["gasUsedForL1"], 16)
        # print(f"gas price: {round(gas_price/1e9,2)} gwei, gasUsedForL1: {gasUsedForL1}")
        tx_fee = gas_price * gas_used / 1e18
        L1pct = round(gasUsedForL1 / gas_used, 2)
        tx_fee_info = f"tx fee: {tx_fee:.6f} eth, L1 {L1pct:.0%}"
        # print(f"tx fee: {round(tx_fee,6):.6f} eth, L1: {L1pct:.0%}")

    return {
        "status": status,
        "gas_used": gas_used,
        "gas_price": gas_price,
        "gas_price_info": gas_price_info,
        "tx_fee": tx_fee,
        "tx_fee_info": tx_fee_info,
    }


def get_tx_journal(account_address, group_no, task_name, task_result):
    # task_result = {"status": status, "tx_hash": tx_hash, "tx_fee": tx_fee, "message": message}
    timestamp = str(datetime.now())
    tx_journal_id = string_tools.get_hash(
        timestamp + task_name + account_address + str(task_result)
    )
    task_status = task_result.get("status")
    tx_hash = task_result.get("tx_hash")
    tx_fee = task_result.get("tx_fee")
    value = task_result.get("value")
    message = task_result.get("message")

    # 判定异常交易状况
    if tx_hash and task_status == 0 and (value + tx_fee) > 0:
        task_status = -1

    tx_journal = {
        tx_journal_id: {
            "date": timestamp,
            "task": task_name,
            "status": task_status,
            "account": account_address,
            "group": group_no,
            "value": value,
            "fee": tx_fee,
            "transaction": tx_hash,
            "message": message,
        }
    }
    return tx_journal


# 测试代码
# account_address = "0x22C5fc59157C4EB3456EA1BaB2Ec0bADDB93966E"
# task_name = "opDelegate - op_delegate"
# task_result = {
#     "status": 1,
#     "tx_hash": "0x0a831b82a46a5b1b30b19f9db42d10dcc58a902dbd4540609fca00e702cd953c",
#     "message": "contract 0x4200000000000000000000000000000000000042, function delegate, gas price: 1.08 gwei, tx fee: 0.000088 eth, L1 64%",
#     "tx_fee": 0.000088,
# }
# tx_journal = get_tx_journal(account_address, task_name, task_result)
# print(tx_journal)


# def read_and_write_json_with_lock(
#     file_path, data_to_write, flag, max_retries, retry_interval
# ):
#     for attempt in range(max_retries):
#         try:
#             # 检查文件是否存在
#             file_exists = True
#             try:
#                 with open(file_path, "r") as file:
#                     pass
#             except FileNotFoundError:
#                 file_exists = False

#             # 文件不存在初始化文件（直接写入当前数据或者不处理）
#             if not file_exists:
#                 if flag:
#                     with open(file_path, "w") as file:
#                         json.dump(data_to_write, file, indent=4)
#                 return True

#             # 读取文件内容并加锁
#             with open(file_path, "r+") as file:
#                 portalocker.lock(file, portalocker.LOCK_SH)
#                 existing_data = json.load(file)

#                 # 在写入文件时获取锁
#                 file.seek(0)
#                 portalocker.lock(file, portalocker.LOCK_NB)

#                 # 修改数据
#                 if flag:
#                     existing_data.update(data_to_write)
#                 else:
#                     for key in data_to_write:
#                         existing_data.pop(key, None)

#                 # 写入更新后的数据
#                 file.truncate(0)
#                 json.dump(existing_data, file, indent=4)

#             return True

#         except portalocker.exceptions.LockException:
#             print(
#                 f"Attempt {attempt + 1}: File is locked, retrying in {retry_interval} seconds..."
#             )
#             time.sleep(retry_interval)
#         except Exception as e:
#             print(f"Error: {e}")
#             return False

#     return False
