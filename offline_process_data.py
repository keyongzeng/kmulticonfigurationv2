import proceess_data

list_name = input("请输入待处理目录：").strip()
if "log" not in list_name:
    list_name = "log/" + list_name
proceess_data.process_data(list_name)