from petcat_tools import *

from web3 import Web3
from web3.middleware import geth_poa_middleware


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


# 转账交易
def transfer(chain, amount_eth, sender, receiver, balance_limit):
    transaction_flag = True
    status = "0"
    message = ""

    try:
        web3 = get_web3(chain)
        sender_address = Web3.toChecksumAddress(sender)
        recipient_address = Web3.toChecksumAddress(receiver)
        private_key = get_pkey(sender_address)

        # 转账金额（以 wei 为单位）
        amount_wei = web3.toWei(amount_eth, "ether")
        balance_limit_wei = web3.toWei(balance_limit, "ether")

        # 确认账户余额
        account_balance = web3.eth.getBalance(sender_address)
        print(sender_address, round(account_balance / 1e18, 4), "ETH")
        input("please confirm account balance...")

        # 确认转账金额
        amount_input = input(f"transfer amount: {amount_eth} ETH, input new amount...")
        amount_wei = Web3.toWei(
            float(amount_input) if amount_input.strip() else amount_eth, "ether"
        )

        # 检查交易后账户余额是否达到阈值
        if balance_limit_wei > account_balance - amount_wei:
            transaction_flag = False
            message = "Low balance!"

        # 确认gas limit
        gas_estimate = web3.eth.estimate_gas(
            {
                "from": sender_address,
                "to": recipient_address,
                "value": amount_wei,
            }
        )

        # 检查账户余额是否足够支付转账金额和gas费用
        balance_after = account_balance - (
            amount_wei + web3.eth.gas_price * gas_estimate
        )
        if balance_after >= 0:
            print("new balance estimate:", round(balance_after / 1e18, 4), "ETH")
        else:
            transaction_flag = False
            message = "Insufficient balance!"

        user_confirm = input(
            f"ready to transfer {round(amount_wei/1e18,4)} ETH from {sender_address} to {recipient_address} ...y/n"
        )
        if user_confirm == "n":
            transaction_flag = False
            message = "User aborted!!"

        if transaction_flag:
            # 构造交易对象
            transaction = {
                "to": recipient_address,
                "value": amount_wei,
                "gas": gas_estimate,
                "gasPrice": web3.eth.gas_price,
                "nonce": web3.eth.getTransactionCount(sender_address),
                # "chainId": 42161,  # Arbitrum主网的chainId
            }

            # 签名交易
            signed_transaction = web3.eth.account.signTransaction(
                transaction, private_key
            )

            # 发送交易
            transaction_hash = web3.eth.sendRawTransaction(
                signed_transaction.rawTransaction
            )

            # 等待交易确认
            transaction_receipt = web3.eth.waitForTransactionReceipt(transaction_hash)

            status = transaction_receipt["status"]
            message = transaction_hash.hex()

    except Exception as e:
        message = str(e)

    return {"status": status, "message": message}
