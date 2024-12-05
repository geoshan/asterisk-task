from urllib import response
import requests
import time,threading
from asterisktask.error.api import HttpResultFailedError, FunctionNotSupport
from asteriskutils.tools import error_print,iprint,dprint
from urllib3.exceptions import NewConnectionError,MaxRetryError, ConnectTimeoutError
from asterisktask.setup.setting import AppConfig
from deprecated.sphinx import deprecated

'''
基于http的API
使用http协议的api接口调用等
'''
class MetaHttpApi():
    '''
    HTTP请求的基础类，将requests进行了封装，通过配置字段自动发起请求，并发挥结果；
    同时对返回结果进行必要的错误判断
    '''

    def __init__(self,config:dict):
        '''
        初始化时将配置文件导入，同时根据配置动态生成相应类
        Args:
            config(dict): 配置文件具体格式模版为（其中“GiteeApi”为http api的名称：
            "GiteeApi": {
                "protocal": "https://",
                "host": "gitee.com",
                "port": 443,
                "default_method":"access_token", //默认的接口
                "http_api": {
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
                }
            }
        '''
        # self.thread_status = True 新的流程暂时不需要
        self.http_time_out= AppConfig['connection_timeout'] if AppConfig.get('connection_timeout') else 30 # 连接http，如果超过30秒，没有结果即超时
        self.resp = None # http 返回值
        self.header_status = 0 # 返回http header的状态号
        try:
            self.host = config['host']
            self.protocal = config['protocal']
            self.port = config['port']
        except:
            error_print('配置文件出错，退出！')
            exit()
        self._bind_connect(config['http_api'])
        
    def _bind_connect(self,api_names:dict):
        '''
        将api接口绑定到私有连接方法，以达到隐藏实际连接方法的目的

        '''
        for i in api_names:
            # 将API接口的方法与类方法进行映射
            setattr(self,i,self.__connect)

    @deprecated(reason='将逐步由HttpApiV2.__connectV2来替代',version='1.6.2')
    def __connect(self,api_setting:dict,**kwargs)->response:
        '''
        根据提供的api参数连接http api。根据配置文件自动以post或者get方法连接。
        Args:
            api_setting(dict):配置文件GiteeApi节点下数据
            **kwargs（**dict):接口需要传递的参数
        Returns:
            str: http api返回的字符串，可能是html、json等格式。
        '''
        self._process_connect(api_setting,**kwargs)
        rtn_dict = self._return_status()
        if self.resp and rtn_dict['success']:
            return self.resp
        else:
            error_print(rtn_dict['result']['msg'])
            error_print('失败')
            self.connecting_thread.join(timeout=0.1) # 如果已经超时了，就尽快把线程结束
            self.connecting_thread = None
            dprint('回收http连接线程') # 测试是否回收成功
        '''
        此处暂时注释做试验
        if self.header_status > 0:
            self.connecting_thread.join(timeout=0.1) # 如果已经超时了，就尽快把线程结束
        if i >= self.http_time_out:    
            error_print('失败')
            error_print('连接http服务器器超过了配置文件设定的时间 -- 请稍后再试')
            self.connecting_thread.join(timeout=0.1) # 如果已经超时了，就尽快把线程结束
            return '{"success": false, "result": {"code": 504, "msg": "服务器响应超时，请稍后再试。"}}'
        if self.header_status > 0:
            self.connecting_thread.join(timeout=0.1) # 如果已经超时了，就尽快把线程结束
            return '{"success": false, "result": {"code": '+ str(self.header_status) + ', "msg": "出现错误。"}}'
        '''
    def _process_connect(self,api_setting:dict,**kwargs)->response:
        '''
        根据提供的api参数连接http api。执行连接流程。
        Args:
            api_setting(tuple):配置文件GiteeApi节点下数据
            **kwargs（**dict):接口需要传递的参数
        Returns:
            str: http api返回的字符串，可能是html、json等格式。
        '''
        iprint('开始从{}连接HTTP API.'.format(self.host),end='')
        self._waiting(api_setting,**kwargs)
        self._connect_status()
    
    def _connect_status(self)-> None:
        '''
        以...的方式显示连接的状态
        '''
        i = 0
        while not self.resp and self.header_status ==0:
            if i < self.http_time_out:
                iprint('.' ,header=False,end='',flush=True)
                time.sleep(0.2)
                i += 0.2
            else:
                self.header_status = 504
                error_print('连接超过设定时限！!')
                break
        print() # 用于换行
            
    def _waiting(self,api_setting:dict,**kwargs):
        '''
        起一个等待的线程，实际执行连接在线程中执行
        '''
        self.connecting_thread = threading.Thread(target=self.__exec_http_connect,args=[api_setting],kwargs=kwargs,name='connecting...')
        self.connecting_thread.daemon = True  # 这里暂时不设置
        self.connecting_thread.start()

    def __exec_http_connect(self,api_setting:dict,**kwargs):
        '''
        根据提供的api参数连接http api。根据配置文件自动以post或者get等方法连接，并将结果临时存储在实例属性resp上
        本私有方法实际执行连接
        Args:
            api_setting(dict):配置文件GiteeApi节点下数据
            **kwargs（**dict):接口需要传递的参数
        
        '''
        try:
            api_url = '{}{}:{}{}'.format(self.protocal,self.host,self.port,api_setting['path'])
            if api_setting.get('data'): # 允许data为空           
                connect_data = dict(api_setting['data'],**kwargs)
            if connect_data.get('debug'):
                dprint(api_url)
                dprint(connect_data)
            if(api_setting['method']=='post'):               
                r = requests.post(api_url,data=connect_data, \
                    headers={'Content-Type':api_setting['Content-Type'],'Connection':'close'})
                
            elif(api_setting['method']=='get'):
                api_url +='?'
                for querry in connect_data:
                    api_url += f'{querry}={connect_data[querry]}&' 
                r = requests.get(api_url,data=connect_data,\
                    headers={'Content-Type':api_setting['Content-Type']})
            elif(api_setting['method']=='put'):
                r = requests.put(api_url,data=connect_data)
                
            elif(api_setting['method']=='delete'):
                r = requests.delete(api_url,data=connect_data)               
            # 以上method都不是，那么报错
            else:
                raise FunctionNotSupport()
            self.thread_status = False # 用于停止线程
            # print() # 用于换行
            if(r.status_code==404):
                raise HttpResultFailedError()
            self.resp = r
        except FunctionNotSupport:
            error_print(self.host)
            self.header_status = 500
        except (KeyError,HttpResultFailedError) as e:
            error_print(self.host)
            dprint(e)
            self.header_status = 404
        except requests.exceptions.ConnectTimeout as e:
            dprint(e)
            self.header_status = 504
        except (NewConnectionError,MaxRetryError, ConnectTimeoutError):
            error_print(self.host)
            self.header_status = 501
        except requests.exceptions.ConnectionError:
            error_print(self.host)
            self.header_status = 502
        except requests.exceptions.ChunkedEncodingError:
            self.header_status = 503
        except:
            self.header_status = 509
    def _return_status(self) -> dict:
        '''
        连接http之后，返回的信息，主要是成功、错误信息
        Returns:
            dict：连接状态的返回字典
        '''
        return_status = {
                'success':False,
                'result':{}
        }
        if self.resp:
            return_status['success'] = True if self.resp.status_code == 200 else False
            return_status['result']['code'] = self.resp.status_code
            return_status['result']['error_code'] = self.resp.headers['Error-Code'] if self.resp.headers.get('Error-Code') else 0
            return_status['result']['msg'] = self.resp.headers.get('Error-Msg')
        else:
            return_status['success'] = False
            return_status['result']['code'] = self.header_status
            return_status['result']['msg'] = f'\n {AppConfig["errors"][f"{self.header_status}"]}'
        return return_status


