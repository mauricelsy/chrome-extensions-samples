from petcat_tools import *
from web3 import Web3
from eth_abi import encode
from web3.middleware import geth_poa_middleware

from datetime import datetime


# 获取节点
def get_web3(chain):
    if chain == "eth":
        web3 = Web3(
            Web3.HTTPProvider(
                "https://mainnet.infura.io/v3/80b882a99dcd4bf8a14eb4ac2b541152"
            )
        )
    elif chain == "op":
        web3 = Web3(
            Web3.HTTPProvider(
                "https://optimism-mainnet.infura.io/v3/80b882a99dcd4bf8a14eb4ac2b541152"
            )
        )
    elif chain == "arb":
        web3 = Web3(
            Web3.HTTPProvider(
                "https://arbitrum-mainnet.infura.io/v3/80b882a99dcd4bf8a14eb4ac2b541152"
            )
        )
    elif chain == "stark":
        web3 = Web3(
            Web3.HTTPProvider(
                "https://starknet-mainnet.infura.io/v3/80b882a99dcd4bf8a14eb4ac2b541152"
            )
        )
    elif chain == "matic":
        web3 = Web3(
            Web3.HTTPProvider(
                "https://polygon-mainnet.infura.io/v3/80b882a99dcd4bf8a14eb4ac2b541152"
            )
        )
        # web3 = Web3(
        #     Web3.HTTPProvider(
        #         "https://newest-snowy-needle.matic.discover.quiknode.pro/9d6d937a34e7d9fe9b9ca7b7f0cab8457db3a428/"
        #     )
        # )
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3


# 获取当前主网 gas price
def get_gas_price():
    web3 = get_web3("eth")
    return web3.eth.gas_price


# 检查当前 gas price 是否低于阈值
def gas_below_threshold(threshold):
    gas_price = get_gas_price()
    print("gas price now:", round(gas_price / 1e9), "gwei")
    return gas_price < threshold


# 获取当前区块网络基础费用
def get_base_fee(chain):
    web3 = get_web3(chain)
    # 获取最新区块号
    latest_block_number = web3.eth.block_number
    # 获取最新区块信息
    latest_block = web3.eth.get_block(latest_block_number)
    # 提取最新区块的基础费用
    base_fee = latest_block["baseFeePerGas"]
    return base_fee


# 合约读函数
def function_read(chain, contract_address, function_name, args):
    web3 = get_web3(chain)
    contract_address = web3.to_checksum_address(contract_address)
    contract_abi = get_abi_gs(contract_address, chain)
    contract_instance = web3.eth.contract(address=contract_address, abi=contract_abi)
    function = getattr(contract_instance.functions, function_name)
    kwargs = {}
    return function(*args, **kwargs).call()


