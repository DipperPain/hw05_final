# Generated by Django 2.2.16 on 2021-10-21 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_post_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
    ]
