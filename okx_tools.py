import time
import hmac
import hashlib
import base64
import requests
import json
from datetime import datetime
from urllib.parse import urlencode


# 配置参数
BASE_URL = "https://www.okx.com"


def get_timestamp():
    now = datetime.utcnow()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def get_signature(timestamp, method, request_path, body, secret_key):
    if isinstance(body, dict):
        body = json.dumps(body)
    message = timestamp + method + request_path + body
    mac = hmac.new(
        bytes(secret_key, encoding="utf8"),
        bytes(message, encoding="utf-8"),
        digestmod=hashlib.sha256,
    )
    d = mac.digest()
    return base64.b64encode(d)


def get_okx(key_info, request_path):
    api_key = key_info.get("apikey")
    api_secret = key_info.get("secretkey")
    api_passphrase = key_info.get("passphrase")
    if api_key and api_secret and api_passphrase:
        timestamp = get_timestamp()
        method = "GET"
        body = ""

        signature = get_signature(timestamp, method, request_path, body, api_secret)

        header = {
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": api_passphrase,
            "Content-Type": "application/json",
        }

        response = requests.get(BASE_URL + request_path, headers=header)

        if response.status_code == 200:
            return response.json()
        else:
            return response.json()
    else:
        return {}


def get_chain_id_ok(token_name, chain):
    # chain = {"ETH":["ETH-ERC20", "ETHK-OKTC", "ETH-Arbitrum One", "ETH-zkSync Lite", "ETH-Optimism", "ETH-StarkNet", "ETH-zkSync Era"]}
    # chain = {"USDC": ["USDC-OKTC", "USDC-ERC20", "USDC-TRC20", "USDC-Polygon", "USDC-Avalanche C-Chain", "USDC-Arbitrum One (Bridged)", "USDC-Optimism", "USDC-Arbitrum One"]}
    # chain = {"USDT": ["USDT-OKTC", "USDT-ERC20", "USDT-TRC20", "USDT-Polygon", "USDT-Avalanche C-Chain", "USDT-Arbitrum One", "USDT-Optimism"]}
    chain_string_ok = {
        "ETH": {
            "eth": "ETH-ERC20",
            "ok": "ETHK-OKTC",
            "arb": "ETH-Arbitrum One",
            "zk1": "ETH-zkSync Lite",
            "op": "ETH-Optimism",
            "stark": "ETH-StarkNet",
            "zk2": "ETH-zkSync Era",
        },
        "USDC": {
            "ok": "USDC-OKTC",
            "eth": "USDC-ERC20",
            "tron": "USDC-TRC20",
            "matic": "USDC-Polygon",
            "avax": "USDC-Avalanche C-Chain",
            "arb": "USDC-Arbitrum One",
            "op": "USDC-Optimism",
        },
        "USDT": {
            "ok": "USDT-OKTC",
            "eth": "USDT-ERC20",
            "tron": "USDT-TRC20",
            "matic": "USDT-Polygon",
            "avax": "USDT-Avalanche C-Chain",
            "arb": "USDT-Arbitrum One",
            "op": "USDT-Optimism",
        },
    }
    if chain_string_ok.get(token_name):
        if chain_string_ok[token_name].get(chain):
            return chain_string_ok[token_name][chain]


def get_token_info(key_info, token_name, chain_id_ok):
    request_path = "/api/v5/asset/currencies"
    token_list = get_okx(key_info, request_path).get("data")
    for token_info in token_list:
        if token_info["ccy"] == token_name and token_info["chain"] == chain_id_ok:
            return token_info
            # {"canDep": true, "canInternal": true, "canWd": true, "ccy": "ETH", "chain": "ETH-ERC20", "depQuotaFixed": "", "depQuoteDailyLayer2": "", "logoLink": "https://static.coinall.ltd/cdn/oksupport/asset/currency/icon/eth20230419112854.png", "mainNet": true, "maxFee": "0.0016", "maxFeeForCtAddr": "0.0016", "maxWd": "4701", "minDep": "0.001", "minDepArrivalConfirm": "64", "minFee": "0.0008", "minFeeForCtAddr": "0.0008", "minWd": "0.01", "minWdUnlockConfirm": "96", "name": "Ethereum", "needTag": false, "usedDepQuotaFixed": "", "usedWdQuota": "0", "wdQuota": "10000000", "wdTickSz": "8"}


