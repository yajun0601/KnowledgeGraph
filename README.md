# KnowledgeGraph
learn Knowledge Graph
知识图谱概念

之前看过米哥的一篇文章《知识图谱及金融相关》，文章主要是一些介绍，所以一直打算写个关于股票方面图谱的东西。关于知识图谱，概念有很多，具体大家可自行百度，我这里只摘录米哥之前的文章里面的概念。
什么是知识图谱？ 直接了当的说，知识图谱是人工智能技术的重要组成部分，它是具有语义处理与信息互联互通能力的知识库。通常在智能搜索、机器人聊天、智能问答以及智能推荐方面有着广泛的应用。 今天我们学习和探讨的知识图谱，实际是Google公司在2012年提出的为了提高搜索引擎能力，增强用户的搜索效率效果以及搜索体验的一种技术实践。 而在10年前，就已经提出了语义网的概念，呼吁业界推广并完善利用本体（Ontology）模型来形式化表达数据中的隐含语义，便于知识的高效呈现和利用。知识图谱技术的出现正是基于以上相关研究，是对语义网相关技术和标准的提升。

知识图谱中的一些概念要素： 

实体：是指具有可区别性且独立存在的某种事物(有点像面向对象编程里的Object)。如某一种动物、某一个城市、某一种水果、某一类商品等等。世界万物有具体事物组成，此指实体。实体是知识图谱中的最基本元素，不同的实体间存在不同的关系。 

语义类（概念）：概念主要指集合、类别、对象类型、事物的种类，例如人物、地理等。 属性：主要指对象可能具有的属性、特征、特性、特点以及参数，例如国籍、生日等。 

属性值：主要指对象指定属性的值，例如国籍对应的“中国”、生日对应1988-09-08等。每个属性-属性值对可用来刻画实体的内在特性。 

关系：用来连接两个实体，刻画它们之间的关联。形式化为一个函数，它把kk个点映射到一个布尔值。在知识图谱上，关系则是一个把kk个图节点(实体、语义类、属性值)映射到布尔值的函数。

知识图谱中一般用三元组的方式来表达，三元组的基本形式主要包括(实体1-关系-实体2)和(实体-属性-属性值)等。每个实体可用一个全局唯一确定的ID来标识，每个属性-属性值对可用来刻画实体的内在特性。

提取Tushare数据

这个是重点，关注Tushare有一段时间了，想写点什么东西，一直没有时间。

Tushare免费提供各类金融数据和区块链数据，这篇文章用的就是Tushare的数据做展示。Tushare支持很多种类型的数据，限于篇幅限制，我只能找最基础的属性建立一个简单的图谱。 属性为，股票所属的地区(area)，所属的工业分类(industry)，所属的版块(market)。 

获取该数据的API接口说明 ：

红框为需要用到的分类属性 

我们可以通过Python API获取数据，代码如下：

import tushare as ts

ts.set_token('...')  # token需要注册之后，然后获取到的token，这里就不写明我的token了
pro = ts.pro_api()
df = pro.stock_basic(exchange_id='', list_status='L', fields='ts_code,symbol, name,area,industry,fullname, enname, market,exchange, curr_type, list_status, list_date, delist_date,is_hs')  

# 股票的基本信息，这里面有三个股票的基本信息，地区(area)，工业类别(industry)，市场(market)


利用InteractiveGraph建立图谱

此处推荐另一个不错的开源项目InteractiveGraph，感谢原作者。 以下这是原项目的一个截图，数据是红楼梦的人物关系。

01
InteractiveGraph数据格式

完整的数据比较大，此处只写个简单的数据格式。 我们需要把Tushare返回的数据结构，改造为InteractiveGraph认识的数据结构。

import json
import os
import uuid

import pandas as pd

from data_hive import BASIC_DATA_STORE_FOLDER, GRAPH_DATA_FULLNAME


