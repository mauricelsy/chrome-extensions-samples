from petcat_tools import *


def read_and_write_json_with_lock(
    file_path, data_to_write, flag, max_retries, retry_interval
):
    # 检查文件是否存在
    file_exists = True
    try:
        with open(file_path, "r") as file:
            pass
    except FileNotFoundError:
        file_exists = False

    # 文件不存在初始化文件（直接写入当前数据或者不处理）
    if not file_exists:
        if flag:
            with open(file_path, "w") as file:
                json.dump(data_to_write, file, indent=4)
        return True

    # 读取文件内容并加锁
    with open(file_path, "a+") as file:
        portalocker.lock(file, portalocker.LOCK_SH)
        existing_data = json.load(file)

        # 在写入文件时获取锁
        file.seek(0)
        portalocker.lock(file, portalocker.LOCK_NB)

        # 修改数据
        if flag:
            existing_data.update(data_to_write)
        else:
            for key in data_to_write:
                existing_data.pop(key, None)

        # 写入更新后的数据
        file.truncate(0)
        json.dump(existing_data, file, indent=4)

    return True


print("执行任务 - 交易日志归档...")
journal_file = "journal.json"
try:
    with open(journal_file, "r") as f:
        tx_journal_local = json.load(f)
except:
    print("no local journal file found!")
    tx_journal_local = {}

# 写入谷歌表格
tx_journal_gs(tx_journal_local)
print(f"写入gs交易日志记录 {len(tx_journal_local)} 条")
# 删除本地记录（避免重复写入）
if read_and_write_json_with_lock(journal_file, tx_journal_local, 0, 5, 1):
    print("更新本地交易日志记录成功...")
else:
    print("更新本地交易日志记录失败...")