def withdrawal_onchain(
    key_info, token_name, amount, fee, to_addr, chain_id_ok, client_id=""
):
    # 初始化返回参数
    status = 0
    tx_hash = ""
    message = ""
    tx_fee = None
    value = None

    transaction_flag = True

    request_path = "/api/v5/asset/withdrawal"
    api_key = key_info.get("apikey")
    api_secret = key_info.get("secretkey")
    api_passphrase = key_info.get("passphrase")
    if api_key and api_secret and api_passphrase:
        # 检查转账金额是否符合要求
        token_info = get_token_info(key_info, token_name, chain_id_ok)
        if token_info:
            min_fee = token_info["minFee"]  # 普通地址最小提币手续费
            min_wd = token_info["minWd"]  # 币种单笔最小提币量
            can_wd = token_info["canWd"]  # 允许提币状态
            if not can_wd:
                transaction_flag = False
                message = f"交易所暂停提币{chain_id_ok}"

            if amount < float(min_wd):
                transaction_flag = False
                message = f"提币金额{amount}小于交易所最低限制{min_wd}"

            if fee < float(min_fee):
                transaction_flag = False
                message = f"交易所提币费用{min_fee}高于阈值{fee}"
        else:
            transaction_flag = False
            message = "交易所提币信息获取失败"

        if transaction_flag:
            # 创建交易签名
            timestamp = get_timestamp()
            method = "POST"
            body = {
                "ccy": token_name,
                "amt": str(amount),
                "dest": "4",
                "toAddr": to_addr,
                "fee": min_fee,
                "chain": chain_id_ok,
                "clientId": client_id,
            }
            signature = get_signature(timestamp, method, request_path, body, api_secret)
            header = {
                "OK-ACCESS-KEY": api_key,
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": api_passphrase,
                "Content-Type": "application/json",
            }
            response = requests.post(BASE_URL + request_path, headers=header, json=body)

            if response.status_code == 200:
                result = response.json()
                # 成功返回结果{'code': '0', 'data': [{'amt': '0.001', 'ccy': 'ETH', 'chain': 'ETH-Optimism', 'clientId': 'testFromMaurice', 'wdId': '98956880'}], 'msg': ''}
                # 含错误代码返回结果{'code': '58207', 'data': [], 'msg': 'Withdrawal address is not allowlisted for verification exemption'}
                if result.get("data"):
                    status = 1
                    wd_id = result["data"][0]["wdId"]
                    message = f"交易所提币{amount} {token_name}申请成功, 提币申请ID: {wd_id}"
                else:
                    status = -1
                    result_code = result.get("code")
                    result_message = result.get("msg")
                    message = f"code:{result_code} {result_message}"
            else:
                
                message = response.text
    else:
        message = "api信息获取失败"

    return {
        "status": status,
        "tx_hash": tx_hash,
        "tx_fee": tx_fee,
        "value": value,
        "message": message,
    }


