# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 作为web后台提供的唯一查询接口
import hashlib
import logging
import os
import random
import time
import xml.etree.cElementTree as ET

from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from kbqa.jena_sparql_endpoint import JenaFuseki
from kbqa.question2sparql import Question2Sparql
from kbqa.wx_msg import TextMsg

logger = logging.getLogger('django')
ques_logger = logging.getLogger('ques_logger')
fuseki = JenaFuseki()  # 预加载jeneFuseki连接对象
print('Fuseki server service start success ...')
q2s = Question2Sparql()  # 运行该文件的时候就加载好q2s对象，避免重复创建该对象导致的模型加载等的耗时
print('q2s service start success ...')
# 加载模型后先使用测试数据预测一下，不然等到接收的问句去预测时会报错
my_query = q2s.get_sparql(u'电影功夫之王有哪些演员？')
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
    sparql, label, func, new_question, slots = q2s.get_sparql(question)
    if label == -1:
        answer = '抱歉，暂不能回答您的这个问题'
    elif sparql is None:
        answer = u'抱歉，您提供的信息不够完整'
    else:
        result = fuseki.get_sparql_result(sparql)  # json形式的查询结果
        answer = fuseki.get_sparql_result_value(result)  # 列表形式的查询结果
        if len(answer) == 0:
            answer = u'抱歉，暂时查不到该问题答案'
        else:
            answer = ','.join(answer)
    ques_logger.info(
        msg='{question} {label} {func} {new_question} {slots} [{answer}]'.format(question=question, label=label,
                                                                                 func=func, new_question=new_question,
                                                                                 slots=slots, answer=answer[
                                                                                                     :20] + '...'))  # TODO 记录实体识别效果
    return answer


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
    from_user_name = root.find('FromUserName').text
    msg_type = root.find('MsgType').text
    if msg_type == 'text':
        userid = requests.GET['openid']
        question = root.find('Content').text
        if userid == 'o4QWQ1krAxO88bVEL7HW0S7QyXTc':
            return TextMsg(from_user_name, to_user_name, to_tang()).send()
        return TextMsg(from_user_name, to_user_name, query(question)).send()
    elif msg_type == 'image':
        # url = 'http://img1.imgtn.bdimg.com/it/u=3992277371,3755901066&fm=27&gp=0.jpg'
        # return ImageMsg(from_user_name, to_user_name, media_id).send()
        return TextMsg(from_user_name, to_user_name, '图片已接收到').send()
    elif msg_type == 'voice':
        return TextMsg(from_user_name, to_user_name, '语音已接收到').send()
    elif msg_type == 'video':
        return TextMsg(from_user_name, to_user_name, '视频已接收到').send()
    elif msg_type == 'shortvideo':
        return TextMsg(from_user_name, to_user_name, '小视频已接收到').send()
    else:
        return TextMsg(from_user_name, to_user_name, '不支持该数据类型').send()


def to_tang():
    msgs = ['死胖子你在干啥子呢？', '狗娃儿我想你了！', '狗胖', '你是狗胖啊？', '想你，要抱抱。', '爱你哦~', '么么哒', 'MUAMUA', '抱~~', '我爱你', '要抱', '你看你好特殊，公众号超级VIP']
    return random.choice(msgs)


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

