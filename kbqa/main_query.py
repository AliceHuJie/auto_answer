# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 作为web后台提供的唯一查询接口
from kbqa.jena_sparql_endpoint import JenaFuseki
from kbqa.question2sparql import Question2Sparql
import logging
from django.shortcuts import render
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import xml.etree.cElementTree as ET
import hashlib
import time
import os

logger = logging.getLogger('django')

fuseki = JenaFuseki()  # 预加载jeneFuseki连接对象
q2s = Question2Sparql()  # 运行该文件的时候就加载好q2s对象，避免重复创建该对象导致的模型加载等的耗时
# 加载模型后先使用测试数据预测一下，不然等到接收的问句去预测时会报错
ques = [u'电影功夫之王有哪些演员？']
for q in ques:
    my_query = q2s.get_sparql(q)
    print(my_query)
    print('服务启动成功......')


def index(request):
    return render(request, 'index.html')


def query(question):
    """
    根据问题返回查询结果
    :param question: 自然语言问题
    :return: 答案
    """
    # TO DO 问题写入文件记录
    sparql = q2s.get_sparql(question)
    print(sparql)  # 打印出转换后的查询语句
    result = fuseki.get_sparql_result(sparql)  # json形式的查询结果
    answer = fuseki.get_sparql_result_value(result)  # 列表形式的查询结果
    return '，'.join(answer)


@csrf_exempt
def wx_main(request):
    if request.method == "GET":
        signature = request.GET.get('signature', None)    # 接收微信服务器get请求发过来的参数
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echo_str = request.GET.get('echostr', None)
        token = settings.TOKEN  # 服务器配置中的token
        hash_list = [token, timestamp, nonce]
        hash_list.sort()
        hash_str = ''.join([s for s in hash_list])
        hash_str = hashlib.sha1(hash_str.encode('utf-8')).hexdigest()
        print(hash_str, signature)
        if hash_str == signature:
            return HttpResponse(echo_str)
        else:
            return HttpResponse("field")
    else:
        data = auto_reply(request)
        return HttpResponse(data.encode('utf-8'))


def auto_reply(requests):
    web_data = requests.body
    root = ET.fromstring(web_data)
    to_user_name = root.find('ToUserName').text
    # from_user_name = root.find('FromUserName').text
    # create_time = root.find('CreateTime').text
    msg_type = root.find('MsgType').text
    # msg_id = root.find('MsgId').text
    if msg_type == 'text':
        question = root.find('Content').text
        return create_xml(ToUserName=requests.GET['openid'], FromUserName=to_user_name, CreateTime=int(time.time()),
                          MsgType='text', Content=query(question))
    elif msg_type == 'image':
        resource_url = root.find('PicUrl').text
        return create_xml(ToUserName=requests.GET['openid'], FromUserName=to_user_name, CreateTime=int(time.time()),
                          MsgType='text', Content='图片已经接收\nUrl:%s' % resource_url)
    elif msg_type == 'voice':
        return create_xml(ToUserName=requests.GET['openid'], FromUserName=to_user_name, CreateTime=int(time.time()),
                          MsgType='text', Content='语音已接收到')
    elif msg_type == 'video':
        return create_xml(ToUserName=requests.GET['openid'], FromUserName=to_user_name, CreateTime=int(time.time()),
                          MsgType='text', Content='视频已接收到')
    elif msg_type == 'shortvideo':
        return create_xml(ToUserName=requests.GET['openid'], FromUserName=to_user_name, CreateTime=int(time.time()),
                          MsgType='text', Content='小视频已接收到')
    else:
        return create_xml(ToUserName=requests.GET['openid'], FromUserName=to_user_name, CreateTime=int(time.time()),
                          MsgType='text', Content='不支持该数据类型')


def log(text):  # 记录装饰器
    def decorator(func):
        def wrapper(*args, **kwargs):
            print('Pid:%s running %s [function:%s] at %s' % (
                os.getpid(), text, func.__name__, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            return func(*args, **kwargs)
        return wrapper
    return decorator


xml_template = '<xml> <ToUserName>< ![CDATA[%s] ]></ToUserName> <FromUserName>< ![CDATA[%s] ]></FromUserName> <CreateTime>%s</CreateTime> <MsgType>< ![CDATA[%s] ]\
        ></MsgType> <Content>< ![CDATA[%s] ]></Content> </xml>'


def create_xml(**kwds):  # 生成返回消息的XML
    return (xml_template % (
    kwds['ToUserName'], kwds['FromUserName'], kwds['CreateTime'], kwds['MsgType'], kwds['Content'])).replace(' ', '')

