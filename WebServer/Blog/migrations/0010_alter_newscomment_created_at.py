# Generated by Django 4.2.4 on 2023-08-30 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0009_alter_newscomment_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newscomment',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
