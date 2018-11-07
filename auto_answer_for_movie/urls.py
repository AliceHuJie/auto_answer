"""auto_answer_for_movie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from kbqa import main_query

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auto_answer_for_movie/query', main_query.query),
    url(r'^auto_answer_for_movie/wx', main_query.wx_main),
    url(r'', main_query.index),
    url(r'^auto_answer_for_movie/', main_query.index),
]
