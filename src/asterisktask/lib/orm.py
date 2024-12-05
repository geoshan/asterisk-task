from sqlalchemy.orm import DeclarativeBase,Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer,select as sql_select,update
import time

class AsteriskModel(DeclarativeBase):
    '''
    数据库模型的基本类
    AsteriskModel的理念是，所有的表必须默认有id，is_deleted，created_at，updated_at字段
    必须将数据库表的软删除与实际删除分开，软删除只是将is_deleted字段置为True
    '''
    id: Mapped[int] = mapped_column(primary_key=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[int] = mapped_column(Integer(), default=int(time.time())) # 创建时间的unix时间戳
    updated_at: Mapped[int] = mapped_column(Integer(), default=int(time.time())) # 更新时间的unix时间戳


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
                i.is_deleted = True
                self.add(i)
        else:
            instance.is_deleted = True
            self.add(instance)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



def select(*args, **kwargs):
    '''
    重写select方法，使得默认查询时，不查询已经删除的数据'''
    s = sql_select(*args, **kwargs)
    for i in args:
        if hasattr(i,'is_deleted'):
            s = s.where(i.is_deleted == False)
    return s

def delete(table:AsteriskModel):
    '''
    重写delete方法，使得默认删除时，不删除数据，而是将is_deleted字段置为True'''
    return update(table).values(is_deleted=True)