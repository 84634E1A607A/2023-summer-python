from django.urls import path
import Blog.views as views

urlpatterns = [
    path('', views.Index, name='default'),
    path('Index', views.Index, name='index'),
    path('Search', views.Search, name='search'),
    # path('Search/Init', views.InitSearchDb, name='initSearch'),
    # path('Import', views.ImportNewsData, name='import'),
    path('View/<str:document_id>', views.ViewNews, name='view'),
    path('Comment', views.Comment, name='comment'),
    # path('Comment/Clear', views.ClearComment, name='clearComment'),
    # path('Comment/Import', views.ImportComment, name='importComment'),
    # path("Comment/Update", views.UpdateCommentCount, name="updateCommentCount"),
    path('List', views.ListNews, name='list'),
    path('Categories', views.Categories, name='categories'),
    # path('Categories/Import', views.ImportNewsCategories, name='importCategories'),
    path('Analysis', views.Analysis, name='analysis'),
    path('Document', views.Document, name='document'),
]
