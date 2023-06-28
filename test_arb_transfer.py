from petcat_tools import *
from web3 import Web3

# 连接到Arbitrum网络
w3 = Web3(
    Web3.HTTPProvider(
        "https://arbitrum-mainnet.infura.io/v3/80b882a99dcd4bf8a14eb4ac2b541152"
    )
)

# 账户地址和私钥
account_address = "sender"
private_key = get_pkey(account_address)


# 接收方地址和转账金额
recipient_address = Web3.toChecksumAddress("receiver")
transfer_amount = Web3.toWei(0.01, "ether")

# 确认账户余额
account_balance = w3.eth.getBalance(account_address)

print(account_balance)
input("please confirm account balance...")

# 确认gas limit
gas_estimate = w3.eth.estimate_gas(
    {
        "from": account_address,
        "to": recipient_address,
        "value": transfer_amount,
    }
)
print(gas_estimate)
input("please confirm gas limit...")

amount = float(input("please input transfer amount..."))
transfer_amount = Web3.toWei(amount, "ether")

# 构造交易对象
transaction = {
    "to": recipient_address,
    "value": transfer_amount,
    "gas": gas_estimate,
    "gasPrice": w3.eth.gas_price,
    "nonce": w3.eth.getTransactionCount(account_address),
    "chainId": 42161,  # Arbitrum主网的chainId
}

# 签名交易
signed_transaction = w3.eth.account.signTransaction(transaction, private_key)

# 发送交易
transaction_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

# 等待交易确认
transaction_receipt = w3.eth.waitForTransactionReceipt(transaction_hash)

# 打印交易哈希和交易状态
print("Transaction Hash:", transaction_hash.hex())
print("Transaction Status:", transaction_receipt["status"])
