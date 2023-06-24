import sys
sys.path.append("../toolbox")

import config_thread


def get_group_accounts(group_no):
    sheet_name = "Groups"
    worksheet_name = f"Group{group_no}"
    creds = "../gCloud/pet-cats-09f0e10784ea.json"

    thread = config_thread.ConfigThread(creds, "read", sheet_name, worksheet_name)
    thread.start()
    thread.join()
    return thread.result


# print(get_group_accounts(input("please input group no: ")))
