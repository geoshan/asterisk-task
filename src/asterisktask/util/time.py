
from datetime import datetime,timedelta
def today_beginning()->datetime:
    '''
    起始时间从00:00算起的今天
    Returns
        datetime:以00:00起始时间的今天datetime对象
    '''
    return datetime.strptime(f"{datetime.strftime(datetime.now(),'%Y-%m-%d')} 00:00",'%Y-%m-%d %H:%M')
def this_monday()->datetime:
    '''
    起始时间从00:00算起的本周一
    Returns
        datetime:以00:00起始时间的本周一datetime对象
    '''
    today = today_beginning()
    return today -timedelta(today.weekday())
def week_beginning()->datetime:
    '''
    起始时间从00:00算起的本周开始，注：从周日开始
    Returns
        datetime:以00:00起始时间的本周开始datetime对象
    '''
    today = today_beginning()
    return today -timedelta(today.weekday()+1) 
def by_thisweek()->datetime:
    '''
    结束时间从00:00算起的本周结束。即周日的00:00
    Returns
        datetime:以00:00结束时间的本周结束datetime对象
    '''
    today = today_beginning()
    return today + timedelta(7 - today.weekday() - 1)

def this_month()->tuple[datetime,datetime]:
    '''
    起始时间从月初00:00算起的本月结束。
    Returns
        tuple:datetime:以月初00:00开始，月末59:50结束时间的本月头尾datetime对象
    '''
    
    import calendar
    y = datetime.now().year
    m = datetime.now().month
    w_day,endday = calendar.monthrange(y,m)
    return datetime.strptime(f'{y}-{m}-01 00:00','%Y-%m-%d %H:%M'),datetime.strptime(f'{y}-{m}-{str(endday)} 23:59','%Y-%m-%d %H:%M') 
def this_quater()->tuple[datetime,datetime]:
    '''
    起始时间从季度初的00:00算起到本季度结束。
    Returns
        tuple:datetime:以季初00:00开始，季末59:50结束时间的本季头尾datetime对象
    '''
    
    import calendar
    y = datetime.now().year #当前年
    m = datetime.now().month # 当前月
    m = m if m % 3 ==0 else (m//3+1) *3 # 变化成季末
    w_day,q_endday = calendar.monthrange(y,m)
    return datetime.strptime(f'{y}-{m-2}-01 00:00','%Y-%m-%d %H:%M'),datetime.strptime(f'{y}-{m}-{str(q_endday)} 23:59','%Y-%m-%d %H:%M') 

def this_year()->tuple[datetime,datetime]:
    '''
    起始时间从年度度初的00:00算起到本年度度结束。
    Returns
        tuple:datetime:以年初初00:00开始，年末59:50结束时间的本年头尾datetime对象
    '''
    
    import calendar
    y = datetime.now().year #当前年
    return datetime.strptime(f'{y}-01-01 00:00','%Y-%m-%d %H:%M'),datetime.strptime(f'{y}-12-31 23:59','%Y-%m-%d %H:%M') 



def by_nextweek()->datetime:
    '''
    结束时间从00:00算起的下周结束。即周日的00:00
    Returns
        datetime:以00:00结束时间的下周结束datetime对象
    '''
    return by_thisweek() + timedelta(7)
def datetime_diff(timediff:int)->datetime:
    '''
    返回当前时间的之前、之后的时间。
    Args：
        timediff(int): 按照天数向前、向后计算时间
    Returns:
        datetime:计算差值后的时间
    '''
    if isinstance(timediff,int):
        return datetime.now() + timedelta(timediff)
    else:
        from error.util import InvalidTypeError
        raise InvalidTypeError('应填写天数，为整型。')