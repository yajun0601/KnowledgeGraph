# coding: utf-8
# @Time    : 2019-04-09 15:58
# @Author  : Libra
# @Site    : 
# @File    : app_liang.py

import os
import sys

from flask import Flask

sys.path.append(".." + os.path.sep)
from webapp.views.graph_view import graph

app = Flask(__name__)
app.register_blueprint(graph)

if __name__ == '__main__':
    app.run()
