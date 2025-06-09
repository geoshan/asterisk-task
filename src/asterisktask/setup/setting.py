import json
import os
from asteriskutils.tools import wprint,error_print
from asteriskutils.setting import AppConfig,lang_pack,get_lang_pack

if  __name__ == "__main__":
    import sys
    error_print('本段代码必须从应用主入口导入执行。退出！')
    sys.exit(1)

try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asterisk.json'),'r',encoding='utf8') as fp:
        app_conf = json.load(fp)
        for k,v in app_conf.items():
            AppConfig[k] = v    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'title.attpl'),"r",encoding='utf8') as fp:
        AppConfig['title_text'] = fp.read()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.attpl'),"r",encoding='utf8') as fp:
        AppConfig['logo_text'] = fp.read()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'lang/{AppConfig["lang"].lower()}.json'),'r',encoding='utf8') as fp:
            lang = json.load(fp)
            # lang_pack = get_lang_pack(AppConfig["lang"].lower())
            for k,v in lang.items():
                lang_pack[k] = v
    
except FileNotFoundError:
    wprint('当前目录下的配置文件asterisk.json不存在，启用默认配置。')
    '''
    AppConfig的默认配置，当AppConfig.json文件缺失时使用

    '''
    AppConfig = {
        "app_name":"asterisk_demo",
        "task_module":"asterisk_demo.tasks",
        "version":"0.0.1",
        "debug": 1,
        "prompt":"Asterisk-task > ",
        "log":{
            "log_level":"DEBUG",
            "log_path":"{App}/log",
            "log_file_name":"%Y-%m-%d",
            "log_format":"%(asctime)s - %(levelname)s - %(message)s"
        },
        "logo_text_file":"logo.attpl",
        "title_text_file":"title.attpl",
        "errors":{
            "404":"服务器接口不存在 ，请请确认服务器配置后再试。",
            "500":"服务器接口不存在 ，或者http api的方法不支持",
            "504":"ConnectTimeout -- 请稍后再试",
            "501":"服务器可能未启动 ，请请稍后再试。",
            "502":"无法连接服务器 ，请请稍后再试。",
            "503":"ChunkedEncodingError -- 请稍后再试",
            "509":"Unfortunately -- 请稍后再试"
        },
        "data_sources":{
            "mysql":{
                "driver":"pymysql",
                "host":"localhost",
                "port":3306,
                "user":"spc",
                "password":"encrypted_by_Asterisk-Security==",
                "database":"asterisk"
                },
            "sqlite":{
                "description":"sqlite数据源",
                "path":"data",
                "filename":"asterisk.db"
                }
        },
        "data_source":"mysql"
    }

def get_at_lang_pack(locale: str = None) -> dict:
    """
    获取语言包
    :param locale: 语言包的语言代码，默认为AppConfig中的lang配置
    :return: 返回语言包字典
    """
    # from asteriskutils.setting import lang_pack
    try:
        if locale is None:
            locale = AppConfig.get("lang")
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'lang/{locale.lower()}.json'),'r',encoding='utf8') as fp:
            lang = json.load(fp)
            lang_pack = get_lang_pack(AppConfig["lang"].lower())
            for k,v in lang.items():
                lang_pack[k] = v
        return lang_pack
    except FileNotFoundError:
        lang_pack = get_lang_pack('zh-cn')
        wprint(f'语言包文件lang/{locale.lower()}.json不存在，使用默认语言包。')
        return lang_pack