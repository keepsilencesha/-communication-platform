from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from app import myforms
from app import models
from django.core.paginator import Paginator
from django.db import transaction
import json
from django.db.models import F
from django.contrib.auth.decorators import login_required
import os
from know import settings


# Create your views here.
def login(request):
    if request.method == 'GET':

        return render(request, 'frist/login.html', locals())

    elif request.is_ajax():
        response = {'user': None, 'msg': None}
        name = request.POST.get('name')
        pwd = request.POST.get('password')

        user = auth.authenticate(request, username=name, password=pwd)
        if user:

            auth.login(request, user)
            response['user'] = name

            response['msg'] = '登录成功'
        else:
            # 用户名密码错误
            response['msg'] = '用户名或密码错误'

        return JsonResponse(response)


def register(request):
    if request.method == 'GET':
        my_forms = myforms.MyForm
        return render(request, 'frist/register.html', {'my_forms': my_forms})

    elif request.is_ajax():
        back = {'status': None, 'msg': None}
        myform = myforms.MyForm(request.POST)
        if myform.is_valid():

            back['status'] = 100
            dic = myform.cleaned_data
            dic.pop('re_password')
            title=request.POST.get('blog_title')
            print(title)
            site_name=request.POST.get('site_name')
            theme=request.POST.get('theme')
            models.Blog.objects.create(title=title,site_name=site_name,theme=theme)
            blog=models.Blog.objects.filter(site_name=site_name).first()


            dic['blog']=blog
            my_picture = request.FILES.get('my_picture')
            if my_picture:
                dic['avatar'] = my_picture
            models.UserInfo.objects.create_user(**dic)
        else:

            back['msg'] = myform.errors
        return JsonResponse(back)


def check_name(request):

    back = {'status': 200, 'msg': None}
    name = request.POST.get('name')

    user = models.UserInfo.objects.filter(username=name).first()

    if user:
        back['status'] = 100
        back['msg'] = '该用户已存在'

    return JsonResponse(back)


def index(request):
    article_list = models.Article.objects.all()
    paginator = Paginator(article_list, 4)
    try:
        current_page_num = int(request.GET.get('page'))
        current_page = paginator.page(current_page_num)
        if paginator.num_pages > 11:
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:
            page_range = paginator.page_range
    except Exception as e:
        current_page_num = 1
        current_page = paginator.page(current_page_num)
        page_range = range(1, 12)

    return render(request, 'home/index.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def article_detail(request, username, id):
    username = username
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')

    blog = user.blog

    article = models.Article.objects.filter(pk=id).first()

    # content_list=models.Commit.objects.filter(article=article)

    content_list = article.commit_set.all().order_by('pk')

    return render(request, 'site/article_detail.html', locals())


def user_blog(request, username, *args, **kwargs):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')
    blog = user.blog
    try:
        article_list = blog.article_set.all()
    except Exception as e:
        return redirect('/index/')

    condition = kwargs.get('condition')
    param = kwargs.get('param')
    if 'tag' == condition:
        article_list = article_list.filter(tag__pk=param)
    elif 'category' == condition:
        article_list = article_list.filter(category__pk=param)
    elif 'archive' == condition:
        archive_list = param.split('-')
        article_list = article_list.filter(create_time__year=archive_list[0], create_time__month=archive_list[1])
    return render(request, 'site/user_blog.html', locals())


def diggit(request):
    response = {'status': 100, 'msg': None}

    if request.user.is_authenticated():
        # 从前端传过来的数据,都转成str类型

        article_id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')
        is_up = json.loads(is_up)

        user = request.user
        # 存之前先查询,当前用户对该篇文章是否点过
        ret = models.UpAndDown.objects.filter(user_id=user.pk, article_id=article_id).exists()

        if ret:
            # 当有数据,说明,已经点过赞或者踩了
            response['msg'] = '您已经点过了'
            response['status'] = 101
        else:
            # 原子性操作.用事务

            with transaction.atomic():

                models.UpAndDown.objects.create(user=user, article_id=article_id, id_up=is_up)

                # 先取出文章的queryset对象
                article = models.Article.objects.filter(pk=article_id)
                if is_up:
                    article.update(up_num=F('up_num') + 1)
                    response['msg'] = '点赞成功'
                else:
                    article.update(down_num=F('down_num') + 1)
                    response['msg'] = '反对成功'
    else:
        response['msg'] = '请先登录'
        response['status'] = 102
    return JsonResponse(response)


def commit_content(request):
    back = {'status': 100, 'msg': None}

    if request.is_ajax():

        if request.user.is_authenticated():

            user = request.user
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')
            pid = request.POST.get('pid')
            print(user, article_id, content, pid)
            with transaction.atomic():

                ret = models.Commit.objects.create(user=user, article_id=article_id, content=content, parent_id=pid)

                models.Article.objects.filter(pk=article_id).update(commit_num=F('commit_num') + 1)

            back['msg'] = '评论成功'
            back['content'] = ret.content
            back['time'] = ret.create_time.strftime('%Y-%m-%d %X')
            back['user_name'] = ret.user.username
            if pid:
                back['parent_name'] = ret.parent.user.username
        else:

            back['status'] = 101
            back['msg'] = '您没登录'
    else:
        back['status'] = 101
        back['msg'] = '您的要求非法'
    return JsonResponse(back)


@login_required(login_url='/login/')
def backend(request):
    if request.method == 'GET':
        # 查询出当前登录用户的所有文章
        blog = request.user.blog
        article_list = models.Article.objects.filter(blog=blog)
        return render(request, 'back/backend.html', {"article_list": article_list})


from bs4 import BeautifulSoup


@login_required(login_url='/login/')
def add_article(request):
    if request.method == 'GET':
        return render(request, 'back/add_article.html', )

    elif request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]

        models.Article.objects.create(title=title, desc=desc, content=str(soup), blog=request.user.blog)

        return redirect('/backend/')


def upload_img(request):
    myfile = request.FILES.get('myfile')
    path = os.path.join(settings.BASE_DIR, 'media', 'img')
    if not os.path.isdir(path):
        os.mkdir(path)
    file_path = os.path.join(path, myfile.name)
    with open(file_path, 'wb') as f:
        for line in myfile:
            f.write(line)
    dic = {'error': 0, 'url': '/media/img/%s' % myfile.name}
    return JsonResponse(dic)


@login_required
def update_head(request):
    if request.method=='GET':
        return render(request,'home/update_head.html')
    else:
        myfile = request.FILES.get('head')
        user = request.user
        user.avatar = myfile
        user.save()
        return redirect('/index/')


def update_article(request,pk):
    if request.method=='GET':
        return render(request,'back/update_article2.html',{'article_id':pk})

def get_article(request, pk):
    article = models.Article.objects.get(pk=pk)

    return JsonResponse({'title': article.title, 'content': article.content})




def error(request):
    if request.method == 'GET':
        return render(request, 'error.html', locals())
