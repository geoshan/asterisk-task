from abc import ABCMeta,abstractmethod
from urllib import response
from asteriskutils.tools import success_print,error_print,iprint,wprint,dprint
import json
from asterisktask.util.tool import AsteriskContext
from threading import current_thread
from asterisktask.error.api import ApiMethodNotFoundError
# from asterisktask.lib.nn import AsteriskRegressor




class MetaTask(type):
    '''
    任务的元类,需要规范任务的名称以及注释的写法
    '''

    description: str = '任务的简要说明'
    '''任务的简要说明'''

    is_sub_task:bool = False
    '''是否是子任务,如果是，则无法独立运行，需要在主任务中调用'''

    threading:bool = False
    '''是否使用多线程'''

    is_loop:bool = False
    '''是否循环执行，定时任务的设定，首先要设定is_loop为True'''

    timer:dict = {
        'period':0,
        'fixed_time':['00:00']
    }
    '''定时器的设置，只有在is_loop为True时才有效。period为间隔时间，fixed_time为固定时间'''


    next_tasks:list = []
    '''后续任务'''

    next_tasks_paralelle:bool = False
    '''后续任务并行执行，如果为False，则按照顺序执行。并行执行实际为多线程执行'''

    abstract_task:bool = False
    '''
    当设定为抽象任务时，不作为具体任务执行。必须有子类的任务才能执行任务。
    并行的好处是，以多线程的方式执行，可以提高任务的执行效率。同时可以快速释放主任务的内存。
    '''

    is_heavy_task:bool = False
    '''
    是否是重量级任务，如果是，则需要考虑任务的执行时间，以及任务的执行效率。
    目前的设计是，如果是重量级任务，则需在任务执行结束后，释放内存。
    调用系统的clear方法，清除内存。
    '''

    hidden_task:bool = False
    '''
    是否是隐藏任务，如果是，则不会在任务列表中显示。
    对于不常用但需要谨慎执行的任务，可以设置为隐藏任务。
    对于工程的初始化任务，因执行一次，也可以设置为隐藏任务。
    也适用于一些测试任务，不希望在任务列表中显示。
    '''

    def __init__(self, class_name:str, class_bases:tuple, class_dict:dict):

        '''
        print(class_name)  # 类名
        print(class_bases) # (<class 'object'>,)基类
        print(class_dict)  # {'__module__': '__main__', '__qualname__': 'chinese', 'country': 'China', '__init__': <function chinese.__init__ at 0x0000000009FBFD90>, 'kongfu': <function chinese.kongfu at 0x0000000009FBFE18>}
        '''
        # 类名首字母必须大写
        if not class_name[:1].istitle():
            raise TypeError('任务类的首字母必须大写!')

        # 类中必须有注释
        if not class_dict.get('__doc__'):
            raise TypeError('任务类中必须有文档注释!')
        
        # 调用type中的__init__方法初始化对象
        super().__init__(class_name, class_bases, class_dict)


class TaskType(MetaTask,ABCMeta):
    '''
    任务的元类，通过多重继承，引入抽象类的特性
    '''
    pass
class AsteriskTask(metaclass=TaskType):
    '''
    第二代任务的抽象类，保留提供了抽象run方法。
    将减少依赖.json文件来定义任务，而是通过类的属性来定义任务
    '''
    def __init__(self) -> None:
        '''
        初始化时赋值参数，并调用调正数据的方法。调整数据的目的是把任务执行的外部参数进行处理'''
        if not current_thread().name == 'MainThread':
            self.is_main_thread = False
            print()
        else:
            self.is_main_thread = True
        
    @abstractmethod
    def run(self)->None:
        pass


    def set_context(self,context,alive=0):
        '''
        将task运行后得到结果存储在上下文中，一般在有关联子任务时，用于传递上下文信息用
        Args:
            context(Any):上下文信息
            alive(int=0): 上下文需要保持的秒数
        '''
        try:
            AsteriskContext.add_key(self.next_context_id,context,alive)
        except KeyError:
            wprint('本任务可能没有设置关联下一个任务，故无法设置上下文。')
        except AttributeError:
            wprint('本任务可能没有设置关联下一个任务，故无法设置上下文。')
    
    def get_context(self):
        '''
        取出上下文，一般在子任务中调用
        '''
        try:
            return AsteriskContext.get_content(self.prev_context_id)
        except KeyError:
            return None
        
    def update_context(self,context):
        '''
        更新上下文，一般在子任务中调用
        '''
        try:
            AsteriskContext.update_key(self.prev_context_id,context)
        except KeyError:
            wprint('没有相关的上下文可以更新。')
            # self.set_context(context)
        except AttributeError:
            wprint('本任务可能没有设置关联上一个任务，故无法更新上下文。')

    
