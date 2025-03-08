from sqlalchemy.orm import DeclarativeBase,Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer,select as sql_select,update,Boolean,TIMESTAMP
from sqlalchemy.sql import func,text
import time
from asterisktask.setup.setting import AppConfig

class AsteriskModel(DeclarativeBase):
    '''
    数据库模型的基本类
    AsteriskModel的理念是，所有的表必须默认有id，is_deleted，created_at，updated_at字段
    必须将数据库表的软删除与实际删除分开，软删除只是将is_deleted字段置为True
    '''
    id: Mapped[int] = mapped_column(primary_key=True)
    create_time: Mapped[int] = mapped_column(Integer(), default=int(time.time())) # 创建时间的unix时间戳
    update_time: Mapped[int] = mapped_column(Integer(), default=int(time.time())) # 更新时间的unix时间戳
    delete_time: Mapped[int] = mapped_column(Integer(), nullable=True) # 删除时间

    # 设置表的的默认charset和collate
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }


class AsteriskSession(Session):
    '''
    数据库会话的基本类,主要修改delete方法，使得默认删除时，不删除数据，而是将is_deleted字段置为True
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def delete(self, instance):
        '''
        重写delete方法，使得默认删除时，不删除数据，而是将is_deleted字段置为True
        '''
        if type(instance) == list:
            for i in instance:
                i.delete_time = int(time.time())
                self.add(i)
        else:
            instance.is_deleted = True
            self.add(instance)

    def __enter__(self):
        return self

    



def select(*args, **kwargs):
    '''
    重写select方法，使得默认查询时，不查询已经删除的数据'''
    s = sql_select(*args, **kwargs)
    for i in args:
        if hasattr(i,'delete_time'):
            s = s.where(i.delete_time.is_(None))
    return s

def delete(table:AsteriskModel):
    '''
    重写delete方法，使得默认删除时，不删除数据，而是将is_deleted字段置为True'''
    return update(table).values(delete_time=int(time.time()))


class InterfaceToConnectDataSource:
    '''
    一个带有数据源的任务
    '''
    
    
    def __get_data_source(self)->str:
        '''
        获取数据源
        :return: 数据源
        '''
        match AppConfig['data_source'] :
            case 'mysql':
                from asterisksecurity.encryption import AsteriskEncrypt
                a = AsteriskEncrypt(AppConfig['app_name'])
                pwd = a.decrypt(AppConfig['data_sources']['mysql']['password'])
                return f"mysql+{AppConfig['data_sources']['mysql']['driver']}://{AppConfig['data_sources']['mysql']['user']}:{pwd}@{AppConfig['data_sources']['mysql']['host']}:{AppConfig['data_sources']['mysql']['port']}/{AppConfig['data_sources']['mysql']['database']}"
            case 'sqlite':
                return f"sqlite:///{AppConfig['data_sources']['sqlite']['path']}/{AppConfig['data_sources']['sqlite']['filename']}"
            case 'postgresql':
                return 'postgresql'
            case _:
                return 'unknown'
            
            
    def _get_engine(self,echo:bool = False):
        '''
        获取数据库引擎
        :param echo: 是否打印SQL语句
        :return: 数据库引擎
        '''
        from sqlalchemy import create_engine
        return create_engine(self.__get_data_source(),echo=echo)