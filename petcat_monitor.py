from petcat_tools import *
import time

import threading


# 定义任务函数
def tx_journal2gs(exit_event, interval):
    while not exit_event.is_set():
        try:
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

        except Exception as e:
            print("交易日志归档 异常:", e)

        time.sleep(interval)


def task2(exit_event):
    while not exit_event.is_set():
        try:
            print("执行任务2...")
        except Exception as e:
            print("任务执行出现异常:", e)

        time.sleep(10)  # 任务每10秒执行一次


if __name__ == "__main__":
    # 创建线程
    exit_event1 = threading.Event()
    thread1 = threading.Thread(
        target=tx_journal2gs,
        args=(
            exit_event1,
            5,
        ),
    )

    # 启动线程
    thread1.start()

    try:
        while True:
            # 主线程持续运行，等待键盘中断信号
            time.sleep(1)
    except KeyboardInterrupt:
        # 当捕获到 Ctrl-C 时，设置退出事件并终止程序
        exit_event1.set()
        thread1.join()
