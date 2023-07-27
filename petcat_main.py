from task import *
from job import *
import time
import copy

job_request = jobClass()
group_no = int(input("please input group number: "))

try:
    while True:
        time.sleep(5)

        print(f"pet cat robot for group {group_no} sweatslaving...")
        # 任务状态文件
        status_file = "status.json"
        try:
            with open(status_file, "r") as f:
                account_status_local = json.load(f)
        except:
            print("no account status file found!")
            account_status_local = {}

        # 任务日志文件
        journal_file = "journal.json"
        try:
            with open(journal_file, "r") as f:
                tx_journal_local = json.load(f)
        except:
            print("no local journal file found!")
            tx_journal_local = {}

        # 读取地址列表
        if group_no == -1:
            account_list = {input("please input wallet address: "): ""}
        else:
            account_list = get_group_accounts(group_no)
            print(f"get {len(account_list)} accounts from group {group_no}...")
            time.sleep(2)

        # 读取任务列表
        # {
        #     "0c44688f99ae361e322a1983b1c5a52678498112f735afadde4153eb3a05f1b7": {
        #         "mission": "0c8a06149e5ded96d38344661e131c7ff35a9841aa62e10e7d605caae1ff418b",
        #         "name": "DepositToCEX",
        #         "params": {"gas": 16},
        #         "status": "active",
        #         "job": {},
        #     },
        # }

        # 读取任务状态参数
        assignment_list = get_assignment(
            group_no, ("active", "processing", "paused", "expired")
        )
        print(f"get {len(assignment_list)} assignments for group {group_no}...")

        # 读取Task列表（task函数执行参数）
        task_list = get_task()

        # 读取Job列表
        for assignment_info in assignment_list.values():
            job_list = get_job(assignment_info["mission"])
            print(
                f'get {len(job_list)} jobs for mission {assignment_info["mission"]}...'
            )
            assignment_info.update({"job": copy.deepcopy(job_list)})

        # 初始化任务执行状态表
        for account_id in account_list:
            # 此处添加判断是否已经存在任务状态
            # 如果不存在该任务，直接更新
            account_list[account_id] = copy.deepcopy(assignment_list)

            # 初始化任务状态
            for assignment_id in assignment_list:
                account_assignment = account_list[account_id][assignment_id]
                # 变更新加任务状态（已读取）
                if account_assignment["status"] == "active":
                    account_assignment.update({"status": "processing"})
                mission_status_check = 1
                # 初始化job状态(0,1,-1)
                for job_id, job_info in account_assignment["job"].items():
                    # 检查当前账号当前任务是否存在job状态（例外判断考虑可能修改设置出现新job）
                    try:
                        job_status_update = account_status_local[account_id][
                            assignment_id
                        ]["job"][job_id]["status"]
                    except:
                        job_status_update = 0
                    job_info.update({"status": job_status_update})
                    mission_status_check *= job_status_update
                # 任务完成检查参数与逐个job状态相乘大于零（没有0和-1状态）设置当前任务完成状态
                if mission_status_check > 0:
                    account_assignment.update({"status": "completed"})
                else:
                    # 未完成检查超时
                    if (
                        account_assignment["deadline"]
                        and time.time() > account_assignment["deadline"]
                    ):
                        account_assignment.update({"status": "expired"})

        # 修改谷歌日志记录 - 添加JobID

        # 更新任务状态文件
        with open(status_file, "w") as f:
            json.dump(account_list, f)
        # 更新谷歌表格（监控任务状态）
        for assignment_item in assignment_list:
            print(assignment_item)
            update_assignment(assignment_item, account_list)

        # 任务循环
        # 未来考虑任务动态更新机制（条件，状态等）特别注意线程安全（循环变量）
        for assignment_id, mission_info in assignment_list.items():
            # 获取任务信息
            mission_id = mission_info.get("mission")
            mission_name = mission_info.get("name")
            mission_params = mission_info.get("params")
            mission_status = mission_info.get("status")
            # 获取任务对应的task清单（未排序）
            mission_jobs = mission_info.get("job")

            print("开始任务", mission_status, mission_name, mission_params)
            time.sleep(1)

            # 判断任务状态
            if mission_status in ("active", "processing"):
                # 获取执行地址清单（排序）
                account_list_shuffled = get_shuffled(account_list)

                # 进入执行地址循环
                for account_address in account_list_shuffled:
                    # 判断地址是否在当前任务列表中
                    if account_list[account_address].get(assignment_id):
                        # 当前地址任务信息
                        account_mission = account_list[account_address][assignment_id]
                        # 判断当前地址任务状态
                        if account_mission["status"] in (
                            "active",
                            "processing",
                        ):
                            # 判断超时状态
                            if (
                                account_mission["deadline"]
                                and time.time() > account_mission["deadline"]
                            ):
                                account_mission.update({"status": "expired"})
                                print(
                                    f"{string_tools.mask_address(account_address)} - {mission_name} - 当前任务已超时，暂停执行..."
                                )
                                continue

                            # 获取job执行顺序
                            job_list_ordered = get_job_ordered(mission_jobs)
                            # 进入任务执行循环
                            for job_id in job_list_ordered:
                                # 判断job状态（注意这里需要添加关于失败后重复执行的判断，避免过多尝试）
                                # 已完成
                                if account_mission["job"][job_id]["status"] == 1:
                                    continue

                                # 异常状况(暂定出现失败交易)
                                if account_mission["job"][job_id]["status"] == -1:
                                    break

                                # 未完成
                                if account_mission["job"][job_id]["status"] == 0:
                                    # 开始执行job
                                    # 合并mission+job参数（相同参数job覆盖mission）
                                    task_params = {
                                        **mission_params,
                                        **mission_jobs[job_id]["params"],
                                    }
                                    task_name = mission_jobs[job_id]["task"]
                                    # 合并task参数
                                    if task_list.get(task_name):
                                        task_params.update(task_list[task_name])
                                    # 屏幕提示交易参数（来自配置信息）
                                    print(
                                        f"{string_tools.mask_address(account_address)} - {mission_name} - {task_name} - {task_params}"
                                    )
                                    # 设定执行gas
                                    gas_price_threshold = (
                                        task_params["gas"]
                                        if task_params.get("gas")
                                        else 10
                                    )
                                    if gas_price_threshold:
                                        gas_price_threshold = Web3.to_wei(
                                            gas_price_threshold, "gwei"
                                        )

                                    sleep_loop = 0
                                    while (
                                        not (
                                            low_gas := gas_below_threshold(
                                                gas_price_threshold
                                            )
                                        )
                                        and sleep_loop < 5
                                    ):
                                        print(
                                            f"{string_tools.mask_address(account_address)} - {mission_name} - {task_name}"
                                        )
                                        print("超过阈值，等待中...")
                                        time.sleep(5)  # 每5秒检查一次 gas price
                                        sleep_loop += 1

                                    if low_gas:
                                        print("低于阈值，执行交易")
                                    else:
                                        # 等待超时，终止当前任务
                                        break

                                    # 当前地址加入参数
                                    task_params.update(
                                        {"wallet_address": account_address}
                                    )
                                    # 是否有额外参数请求过程
                                    if task_params.get("request"):
                                        job_request = jobClass()
                                        method_name = task_params["request"]
                                        request_method = getattr(
                                            job_request, method_name
                                        )
                                        extra_params_result = request_method(
                                            task_params
                                        )
                                        task_params.update(extra_params_result)

                                    task_result = task_do(account_address, task_params)

                                    # 更新任务执行状态表
                                    account_mission["job"][job_id][
                                        "status"
                                    ] = task_result["status"]
                                    # 更新任务状态文件
                                    with open(status_file, "w") as f:
                                        json.dump(account_list, f)

                                    # 更新任务执行日志表
                                    tx_journal = get_tx_journal(
                                        account_address,
                                        group_no,
                                        f"{mission_name} - {task_name}",
                                        task_result,
                                    )
                                    tx_journal_local.update(tx_journal)

                                    # 更新任务日志文件
                                    with open(journal_file, "w") as f:
                                        json.dump(tx_journal_local, f)

                                    # 判断执行结果，如果不成功则中止当前任务执行循环
                                    if task_result != 1:
                                        break

                            # 当前账号完成一次任务执行循环后检查mission状态
                            mission_status_check = True
                            for job_info in account_mission["job"].values():
                                if job_info["status"] != 1:
                                    mission_status_check = False
                                    break
                            if mission_status_check:
                                print(
                                    f"{string_tools.mask_address(account_address)} - {mission_name} completed!"
                                )
                                account_mission["status"] = "completed"
                                # 更新任务状态文件
                                with open(status_file, "w") as f:
                                    json.dump(account_list, f)
                                # 更新谷歌任务监控表
                                update_assignment(assignment_id, account_list)

                    # 交易日志写入谷歌表格
                    try:
                        if tx_journal_local:
                            if tx_journal_gs(tx_journal_local):
                                print(f"写入gs交易日志记录 {len(tx_journal_local)} 条")
                                # 删除本地日志（避免重复写入）
                                tx_journal_local = {}
                                # 更新任务日志文件
                                with open(journal_file, "w") as f:
                                    json.dump(tx_journal_local, f)
                    except:
                        print("交易日志写表失败...")

except KeyboardInterrupt:
    print("用户暂停！")
