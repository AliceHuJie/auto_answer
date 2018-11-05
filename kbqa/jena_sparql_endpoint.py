# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 往jena服务器发起查询, 封装的一些查询函数

from SPARQLWrapper import SPARQLWrapper, JSON
from collections import OrderedDict
import json


class JenaFuseki:
    def __init__(self, endpoint_url='http://localhost:3030/auto_answer_for_movie/query'):
        self.sparql_conn = SPARQLWrapper(endpoint_url)

    def get_sparql_result(self, query):
        self.sparql_conn.setQuery(query)
        self.sparql_conn.setReturnFormat(JSON)
        return self.sparql_conn.query().convert()

    @staticmethod
    def parse_result(query_result):
        """
        解析返回的结果
        :param query_result:
        :return:
        """
        try:
            query_head = query_result['head']['vars']
            query_results = list()
            for r in query_result['results']['bindings']:
                temp_dict = OrderedDict()
                for h in query_head:
                    temp_dict[h] = r[h]['value']
                query_results.append(temp_dict)
            return query_head, query_results
        except KeyError:
            return None, query_result['boolean']

    def print_result_to_string(self, query_result):
        """
        直接打印结果，用于测试
        :param query_result:
        :return:
        """
        query_head, query_result = self.parse_result(query_result)

        if query_head is None:
            if query_result is True:
                print('Yes')
            else:
                print('False')
            print()
        else:
            for h in query_head:
                print((h, ' '*5))
            print()
            for qr in query_result:
                for _, value in qr.items():
                    print(value, ' ', end=' ')
                print()

    def get_sparql_result_value(self, query_result):
        """
        用列表存储结果的值
        :param query_result:
        :return:
        """
        query_head, query_result = self.parse_result(query_result)
        if query_head is None:
            return query_result
        else:
            values = list()
            for qr in query_result:
                for _, value in qr.items():
                    values.append(value)
            return values


if __name__ == '__main__':
    fuseki = JenaFuseki()
    my_query = """
    PREFIX : <http://www.auto_answer_for_movie.com#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT  ?t WHERE {
            ?s :personName '姜文'.
            ?s rdf:type :Director.
               ?s :hasDirected ?m.
               ?m :movieTitle ?t.
            }
    """
    result = fuseki.get_sparql_result(my_query)
    result_value = fuseki.get_sparql_result_value(result)  # 列表形式打印结果
    # fuseki.print_result_to_string(result)
    print(result_value)