class AsteriskHttpTask(AsteriskTask):
    '''
    基于第二代Task类的http api任务
    
    '''
    protocal:str = 'https://'
    '''默认https协议'''
    host:str = ''
    '''http api的主机地址'''
    port:int = 443
    '''http api的端口'''
    http_api:dict = {} 
    '''
    http api的配置,例如：
    "access_token": {
        "method":"post",
        "path":"/oauth/token",
        "Content-Type":"application/x-www-form-urlencoded",
        "data": {
            "grant_type":"password",
            "username":"shantian@max-optics.com",
            "password":"xxx",
            "client_id":"fabb2ebd43ec4a81696a28733322c7d747dbc025f4a1fd2a33554d01563f2089",
            "client_secret":"71230147421f55ab75e80676ad7cf0903eeacfcfddf67ed49817661672f9b6f2",
            "scope":"user_info projects pull_requests issues notes keys hook groups gists enterprises"
        }
    }
    
    父类可以定义多个api method，如上面的access_token，可以定义多个api method，在子类中通过api_method来指定即可
    '''
    api_method:str = ''
    '''当前类的api的方法名,在父类中定义多个api method，相当于默认的api method，可以在子类中通过api_method来指定'''
    
    def __init__(self) -> None:
        '''
        初始化时赋值参数，并调用调正数据的方法。调整数据的目的是把任务执行的外部参数进行处理
        这里需要增加http api调用的custom_data
        '''
        super().__init__()
        self.adjustdata()
        self.custom_data = {}

    def run(self):
        '''
        根据task_conf执行http api的请求，并将请求返回的结果存储在以api_name命名的上下文中
        '''
        try:
            result = self.exec_json_http_api()
            AsteriskContext.add_key(self.api_method,result)
            # dprint(result)    # 目前比较稳定，不再debug_print
            if result:
                success_print(f"连接{self.host}成功。")
        except KeyError:
            error_print(result)
        except ApiMethodNotFoundError as e:
            error_print('Api 方法未定于，或者定义错误！')
            dprint(e)

    def adjustdata(self):
        '''
        可以通过overwrite这个方法来具体处理任务执行可能需要的外部数据。
        '''
        pass
        

    def exec_json_http_api(self)->json:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            json:将http请求的json结果返回
        '''
        result = self.exec_http_api()
        return json.loads(result.text) if result else None
    
    def exec_txt_http_api(self)->str:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            str:将http请求的返回的文本
        '''
        result = self.exec_http_api()
        return result.text if result else ''

    def exec_http_api(self)->response:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            response:将http请求的response原始结果返回
        '''
        from asterisktask.api.http import HttpApiV2
        task_conf= {
            'host':self.host,
            'protocal':self.protocal,
            'port':self.port,
            'http_api':self.http_api
        }
        # dprint(task_conf)
        task_api = HttpApiV2(task_conf)
        try:
            if hasattr(task_api,self.api_method):
                exec = getattr(task_api,self.api_method)
            else:
                raise ApiMethodNotFoundError
            result,resp = exec(self.http_api[self.api_method],**self.custom_data)
            if result['success']:
                return resp
            else:
                return None
        except KeyError:
            error_print(resp)
            error_print(f'连接{self.host}失败，退出！')
        del(task_api)
                        


class TaskEngine(metaclass=ABCMeta):
    '''
    Task的抽象类，提供了抽象run方法。
    在TaskManager中实例出来对象，统一调用run()方法来执行任务
    '''
    
    def __init__(self,**task_conf) -> None:
        '''
        初始化时赋值参数，并调用调正数据的方法。调整数据的目的是把任务执行的外部参数进行处理
        Args:
            task_conf(kwargs): 任务执行的配置信息，一般为json格式
        '''
        self.task_conf = task_conf
        self.custom_data={}
        self.adjustdata()
        try:
            iprint('取得上下文id为{}'.format(self.task_conf['prev_context_id']))
            # dprint(AsteriskContext.get_content(self.task_conf['prev_context_id'])) # 已稳定运行，取消debug_print
            
        except KeyError:
            # 没有设置prev_context_id
            iprint('当前执行的为主任务。')
            
    @abstractmethod
    def run(self):
        '''
        运行任务
        这里是抽象方法，具体实现在子类中实现
        '''
        pass

    
    def adjustdata(self):
        '''
        可以通过overwrite这个方法来具体处理任务执行可能需要的外部数据。
        '''
        pass

    def get_context(self):
        '''
        取出上下文，一般在子任务中调用
        '''
        try:
            return AsteriskContext.get_content(self.task_conf['prev_context_id'])
        except KeyError:
            return None
    def set_context(self,context,alive=0):
        '''
        将task运行后得到结果存储在上下文中，一般在有关联子任务时，用于传递上下文信息用
        Args:
            context(Any):上下文信息
            alive(int=0): 上下文需要保持的秒数
        '''
        try:
            AsteriskContext.add_key(self.task_conf['next_context_id'],context,alive)
        except KeyError:
            wprint('本任务可能没有设置关联下一个任务，故无法设置上下文。')

class HttpApiTask(TaskEngine):
    '''
    这是一个非常好的范例
    继承了TaskEngine，实现了run方法
    这是一个比较标准的运用HttpApi的，实现了通用的http Api的连接
    相关的参数以及配置可以通过HpptApiConnfig.json文件来设置
    '''

    def run(self):
        '''
        根据task_conf执行http api的请求，并将请求返回的结果存储在以api_name命名的上下文中
        '''
        try:
            result = self.exec_json_http_api()
            AsteriskContext.add_key(self.task_conf['api_method'],result)
            # dprint(result)    # 目前比较稳定，不再debug_print
            if result:
                success_print(f"连接{self.task_conf['host']}成功。")
        except KeyError:
            error_print(result)
        

    def exec_json_http_api(self)->json:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            json:将http请求的json结果返回
        '''
        result = self.exec_http_api()
        return json.loads(result.text) if result else None
    
    def exec_txt_http_api(self)->str:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            str:将http请求的返回的文本
        '''
        result = self.exec_http_api()
        return result.text if result else ''

    def exec_http_api(self)->response:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            response:将http请求的response原始结果返回
        '''
        from asterisktask.api.http import HttpApi
        default_api = type('DefaultAPI',(HttpApi,),{})
        task_api = default_api(self.task_conf)
        try:
            if hasattr(task_api,self.task_conf['api_method']):
                exec = getattr(task_api,self.task_conf['api_method'])
            resp = exec(self.task_conf['http_api'][self.task_conf['api_method']],**self.custom_data)
            # iprint(f"连接{self.task_conf['host']}结束。") #已稳定运行，不再需要打印
            return resp
        except KeyError:
            error_print(resp)
            error_print(f'连接{self.task_conf["host"]}失败，退出！')

