from setuptools import setup,find_packages
import time,json,os

'''
只提供setup.py文件，setup.cfg文件将在后续版本提供
使用以下命令生成whl文件：
python3.12 -m build
使用以下命令上传pypi
python3.12 -m twine upload dist/*
注意：需要提前安装wheel包
'''

# 读取软件的版本号
with open('src/asterisktask/setup/asterisk.json','r',encoding='utf8') as fp:
    setting = json.load(fp)
# 生成版本号，带有时间戳
build_no = time.strftime('%m%d.%H%M',time.localtime())
# 该版本号将在后续版本中以package的属性实现，以便于setup.cfg文件方便使用
with open('README.md','r', encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    name="asterisk-task",  #pypi中的名称，pip或者easy_install安装时使用的名称
    version="{}.{}".format(setting['version'],build_no),
    author="Shan,Tian",
    author_email="geoshan@163.com",
    description=("Task management system."),
    license="Apache License 2.0",
    keywords="task,scheduled task",
    packages=find_packages(where="src/",exclude=['build','dist','*egg*','submarine','asterisk_dev']),  # 需要打包的目录列表，排除测试项目以及build之后产生的目录
    package_dir={'': 'src'},  # 包对应的目录，""表示src目录
    # 需要安装的依赖
    install_requires=[
        'requests>=2.31.0',
        'colorama>=0.4.4',
        'prettytable>=3.1',
        'schedule>=1.1.0',
        'Deprecated >=1.2.13',
        'asterisk-utils >= 0.1.0',
        'sqlalchemy >=2.0.36'
    ],
    include_package_data=True,


    package_data={
        # If any package contains *.json or *.attpl or *.config files, include them:
        "": ["*.json", "*.attpl","*.config"]    
    },

    # Python版本的要求
    python_requires='>=3.10.0',

    platforms='Independent',

    # 添加这个选项，是为了在安装后，可以使用命令行自动生成项目文件和目录，以及目录下的默认配置文件等
    # 注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
        'atnewapp = asterisktask.atnewapp:main',
    ]},

    long_description=long_description, # 本段代码将在编辑readme后使用
    long_description_content_type='text/markdown',
    classifiers=[  # 程序的所属分类列表
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10"
    ],
    # 此项需要，否则卸载时报windows error
    zip_safe=False
)