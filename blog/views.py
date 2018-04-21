from django.shortcuts import render, redirect
from blog.models import Category
from blog.models import Ad
from blog.models import Article
from blog.models import Comment
from blog.models import User
from blog.models import Tag
from blog.models import Links
from blog_project import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from blog.forms import CommentForm, RegForm, LoginForm
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Count


# Create your views here.


def global_setting(request):
    # 分类标题加载
    category_list = Category.objects.all()

    # 广告数据加载
    ad_list = Ad.objects.all()[:5]

    # 归档分类加载
    archive_list = Article.objects.distinct_date()[:5]

    # 浏览排行数据
    click_list = Article.objects.all().order_by('-click_count')[:7]

    # 评论排行数据
    comment_rank_list = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by(
        '-comment_count')

    article_comment_list = [Article.objects.get(pk=comment['article']) for comment in comment_rank_list]

    # 作者推荐
    article_recommend_list = Article.objects.filter(is_recommend=1).order_by('-date_publish')

    # 标签分类数据
    tag_list = Tag.objects.all()

    # 友情链接
    friends_link_list = Links.objects.all()[:6]
    return {
        'blog_name': settings.BLOG_NAME,
        'blog_desc': settings.BLOG_DESC,
        'email': settings.EMAIL,
        'category_list': category_list,
        'ad_list': ad_list,
        'archive_list': archive_list,
        'click_list': click_list,
        'article_comment_list': article_comment_list,
        'article_recommend_list': article_recommend_list,
        'tag_list': tag_list,
        'friends_link_list': friends_link_list
    }


def index(request):
    is_index = True
    article_list = Article.objects.all()
    article_list = get_page(request, article_list)
    return render(request, "index.html", locals())


def archive(request, year, month):
    is_index = False
    article_list = Article.objects.filter(date_publish__icontains=year+'-'+month)
    article_list = get_page(request, article_list, 2)
    archive_year = year
    archive_month = month
    return render(request, 'archive.html', locals())


def article(request, year, month, day, article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return render(request, 'failure.html', {'reason': '没有找到相应的文章'})
        # 评论表单
    comment_form = CommentForm({'author': request.user.username,
                                'email': request.user.email,
                                'url': request.user.url,
                                'article': article_id} if request.user.is_authenticated else {'article': article_id})
    # 获取评论信息
    comments = Comment.objects.filter(article=article).order_by('id')
    comment_list = []
    for comment in comments:
        for item in comment_list:
            if not hasattr(item, 'children_comment'):
                setattr(item, 'children_comment', [])
            print('children_comment', item.children_comment)
            if comment.pid == item:
                item.children_comment.append(comment)
                break
        if comment.pid is None:
            comment_list.append(comment)
    article.click_count = article.click_count + 1
    article.save()
    return render(request, 'article.html', locals())


def comment_post(request):
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        # 获取表单信息
        comment = Comment.objects.create(username=comment_form.cleaned_data["author"],
                                         email=comment_form.cleaned_data["email"],
                                         url=comment_form.cleaned_data["url"],
                                         content=comment_form.cleaned_data["comment"],
                                         article_id=comment_form.cleaned_data["article"],
                                         user=request.user if request.user.is_authenticated else None)
        comment.save()
    else:
        return render(request, 'failure.html', {'reason': comment_form.errors})
    return redirect(request.META['HTTP_REFERER'])


def do_login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 登录
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                login(request, user)
            else:
                return render(request, 'failure.html', {'reason': '登录验证失败'})
            return redirect(request.POST.get('source_url'))
        else:
            return render(request, 'failure.html', {'reason': login_form.errors})
    else:
        login_form = LoginForm()
    return render(request, 'login.html', locals())


def do_logout(request):
    logout(request)
    return redirect(request.META['HTTP_REFERER'])


def do_reg(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            # 注册
            user = User.objects.create(username=reg_form.cleaned_data["username"],
                                       email=reg_form.cleaned_data["email"],
                                       url=reg_form.cleaned_data["url"],
                                       password=make_password(reg_form.cleaned_data["password"]), )
            user.save()

            # 登录
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
            login(request, user)
            return redirect(request.POST.get('source_url'))
        else:
            return render(request, 'failure.html', {'reason': reg_form.errors})
    else:
        reg_form = RegForm()
    return render(request, 'reg.html', locals())


def do_tag(request, tag_id):
    tag = None
    try:
        tag = Tag.objects.all().get(id=tag_id)
    except Tag.DoesNotExist:
        render(request, 'failure.html', {'reason': '没有找到相应的文章'})
    article_list = tag.article_set.all()
    article_list = get_page(request, article_list)
    return render(request, 'tag.html', locals())


def get_page(request, lists, pages=settings.PAGE_SETTING):
    paginator = Paginator(lists, pages)
    try:
        page = request.GET.get('page', 1)
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        lists = paginator.page(1)
    return lists


def do_category(request, category_id):
    try:
        category = Category.objects.all().get(id=category_id)
        article_list = category.article_set.all()
        article_list = get_page(request, article_list, 2)
    except Category.DoesNotExist:
        article_list = []
    return render(request, 'category.html', locals())