if __name__ == "__main__":
    API_KEY = "2066b1c8-6bcf-4674-953b-516215f1583f"
    API_SECRET = "EB75D706DE7FB7123B9DD46CF55D40A5"
    API_PASSPHRASE = "gvg5frc_cbx5YPF8hdk"
    key_info = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "api_passphrase": API_PASSPHRASE,
    }
    # # get balance 资金账号余额
    # request_path = "/api/v5/asset/balances"
    # print(json.dumps(get_okx(key_info, request_path)))

    # get withdrawal history 最近提币记录
    request_path = "/api/v5/asset/withdrawal-history"
    # print(json.dumps(get_okx(key_info, request_path)))
    params = {"wdId": "98956880"}
    request_path = f"{request_path}?{urlencode(params)}"
    result = get_okx(key_info, request_path)
    # print(result)
    # print(get_okx(key_info, request_path)["data"][0])
    if result.get("data"):
        tx_record = result["data"][0]
        print(tx_record)
        print(
            tx_record["amt"],
            tx_record["fee"],
            tx_record["ccy"],
            tx_record["chain"],
            tx_record["to"],
            tx_record["txId"],
            tx_record["state"],  # 0：等待提币  1：提币中  2：提币成功
        )

    # get tokens 获取币种信息
    # chain = {"ETH":["ETH-ERC20", "ETHK-OKTC", "ETH-Arbitrum One", "ETH-zkSync Lite", "ETH-Optimism", "ETH-StarkNet", "ETH-zkSync Era"]}
    # chain = {"USDC": ["USDC-OKTC", "USDC-ERC20", "USDC-TRC20", "USDC-Polygon", "USDC-Avalanche C-Chain", "USDC-Arbitrum One (Bridged)", "USDC-Optimism", "USDC-Arbitrum One"]}
    # chain = {"USDT": ["USDT-OKTC", "USDT-ERC20", "USDT-TRC20", "USDT-Polygon", "USDT-Avalanche C-Chain", "USDT-Arbitrum One", "USDT-Optimism"]}
    # {"canDep": true, "canInternal": true, "canWd": true, "ccy": "ETH", "chain": "ETH-ERC20", "depQuotaFixed": "", "depQuoteDailyLayer2": "", "logoLink": "https://static.coinall.ltd/cdn/oksupport/asset/currency/icon/eth20230419112854.png", "mainNet": true, "maxFee": "0.00144", "maxFeeForCtAddr": "0.081816", "maxWd": "4730", "minDep": "0.001", "minDepArrivalConfirm": "64", "minFee": "0.00072", "minFeeForCtAddr": "0.040908", "minWd": "0.01", "minWdUnlockConfirm": "96", "name": "Ethereum", "needTag": false, "usedDepQuotaFixed": "", "usedWdQuota": "0", "wdQuota": "10000000", "wdTickSz": "8"}

    # request_path = "/api/v5/asset/currencies"
    # token_list = get_okx(key_info, request_path).get("data")
    # for token_info in token_list:
    #     if token_info["ccy"] == "ETH":
    #         print(json.dumps(token_info))

    # # 获取提现详细状态 限速：1次/2s
    # request_path = "/api/v5/asset/deposit-withdraw-status"
    # params = {"wdId": "92825673"}
    # request_path = f"{request_path}?{urlencode(params)}"
    # result = get_okx(key_info, request_path)
    # print(result)
    # # {'code': '0', 'data': [{'estCompleteTime': '', 'state': 'Withdrawal complete', 'txId': '0x9edd0fa99fcd751189735a51c4d166881c3091214e0dd459e5fcf33c68ac6fce', 'wdId': '92825673'}], 'msg': ''}
    # if result.get("data"):
    #     if result["data"][0].get("state") == "Withdrawal complete":
    #         print("Transaction ID:", result["data"][0].get("txId"))

    # # 获取充值详细状态 限速：1次/2s
    # request_path = "/api/v5/asset/deposit-withdraw-status"
    # params = {
    #     "txId": "0x79f4ed954fb88569e774c72bed79777fd820349f9085030fe9ee8f92e22f9212",
    #     "ccy": "ETH",
    #     "to": "0xc94f6e40920494bc96c30e509f546f148cca5550",
    #     "chain": "ETH-Arbitrum One",
    # }
    # request_path = f"{request_path}?{urlencode(params)}"
    # result = get_okx(key_info, request_path)
    # print(result)
    # # {'code': '0', 'data': [{'estCompleteTime': '', 'state': 'Withdrawal complete', 'txId': '0x9edd0fa99fcd751189735a51c4d166881c3091214e0dd459e5fcf33c68ac6fce', 'wdId': '92825673'}], 'msg': ''}
    # if result.get("data"):
    #     if result["data"][0].get("state") == "Deposit complete":
    #         print("Transaction ID:", result["data"][0].get("txId"))

    # # /api/v5/asset/deposit-history 最近充币记录
    # request_path = "/api/v5/asset/deposit-history"
    # params = {
    #     "txId": "0x79f4ed954fb88569e774c72bed79777fd820349f9085030fe9ee8f92e22f9212"
    # }
    # request_path = f"{request_path}?{urlencode(params)}"
    # result = get_okx(key_info, request_path)
    # print(result)
    # if result.get("data"):
    #     tx_record = result["data"][0]
    #     print(tx_record)
    #     print(
    #         tx_record["amt"],
    #         tx_record["ccy"],
    #         tx_record["chain"],
    #         tx_record["to"],
    #         tx_record["txId"],
    #     )

    # POST /api/v5/asset/withdrawal 提币
    # post body {"ccy":"ETH", "amt":0.02, "dest":"3"内部转账/"4"链上提币, "toAddr":"0x", "fee":"0.00072", "chain":"ETH-ERC20", "clientId":"32位用户自定义id"}
    # chain_id_ok = get_chain_id_ok("ETH", "op")
    # print(
    #     withdrawal_onchain(
    #         key_info,
    #         "ETH",
    #         0.001,
    #         0.0001,
    #         "0x40D2326FBa5C1a5ad044B1F2B2E0ca25285922Ff",
    #         chain_id_ok,
    #         "testFromMaurice",
    #     )
    # )
