from uiautomation import WindowControl
from pywinauto import Desktop
import uiautomation as auto
from dataclasses import dataclass
import re
import time
import threading
# import pyautogui

DEBGU=False


@dataclass
class Message:
    user:str=''
    msg:str=''

    def display(self):
        print(f'user:\033[31m{self.user}\033[0m,msg:\033[31m{self.msg}\033[0m')
    
    def toString(self):
        return f'user:\033[31m{self.user}\033[0m,msg:\033[31m{self.msg}\033[0m'
    
    def formattedMsg(self):
        return f'{self.user}:\033[31m{self.msg}\033[0m'

def is_valid_time(time_str):
    # 正则表达式匹配 "xx:xx" 格式（24小时制）
    pattern = r'^\d{2}:\d{2}$'
    if re.match(pattern, time_str):
        return True
    return False

class QQRobot:
    meg_list_route='001220200'
    user_route='000'
    msg_route='00100'

    user_route_with_time='010'
    msg_route_with_time='00100'

    send_panel_route='00122130100'
    send_btn_route='001221410'

    def __init__(self,name):
        # self.window = WindowControl(searchDepth=1, Name=name)

        # if self.window.Exists(0):
        #     print('找到窗口')
        #     self.window.SetActive()
        # else:
        #     print('未找到窗口')

        for win in auto.GetRootControl().GetChildren():
            print(f"窗口: {win.Name}, Class: {win.ClassName}")
            if win.Name==name:
                print('找到窗口')
                self.window=win
                break

        self.last_msg=None
        self.name=name
        self.send_panel=None
        self.send_btn=None
        self.send_list=[]

    def inited(self):
        return self.window!=None
    
    def find_chat_list(self):
        panel=self.window.GetChildren()
        panel=panel[0].GetChildren()
        panel=panel[0].GetChildren()

        if DEBGU:
            for p in panel:
                print(f'组件：{p.Name},class:{p.ClassName}')

    def find_all_child(self,panel,route):
        child=self.find_child(panel,route)
        for index,c in enumerate(child):
            self.find_all_child(c,route+f'{index}')

    def find_child(self,panel,route=None):
        childs=panel.GetChildren()
        if DEBGU:
            for p in childs:
                if route==None:
                    print(f'组件：{p.Name},class:{p.ClassName},父组件：{panel.Name}')
                else:
                    print(f'组件：{p.Name},class:{p.ClassName},controltype:{p.ControlType},父组件：{panel.Name},父级索引：{route}')
        return childs
    
    def find_child_by_route(self,panel,route):
        if DEBGU:
            print('find child by route ----------------------')
        for c in route:
            if DEBGU:
                print(f"当前路由：{c}")
            child=self.find_child(panel)
            panel=child[int(c)]
        return panel
    

    def find_msg_panel(self):
        self.msg_panel=self.find_child_by_route(self.window,self.meg_list_route)

    def find_send_panel(self):
        self.send_panel=self.find_child_by_route(self.window,self.send_panel_route)
        # self.send_panel=send_panel.EditControl()
    
    def find_send_btn(self):
        self.send_btn=self.find_child_by_route(self.window,self.send_btn_route)
    
    def msg_list(self):
        msgs=self.find_child(self.msg_panel)
        return msgs
    
    def get_last_msg(self):
        msgs=self.msg_list()
        message=Message()
        if len(msgs)>0:
            last_msg=msgs[0]
            if DEBGU:
                print('find all child from last msg----------------------')
                self.find_all_child(last_msg,'')
            try:
                user=self.find_child_by_route(last_msg,self.user_route)
            except IndexError as e:
                user=None
            if user!=None:
                msg_route=self.msg_route
                if is_valid_time(user.Name):
                    user=self.find_child_by_route(last_msg,self.user_route_with_time)
                    msg_route=self.msg_route_with_time
                try:
                    info=self.find_child_by_route(last_msg,msg_route)
                except IndexError as e:
                    info=None
            if user!=None:
                message.user=user.Name
            else:
                message.user='查询出错'
            if info!=None:
                message.msg=info.Name
            else:
                message.msg='查询出错'
        return message

    def start(self,stopEvent):
        self.find_msg_panel()
        self.find_send_panel()
        self.find_send_btn()
        print('开始循环监听')
        while True:
            if stopEvent.is_set():
                print(f'robot {self.name}:退出')
                break
            last_msg=self.get_last_msg()
            if self.last_msg!=last_msg:
                print(f'{self.name}[{last_msg.formattedMsg()}]')
                # last_msg.display()
                self.last_msg=last_msg

            if len(self.send_list)>0:
                # self.send_panel.SetFocus()
                self.send_panel.SendKey(self.send_list.pop())
                self.send_panel.SendKey("{Enter}")

            time.sleep(0.5)
        # self.send_panel.SetFocus()
        # time.sleep(0.5)
        # pyautogui.typewrite('对的')
        # pyautogui.press('enter')
    

    def send_msg(self,msg):
        self.send_list.append(msg)
        if DEBGU:
            print('msg----------------')
            print(msg)

def test():
    robots=[]
    # robots.append(QQRobot('尖塔引擎学习与游戏制作交流群千年学院分群'))
    # if robot.inited():
    #     robot.find_all_child(robot.window,'')
        # robot.find_msg_panel()
        # msg=robot.get_last_msg()
        # print(f'user:{msg.user},msg:{msg.msg}')

def main():
    robots=[]
    robots.append(QQRobot('尖塔引擎学习与游戏制作交流群千年学院分群'))
    # robots.append(QQRobot('杀戮尖塔Mod交流群'))

    threads=[]
    stop_Event=threading.Event()
    for r in robots:
        if r.inited():
            thread=threading.Thread(target=r.start,args=(stop_Event,))
            threads.append(thread)
            thread.start()
    
    try:
        while True:
            text=input()
            if text.lower()=="exit":
                break
            robots[0].send_msg(text)
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    print('终止所有进程')
    stop_Event.set()
    for thread in threads:
        thread.join()
    print('进程已终止')


if __name__=='__main__':
    main()
    # test()
