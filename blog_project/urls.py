"""blog_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from blog.views import index, archive, article, comment_post, do_login, do_reg, do_logout, do_tag, do_category
from django.conf import settings
from blog.upload import upload_image

import django

urlpatterns = [
    path('', index, name="index"),
    path('admin/', admin.site.urls),
    path('uploads/<path:path>/', django.views.static.serve, {"document_root": settings.MEDIA_ROOT}),
    path('admin/upload/<path:dir_name>', upload_image, name='upload_image'),
    path('archive/<str:year>/<str:month>', archive, name='archive'),
    path('article/<str:year>/<str:month>/<str:day>/<int:article_id>', article, name='article'),
    path('comment/post', comment_post, name='comment_post'),
    path('login', do_login, name='login'),
    path('reg', do_reg, name='reg'),
    path('logout', do_logout, name='logout'),
    path('tag/<int:tag_id>', do_tag, name='tag'),
    path('category/<int:category_id>', do_category, name='category')
]
