from web3 import Web3
from task import *

params = {
    "gas": 20,
    "chain": "op",
    "request": "rh_claim_rewards",
    "quest_id": "f7b6b464-b7ec-4b7d-8561-7fe71049d3f3",
    "api": "function_write",
    "function_name": "claimRewards",
    "contract_address": "0x52629961f71c1c2564c5aa22372cb1b9fa9eba3e",
    "abi": True,
    "params_name": ["quest_id", "hash", "signature"],
    "params_type": ["string", "bytes32", "bytes"],
    "wallet_address": "0x40D2326FBa5C1a5ad044B1F2B2E0ca25285922Ff",
    "hash": "0xd6f87744bb22ae288f7fa48cedde4c3e0a079975b74373e157603d9c067a81db",
    "signature": "0xd2dbc5b1b358989eb72fc0603971dc772525ceeff236333290aa7bc6203757463ec1f60c6db515ca2ba1044e000c7049bba7d9cd1f356026f28e9131abcc591f1b",
    "args": [
        "f7b6b464-b7ec-4b7d-8561-7fe71049d3f3",
        "0xd6f87744bb22ae288f7fa48cedde4c3e0a079975b74373e157603d9c067a81db",
        "0xd2dbc5b1b358989eb72fc0603971dc772525ceeff236333290aa7bc6203757463ec1f60c6db515ca2ba1044e000c7049bba7d9cd1f356026f28e9131abcc591f1b",
    ],
}
wallet_address = params["wallet_address"]
chain = params["chain"]
function_name = params["function_name"]
args = params["args"]
web3 = get_web3(chain)
args[1] = bytes.fromhex(args[1][2:])
args[2] = bytes.fromhex(args[2][2:])
print(args)

contract_address = web3.to_checksum_address(params["contract_address"])
contract_address = web3.to_checksum_address(
    "0x53431b13e9d353676658e6dA81186301fee31526"
)
contract_abi = get_abi_gs(contract_address, params["chain"])
if not contract_abi:
    print("no abi got for contract", contract_address)
else:
    contract_instance = web3.eth.contract(address=contract_address, abi=contract_abi)
    private_key = get_pkey(wallet_address)

    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(wallet_address)
    gas_price = web3.eth.gas_price
    base_fee = get_base_fee(chain)

    transaction_params = {
        "from": wallet_address,
        # "to": contract_address,
        "gasPrice": base_fee
        * 2,  # gasPrice 和 (maxFeePerGas or maxPriorityFeePerGas) 不可同时指定
        "nonce": nonce,
        "chainId": chain_id,
        # "maxFeePerGas": base_fee * 2,
        # gas估算必须参数（可能默认值低于当前网络基础费 max fee per gas less than block base fee）
    }
    transaction = contract_instance.functions[function_name](*args).build_transaction(
        transaction_params
    )
    print("Transaction Data:", transaction["data"])
    input("press any key to continue...")
