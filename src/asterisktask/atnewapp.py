import argparse
import os
from colorama import init
import shutil

# 解决Window环境中打印颜色问题
init(autoreset=True)

'''
用于创建基于Asterisk-Task的项目

'''
def main()->None:
    
    parser = argparse.ArgumentParser(description='创建asterisk-task的任务项目')
    parser.add_argument('-app', metavar='P', type=str, default='asterisk_demo', \
        help='项目名称，如未提供使用默认名称')
    
    project_name = parser.parse_args().app if parser.parse_args() else 'asterisk_demo'

    if project_name.find('-') > -1:
        print(f'\033[31m创建[{project_name}]项目失败，项目名称中不得包含“-”。\033[0m')
        return
    
    try:
        # 以项目名称创建项目名称目录
        print(f'\033[36m正在创建[{project_name}]项目目录...\033[0m')
        os.mkdir(project_name)
        
        # 添加package的init文件
        fw = open(f'{project_name}/__init__.py','w',encoding='utf8')
        fw.close()

        # 读取默认AppConfig.json然后替换project_name后写入项目中
        print(f'\033[36m正在创建[{project_name}]项目的默认配置文件...\033[0m')
        __add_project_default_files('AppConfig.json.attpl',project_name)

        # 读取默认setting模版，然后替换project_name后写入项目中
        print(f'\033[36m正在创建[{project_name}]项目的配置载入文件...\033[0m') 
        __add_project_default_files('setting.py.attpl',project_name)
        

        # 读取默认setting模版，然后替换project_name后写入项目中
        print(f'\033[36m正在创建[{project_name}]项目的默认任务类...\033[0m')
        __add_project_default_files('tasks.py.attpl',project_name)


        print(f'\033[36m正在创建[{project_name}]项目的启动文件...\033[0m')
        __add_project_default_files('run.py.attpl',project_name,is_startup_file=True)
        '''
        在后续版本中支持生成setup脚本
        print(f'\033[36m正在创建[{project_name}]项目的setup.py文件...\033[0m')
        __add_project_default_files('setup.py.attpl',project_name,is_setup_file=True)
        在后续版本中支持生成setup脚本
        '''
    except FileExistsError:
        # 如果项目名称目录已存在，无法继续
        if os.path.isfile(f'run_{project_name}.py'):
            print(f'\033[31m[{project_name}]项目已经存在，若需要重新创建，请移除项目目录，并重新执行命令。\033[0m')
            return
        else:
            print(f'\033[31m无法创建[{project_name}]项目，因当前目录中已经有该项目名称的目录。请更改项目名称后再试。\033[0m') 
            return
    except:
        print('\033[31m创建项目失败\033[0m') # 调试时使用
        # error_print('创建项目失败') # 调试时需要注释
    if os.path.isfile(f'run_{project_name}.py'):
        print(f'\033[32m[{project_name}]项目创建成功!请键入命令“python3 run_{project_name}.py”,以验证安装成功。\033[0m')
    else:
        __del_file(project_name)
        print('\033[31m创建项目失败，请重新尝试\033[0m')



def __del_file(path):
    '''
    删除目录以及目录下文件和子目录
    Args:
        path(str):目录的径路
    '''

    if not os.listdir(path):
        shutil.rmtree(path)
    else:
        for i in os.listdir(path):
            path_file = os.path.join(path,i)  #取文件绝对路径
            print(path_file)
            if os.path.isfile(path_file):
                os.remove(path_file)
            else:
                __del_file(path_file)
                shutil.rmtree(path_file)




def __add_project_default_files(template_filename:str,project_name:str,is_startup_file=False,is_setup_file=False)->None:
    '''
    创建项目时，需要增加项目目录，以及目录中的默认配置文件等。
    Args:
        template_filename(str):模版文件名，默认路径在asterisktask下
        project_name(str):项目名称
        is_startup_file(bool):是否为项目启动文件的标识，是为启动文件。默认为否
    
    '''
    target_file = template_filename.replace('.attpl','')
    fp = open(os.path.join(os.path.dirname(__file__),template_filename),'r',encoding='utf8')
    txt = fp.read()
    txt = txt.replace("{project_name}",project_name)
    fw = open(f'run_{project_name}.py','w',encoding='utf8') if is_startup_file \
        else  open(f'{project_name}_{target_file}','w',encoding='utf8') if is_setup_file \
        else open(f'{project_name}/{target_file}','w',encoding='utf8')
    fw.write(txt)
    fw.close()
    

if  __name__ == "__main__":
    main()

