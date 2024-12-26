import sys,inspect
from asterisktask.setup.setting import AppConfig
from asterisktask.util.tool import AsteriskContext, print_prompt,classproperty
from asteriskutils.tools import dprint,iprint,wprint,error_print
from asterisktask.lib.task import TaskEngine,AsteriskTask
from asterisksecurity.encryption import AsteriskEncrypt
# import importlib
import uuid
from time import sleep
from threading import Thread,current_thread
import schedule
from deprecated.sphinx import deprecated
import os,time

class TaskManager():
    '''
    任务管理器，在主程序启动时初始化
    '''
    def __init__(self) -> None:
        '''
        任务类通过读取AppConfig.json自定义的package和module。
        将所有的task装载到任务容器中，启动默认task；
        然后启动所有的定时任务。
        '''
        self.__schedule = False # 当为True时，已开始定时任务，为False时，已停止定时任务
        # 自动导入tasks模块下的task类
        try:   
            # importlib.import_module(AppConfig['task_module'])
            __import__(AppConfig['task_module'])
            tasks = inspect.getmembers(sys.modules[AppConfig['task_module']], inspect.isclass)

            # 去除非tasks模块类
            ex = []
            for name, task_class in tasks:
                # if task_class.__module__ != AppConfig['task_module'] or not (TaskEngine in task_class.__mro__):
                if not task_class.__module__.__contains__(AppConfig['task_module'])  or \
                    not (TaskEngine in task_class.__mro__ or AsteriskTask in task_class.__mro__ ) or task_class.__dict__.get('abstract_task'):
                    ex.append(tasks.index((name,task_class)))
            if len(ex)>1:
                ex.sort(reverse=True)
            for i in ex:
                tasks.pop(i)
            del(ex)
            # dprint(tasks) # 已经非常稳定，暂时不再dubug_print

            # 将应用自定义任务类放进任务类池
            for name, task_class in tasks:
                TaskPool.add_to_pool(name,task_class)
        except ModuleNotFoundError as e:
            error_print('未找到任何任务类！')
            dprint(e)
        self.start_init_task()
        self.start_default_task()
        self.start_schedule_tasks()
    def start_init_task(self) -> None:
        '''
        启动初始化任务。
        初始化任务配置在AppConfig.json中，例如:
        "init_task":"get_gitee_token",

        '''
        key = AppConfig['app_name'].replace('_','')
        init_task = AppConfig.get('init_task').replace('_','')
        ae = AsteriskEncrypt(key)
        try:
            fp = open('.initat','r',encoding='utf8')
            file_stat = os.stat('.initat')
            create_time = int(file_stat.st_ctime)
            
            checker = ae.encrypt(f'{init_task}{create_time}')
            if(fp.read() != checker):
                wprint('初始化任务文件被篡改，重新初始化。')
                self.exec_task(AppConfig['init_task'])
            fp.close()
            
        except FileNotFoundError:
            iprint('启动初始化任务')
            try:
                self.exec_task(AppConfig['init_task'])
                checker = ae.encrypt(f'{init_task}{int(time.time())}')
                fp = open('.initat','w',encoding='utf8')
                fp.write(checker)
                fp.close()
            except KeyError:
                wprint('没有初始化任务。')
        
        

    def start_default_task(self) -> None:
        '''
        启动应用的默认任务。
        默认任务配置在AppConfig.json中，例如:
        "default_task":"get_gitee_token",

        '''
        iprint('启动默认任务')
        try:
            self.exec_task(AppConfig['default_task'])
        except KeyError:
            wprint('没有默认任务。')
        
        

    def start_schedule_tasks(self) -> None:
        '''
        启动定时任务。
        应用启动时自动启动定时任务。实现的原理其实是以多线程启动schedule模块
        '''
        if not self.__schedule:
            iprint('开启定时任务')
            self.__schedule = True
            t = Thread(target=self.__init_schedule_tasks,name='scheduled_tasks')
            t.daemon = True
            t.start()
        else:
            wprint('定时任务已在开启状态。')
    def stop_schedule_tasks(self) -> None:
        '''
        停止定时任务。
        可以在命令行中执行
        注:应用退出时会自动执行。
        '''
        if self.__schedule:
            iprint('关闭定时任务...')
            self.__schedule = False
            schedule.clear()
        else:
            wprint('定时任务未开启。')

    def __init_schedule_tasks(self) -> None:
        '''
        执行定时任务。先从配置中取出所有的定时任务，然后加入到定时任务重，已多线程方式启动
        '''
        try:
            if len(AppConfig['tasks'])== 0:
                wprint('未设置定时任务。')
                self.__schedule = False
            for task_item in AppConfig['tasks']:                
                if AppConfig['tasks'][task_item].get('is_loop'):                        
                    # 将任务的定时信息添加到任务配置中
                    if int(AppConfig['tasks'][task_item]['timer']['period']) > 0 :
                        schedule.every(AppConfig['tasks'][task_item]['timer']['period']).seconds.do(\
                            self.__threaded_schedule_task,self.exec_task,task_item)                            
                    else:
                        self.__init_timer_task(task_item)

            '''
            以下这段是检查V2版任务的定时任务，V2版本的任务不再使用定时任务
            '''
            for task_name in TaskPool.items:
                task_class = TaskPool.get_task(task_name)
                if task_class.__dict__.get('is_loop'):
                    if task_class.timer.get('period') > 0:
                        schedule.every(task_class.timer.get('period')).seconds.do(self.__threaded_schedule_task,self.exec_task,task_name)
                    else:
                        self.__init_timer_task(task_name)

            
            while self.__schedule:
                schedule.run_pending()
                sleep(1)
        except KeyError as e:
            error_print("AppConfig.json配置有误")
            dprint(e)
        except BaseException as e:
            error_print('定时任务的配置有误，无法执行。')
            dprint(e)

    def __init_timer_task(self,task_item):
        '''
        初始化每周、每日之类定时任务。每日任务直接初始化，其他再调用其他方法
        Args:
            task_item(str):任务名称
        '''

        try: # 兼容V1.0 定义
            if AppConfig['tasks'][task_item]['timer'].get('fixed_time'):
                for timing in AppConfig['tasks'][task_item]['timer'].get('fixed_time'):
                    schedule.every().day.at(timing).do(self.__threaded_schedule_task,self.exec_task,task_item)
            if AppConfig['tasks'][task_item]['timer'].get('weekly'):
                for timing in AppConfig['tasks'][task_item]['timer'].get('weekly'):
                    self.__init_weekly_task(timing,task_item)
        except KeyError:
            task_class = TaskPool.get_task(task_item)
            if task_class.timer.get('fixed_time'):
                for timing in task_class.timer.get('fixed_time'):
                    schedule.every().day.at(timing).do(self.__threaded_schedule_task,self.exec_task,task_item)
            if task_class.timer.get('workday'):
                for timing in task_class.timer.get('workday'):
                    schedule.every().day.at(timing).do(self.__threaded_schedule_task,self.__workday_task,task_item)
            if task_class.timer.get('business_day'):
                for timing in task_class.timer.get('business_day'):
                    schedule.every().day.at(timing).do(self.__threaded_schedule_task,self.__business_day_task,task_item)
            if task_class.timer.get('weekly'):
                for timing in task_class.timer.get('weekly'):
                    self.__init_weekly_task(timing,task_item)

    def __workday_task(self,task_item:str):
        '''
        初始化工作日定时任务
        Args:
            task_item(str):任务名称
        '''
        import chinese_calendar
        import datetime
        if chinese_calendar.is_workday(datetime.datetime.now()):
            self.exec_task(task_item)

    def __business_day_task(self,task_item:str):
        '''
        初始化交易日定时任务
        交易日的特点是，周一到周五，且不是法定节假日
        Args:
            task_item(str):任务名称
        '''
        import chinese_calendar
        import datetime
        if chinese_calendar.is_workday(datetime.datetime.now()) and datetime.datetime.today().weekday() < 5 :
            self.exec_task(task_item)



    def __init_weekly_task(self,timing:tuple,task_item:str):
        '''
        初始化每周定时任务
        Args:
            timing(tuple):两个元素，周几执行（0-6代表周一到周日）；几时几分执行
            task_item(str):任务名称
        '''
        if timing[0] == 0:
            schedule.every().monday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        elif timing[0] == 1:
            schedule.every().tuesday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        elif timing[0] == 2:
            schedule.every().wednesday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        elif timing[0] == 3:
            schedule.every().thursday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        elif timing[0] == 4:
            schedule.every().friday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        elif timing[0] == 5:
            schedule.every().saturday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        elif timing[0] == 6:
            schedule.every().sunday.at(timing[1]).do(self.__threaded_schedule_task,self.exec_task,task_item)
        else:
            error_print('每周定时任务设置错误，0-6标识周一至周日') 


    def __threaded_schedule_task(self,task_func,task_name:any):
        '''
        将定时任务的执行在多线程中执行，以免任务串行后互相干扰
        Args
            task_func(obj):需要执行定时任务的方法，一般为self.start_task
            task_name(any):需要执行定时任务的方法的参数，一般为任务名称(str),或者是任务类（第二代）
        '''
        job_thread = Thread(target=task_func,args=[task_name],name=f'threading_scheduled_task_{task_name}')
        job_thread.daemon = True
        job_thread.start()

    def exec_task(self,t:str,context_id:str = '') -> None:
        '''
        执行任务（第二代）
        具体的执行条件需要根据任务的类属性来判断，如是否循环执行，是否使用多线程等。
        Args:
            t(str):任务名称
            context_id(str):上下文id
        '''
        try:
            t = TaskPool.get_task(t)
        except KeyError as e:
            error_print(f'任务[{t}]未定义。')
            dprint(e)
            iprint('输入命令“help“获取帮助')
            return    
       
        if t.is_sub_task and context_id == '':
            wprint('子任务无法独立执行。')
            return
        
        is_main_thread = True if current_thread().name == 'MainThread' else False
        # 对任务类实例化
        task = t()

        if task.__dict__.get('is_main_thread') and t.threading:
            self.start_threading_task(task.__class__.__name__,context_id)
            return
        if context_id:
            task.prev_context_id = context_id
        # dprint(t.__dict__.get('next_tasks'))
        if t.__dict__.get('next_tasks') is not None:
            # dprint(task.next_tasks)
            task.next_context_id = str(uuid.uuid1())
        task.run()

        if task.__dict__.get('next_context_id'):
            for next_task in t.next_tasks:
                if t.next_tasks_paralelle:
                    '''为尽快将主程序结束，解决主线程占用问题'''
                    self.start_threading_task(next_task,task.next_context_id)
                else:
                    self.exec_task(next_task,task.next_context_id)
        
        if not task.__dict__.get('is_main_thread'): #and not context_id:
            print() # 非主线中的主任务需要打印回车
        heavy_task = True if t.__dict__.get('is_heavy_task') else False        
        # #释放下下文
        # AsteriskContext.remove_content(task.next_context_id)
        # 当任务完成时,删除task，释放内存
        del(task)
        if heavy_task:
            self.__clear_memory()
        
        if not is_main_thread  and not context_id:
            
            print_prompt() # 只有在主线程以及定时任务的多线程任务在任务结束时答应提示符

    def __clear_memory(self):
        '''
        清理内存，释放内存
        '''
        import gc,subprocess,sys
        gc.collect()
        match sys.platform:
            case 'win32':
                subprocess.run(['cls'],text=True,capture_output=False)
            case 'linux':
                subprocess.run(['clear'],text=True,capture_output=False)
            case 'darwin':
                subprocess.run(['clear'],text=True,capture_output=False)
        iprint('任务执行完毕，释放内存。')


    @deprecated(reason='将逐步由exec_task来替代',version='2.1.0')
    def start_task(self,name:str,context_id:str='') -> None:
        '''
        按照name名称启动任务。
        Args:
            name(str):任务名称，如:
                "tasks":{
                    "get_gitee_token":{
                        ...
                    },
                    ...
                }
            context_id(str): 上文的context_id。
        '''
        is_main_thread = True if current_thread().name == 'MainThread' else False
        
        
        if not is_main_thread and context_id=='':
            if current_thread().name.startswith("threading_task"):
                sleep(1) # 当手动启动多线程的任务时，需要延迟少许，以便提示符能正确显示
            print() # 非主线中的主任务需要打印空行开始
            iprint(f'当前线程为[{current_thread().name}]')
        
        try:
            # dprint(AppConfig['tasks'][name].get('threading')) # 检车是否多线程任务
            # 如果在主线程中，需要检查该任务是否需要多线程运行
            if is_main_thread and AppConfig['tasks'][name].get('threading'):
                self.start_threading_task(name,context_id)
                return
            task_conf = self.__init_task_conf(name,context_id)
            # 以下修改尝试每次执行任务时从任务池取类，实例化并执行任务后即析构释放内存
            t = TaskPool.get_task(AppConfig['tasks'][name]['task_class'])(**task_conf)
            t.run()
            del t
            #TaskPool.get_task(AppConfig['tasks'][name]['task_class'])(**task_conf).run()
            # 执行完主任务后，如有关联任务，则执行关联任务
            if task_conf.get('next_context_id'):
                self.start_sub_task(name,task_conf['next_context_id'])
            # 当任务完成时，会将使用api的任务中产生的临时上下文删除
            # 临时上下文的名称以api_methond命名
            if AppConfig['tasks'][name].get('use_api',False) :
                AsteriskContext.remove_content(task_conf['api_method'])
            # if AppConfig['tasks'][name].get('use_api',False) and \
            #     AsteriskContext.get_content(task_conf['api_method']) is not None:
            #     AsteriskContext.remove_content(task_conf['api_method'])
        except KeyError as e:
            try:

                if(TaskPool.get_task(name)):
                    self.exec_task(TaskPool.get_task(name))
                else:
                    dprint(e)
                    error_print(f'[{name}]任务无相关联api配置，或者没有相匹配的任务类。任务未执行!')
                    iprint('输入命令“help“获取帮助')
            except KeyError as e:
                dprint(e)
                error_print(f'任务[{name}]未定义。')
        except KeyboardInterrupt:
            # 当使用ctrl + C时，取消任务执行
            print()
            wprint(f'取消任务[{name}]的执行！')
            sleep(0.4)
        except BaseException as e:
            dprint(e)
            error_print(f'任务[{name}]出错!')
    
        if not is_main_thread  and not context_id:
            print_prompt() # 非主线中的主任务需要打印提示符结束

    def __init_task_conf(self,name:str,context_id:int) -> dict:
        '''
        为每个任务准备任务配置
        Args
            name(str):任务名称
            context_id(int):上下文id
        Returns
            dict: 任务配置信息
        '''
        if (AppConfig['tasks'][name].get('use_api') is not None) and AppConfig['tasks'][name].get('use_api'):
                task_conf = AppConfig[AppConfig['tasks'][name]['api_name']]
                task_conf['api_method'] = AppConfig['tasks'][name]['api_method']
        else:
            task_conf = AppConfig['tasks'][name] # 需要将该任务的配置放在配置文件中
        
        # 若有context_id说明本次为关联任务，将context_id 放入运行配置的prev_context_id中，以便run()
        # 方法可以从上下文之中读取读取上文
        if context_id:
            task_conf['prev_context_id'] = context_id
        # 如果有后续的关联任务，需要产生next_context_id，放入运行配置的prev_context_id中，以便run()
        # 方法直接以此context id设置下文内容
        if AppConfig['tasks'][name].get('next_task') is not None:
            task_conf['next_context_id'] = str(uuid.uuid1())
        else:
            iprint(f'[{name}]任务无关联任务。')     
        return task_conf


    def start_sub_task(self,name,next_context_id):
        '''
        执行子任务
        Args:
            name(str):任务名称，如:
                "tasks":{
                    "get_gitee_token":{
                        ...
                    },
                    ...
                }
            next_context_id(int): 下文的context_id
        '''
        try:
            next_task = AppConfig['tasks'][name]['next_task']
            
            iprint("准备启动关联的[{}]任务".format(next_task))
            for sub_task in next_task:
                self.start_task(sub_task,context_id = next_context_id)
                iprint('关联任务[{}]结束。'.format(sub_task))
            # 清除关联任务的上下文
            AsteriskContext.remove_content(next_context_id)

        except KeyError:
            iprint('[{}]任务无关联任务。'.format(name))
        except BaseException as e:
            dprint(e)
            error_print('[{}]任务执行出错!'.format(name))
        else:
            iprint('[{}]任务结束。'.format(name))


    def start_threading_task(self,name:str,context_id:int):
        '''
        以多线程的方式回调start_task方面，参数相同
        Args:
            name(str):任务名称，如:
                "tasks":{
                    "get_gitee_token":{
                        ...
                    },
                    ...
                }
            context_id(int): 上文的context_id

        '''
        t = Thread(target=self.exec_task,args=[name,context_id],name=f'threading_task_{name}')
        t.daemon = True
        t.start()

