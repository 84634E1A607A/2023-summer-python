# Generated by Django 4.2.4 on 2023-08-27 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('summary', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('author', models.CharField(max_length=30)),
                ('media_name', models.CharField(max_length=30)),
                ('tags', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField()),
                ('document_id', models.CharField(max_length=30, unique=True)),
                ('source_url', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='NewsKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=30)),
                ('weight', models.FloatField()),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Blog.news')),
            ],
        ),
        migrations.CreateModel(
            name='NewsComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=30)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField()),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Blog.news')),
            ],
        ),
    ]
