import requests


# https://lanyard.org/api/v1/tree?root=0x7c003e2bdc9c11ff6142eb72f32e7e4dfbf4c235486f3c2eed6d16f30c90a535
def mintfun_zora_pass_getTree(merkle_root, session=None):
    url = f"https://lanyard.org/api/v1/tree?root={merkle_root}"
    if session:
        response = session.get(url)
    else:
        response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print("mintfun_zora_pass_getTree - 请求出错，状态码:", response.status_code)
        print(response.text)
        return {}


# merkle_root = "0x7c003e2bdc9c11ff6142eb72f32e7e4dfbf4c235486f3c2eed6d16f30c90a535"
# address = input("please input address: ")
# address_list = mintfun_zora_pass_getTree(merkle_root).get("unhashedLeaves")
# print(address.lower() in address_list)


# https://lanyard.org/api/v1/proof?root=0x7c003e2bdc9c11ff6142eb72f32e7e4dfbf4c235486f3c2eed6d16f30c90a535&address=0x2732f76F5154080c2f8Ad3b029443ce49931cd87
def mintfun_zora_pass_getProof(merkle_root, address, session=None):
    url = f"https://lanyard.org/api/v1/proof?root={merkle_root}&address={address}"
    if session:
        response = session.get(url)
    else:
        response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print("mintfun_zora_pass_getProof - 请求出错，状态码:", response.status_code)
        print(response.text)
        return {}


# merkle_root = "0x7c003e2bdc9c11ff6142eb72f32e7e4dfbf4c235486f3c2eed6d16f30c90a535"
# address = input("please input address: ")
# print(mintfun_zora_pass_getProof(merkle_root, address).get("proof"))
