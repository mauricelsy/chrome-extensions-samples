from rabbithole_tools import *
import time
from task import *
from datetime import datetime

from eth_account.messages import defunct_hash_message

wallet_address = input("please input wallet address: ")
wallet_address = Web3.to_checksum_address(wallet_address)

session = requests.Session()
signin_nonce = rabbithole_getSigninNonce(session)
if signin_nonce:
    time.sleep(get_random_number(1, 3))
    current_time = datetime.utcnow()
    # timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # 获取毫秒数值
    milliseconds = current_time.microsecond // 1000
    # 格式化时间字符串，手动添加毫秒部分
    timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S") + f".{milliseconds:03d}Z"

    chain = "eth"
    web3 = get_web3(chain)
    chain_id = web3.eth.chain_id
    private_key = get_pkey(wallet_address)
    challenge_string = "Sign in With Ethereum."

    message = f"rabbithole.gg wants you to sign in with your Ethereum account:\n{wallet_address}\n\n{challenge_string}\n\nURI: https://rabbithole.gg\nVersion: 1\nChain ID: {chain_id}\nNonce: {signin_nonce}\nIssued At: {timestamp}"
    # message = "rabbithole.gg wants you to sign in with your Ethereum account:\n0x2732f76F5154080c2f8Ad3b029443ce49931cd87\n\nSign in With Ethereum.\n\nURI: https://rabbithole.gg\nVersion: 1\nChain ID: 42161\nNonce: yFqA24cEEsKjTNxHz\nIssued At: 2023-07-11T17:34:16.083Z"
    # "signature":"0x2fb6cae26f6cb301ab9cd30b6ff54574af65a8a6bd39b1a754f50af97ffdf9d021ab600877de8f4c5c377d0f7ecc56a5575ddf56e1b43f15c55f7111b7f931131b"
    # "message":"rabbithole.gg wants you to sign in with your Ethereum account:\n0x2ceE1E96942cE9C888C5A3B7F1CB4570257C0a2F\n\nSign in With Ethereum.\n\nURI: https://rabbithole.gg\nVersion: 1\nChain ID: 1\nNonce: 34rAgjKHGKyodHqim\nIssued At: 2023-07-12T17:20:59.811Z"
    # message = "rabbithole.gg wants you to sign in with your Ethereum account:\n0x2ceE1E96942cE9C888C5A3B7F1CB4570257C0a2F\n\nSign in With Ethereum.\n\nURI: https://rabbithole.gg\nVersion: 1\nChain ID: 1\nNonce: 34rAgjKHGKyodHqim\nIssued At: 2023-07-12T17:20:59.811Z"

    # 生成签名
    # message_hash = Web3.keccak(text=message).hex()

    # 转换消息为字节数组
    message_bytes = message.encode("utf-8")

    # 生成消息哈希
    message_hash = defunct_hash_message(message_bytes)

    signed_message = web3.eth.account.signHash(message_hash, private_key=private_key)
    # 获取签名结果
    signature = signed_message.signature.hex()
    print(str(signature))
    print(message)
    input("press any key to continue...")

    # 将签名结果发送给Web3网站进行验证
    # 在此处编写发送签名的代码，与具体的Web3网站进行通信
    rabbithole_signin(str(signature), message, session)

    # 验证签名
    recovered_address = web3.eth.account._recover_hash(
        message_hash, signature=signature
    )

    # 检查签名恢复的地址是否与用户的钱包地址匹配
    if recovered_address.lower() == wallet_address.lower():
        print("签名验证成功，用户身份已确认。")
    else:
        print("签名验证失败，用户身份未能确认。")

# 发起第一个请求，并保持会话
questId = "f7b6b464-b7ec-4b7d-8561-7fe71049d3f3"
# address = "0x40D2326FBa5C1a5ad044B1F2B2E0ca25285922Ff"
result = rabbithole_getQuestMintInfo(questId, wallet_address, session=session)
result = rabbithole_getSession(session)

# 关闭会话
session.close()
