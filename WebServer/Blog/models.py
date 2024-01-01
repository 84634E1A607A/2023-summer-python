from django.db import models

class News(models.Model):
    title = models.CharField(max_length=100, null=False)
    summary = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    author = models.CharField(max_length=30, null=True)
    media_name = models.CharField(max_length=30, null=True)
    tags = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=False, null=False)
    document_id = models.CharField(max_length=30, null=False, unique=True, db_index=True)
    source_url = models.CharField(max_length=100, null=False)
    category = models.IntegerField(null=False, default=0)
    comment_count = models.IntegerField(null=False, default=0)

class NewsComment(models.Model):
    id = models.AutoField(primary_key=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    user = models.CharField(max_length=30, null=False)
    content = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=False, null=False)

class NewsKeyword(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=30, null=False)
    weight = models.FloatField(null=False)

class NewsCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=30, null=False)

class NewsWord(models.Model):
    word = models.CharField(max_length=30, null=False)
    news = models.ForeignKey(News, on_delete=models.CASCADE)