# 合约写函数
def function_write(
    chain,
    wallet_address,
    contract_address,
    function_name,
    args,
    data=None,
    gas_limit=None,
    value_wei=0,
    **kwargs,
):
    # 返回参数初始化
    status = 0
    tx_hash = ""
    message = ""

    web3 = get_web3(chain)
    contract_address = web3.to_checksum_address(contract_address)

    contract_abi = get_abi_gs(contract_address, chain)
    if not contract_abi:
        print("no abi got for contract", contract_address)
        return
    contract_instance = web3.eth.contract(address=contract_address, abi=contract_abi)

    private_key = get_pkey(wallet_address)

    # print(wallet_address, nonce)
    # print(spender_address, allowance)
    # print(*args)
    # print({**kwargs})
    # input("press any key to continue...")

    # function = getattr(contract_instance.functions, function_name)
    # transaction = function(*args).buildTransaction({**kwargs})

    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(wallet_address)
    gas_price = web3.eth.gas_price
    base_fee = get_base_fee(chain)
    print(
        "chain id:",
        chain_id,
        "nonce:",
        nonce,
        "gas price:",
        gas_price,
        "base fee:",
        base_fee,
    )
    print(f"wallet_address: {wallet_address}  contract address: {contract_address}")

    # 构建交易对象（无abi直接data方式/通过abi及参数构建）
    if data:
        transaction_params = {
            "from": wallet_address,
            "to": contract_address,
            "value": value_wei,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": chain_id,
            # "maxFeePerGas": base_fee * 2,
        }
        transaction = {**transaction_params, "data": data}
    else:
        transaction_params = {
            "from": wallet_address,
            # "to": contract_address,
            "value": value_wei,
            "gasPrice": gas_price,
            # gasPrice 和 (maxFeePerGas or maxPriorityFeePerGas) 不可同时指定
            "nonce": nonce,
            "chainId": chain_id,
            # "maxFeePerGas": base_fee * 2,
            # gas估算必须参数（可能默认值低于当前网络基础费 max fee per gas less than block base fee）
        }
        # function_call = contract_instance.functions[function_name](*args)
        # transaction = function_call.buildTransaction(transaction_params)

        transaction = contract_instance.functions[function_name](
            *args
        ).build_transaction(transaction_params)

    # print("Transaction Data:", transaction["data"])
    # input("press any key to continue...")

    if gas_limit:
        transaction.update({"gas": gas_limit})
    else:
        # 获取网络当前gas估算值
        gas_limit = web3.eth.estimate_gas(transaction)
        print(f"get gas estimate: {gas_limit}")

    # gas limit加入交易参数
    transaction.update({"gas": gas_limit})
    # input(f"{transaction}\nPress any key to continue...")

    # 签名交易
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    # 发送已签名的交易
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    # 等待交易确认
    transaction_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    # 检查交易结果
    # now = datetime.now()
    # if transaction_receipt["status"] == 1:
    #     print(wallet_address, "交易成功", transaction_hash.hex())
    #     tx_info = [taskname, "Sucess", wallet_address, "", 0, transaction_hash.hex()]
    #     tx_journal(str(now), tx_info)
    # else:
    #     print(wallet_address, "交易失败", transaction_hash.hex())
    #     tx_info = [taskname, "Fail", wallet_address, "", 0, transaction_hash.hex()]
    #     tx_journal(str(now), tx_info)

    tx_info = get_tx_info(chain, transaction_receipt)
    tx_hash = transaction_hash.hex()
    status = tx_info["status"]
    gas_price_info = tx_info["gas_price_info"]
    tx_fee_info = tx_info["tx_fee_info"]
    tx_fee = tx_info["tx_fee"]
    value = round(value_wei / 1e18, 6)
    message = f"contract {contract_address}, function {function_name}, {gas_price_info}, {tx_fee_info}"

    return {
        "status": status,
        "tx_hash": tx_hash,
        "tx_fee": tx_fee,
        "value": value,
        "message": message,
    }


# 生成交易数据
def make_calldata(function_name, params_type, params_value):
    function_signature = Web3.keccak(text=function_name)[:4].hex()

    # # 定义特殊类型的参数和对应的编码函数
    # special_types_encoders = {
    #     "address": lambda value: encode_abi(["address"], [value]),
    #     "bytes32": lambda value: encode_abi(["bytes32"], [value]),
    #     "bytes": lambda value: bytes.fromhex(value[2:]),
    #     "bytes[]": lambda value: encode_abi(
    #         ["bytes[]"], [[bytes.fromhex(v[2:]) for v in value]]
    #     ),
    # }

    # def encode_parameter(param_type, param_value):
    #     if param_type in special_types_encoders:
    #         return special_types_encoders[param_type](param_value)
    #     else:
    #         return encode_abi([param_type], [param_value])

    # # parameters_data = encode_abi(params_type, function_params).hex()

    # encoded_params = []
    # # 构造函数调用的 ABI 编码数据
    # encoded_params = [
    #     encode_parameter(param_type, param_value)
    #     for param_type, param_value in zip(params_type, function_params)
    # ]

    # # 添加动态字节数组长度编码  **** 以下逻辑有待进一步验证 ****
    # for i, param_type in enumerate(params_type):
    #     # print(i, param_type, encoded_params[i].hex())
    #     # input("press any key to continue...")
    #     if param_type == "bytes":
    #         byte_lenth = len(encoded_params[i])
    #         dynamic_data_1 = encode_abi(["uint256"], [byte_lenth + 64])
    #         dynamic_data_2 = encode_abi(["uint256"], [byte_lenth])
    #         encoded_params[i] = dynamic_data_1 + dynamic_data_2 + encoded_params[i]

    # parameters_data = b"".join(encoded_params).hex()

    # data = function_signature + parameters_data
    # return data

    encoded_params = encode(params_type, params_value).hex()

    encoded_data = function_signature + encoded_params
    return encoded_data