class HttpApiTaskV2(HttpApiTask):

    def exec_http_api(self)->response:
        '''
        将http api的请求单独抽象到此方法执行
        Returns
            response:将http请求的response原始结果返回
        '''
        from asterisktask.api.http import HttpApiV2
        defaut_api = type('DefaultAPI',(HttpApiV2,),{})
        task_api = defaut_api(self.task_conf)
        try:
            if hasattr(task_api,self.task_conf['api_method']):
                exec = getattr(task_api,self.task_conf['api_method'])
            result,resp = exec(self.task_conf['http_api'][self.task_conf['api_method']],**self.custom_data)
            # iprint(f"连接{self.task_conf['host']}结束。") #已稳定运行，不再需要打印
            if result['success']:
                return resp
            else:
                return None
        except KeyError:
            error_print(resp)
            error_print(f'连接{self.task_conf["host"]}失败，退出！')


class AsteriskLinearModelTask(AsteriskTask):
    '''
    一个神经网络线性模型任务
    一个线性模型任务的共性就是需要训练数据和测试数据
    '''
    
    abstract_task = True

    input_features:int = 9
    '''输入特征数'''
    output_features:int = 1
    '''输出特征数'''

    

    training_status = True
    '''训练状态，True表示训练，False表示预测'''

    def run(self) -> None:
        '''
        初始化，无轮是做训练还是预测，都需要获取数据以及初始化模型'''
        
        self.training_data, self.test_data = self._collect_data()
        self._framework_setup(self.training_status)

    @abstractmethod
    def _collect_data(self) -> tuple:
        '''
        收集模型训练的的数据，并返回训练数据和测试数据
        数据格式为numpy数组。
        Returns:
            tuple: 返回训续数据和测试数据
        '''
        pass
    
    @abstractmethod
    def _framework_setup(self,traning_status:bool):
        
        pass

class AsteriskTrainingTask(AsteriskLinearModelTask):
    '''
    线性训练任务，需要实现训练模型的方法
    一般需要一些参数，如epoch_num,batch_size,learning_rate等
    这里预设了一下默认值，可以根据实际情况在子类中进行修改
    '''
    epoch_num:int = 10
    '''设置外层循环最多次数'''
    batch_size:int = 15
    '''设置batch大小'''
    learning_rate:float = 0.01
    '''设置学习率'''

    ratio:float = 0.8
    '''训练数据占总数据的比例'''

    max_loss_to_stop:float = 0.0001
    '''训练时当loss小于这个值时停止训练'''
    training_idx_start:int = None
    '''
    训练数据的开始索引,指的是训练数据的开始列索引'''
    training_idx_end:int = None
    '''
    训练数据的结束索引,指的是训练数据的结束列索引'''
    lable_idx_start = None
    '''
    标签数据的开始索引,指的是标签数据的开始列索引'''
    lable_idx_end = None
    '''
    标签数据的结束索引,指的是标签数据的结束列索引'''

    abstract_task = True
    

    
                
    def run(self):
        super().run()
        self._training()
        self._save_model()

    @abstractmethod
    def _training(self):
        '''
        将准备好的数据进行训练
        '''
        pass
   
    @abstractmethod
    def _save_model(self):
        '''
        保存训练好的模型
        '''
        pass
    
class AsteriskPredictTask(AsteriskLinearModelTask):
    '''
    一个神经网络线性模型任务
    '''
    abstract_task = True

    training_status = False

    def __init__(self) -> None:
        super().__init__()

    def run(self):
        super().run()
        
        self._predict()

    @abstractmethod
    def _predict(self):
        '''
        对给定的条件的数据进行预测
        '''
        pass
    
    @abstractmethod
    def _load_model(self):
        '''
        加载训练好的模型
        '''
        pass