def __init_graph_categories():
    """
    将基础数据合并为图数据
    :return:
    """
    # 加载地区数据，工业指数，概念

    industry_fullname = os.path.join(os.environ['STOCK_DATA'], 'data_hive', 'basic_data', 'industry.csv')
    industry_series = pd.Series.from_csv(industry_fullname)
    industry_list = industry_series.tolist()
    concept_fullname = os.path.join(os.environ['STOCK_DATA'], 'data_hive', 'property_data', 'concept.csv')
    concept_dataframe = pd.read_csv(concept_fullname)
    concept_list = concept_dataframe['name'].tolist()

    dic_categories = dict()

    for concept in concept_list:
        dic_categories[concept] = concept
    for industry in industry_list:
        dic_categories[industry] = industry
    return dic_categories


def create_graph_data_job():
    dic_categories = {'Stock': '股票', 'Area': '地区', 'Industry': '工业分类', 'Market': '市场'}
    basic_fullname = os.path.join(BASIC_DATA_STORE_FOLDER, 'basic.csv')
    nodes = []
    edges = []
    basic_dataframe = pd.read_csv(basic_fullname)

    dic_area_id = __get_area_nodes(basic_dataframe, nodes)
    dic_industry_id = __get_industry_nodes(basic_dataframe, nodes)
    dic_market_id = __get_market_nodes(basic_dataframe, nodes)
    __get_stock_nodes(basic_dataframe, nodes)

    __get_stock_edges_with_area(basic_dataframe, dic_area_id, edges)
    __get_stock_edges_with_industry(basic_dataframe, dic_industry_id, edges)
    __get_stock_edges_with_market(basic_dataframe, dic_market_id, edges)

    dic = dict()
    dic['categories'] = dic_categories
    dic['data'] = dict()
    dic['data']['nodes'] = nodes
    dic['data']['edges'] = edges
    if os.path.exists(GRAPH_DATA_FULLNAME):
        os.remove(GRAPH_DATA_FULLNAME)
    with open(GRAPH_DATA_FULLNAME, 'w') as f:
        json.dump(dic, f, ensure_ascii=False)


InteractiveGraph数据格式:

{
    "categories": 
    {
        "Area": "地区",
        "Market": "市场",
        "Industry": "工业分类",
        "Stock": "股票"
    },
    "data":
    {
        "nodes": 
        [
            {
                "info": "",
                "value": 288,  // value是该分类，有多少支股票
                "label": "上海",
                "categories": ["Area"],
                "id": 186063112711690369465957503787509417235
            },
            {
                "info": "",
                "value": 130,
                "label": "专用机械",
                "categories": ["Industry"],
                "id": 186084073314365143238378290935655761171
            },
            {
                "info": "",
                "value": 931,
                "label": "中小板",
                "categories": ["Market"],
                "id": 186109520132514124716557123458730493203
            },
            {
                "info": "",
                "value": 1,
                "label": "平安银行",
                "categories": ["Stock"],
                "id": "000001.SZ"
            },
            ...
        ],
        "edges": 
        [
            {
                "label": "Area",
                "from": "000001.SZ",
                "to": 186078121060971771585817877132061902099,
                "id": 187756920664596399771974970653013640467
            }, 
            ...
        ]
    }
}


02

Flask发布服务



import os

from flask import Blueprint, request, redirect, render_template
from jinja2 import Environment, FileSystemLoader

graph = Blueprint('graph', __name__)

@graph.route('/graph/relation', methods=['GET'])
def get_relation():
    """
    :return:
    """
    logger.info('获取关系')
    stock1 = request.args.get('stock1')
    stock2 = request.args.get('stock2')
    return render_template('relation.html', stock1=stock1, stock2=stock2)




app = Flask(__name__)
app.register_blueprint(graph)

if __name__ == '__main__':
    app.run()


图谱效果



运行Flask服务后，我们可以在地址栏里输入地址，可以传入两个股票作为参数。


（请修改为自己的域名或者IP地址）

大致的效果如下：


