"""BookManager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include


# 使用namespace的时候需要增加app_name变量,或者直接在include中添加
# app_name = 'book'
urlpatterns = [
    path('admin/', admin.site.urls),

    # 给Book.urls的路由起一个别名，用作反向解析
    # re_path(r'^', include('Book.urls', namespace='book'))
    re_path(r'^', include(('Book.urls', 'book'), namespace='book')),

]
