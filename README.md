# Asterisk-Task

## 介绍

这是一个任务管理的框架，可以把需要执行的任务在命令行进行执行，配置定时任务、多线程运行的任务等。
可以应用到日常监控、自动化执行、数据自动采集、定时自动机器学习等方面。

注意：

* 发行版本的版本号不一定连续，中间的版本号都是开发中的版本号，不正式发布。
* 版本号为A.B.C.mmdd.hhmm的格式，只须关注A.B.C即可，mmdd.hhmm为build时间戳

## 发行日志

详细可以参考[github版发布日志](https://github.com/geoshan/asterisk-task/blob/master/docs/release_log.md)
技术文档参考[Documentation](https://github.com/geoshan/asterisk-task/blob/master/docs/documentation.md)

### 最新V3.0.0

* 完全移除V1.0的TaskEngine以及相关的子类支持
* Task的类属性可从AppConfig.json中读取改为类属性的动态加载
* 完全移除TaskManager对V1.0的TaskEngine的支持
* 优化AI相关的任务类的实现
* 增加ORM的数据源配置支持
* 支持多语言

### 软件架构

Aterisk-Task以TaskManager作为任务管理器的类，在系统启动时，读入配置文件，读取可以调用任务类，启动默认任务，并启动定时任务。本框架集成了schedule、logging等常用类库。
为了解决关联任务直接的数据传递，以AsteriskContext来实现了类似cookie的功能。

自V2.0以后，任务类做了一次比较大的升级。任务类（除了启动后的默认任务，需要在AppConfig文件中配置意外）将不需要在配置文件中进行配置。

整体架构非常轻。

### 安装教程

1. 在github中[发行版](https://github.com/geoshan/asterisk-task/releases/ "Asteristk-Task 框架发行版")下载最新发行版
2. 可以命令行中执行`pip3 install asterisk_task-*.whl`进行安装

### 使用说明

1. 安装成功后,可以使用命令行创建项目，例如创建test_project `atnewapp -app test_project`
2. 系统会自动创建 `test_project` 目录，以及`run_test_project.py`
3. 执行`python3 run_test_project.py`即可启动项目运行。创建项目时会自动设置默认任务。

### 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
    新建 Pull Request

### 需求反馈

1. 请在github上提issue
2. 或者直接联系作者 geoshan@163.com