# some test code
# params_values = [
#     4,
#     "0x6D6768A0b24299bEdE0492A4571D79F535c330D8",
#     397559,
#     400000000000,
#     bytes.fromhex(
#         "0000000000000000000000002732f76f5154080c2f8ad3b029443ce49931cd870000000000000000000000002732f76f5154080c2f8ad3b029443ce49931cd870000000700000000000000000000000000000000000000000000000000015ebf"
#     ),
# ]
# params_type = ["uint32", "address", "uint256", "uint256", "bytes"]
# function_name = "bridgeOutRequest(uint32,address,uint256,uint256,bytes)"
# result = make_calldata(function_name, params_type, params_values)
# print(result)


# 转账交易
def transfer(chain, value_eth, sender, receiver, balance_limit=0, **kwargs):
    transaction_flag = True
    status = 0
    tx_hash = ""
    message = ""

    try:
        web3 = get_web3(chain)
        sender_address = Web3.to_checksum_address(sender)
        recipient_address = Web3.to_checksum_address(receiver)
        private_key = get_pkey(sender_address)

        # 转账金额（以 wei 为单位）
        value_wei = web3.to_wei(value_eth, "ether")
        balance_limit_wei = web3.to_wei(balance_limit, "ether")

        # 确认账户余额
        account_balance = web3.eth.get_balance(sender_address)
        print(sender_address, round(account_balance / 1e18, 4), "ETH")
        input("please confirm account balance...")

        # 确认转账金额
        amount_input = input(f"transfer amount: {value_eth} ETH, input new amount...")
        value_wei = Web3.to_wei(
            float(amount_input) if amount_input.strip() else value_eth, "ether"
        )

        # 检查交易后账户余额是否达到阈值
        if balance_limit_wei > account_balance - value_wei:
            transaction_flag = False
            message = "Low balance!"

        # 确认gas limit
        gas_estimate = web3.eth.estimate_gas(
            {
                "from": sender_address,
                "to": recipient_address,
                "value": value_wei,
            }
        )

        # 检查账户余额是否足够支付转账金额和gas费用
        balance_after = account_balance - (
            value_wei + web3.eth.gas_price * gas_estimate
        )
        if balance_after >= 0:
            print("new balance estimate:", round(balance_after / 1e18, 4), "ETH")
        else:
            transaction_flag = False
            message = "Insufficient balance!"

        user_confirm = input(
            f"ready to transfer {round(value_wei/1e18,4)} ETH from {sender_address} to {recipient_address} ...y/n"
        )
        if user_confirm == "n":
            transaction_flag = False
            message = "User aborted!!"

        if transaction_flag:
            # 构造交易对象
            transaction = {
                "to": recipient_address,
                "value": value_wei,
                "gas": gas_estimate,
                "gasPrice": web3.eth.gas_price,
                "nonce": web3.eth.get_transaction_count(sender_address),
                # "chainId": 42161,  # Arbitrum主网的chainId
            }

            # 签名交易
            signed_transaction = web3.eth.account.sign_transaction(
                transaction, private_key
            )

            # 发送交易
            transaction_hash = web3.eth.send_raw_transaction(
                signed_transaction.rawTransaction
            )

            # 等待交易确认
            transaction_receipt = web3.eth.wait_for_transaction_receipt(
                transaction_hash
            )
            tx_info = get_tx_info(chain, transaction_receipt)
            tx_hash = transaction_hash.hex()
            status = tx_info["status"]
            gas_price_info = tx_info["gas_price_info"]
            tx_fee_info = tx_info["tx_fee_info"]
            tx_fee = tx_info["tx_fee"]
            value = round(value_wei / 1e18, 6)
            message = f"transfer {round(value_wei/1e18,6)} ETH, {gas_price_info}, {tx_fee_info}"

    except Exception as e:
        message = str(e)

    return {
        "status": status,
        "tx_hash": tx_hash,
        "tx_fee": tx_fee,
        "value": value,
        "message": message,
    }


