from django.shortcuts import render
from .models import News, NewsComment, NewsKeyword, NewsCategory
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, QueryDict
from django.urls import reverse
import random
import datetime
import sqlite3
import re
import math
import time
from .search import PerformSearch, GenerateIndex

NewsImagePattern = re.compile(r'<_IMAGE_(\d+)_.*?\.(\w+)_/>')
SearchResult = {
    'time': 0,
    'data': [],
}


def Index(request):
    # Get 20 random news
    news_list = list(News.objects.order_by('?')[:20])
    random.shuffle(news_list)

    for i in range(0, len(news_list)):
        news_list[i].keywords = NewsKeyword.objects.filter(news=news_list[i])
        news_list[i].created_time = news_list[i].created_at.strftime(
            '%Y-%m-%d %H:%M')

    return render(request, 'index.html', {'page_title': '首页', 'news_items': news_list, 'categories': NewsCategory.objects.all()})


def Search(request):
    if request.method == 'POST':
        global SearchResult

        redirect, SearchResult = PerformSearch(request)

        return redirect

    return render(request, 'search.html', {'page_title': '搜索', 'categories': NewsCategory.objects.all()})


def InitSearchDb(request):
    return GenerateIndex(request)


# Import news data from local db
def ImportNewsData(request):
    # The following line adds 'other' as a category
    # NewsCategory(category="其它", id=0).save()

    # The following lines are to fix the bug where summary is None
    # for news in News.objects.filter(summary="None"):
    #     news.summary = news.content[:100]
    #     news.save()

    # The following lines are to fix the bug where summary contains image placeholder
    # for news in News.objects.raw("SELECT * FROM Blog_news WHERE summary LIKE '%<_IMAGE_%'"):
    #     news.summary = NewsImagePattern.sub('', news.content)[:100]
    #     news.save()

    # The following lines are to re-import timestamp after turning off timezone support
    # conn = sqlite3.connect("../newsInfo.db")
    # cursor = conn.execute("SELECT docid, created_at FROM news")
    # for row in cursor:
    #     News.objects.raw("UPDATE Blog_news SET created_at = ? WHERE document_id = ?", [row[1], row[0]])

    return HttpResponse("Import Prohibited")
    News.objects.all().delete()
    conn = sqlite3.connect("../newsInfo.db")
    cursor = conn.execute(
        "SELECT news.docid, title, author, media_name, tags, summary, created_at, url, contents.content FROM news LEFT JOIN contents ON news.docid = contents.docid WHERE content_downloaded = 1")
    for row in cursor:
        News(title=row[1],
             summary=row[5] if row[5] is not None and row[5] != "" else row[8][:100],
             content=row[8],
             author=row[2],
             media_name=row[3],
             tags=row[4],
             created_at=datetime.datetime.utcfromtimestamp(row[6]),
             document_id=row[0],
             source_url=row[7]
             ).save()
    conn.close()
    return HttpResponse("Import success")


def ViewNews(request, document_id: str):
    news = News.objects.get(document_id=document_id)
    news.category_name = NewsCategory.objects.get(id=news.category).category

    news.comments = NewsComment.objects.filter(
        news=news).order_by('-created_at')
    for comment in news.comments:
        comment.created_time = comment.created_at.strftime('%Y-%m-%d %H:%M')

    news.keywords = NewsKeyword.objects.filter(news=news)
    news.created_time = news.created_at.strftime('%Y-%m-%d %H:%M')
    news.content = NewsImagePattern.sub(
        f'<br /> <img src="/static/crawled/{news.document_id}_\\1.\\2" style="" /> <br />', news.content)
    news.content = news.content.replace('\n', '<br /><br />')
    return render(request, 'viewNews.html', {'page_title': news.title, 'news': news})


