

# 🧪 TDEase - Top-Down Proteomics Tools


## Language
[English](README.md)| [中文](README_zh.md)

##  ✨ 介绍
✨ TDEase 是专为Top-Down蛋白组学研究设计的自动化数据处理与交互式可视化工具集，

能够帮助实验室快速搭建Top-Down 蛋白组学工作流中的数据处理以及可视化展示部分.

包含两个核心模块：
- 🛠️ **TDpipe**：自动化数据处理流水线
- 📊 **TDvis**：交互式数据可视化平台


## 🌟 核心优势

1. **一键部署** 🚀  
   两个模块均提供即用型exe封装，无需复杂配置
2. **详略得当的UI设计** :
    - TDpipe 采用pyQt来生成复杂的的数据处理流程控制界面,便于实验平台管理员进行高自由度的操作
    - TDvis 采用streamlit来生成风格简约,几乎无参数的操作界面,方便查看数据的用户快速上手
3.  通过python的[http.server](https://docs.python.org/3.13/library/http.server.html)服务对可视化模块进行内网部署,以便于协作者进行远程的访问.而不必传输体积庞大的质谱数据.
    - ⚠️ 注意：由于HTTP明文传输特性，不建议部署在公网环境
    - 对于内网外的合作者,您可以直接发送结果文件,用户可以自行使用TDvis进行查看.

---

## 快速开始:

### 📥安装
直接下载发行版压缩包，解压后双击对应exe即可运行：
- `TDvis.exe`：本地单机版（无用户管理）
- `TDvis_web.exe`：带用户认证的Web版

🌐 访问方式：  
`http://{您的IP}:8501`


TDvis提供了两个平行的exe入口,
**TDvis.exe:**
可以运行没有用户管理界面的本地版本(协作者同样可以在内网环境下查看您的数据,不过文件需要您自行选择,访问者无权选择)

**TDvis_web.exe:**
可以提供用用户管理界面的版本,在完成管理用户的数据库的配置之后,即可进行测试平台的部署.

两种方式均将程序映射到您的8501端口,用户可以通过您的ip加上端口访问到您希望进行分享

```
http://{your_ip}:8501
```

的质谱数据


### TDpipe工作流配置

### TDvis数据库配置
如果您不需要用户认证,那么您可以忽略该部分

#### postgreSQL
TDvis_web版本默认使用[PostgreSQL](https://www.postgresql.org/)数据库进行用户管理

PostgreSQL官方提供了详细的引导文档,因此您只需要按照引导下载pgAdmin进行初始的数据库创建

而后在TDvis/DBUtils/dbconfig.toml中进行配置即可!

#### SQlite

数据库已经存在,您只需要将参数文件修改为如下格式,即可使用内置的SQlite先进行试验性的部署.
```
[database]
mode = "sqlite"
dbname = "{your_path}/TDEase/TDVis/src/DBUtils/TDvis_sqlite3.db"
```

## 开发者:

*如果您有自己的独特功能需求,我们欢迎您参与修改*

以下为推荐合作开发者使用的下载方式


1.  源代码下载
```pwsh
git clone https://github.com/Elcherneske/TDEase.git && cd TDease
```

2. 依赖安装

我们推荐您通过[uv](https://docs.astral.sh/uv/)来代替pip来进行快速的部署.

```pwsh
uv install -r requirements.txt
```

如果您地处国内,可以使用以下命令行


```pwsh
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

当然,您也可以选择使用[conda](https://anaconda.org/anaconda/conda)来进行环境的管理(较慢,但是能够重复使用于多个不同的项目文件夹):


```pwsh
conda create -n tdvis python=3.10 -y
conda activate tdvis
pip install -r requirements.txt
```


### TDpipe
TDpipe 使用pyQt进行图形化界面的展示,其内容存储于`GUI`文件夹中


### TDvis

1.  运行streamlit

我们的web服务框架是基于[streamlit](https://docs.streamlit.io/develop/api-reference)进行搭建的.因此如果您要进行合作开发以及调试的话,请在TDvis文件夹下运行指令:

```pwsh
streamlit run MainPage.py
```


2. 封装

由于streamlit需要命令行去启动,因此我们为您创建了launch.py文件来执行命令行,在运行pyintaller的时候就会将其作为封装的目标.

您可以在虚拟环境(经过测试,在cmd命令行下可以成功操作,而在powershell下可能会无法进入虚拟环境)下先运行

```pwsh
pip install pyinstaller
```


launch.spec的打包配置文件已经准备好了,如果你希望修改图标或者添加新的依赖,可以自行在其中进行调整.
然后在TDvis文件夹下运行:

```pwsh
pyinstaller launch.spec --clean
```


## TDpipe

TDpipe 是一个有GUI的Top-Down蛋白组学数据处理流程整合工具. 通过丰富的按键,您能够轻易调动各个模块,进行workflow参数设置,并且全程自动运行该workflow.


## TDvis

TDvis 通过获取TDpipe所处理生成的TopPic处理结果去进行进行可交互式的可视化.能够帮助专业的研究人员快速从Featuremap定位到目标蛋白质并且进行自定义的修饰分析.

基于简单的单线操作逻辑以及每一步充分的引导,TDvis对于不了解蛋白组学的用户 而言也能够快速走进TopDown数据的花园

其具体的用户使用手册已经被嵌入到程序内部.您可以在运行程序之后再尽情探索.



## 出版论文
如果您觉得我们的工作对您有帮助,欢迎您在您的论文中引用我们的工作:
