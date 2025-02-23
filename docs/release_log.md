# Asterisk-Task发布日志

## V3.0.0(开发中)

### V3.0.0 build新功能

* 完全移除V1.0的TaskEngine以及相关的子类支持 √
* 完全移除TaskManager对V1.0的TaskEngine的支持√
* 支持多语言
* Task的类属性可从AppConfig.json中读取改为类属性的动态加载
* 增加ORM的数据源配置支持
* 优化AI相关的任务类的实现
* 分布式任务的支持

### V3.0.0 缺陷修复以及优化

* 初始.initat文件修改后，重新初始化的流程错误
* 设置orm表的默认charset和collation，并修改create_time,update_time的默认字段名称，修改了软删除的默认字段名称。
* AppConfig.json中，增加了dist_type属性，用于提示目前版本的发型状态，如：开发版、测试版、正式版等。当dist_type为空时，表示正式版

## V2.2.0（最新发布）

### V2.2.0 build新功能

* 增加AI模型训练的内置任务
* 完全移除util模块中的mail包
* 增加基于SQLAlchemy的ORM支持
* 通过配置快速配置数据库连接
* 增加工程初始化任务，只执行一次
* 增加任务的隐藏任务属性。对于初始化任务因只执行一次，故可以在任务列表中隐藏
* AsteriskTask增加update_context方法，以便于多个子任务中更新上下文

### V2.2.0 缺陷修复

* 子任务执行后的提示符重复问题
* http api的进度完成不换行问题
* heavy task属性没有正确执行问题

## V2.1.2

* 修复定时循环任务的执行缺陷

## V2.1.0

* 移除AsteriskSinDout类，该类主要用于加密、解密。可以另外安装asterisk-security
* 实现定时任务中中国工作日，中国交易日的设定。
* 已经deprecated的error_print以及warn_print方法，正式下线
* 启动start_task方法的deprecate历程，逐步改用exec_task方法
* task支持next_tasks_paralelle属性，默认为False，当为True时，后续任务将启动新线程中执行，可以快速将主任务结束。
* 其他细节调整

## V2.0.23

* 只做了细节的修复
* 修改了目录结构，以便于打包并发布pypi

## V2.0.15

主要完善了新的任务类的实现。新的任务类需要继承AsteriskTask，该类包含了以下类属性，来取代原先使用AppConfig.json来配置的烦恼

* description - 任务的简要说明
* sub_task - 是否是子任务,如果是，则无法独立运行，需要在主任务中调用，这是V2新引入特性
* threading - 是否使用多线程
* is_loop - 是否循环执行
* timer - 定时器的设置，只有在is_loop为True时才有效。period为间隔时间，fixed_time为固定时间
* next_tasks - 后续任务
* abstract_task - 当设定为抽象任务时，不作为具体任务执行。必须有子类的任务才能执行任务，这是V2引入的新特性