def Comment(request):
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        user = request.POST.get('user')
        content = request.POST.get('content')

        if document_id is None or user is None or content is None or document_id == '' or user == '' or content == '':
            return JsonResponse({'status': 'failed'})

        try:
            NewsComment(news=News.objects.get(document_id=document_id), user=user,
                        content=content, created_at=datetime.datetime.now()).save()

            news = News.objects.get(document_id=document_id)
            news.comment_count += 1
            news.save()
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
        return JsonResponse({'status': 'success'})

    if request.method == 'DELETE':
        delete_data = QueryDict(request.body)
        comment_id = delete_data.get('id')
        if comment_id is None or comment_id == '':
            return JsonResponse({'status': 'failed'})

        try:
            comment = NewsComment.objects.get(id=comment_id)
            news = comment.news
            news.comment_count -= 1
            news.save()
            comment.delete()
        except:
            return JsonResponse({'status': 'failed'})
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'})


def ClearComment(request):
    return HttpResponse("Clear Prohibited")
    NewsComment.objects.all().delete()
    return HttpResponse("Clear success")


def ImportComment(request):
    return HttpResponse("Import Prohibited")

    NewsComment.objects.all().delete()

    conn = sqlite3.connect("../newsInfo.db")
    cursor = conn.execute(
        'SELECT docid, username, content, created_at FROM comments')

    for row in cursor:
        NewsComment(news=News.objects.get(document_id=row[0]),
                    user=row[1],
                    content=row[2],
                    created_at=datetime.datetime.utcfromtimestamp(row[3])).save()
    
    return HttpResponse("Import success")


def UpdateCommentCount(request):
    return HttpResponse("Update Prohibited")

    for news in News.objects.all():
        news.comment_count = NewsComment.objects.filter(news=news).count()
        news.save()
    
    return HttpResponse("Update success")

def ListNews(request):
    page_size = request.GET.get('page_size') if request.GET.get(
        'page_size') is not None else 20
    page_index = int(request.GET.get('page_index')) if request.GET.get(
        'page_index') is not None else 1
    is_search_mode = int(request.GET.get('search')) if request.GET.get(
        'search') is not None else 0

    if is_search_mode == 1:
        news_category = -1
        news_count = len(SearchResult["data"])
        news_list = SearchResult["data"][(
            int(page_index) - 1) * int(page_size):int(page_index) * int(page_size)]

    else:
        news_category = int(request.GET.get('news_category')) if request.GET.get(
            'news_category') is not None else -1
        if news_category == -1:
            news_count = News.objects.count()
            news_list = list(News.objects.order_by(
                '-created_at')[(int(page_index) - 1) * int(page_size):int(page_index) * int(page_size)])
        else:
            news_count = News.objects.filter(category=news_category).count()
            news_list = list(News.objects.filter(category=news_category).order_by(
                '-created_at')[(int(page_index) - 1) * int(page_size):int(page_index) * int(page_size)])

    for i in range(0, len(news_list)):
        news_list[i].keywords = NewsKeyword.objects.filter(news=news_list[i])
        news_list[i].created_time = news_list[i].created_at.strftime(
            '%Y-%m-%d %H:%M')

    return render(request, 'listNews.html', {
        'page_title': '搜索结果' if is_search_mode == 1 else '新闻列表',
        'news_items': news_list,
        'news_count': news_count,
        'news_category': news_category,
        'page_size': page_size,
        'page_index': page_index,
        'page_count':  math.ceil(news_count / int(page_size)),
        'is_search': is_search_mode,
        'search_time': SearchResult["time"],
    })


def Categories(request):
    categories = NewsCategory.objects.all()
    for category in categories:
        category.news_count = News.objects.filter(category=category.id).count()

    return render(request, 'categories.html', {'page_title': '新闻分类', 'categories': categories})


def ImportNewsCategories(request):
    return HttpResponse("Import Prohibited")
    NewsCategory.objects.all().delete()
    for media_name in ["创事记", "太平洋电脑网", "IT之家", "新浪科技", "新浪科技综合", "快科技2018", "CNMO"]:
        NewsCategory(category=media_name).save()

    categories = list(NewsCategory.objects.all())
    categories = dict([(category.category, category.id)
                      for category in categories])
    for news in News.objects.all():
        if news.media_name in categories:
            news.category = categories[news.media_name]
        else:
            news.category = 0
        news.save()

    return HttpResponse("Import success")


def Analysis(request):
    return render(request, 'analysis.html', {'page_title': '数据分析'})

def Document(request):
    return render(request, 'document.html', {'page_title': '开发文档'})