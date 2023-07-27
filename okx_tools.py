import time
import hmac
import hashlib
import base64
import requests
import json
from datetime import datetime
from urllib.parse import urlencode


# 配置参数
BASE_URL = "https://www.okex.com"


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


def get_okx(request_path, key_info):
    api_key = key_info.get("api_key")
    api_secret = key_info.get("api_secret")
    api_passphrase = key_info.get("api_passphrase")
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
    # print(json.dumps(get_okx(request_path, key_info)))

    # # get withdrawal history 最近提币记录
    # request_path = "/api/v5/asset/withdrawal-history"
    # # print(json.dumps(get_okx(request_path, key_info)))
    # print(get_okx(request_path, key_info)["data"][0])

    # get tokens 获取币种信息
    # chain = {"ETH":["ETH-ERC20", "ETHK-OKTC", "ETH-Arbitrum One", "ETH-zkSync Lite", "ETH-Optimism", "ETH-StarkNet", "ETH-zkSync Era"]}
    # chain = {"USDC": ["USDC-OKTC", "USDC-ERC20", "USDC-TRC20", "USDC-Polygon", "USDC-Avalanche C-Chain", "USDC-Arbitrum One (Bridged)", "USDC-Optimism", "USDC-Arbitrum One"]}
    # chain = {"USDT": ["USDT-OKTC", "USDT-ERC20", "USDT-TRC20", "USDT-Polygon", "USDT-Avalanche C-Chain", "USDT-Arbitrum One", "USDT-Optimism"]}
    # {"canDep": true, "canInternal": true, "canWd": true, "ccy": "ETH", "chain": "ETH-ERC20", "depQuotaFixed": "", "depQuoteDailyLayer2": "", "logoLink": "https://static.coinall.ltd/cdn/oksupport/asset/currency/icon/eth20230419112854.png", "mainNet": true, "maxFee": "0.00144", "maxFeeForCtAddr": "0.081816", "maxWd": "4730", "minDep": "0.001", "minDepArrivalConfirm": "64", "minFee": "0.00072", "minFeeForCtAddr": "0.040908", "minWd": "0.01", "minWdUnlockConfirm": "96", "name": "Ethereum", "needTag": false, "usedDepQuotaFixed": "", "usedWdQuota": "0", "wdQuota": "10000000", "wdTickSz": "8"}

    request_path = "/api/v5/asset/currencies"
    token_list = get_okx(request_path, key_info).get("data")
    for token_info in token_list:
        if token_info["ccy"] == "USDT":
            print(json.dumps(token_info))

    # # 获取提现详细状态 限速：1次/2s
    # request_path = "/api/v5/asset/deposit-withdraw-status"
    # params = {"wdId": "92825673"}
    # request_path = f"{request_path}?{urlencode(params)}"
    # result = get_okx(request_path, key_info)
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
    # result = get_okx(request_path, key_info)
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
    # result = get_okx(request_path, key_info)
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