class TaskPool():
    '''
    任务类的池，由于Python的GC机制，任务类在放入池中后，就进行keep alive的处理
    '''
    __pool = {}
    __ison = True

    @classmethod
    def add_to_pool(cls,name:str,task_class:object) -> None:
        '''
        将可用的任务类装载到内存
        Args:
            name(str): 任务类名
            task_class(object):任务类
        '''
        cls.__pool[name] = task_class
        t = Thread(target=cls.__keep_alive,args=[name],name='keep_alive_{}'.format(name))
        t.daemon = True
        t.start()
    @classmethod
    def get_task(cls,name:str) -> object:
        '''
        以名称取得任务类
        Args:
            name(str):任务类名
        Returns:
            任务类
        '''
        return cls.__pool[name]

    @classmethod
    def __keep_alive(cls,name:str) -> None:
        i =0 
        while  cls.__ison:
            if cls.get_task(name) is not None:
                i += 1
                sleep(1)
            else:
                print()
                dprint(f'[{name}]的内存变量出错，可能被GC回收。')
                print_prompt()
                break
        del(i)
    @classmethod
    def ison(cls,ison = False):
        '''
        设置类状态，当__ison为False时，__keep_alive 将自动停止
        Args:
            ison(bool):是否保持context
        '''
        cls.__ison = ison
    @classproperty
    def items(cls) -> dict:
        '''
        返回任务池中所有的任务类
        '''
        return cls.__pool
