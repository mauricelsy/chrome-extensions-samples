from petcat_tools import *
from encryption import get_pkey
from task import *

from rabbithole_tools import *
from mintfun_tools import *

from eth_account.messages import defunct_hash_message


class jobClass:
    # mint.fun x zora bridge pass 获取merkle proof
    def mint_fun_zora_pass(self, params):
        wallet_address = params.get("wallet_address")
        merkle_root = params.get("merkle_root")

        # Function: depositTransaction(address _to, uint256 _value, uint64 _gasLimit, bool _isCreation, bytes _data)
        session = requests.Session()
        address_list = mintfun_zora_pass_getTree(merkle_root, session).get(
            "unhashedLeaves"
        )
        if wallet_address.lower() in address_list:
            proof = mintfun_zora_pass_getProof(
                merkle_root, wallet_address, session
            ).get("proof")
            if proof:
                proof_bytes = [bytes.fromhex(item[2:]) for item in proof]
                proof_bytes_tuple = (tuple(proof_bytes),)
                function_name = "mint(bytes32[])"
                _data_hexstring = make_calldata(
                    function_name, ["bytes32[]"], proof_bytes_tuple
                )
                _data = bytes.fromhex(_data_hexstring[2:])
                _isCreation = False
                _gasLimit = 222000
                _value = 0
                _to = "0x007777777e83977A6808F19782028b1677117690"
                # function_name = "depositTransaction(address,uint256,uint64,bool,bytes)"
                # params_type = ["address", "uint256", "uint64", "bool", "bytes"]
                # args = [_to, _value, _gasLimit, _isCreation, _data]
                # data = make_calldata(function_name, params_type, args)

                # print(args)
                # input(f"data - {data} press any key to continue...")

                # return {"args": args, "data": data}
                return {
                    "_to": _to,
                    "_value": _value,
                    "_gasLimit": _gasLimit,
                    "_isCreation": _isCreation,
                    "_data": _data,
                }
        return {}

    # RabbitHole Claim Rewards 前端获取交易参数
    def rh_claim_rewards(self, params):
        session = requests.Session()
        signin_nonce = rabbithole_getSigninNonce(session)
        if signin_nonce:
            time.sleep(get_random_number(1, 3))
            current_time = datetime.utcnow()
            # timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            # 获取毫秒数值
            milliseconds = current_time.microsecond // 1000
            # 格式化时间字符串，手动添加毫秒部分
            timestamp = (
                current_time.strftime("%Y-%m-%dT%H:%M:%S") + f".{milliseconds:03d}Z"
            )

            chain = params.get("chain")
            wallet_address = params.get("wallet_address")
            quest_id = params.get("quest_id")
            web3 = get_web3(chain)
            chain_id = web3.eth.chain_id
            private_key = get_pkey(wallet_address)
            challenge_string = "Sign in With Ethereum."

            message = f"rabbithole.gg wants you to sign in with your Ethereum account:\n{wallet_address}\n\n{challenge_string}\n\nURI: https://rabbithole.gg\nVersion: 1\nChain ID: {chain_id}\nNonce: {signin_nonce}\nIssued At: {timestamp}"
            # print(message)

            # 生成签名(经验证该方法失败)
            # message_hash = Web3.keccak(text=message).hex()

            # 转换消息为字节数组
            message_bytes = message.encode("utf-8")
            # 生成消息哈希
            message_hash = defunct_hash_message(message_bytes)

            signed_message = web3.eth.account.signHash(
                message_hash, private_key=private_key
            )
            # 获取签名结果
            signature = signed_message.signature.hex()
            # print(str(signature))

            # input("press any key to continue...")

            # 将签名结果发送给Web3网站进行验证
            # 在此处编写发送签名的代码，与具体的Web3网站进行通信
            rabbithole_signin(str(signature), message, session)

            if rabbithole_getSession(session):
                mint_info = rabbithole_getQuestMintInfo(
                    quest_id, wallet_address, session=session
                )
                if (
                    mint_info
                    and mint_info.get("hash")
                    and mint_info.get("signature")
                    and mint_info.get("fee")
                ):
                    mintRHR_hash = bytes.fromhex(mint_info["hash"][2:])
                    mintRHR_signature = bytes.fromhex(mint_info["signature"][2:])
                    mintRHR_value = int(mint_info.get("fee"))

                    return {
                        "hash": mintRHR_hash,
                        "signature": mintRHR_signature,
                        "value_wei": mintRHR_value,
                    }
        return {}

    # Across Protocol 前端获取交易参数方法
    def across_fee(self, params):
        url = "https://across.to/api/suggested-fees"

        try:
            # deposit(address recipient,address originToken,uint256 amount,uint256 destinationChainId,int64 relayerFeePct,uint32 quoteTimestamp,bytes message,uint256 maxCount)
            recipient = params["from"]
            originToken = get_token_address(params.get("token"), "arb")
            amount = Web3.to_wei(params.get("amount"), "ether")  # 金额值要根据token类型判断
            originChainId = get_chain_info(params.get("chain"))[0].get("ID")
            destinationChainId = get_chain_info(params.get("to_chain"))[0].get("ID")

            request_params = {
                "token": originToken,
                "destinationChainId": destinationChainId,
                "originChainId": originChainId,
                "amount": amount,
                "skipAmountLimit": "true",
            }
            response_text = send_request(url, method="GET", data=request_params)
            response_json = json.loads(response_text)
            relayerFeePct = int(response_json["relayFeePct"])
            quoteTimestamp = int(response_json["timestamp"])
            message = b""
            maxCount = HUGE_NUMBER
            # 返回合约函数参数
            args = (
                recipient,
                originToken,
                amount,
                destinationChainId,
                relayerFeePct,
                quoteTimestamp,
                message,
                maxCount,
            )

            params_type = [
                "address",
                "address",
                "uint256",
                "uint256",
                "int64",
                "uint32",
                "bytes",
                "uint256",
            ]
            params_value = [
                recipient,
                originToken,
                amount,
                destinationChainId,
                relayerFeePct,
                quoteTimestamp,
                message,
                maxCount,
            ]
            data = make_calldata(
                "deposit(address,address,uint256,uint256,int64,uint32,bytes,uint256)",
                params_type,
                params_value,
            )
            input(f"data - {data} press any key to continue...")

            return {"args": args, "data": data}

        except Exception as e:
            print(str(e))
            return {}


# # 测试代码
# params = {
#     "from": "0x2ceE1E96942cE9C888C5A3B7F1CB4570257C0a2F",
#     "chain": "arb",
#     "to_chain": "op",
#     "request": "across_fee",
#     "token": "WETH",
#     "amount": (0.001, 0.0015),
#     "function_name": "deposit",
#     "contract_address": "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a",
#     "abi": True,
# }
# if isinstance(params["amount"], tuple):
#     params.update({"amount": get_random_number(*params["amount"])})
# print(params)
# print(across_fee(params))
