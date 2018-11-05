# # -*- coding: utf-8 -*-
# import json
#
# import pymysql
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# mysql_db = pymysql.connect(host="localhost", user="root", password='2736', db="anto_answer_for_movie", use_unicode=True,
#                            charset="utf8")
#
# mysql_cursor = mysql_db.cursor()
# # 测试时查看各个表数据量
# def get_count(request):
#     user_question = None
#     tables = {'actor': 0, 'director': 0, 'movie': 0}
#     sql_tpl = 'select count(*) as total from anto_answer_for_movie.%s_china'
#     for table in tables.keys():
#         sql = sql_tpl % table
#         mysql_cursor.execute(sql)
#         ret = mysql_cursor.fetchone()[0]
#         tables[table] = ret
#     return HttpResponse(json.dumps(tables), content_type='json')
#
#
# # 测试时查看一个电影及其相关信息
# @csrf_exempt
# def get_info(request):
#     movie_id = 0
#     response = {'movie': 0, 'actor': '', 'director': '', 'genre': '', 'country': '', 'language': ''}
#     params = json.loads(request.body)
#     movie_id = params['movie_id']
#
#     mysql_cursor = mysql_db.cursor()
#     actor_search = 'SELECT person_name FROM anto_answer_for_movie.movie_to_actor, actor_china where actor_id = person_id and movie_id = %d;' % int(movie_id)
#     mysql_cursor.execute(actor_search)
#     ret = mysql_cursor.fetchall()
#     response['actor'] = [i[0] for i in ret]
#
#     director_search = 'SELECT person_name FROM anto_answer_for_movie.movie_to_director, director_china where director_id = person_id and movie_id = %d;' % int(movie_id)
#     mysql_cursor.execute(director_search)
#     ret = mysql_cursor.fetchall()
#     response['director'] = [i[0] for i in ret]
#
#     genre_search = 'SELECT genre_name FROM anto_answer_for_movie.movie_to_genre_china where movie_id = %d;' % int(movie_id)
#     mysql_cursor.execute(genre_search)
#     ret = mysql_cursor.fetchall()
#     response['genre'] = [i[0] for i in ret]
#
#     country_search = 'SELECT country_name FROM anto_answer_for_movie.movie_to_country_china where movie_id = %d;' % int(movie_id)
#     mysql_cursor.execute(country_search)
#     ret = mysql_cursor.fetchall()
#     response['country'] = [i[0] for i in ret]
#
#     language_search = 'SELECT language_name FROM anto_answer_for_movie.movie_to_language_china where movie_id = %d;' % int(
#         movie_id)
#     mysql_cursor.execute(language_search)
#     ret = mysql_cursor.fetchall()
#     response['language'] = [i[0] for i in ret]
#     print(json.dumps(response))
#     return HttpResponse(json.dumps(response), content_type='json')