# Generated by Django 5.2 on 2025-04-04 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100, verbose_name='Наименование')),
                ('price', models.FloatField(max_length=10, verbose_name='Стоимость')),
                ('category', models.TextField(max_length=100, verbose_name='Категория')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100, verbose_name='Имя команды')),
                ('slug', models.SlugField(max_length=100)),
            ],
        ),
    ]