class HttpApi(MetaHttpApi):
    '''
    API的URL地址，以配置文件进行url生成，具体生成操作在类初始化中操作
    '''
    def __init__(self,config:dict):
        super(HttpApi,self).__init__(config)
    
class HttpApiV2(HttpApi):
    '''
    API的URL地址，以配置文件进行url生成，具体生成操作在类初始化中操作
    '''
    def __init__(self,config:dict):
        super(HttpApiV2,self).__init__(config)

    def _bind_connect(self,api_names:dict):
        '''
        将api接口绑定到私有连接方法，以达到隐藏实际连接方法的目的

        '''
        # dprint('测试V2版connect方法') #测试是否在运行第二版连接
        for i in api_names:
            # 将API接口的方法与类方法进行映射
            setattr(self,i,self.__connectV2)

    def __connectV2(self,api_setting:dict,**kwargs)->tuple:
        '''
        根据提供的api参数连接http api。根据配置文件自动以post或者get方法连接。
        Args:
            api_setting(dict):配置文件GiteeApi节点下数据
            **kwargs（**dict):接口需要传递的参数
        Returns:
            str: http api返回的字符串，可能是html、json等格式。
        '''
        self._process_connect(api_setting,**kwargs)
        rtn_dict = self._return_status()
        if self.resp is None:
            error_print(rtn_dict['result']['msg'] )
            error_print('失败')
            self.connecting_thread.join(timeout=0.1) # 如果已经超时了，就尽快把线程结束
            dprint('回收http连接线程') # 测试是否回收成功
        return rtn_dict,self.resp