def check_params(address, params):
    if params.get("api"):
        if params["api"] == "transfer":
            # transfer(chain, amount_eth, sender, receiver, balance_limit=0)
            # 逐个判断参数是否ready
            if params.get("chain") and params.get("amount_eth"):
                params.update({"sender": address})
                if params.get("receiver"):
                    return params
                elif params.get("to_exchange"):
                    receiver = get_cex_address(params["to_exchange"], address).get(
                        address
                    )
                    if receiver:
                        params.update({"receiver": receiver})
                        return params

        elif params["api"] == "function_write":
            # function_write(chain, wallet_address, contract_address, function_name, args, data=None, gas_limit=None, value_wei=0,)
            # 验证是否包含公链/合约地址/函数名 等参数
            if (
                params.get("chain")
                and params.get("contract_address")
                and params.get("function_name")
            ):
                # 添加源地址参数
                params.update({"wallet_address": address})

                # 根据接口参数表生成args参数
                args = []
                if params.get("params_name"):
                    if params["params_name"]:
                        for param_item in params["params_name"]:
                            try:
                                args.append(params[param_item])
                            except:
                                print("get function params error!")
                                args = []
                        if args:
                            params.update({"args": args})
                        else:
                            print("get function params error!")
                else:
                    # 函数无入参
                    params.update({"args": args})

                # 将用户定义value_eth 转为value_wei
                if params.get("value_eth"):
                    value_eth = params["value_eth"]
                    # 判断输入类型（指定数字或范围）
                    if isinstance(value_eth, (int, float)):
                        pass
                    elif isinstance(value_eth, list) and len(value_eth) == 2:
                        value_eth = get_random_number(*value_eth)
                    else:
                        print("get value error!", value_eth)
                    value_wei = Web3.to_wei(value_eth, "ether")
                    params.update({"value_wei": value_wei})

                # 是否使用abi方法
                if params.get("abi"):
                    return params
                # 不使用abi方法直接生成交易data参数
                else:
                    if params.get("params_type"):
                        params_type = params["params_type"]
                    else:
                        params_type = []

                    params_type_str = "(" + ",".join(params_type) + ")"
                    function_name = params["function_name"] + params_type_str
                    data = make_calldata(function_name, params_type, args)
                    params.update({"data": data})
                    return params

    return {}


def task_do(address, params):
    task_result = {"status": 0}
    if params.get("api"):
        if params["api"] == "transfer":
            params = check_params(address, params)
            # print("get params checked -", params)
            # task_result = int(input("please input task result 0/1..."))
            if params:
                task_result = transfer(**params)
            else:
                result_message = "params check error!"
                task_result.update(
                    {
                        "message": result_message,
                        "tx_hash": None,
                        "tx_fee": None,
                        "value": None,
                        "status": -1,
                    }
                )
                print(result_message)
            return task_result
        elif params["api"] == "function_write":
            params = check_params(address, params)
            # print("get params checked -", params)
            if params:
                task_result = function_write(**params)
            else:
                result_message = "params check error!"
                task_result.update(
                    {
                        "message": result_message,
                        "tx_hash": None,
                        "tx_fee": None,
                        "value": None,
                        "status": -1,
                    }
                )
                print(result_message)

    return task_result
