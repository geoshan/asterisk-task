'''
这里定义所有api相关的错误或者意外的类
'''
class WrongHttpApiName(Exception):
    '''
    调用http api时名称参数在配置文件中未找到
    '''
    pass
class FunctionNotSupport(Exception):
    '''
    暂时没有支持的功能
    '''
    pass
class HttpResultFailedError(Exception):
    '''
    接口不存在404，接口出错等可能导致的接口返回错误
    '''
    pass



class ApiMethodNotFoundError(Exception):
    '''
    API method 没有指定
    '''
    pass