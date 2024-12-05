from time import sleep
from asterisktask.lib.taskcontrol import TaskManager, TaskPool
from asterisktask.util.tool import cmd_help,  print_logo, AsteriskContext, print_prompt, version
from asteriskutils.tools import dprint,iprint,error_print,wprint
from asterisktask.setup.setting import AppConfig
import threading

class Asterisk():
    '''
    Asterisk-Task框架的入口类，初始化时打印logo。
    '''
        
    def __init__(self,gui=False,daemon=False):
        '''
        初始化时打印logo
        '''
        self.gui = gui
        self.daemon = daemon
        if gui:
            '''
            self.window = tkinter.Tk()
            self.window.title('Asterisk Task Demo')
            self.window.geometry('480x320')
            label=tkinter.Label(self.window,text='将后期版本中提供界面功能') #生成标签 
            label.pack()
            '''
            wprint('暂时不提供GUI界面！请重新运行。')
        else:
            if not self.daemon:
                print_logo(with_title=True,with_copyrights=True,with_version=True)
            self.tm = TaskManager()
            if not self.daemon:
                cmd_help()

    def main(self):
        '''
        应用入口，实例化TaskManager，自动启动默认任务以及定时任务
        '''
        if self.gui:
            # self.window.mainloop()
            pass
        else:
            if self.daemon:
                iprint('以守护进程后台运行中')
                while self.daemon:
                    sleep(0.2)
            print_prompt()
        
            while self.__at_command():
                print_prompt()
            if AppConfig['debug']:
                for t in threading.enumerate():
                    if t.name != 'MainThread':
                        dprint(t.name)
                        print() # 空行            
            print_logo() 
            iprint(f"欢迎再次使用{AppConfig['app_name']}，再见！")
            print('\n\n') # 空行  
            # sys.exit()
            

    def __at_command(self)-> bool:
        '''
        根据命令行决定如何启动Task Manager
        
        Returns:
            bool: 命令执行返回True；如果是退出命令则返回False

        '''
        try:
            cmd = input("")
            match str.strip(cmd).lower():
                case ":q":
                    return self.__exit_app()
                case "exit":
                    return self.__exit_app()
                case "exit()":
                    return self.__exit_app()
                case "help":
                    cmd_help()
                case "version":
                    version()
                case 'stop_schedule_tasks':
                    self.tm.stop_schedule_tasks()
                case 'start_schedule_tasks':
                    self.tm.start_schedule_tasks()
                case 'show_threads':
                    self.__show_threads()
                case 'show_context_keys':
                    self.__show_context_keys()
                case '':
                    pass
                case _:
                    self.tm.exec_task(cmd)
            
        except (UnicodeDecodeError):
            error_print('命令行输入错误！')
        except EOFError:
            pass
        return True
    def __show_threads(self)-> None:
        for t in threading.enumerate():
            iprint(f'目前正在运行的线程[{t.name}]')
    def __show_context_keys(self)-> None:
        for k in AsteriskContext.keys():
            iprint(f'上下文[{k}]')
    def __exit_app(self)-> None:
        AsteriskContext.ison(False) # 取消 AsteriskContext的keepalive状态
        TaskPool.ison(False) # 取消 TaskPool的keepalive状态
        self.tm.stop_schedule_tasks()
        sleep(1)



    
