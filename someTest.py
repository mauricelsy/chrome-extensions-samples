tx_data = "0x1249c58b"


import requests

url = "https://opt-mainnet.g.alchemy.com/v2/RqdoaptHJ8csL9paME4xOVtV_RLbq9kI"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "eth_estimateGas",
    "params": [
        {
            "from": "0xbc6cb5094314b1996211b64d45ea14e77dbe05ec",
            "to": "0x101010101716d0e465906f2d6f7e6565a9ee372b",
            # "gas": "0x00",
            # "gasPrice": "0x09184e72a000",
            "value": "0x0",
            "data": tx_data,
        },
        "finalized",
    ],
}
headers = {"accept": "application/json", "content-type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(response.text)


# def count_bytes(tx_data):
#     zero_bytes = 0
#     non_zero_bytes = 0

#     # Assume tx_data is a hex string, e.g., "0x1234abcd..."
#     for i in range(2, len(tx_data), 2):
#         byte = tx_data[i : i + 2]
#         if byte == "00":
#             zero_bytes += 1
#         else:
#             non_zero_bytes += 1

#     return zero_bytes, non_zero_bytes


# zero_bytes, non_zero_bytes = count_bytes(tx_data)
# tx_data_gas = zero_bytes * 4 + non_zero_bytes * 16
# l1_gas_price = 16.738175424 * 1e9
# fixed_overhead = 188
# dynamic_overhead = 0.684
# l1_data_fee = l1_gas_price * (tx_data_gas + fixed_overhead) * dynamic_overhead
# print(l1_data_fee / 1e18)
