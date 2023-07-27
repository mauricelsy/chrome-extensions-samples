from task import *
from job import *
from rabbithole_tools import *
import time

job_request = jobClass()

group_no = int(input("please input group number: "))
if group_no == -1:
    account_list = {input("please input wallet address: "): ""}
else:
    account_list = get_group_accounts(group_no)

account_list_shuffled = get_shuffled(account_list)

for key in account_list_shuffled:
    # 任务数据准备
    # function_name = "purchase(uint256)"

    # task_name = "Holograph - Mint NFT - How Far We've Come"
    # chain = "op"
    # contract_address = "0x6d6768a0b24299bede0492a4571d79f535c330d8"
    # mint_quantity = get_random_number(3, 5)

    # function_name = "approve(address,uint256)"
    # task_name = "Approve USDC on Nested"
    # chain = "op"
    # contract_address = "0x7f5c764cbc14f9669b88837ca1490cca17c31607"
    # spender = "0x9A065e500CDCd01c0a506B0EB1A8B060B0cE1379"
    # amount = int(get_random_number(5, 10) * 1e6)

    try:
        wallet_address = Web3.to_checksum_address(key)
    except Exception as e:
        print(key, "address format error!")
        print(str(e))
        continue

    # 任务数据准备

    # 任务参数
    task_name = "AcrossBridge"
    params = {
        "from": wallet_address,
        "chain": "arb",
        "to_chain": "op",
        "request": "across_fee",
        "token": "WETH",
        "amount": (0.001, 0.0015),
        "function_name": "deposit",
        "contract_address": "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a",
        "abi": True,
    }

    # chain = "op"
    # contract_address = "0x52629961f71c1c2564c5aa22372cb1b9fa9eba3e"
    # data_ready = False
    # function_name = "mintReceipt"
    # quest_id = "3e4d0742-f32c-4f44-a73e-38d4fef2cc41"
    # quest_info = rabbithole_getQuestInfo(quest_id, wallet_address)
    # quest_status = quest_info.get("status")
    # quest_name = quest_info.get("name")
    # task_name = f"RabbitHole - {quest_name} - {function_name}"
    # if quest_status:
    #     print(f"{wallet_address} on Quest {quest_id} status: {quest_status}")
    #     if quest_status == "redeemable":
    #         mintRHR_info = rabbithole_getQuestMintInfo(quest_id, wallet_address)
    #         if (
    #             mintRHR_info
    #             and mintRHR_info.get("hash")
    #             and mintRHR_info.get("signature")
    #         ):
    #             mintRHR_hash = mintRHR_info["hash"]
    #             mintRHR_signature = mintRHR_info["signature"]

    #             data_ready = True
    # args = (quest_id, mintRHR_hash, mintRHR_signature)

    # 生成交易data
    data = None
    # params_type = ["address", "uint256"]
    # params_value = [spender, amount]
    # data = make_calldata(function_name, params_type, params_value)
    # input(f"data - {data} press any key to continue...")

    # 设置 gas price 阈值
    gas_price_threshold = Web3.to_wei("25", "gwei")

    # 检查 gas price 是否低于阈值，低于则执行交易，高于则等待
    while not is_gas_price_below_threshold(gas_price_threshold):
        print(
            "address -",
            wallet_address,
            "task -",
            task_name,
        )
        print("超过阈值，等待中...")
        time.sleep(5)  # 每5秒检查一次 gas price

    print("低于阈值，执行交易")

    # tx_value = int(round(random.uniform(1, 3), 1) * 1e6)  # pool together usdc value
    # tx_value = 0.001
    # delegatee_address = "0x8F5415415d9200cCd8523F3Ee88F96F476141CC3"

    try:
        if isinstance(params["amount"], tuple):
            params.update({"amount": get_random_number(*params["amount"])})
        if params["abi"]:
            params.update({"data": None})
        if params["request"]:
            method_name = params["request"]
            request_method = getattr(job_request, method_name)
            params_result = request_method(params)
            if params_result:
                print(params_result)
                args = params_result["args"]
                data = params_result["data"]
                data_ready = True
            else:
                data_ready = False

    except Exception as e:
        data_ready = False
        print(str(e))

    if data_ready:
        print(
            "address -",
            wallet_address,
            "task -",
            task_name,
        )
        print(args)

        chain = params["chain"]
        contract_address = params["contract_address"]
        function_name = params["function_name"]

        function_write(
            chain,
            wallet_address,
            contract_address,
            function_name,
            args,
            data,
            task_name,
        )
