# Generated by Django 4.2.4 on 2023-08-28 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0003_newscategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='category',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='newscategory',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
