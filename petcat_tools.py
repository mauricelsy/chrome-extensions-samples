import sys

sys.path.append("../toolbox")

import config_thread
import encryption

import json


def get_pkey(wallet_address):
    config = encryption.read_config_file(
        encryption.config_file_path, encryption.encryption_key, wallet_address
    )
    if config is not None:
        encrypted_private_key = config["encrypted_private_key"]
        private_key = encryption.decrypt_private_key(
            encrypted_private_key, encryption.encryption_key, config["iv"]
        )
        return private_key
    else:
        return None


def get_group_accounts(group_no):
    sheet_name = "Groups"
    worksheet_name = f"Group{group_no}"
    creds = "../gCloud/pet-cats-09f0e10784ea.json"

    thread = config_thread.ConfigThread(creds, "read", sheet_name, worksheet_name)
    thread.start()
    thread.join()
    return thread.result


def get_assignment(group_no, status="active"):
    sheet_name = "Missions"
    worksheet_name = "assignment"
    creds = "../gCloud/pet-cats-09f0e10784ea.json"

    thread = config_thread.ConfigThread(creds, "readln", sheet_name, worksheet_name)
    thread.start()
    thread.join()
    if thread.result:
        return {
            d["HashID"]: json.loads(d["Params"])
            for d in thread.result
            if d["HashID"]
            and d["Params"]
            and group_no == d["Group"]
            and status == d["Status"]
        }
    else:
        return {}


def get_cex_address(exchange):
    sheet_name = "Exchanges"
    worksheet_name = "deposit"
    creds = "../gCloud/pet-cats-09f0e10784ea.json"

    thread = config_thread.ConfigThread(creds, "readln", sheet_name, worksheet_name)
    thread.start()
    thread.join()
    if thread.result:
        return {
            d["wallet"]: d[exchange]
            for d in thread.result
            if "wallet" in d and exchange in d
        }
    else:
        return {}


# print(get_group_accounts(input("please input group no: ")))
