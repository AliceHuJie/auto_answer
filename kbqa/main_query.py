# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 作为web后台提供的唯一查询接口
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from kbqa.jena_sparql_endpoint import JenaFuseki
from kbqa.question2sparql import Question2Sparql
import json
import logging


logger = logging.getLogger('django')
logger2 = logging.getLogger('kbqa')
fuseki = JenaFuseki()  # 预加载jeneFuseki连接对象
q2s = Question2Sparql()  # 运行该文件的时候就加载好q2s对象，避免重复创建该对象导致的模型加载等的耗时
# 加载模型后先使用测试数据预测一下，不然等到接收的问句去预测时会报错
ques = [u'电影功夫之王有哪些演员？', u'成龙演过什么电影？', u'电影功夫之王有哪些演员？', u'电影功夫之王有哪些演员？']
for q in ques:
    my_query = q2s.get_sparql(q)
    print(my_query)


def index(request):
    return render(request, 'index.html')


def get_question(request):
    """
    从Http请求中获取用户的问题
    :param request: http 请求
    :return: 用户的问题
    """
    method = request.method
    if method == 'GET':
        return request.GET.get('question')
    else:
        params = json.loads(request.body)
        return params['question']


@csrf_exempt
def query(request):
    question = get_question(request)
    print(question)
    logger.info('question:' + question)  # 记录用户提过的问题
    sparql = q2s.get_sparql(question)
    print(sparql)  # 打印出转换后的查询语句
    result = fuseki.get_sparql_result(sparql)  # json形式的查询结果
    answer = fuseki.get_sparql_result_value(result)  # 列表形式的查询结果
    print(answer)
    response = {
        'data': answer
    }
    return HttpResponse(json.dumps(response), content_type='json')
