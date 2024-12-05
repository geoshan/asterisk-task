# Asterisk-Task

## 介绍

这是一个任务管理的框架，可以把需要执行的任务在命令行进行执行，配置定时任务、多线程运行的任务等。
可以应用到日常监控、自动化执行、数据自动采集、定时自动机器学习等方面。

注意：

* 发行版本的版本号不一定连续，中间的版本号都是开发中的版本号，不正式发布。
* 版本号为A.B.C.mmdd.hhmm的格式，只须关注A.B.C即可，mmdd.hhmm为build时间戳

## 发行日志

详细可以参考[gitee版发布日志](https://gitee.com/zhangxin_1/asterisk-task/blob/master/docs/release_log.md)
技术文档参考[Documentation](https://gitee.com/zhangxin_1/asterisk-task/blob/master/docs/documentation.md)

### V2.1.0

* 移除AsteriskSinDout类，该类主要用于加密、解密。可以另外安装asterisk-security
* 实现定时任务中中国工作日，中国交易日的设定。
* 已经宣示deprecated都是的error_print以及warn_print方法，正式下线
* 开始deprecte start_task方法，逐步该用exec_task方法
* task支持next_tasks_paralelle属性，默认为False，当为True时，后续任务将启动新线程中执行，可以快速将主任务结束。

### 软件架构

Aterisk-Task以TaskManager作为任务管理器的类，在系统启动时，读入配置文件，读取可以调用任务类，启动默认任务，并启动定时任务。本框架集成了schedule、logging等常用类库。
为了解决关联任务直接的数据传递，以AsteriskContext来实现了类似cookie的功能。

自V2.0以后，任务类做了一次比较大的升级。任务类（除了启动后的默认任务，需要在AppConfig文件中配置意外）将不需要在配置文件中进行配置。

整体架构非常轻。

### 安装教程

1. 在gitee中[发行版](https://e.gitee.com/zhangxin_1/repos/zhangxin_1/asterisk-task/releases/ "Asteristk-Task 框架发行版")下载最新发行版
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

### 特技

1. 使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2. Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3. 你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4. [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5. Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6. Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
