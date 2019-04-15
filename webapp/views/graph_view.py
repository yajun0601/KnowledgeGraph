# coding: utf-8
# @Time    : 2019-04-09 14:18
# @Author  : Libra
# @Site    : 
# @File    : graph_view.py

from flask import Blueprint, request, render_template

graph = Blueprint('graph', __name__)


@graph.route('/graph/relation', methods=['GET'])
def get_relation():
    """
    :return:
    """
    stock1 = request.args.get('stock1')
    stock2 = request.args.get('stock2')
    return render_template('relation.html', stock1=stock1, stock2=stock2)
