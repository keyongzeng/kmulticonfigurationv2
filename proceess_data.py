import re
import os
import xlrd
import time

def process_data(dir_name):
    timetemp = time.strftime(" %Y%m%d %H%M%S")
    data = xlrd.open_workbook("设备信息库.xlsx")
    pattern_list = data.sheet_by_name("数据处理正则表达式")
    input_re_list = []
    for row in range(1,1000):
        try:
            pattern = pattern_list.cell(row,1).value
            description = pattern_list.cell(row,0).value
            flag =  pattern_list.cell(row,2).value
            if pattern == "EOF":
                break
            input_re_list.append((description,pattern,flag))
        except IndexError:
            break

    #list_name = input("请输入待处理目录：").strip()

    list = os.listdir(dir_name)
    new_txt = dir_name + "/合并文件" + timetemp +".txt"
    #循环每一份文件
    for i in range(0,len(list)):
        path = os.path.join(dir_name,list[i])
        #path = "/".join(["log/ceshi",list[i]])
        path = os.path.normpath(path)
        if os.path.isfile(path):
            if "合并文件" in path:
                continue
            #打开文件
            file_object = open(path)
            try:
                all_the_test = file_object.readlines()

                with open(new_txt,"a") as f:
                    f.write("\n=========================%s======================\n" % path)
                    print("\n=========================%s======================" % path)
                    print("设备IP",end="\t")
                    f.write("设备IP" + "\t")
                    for des in input_re_list:
                        descri = des[0]
                        print(descri, end="\t")
                        f.write(descri+"\t")
                    ip = ""
                    ip = re.findall(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}",path)
                    #开始匹配数据
                    for line in all_the_test:
                        for input_re in input_re_list:
                            match = re.findall(input_re[1], line)
                            if match:
                                if input_re[2].lower() == "first":
                                    print()
                                    print(ip, end="\t")
                                    print(match, end="\t")
                                    f.write("\n")
                                    f.write(str(ip)+"\t")
                                    f.write(str(match) + "\t")
                                    continue
                                else:
                                    print(match,end="\t")
                                    f.write(str(match) + "\t")
                                    continue
                                #f.write(input_re[0])
                                #f.write(str(match) + "\n")
            finally:
                file_object.close()

