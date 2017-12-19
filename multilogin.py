import paramiko
import socket
import re
import time
import telnetlib
import threading
import xlrd
import os
import proceess_data

class LoginUseSSH(object):
    #初始化
    def __init__(self,hostip,portnum,username,userpassword,endStrList=r"[<.+>,\[.+\],More]",timeout=0.5,trytimes=3):
        self.hostip = hostip
        self.portnum = int(portnum)
        self.username = username
        self.userpassword = userpassword
        self.endStrList = endStrList
        self.timeout = timeout    #执行命令后等待时间，命令较长时，可以考虑设置长一点
        self.trytimes = trytimes  #暂时不用

    #尝试连接
    def Connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.hostip, self.portnum))
            self.transportObj = paramiko.Transport(self.sock)
            self.transportObj.connect(username=self.username, password=self.userpassword)
            self.channel = self.transportObj.open_session()
            self.channel.invoke_shell()
            print("连接%s成功" % self.hostip)
            # print(self.channel.recv(65535).decode('utf-8'))
        except Exception:
            self.Close()
            print("连接%s失败" % self.hostip)
            return False
        return True

    #发送命令，获取返回值
    def send_cmd(self,command="\n"):
        command += "\n"
        #p = re.compile(r"[<.*>,\[.*\],More]")
        p = re.compile(self.endStrList)
        result = ""
        self.channel.send(command)
        while True:
            time.sleep(self.timeout)
            ret_data = self.channel.recv(65535)
            ret_data = ret_data.decode("utf-8")
            result += ret_data
            if p.search(ret_data):
                self.channel.send(chr(32))
                continue
            else:
                return result

    #关闭scok、和ssh
    def Close(self):
        try:
            self.transportObj.close()
        except:
            pass
        try:
            self.sock.close()
        except:
            pass

class LoginUseTelnet(object):
    # 初始化
    def __init__(self,hostip,portnum,username,userpassword,endStrList=r"[<.+>,\[.+\],More]",timeout=1,trytimes=3):
        self.hostip = hostip
        self.portnum = int(portnum)
        self.username = username
        self.userpassword = userpassword
        self.endStrList = endStrList  #暂时用不上
        self.timeout = timeout  # send_command方法使用到，获取返回值超时时间，命令执行时间较长可以设置长一些
        self.trytimes = trytimes  # 暂时不用
        

    #尝试连接
    def Connect(self):
        try:
            #print(self.hostip,self.portnum,self.username,self.userpassword,)
            self.telnetObject = telnetlib.Telnet(self.hostip)
            #self.telnetObject.debuglevel(2)
            self.telnetObject.read_until(b"Username:")
            self.username = self.username + "\n"
            self.telnetObject.write(self.username.encode("ascii"))
            self.telnetObject.read_until(b"Password:")
            self.userpassword = self.userpassword + "\n"
            self.telnetObject.write(self.userpassword.encode("ascii"))
            self.telnetObject.write(b"\n")
            text = self.telnetObject.expect([b'<', b'Username or password error'], timeout=5)

            if text[0] == 0:
                print("连接%s成功" % self.hostip)
                return True
            elif text[0] == 1:
                print("连接%s失败，密码错误" % self.hostip)
                return False
            else:
                print("连接%s失败，登陆超时" % self.hostip)
                return False
        except Exception:
            self.Close()
            print("连接%s失败" % self.hostip)
            return False

    # 发送命令，获取返回值,针对more的情况需要进一步测试
    def send_cmd(self,command = "\n"):
        try:
            command += "\n"
            self.telnetObject.write(command.encode("ascii"))
            cur_data = self.telnetObject.read_until(b"More",self.timeout)
            #slect_data = self.telnetObject.expect([b">",b"]",b"More"],self.timeout)
            #cur_data = slect_data[2]

            all_data = ""
            while True:
                cur_data = cur_data.decode("ascii")
                all_data += cur_data
                if "More" in cur_data:
                    self.telnetObject.write(chr(32).encode("ascii"))
                    cur_data = self.telnetObject.read_until(b"More",self.timeout)
                    #print(cur_data)
                else:
                    break
            return all_data
        except Exception:
            self.Close()
            return False

    # 关闭telnet
    def Close(self):
        try:
            self.telnetObject.close()
        except:
            pass

