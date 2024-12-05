'''
一些工具类的错误
'''


class InvalidEncriptionKey(Exception):
    '''
    加密算法的key为字母数字，其他的字符均不支持
    '''
    pass

class InvalidTypeError(Exception):
    '''
    错误的数据类型，例如需要int型，实际输入为float
    '''
    pass