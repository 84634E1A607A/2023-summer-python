# Generated by Django 4.2.4 on 2023-08-27 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='author',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='media_name',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='tags',
            field=models.CharField(max_length=30, null=True),
        ),
    ]