class LoginUseThreading(threading.Thread):
    #初始化
    def __init__(self,loginmethod,hostip,portnum,username,userpassword,commands,endStrList=r"[<.+>,\[.+\],More]",timeout=1,):
        super(LoginUseThreading, self).__init__()
        self.loginmethod = loginmethod
        self.hostip = hostip
        self.portnum = portnum
        self.username = username
        self.userpassword = userpassword
        self.commands = commands
        self.endStrList = endStrList  #暂时用不上
        self.timeout = timeout  # send_command方法使用到，获取返回值超时时间，命令执行时间较长可以设置长一些
        self.result = ""
    #运行
    def run(self):
        semaphore.acquire()
        timetemp = time.strftime(" %Y%m%d %H%M%S")
        filename = "log/" + project + "/" + self.hostip + timetemp + ".txt"
        if self.loginmethod == "SSH2":
            con = LoginUseSSH(self.hostip,self.portnum,self.username,self.userpassword,self.endStrList,self.timeout)
            if con.Connect() == True:
                for command in self.commands:
                    self.result += con.send_cmd(command)
                print(self.result)

                with open(filename,"a") as f:
                    f.write(self.result.replace("  ---- More ----[42D                                          [42D",""))
            else:
                filename_err = "log/" + project + "/" + "登陆失败" + self.hostip
                with open(filename_err,"w") as f:
                    f.write(self.hostip)

            con.Close()
        elif self.loginmethod == "Telnet":
            tn = LoginUseTelnet(self.hostip,self.portnum,self.username,self.userpassword,self.endStrList,self.timeout)
            if tn.Connect() == True:
                for command in self.commands:
                    self.result += tn.send_cmd(command)
                print(self.result)
                with open(filename,"a") as f:
                    f.write(self.result.replace("  ---- More ----[42D                                          [42D",""))
            else:
                filename_err = "log/" + project + "/" + "登陆失败" + self.hostip
                with open(filename_err, "w") as f:
                    f.write(self.hostip)
            tn.Close()
        else:
            print("请选择正确的登陆方式")
            pass
        semaphore.release()
    #获取返回数据
    def get_result(self):     #需要执行完成后才能获取，所有要在join之后获取数据
        return self.result

#获取命令
def get_commands(val):
    data = xlrd.open_workbook("设备信息库.xlsx")
    command_list = data.sheet_by_name("命令行")
    commands = []

    for row in range(1,100):
        try:
            command = command_list.cell(row,1).value
            #print(command)
            if command == "EOF":
                break
            if re.search(r"%s\d+", command):
                try:
                    k = re.findall(r"%s\d+", command)
                    #print(k)
                    for i in k:
                        index = int(i.strip("%s"))
                        #print(index)
                        command = command.replace(i, val.split(";")[index])
                except IndexError:
                    print("参数不够,请添加足够参数")

            #if "%s" in command:
            #    command = command.replace("%s",val)
            commands.append(command)
        except IndexError:
            continue
    #print(commands)
    return commands

project = ""
while True:
    if not os.path.exists("log"):
        os.mkdir("log")
    project = input("请输入本次工程名：").strip()
    if len(project) == 0:
        print("请输出工程号")
        continue
    if os.path.exists("log/%s" % project):
        print("工程号已存在，请重新输入新的工程号")
    else:
        os.mkdir("log/%s" % project)
        break
semaphore = threading.BoundedSemaphore(20)  #设置信号量，即同时进行的线程数
data = xlrd.open_workbook("设备信息库.xlsx")
device_list = data.sheet_by_name("设备信息表")
thread_list = []
for row in range(1,3000):
    try:
        ip = device_list.cell(row,0).value
        user = device_list.cell(row,2).value
        password = device_list.cell(row,3).value
        login_method =  device_list.cell(row,4).value
        port = int(device_list.cell(row,5).value)
        canshu = device_list.cell(row,6).value
        flag = device_list.cell(row,7).value.upper()
        if flag == "N":
            continue
        #print(ip,user,password,login_method,port,canshu,)
        commands = get_commands(canshu)
       # print(commands)
    except IndexError:
        break
    t = LoginUseThreading(login_method,ip,port,user,password,commands)
    t.start()
    thread_list.append(t)

for i in thread_list:
    i.join()
    print(i.get_result())

#生成合并文件
proceess_data.process_data("log/%s" % project)
