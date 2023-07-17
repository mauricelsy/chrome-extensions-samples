import requests


def rabbithole_getQuestMintInfo(questId, address, session=None):
    url = "https://api.rabbithole.gg/quest/mint-receipt"
    data = {"questId": questId, "address": address}
    if session:
        response = session.post(url, json=data)
    else:
        response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        # print("rabbithole_getQuestMintInfo", result)
        return result
    else:
        print("rabbithole_getQuestMintInfo - 请求出错，状态码:", response.status_code)
        print(response.text)
        return {}


def rabbithole_getQuestInfo(questId, address, item=None, session=None):
    # item包含返回quest的信息项如id, name, questEnd, questStart, tasks[], contractAddress(任务合约用于申领代币), status(用户任务状态), rewards(奖励信息), questAddress, questFactoryAddress
    # status: active(可以任务) redeemable(可以mint凭证) claimable(可以申领代币奖励)
    url = f"https://api.rabbithole.gg/v1.2/quest/{address}/{questId}"
    if session:
        response = session.get(url)
    else:
        response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if item:
            info = result[item]
            print(f"{address} on Quest {questId} {item}: {info}")
        else:
            info = result
        return info
    else:
        print("rabbithole_getQuestInfo - 请求出错，状态码:", response.status_code)
        return None


def rabbithole_getSigninNonce(session):
    url = "https://api.rabbithole.gg/auth/nonce"
    response = session.get(url)
    if response.status_code == 200:
        result = response.text
        # print("rabbithole_getSigninNonce", result)
        return result
    else:
        print("rabbithole_getSigninNonce - 请求出错，状态码:", response.status_code)
        print(response.text)
        return ""


def rabbithole_signin(signature, message, session):
    url = f"https://api.rabbithole.gg/auth/login"
    # {
    #     "signature": "0x06076e3be5ab7beef51488441421c191b467b227f7694d88c74d210c492e78c768aae04faf2fc1277bfd839248328df5a029cb065dd15148924845036c6900d81b",
    #     "message": "rabbithole.gg wants you to sign in with your Ethereum account:\n0x2732f76F5154080c2f8Ad3b029443ce49931cd87\n\nSign in With Ethereum.\n\nURI: https://rabbithole.gg\nVersion: 1\nChain ID: 42161\nNonce: yFqA24cEEsKjTNxHz\nIssued At: 2023-07-11T17:34:16.083Z",
    # }
    data = {"signature": signature, "message": message}
    # print(data)
    response = session.post(url, json=data)
    if response.status_code == 200:
        result = response.text
        print("rabbithole signin:", result)
        return result
    else:
        print("rabbithole_signin - 请求出错，状态码:", response.status_code)
        print(response.text)
        return ""


def rabbithole_getSession(session):
    url = "https://api.rabbithole.gg/auth/session"
    response = session.get(url)
    if response.status_code == 200:
        result = response.text
        # print("rabbithole session info:", result)
        return result
    else:
        print("rabbithole_getSession - 请求出错，状态码:", response.status_code)
        print(response.text)
        return ""


# some test code
# quest_id = "f7b6b464-b7ec-4b7d-8561-7fe71049d3f3"
# address = "0x40D2326FBa5C1a5ad044B1F2B2E0ca25285922Ff"
# rabbithole_getQuestInfo(quest_id, address)
# rabbithole_getQuestMintInfo(quest_id, address)

# 创建一个 Session 对象
# session = requests.Session()

# 发起第一个请求，并保持会话
# questId = "f7b6b464-b7ec-4b7d-8561-7fe71049d3f3"
# address = "0x40D2326FBa5C1a5ad044B1F2B2E0ca25285922Ff"
# result = rabbithole_getQuestInfo(questId, address, session=session)
# print("rabbithole_getQuestInfo", result)
# result = rabbithole_getQuestMintInfo(questId, address, session=session)
# print("rabbithole_getQuestMintInfo", result)
# result = rabbithole_getSession(session)
# print("rabbithole_getSession", result)

# # 关闭会话
# session.close()
