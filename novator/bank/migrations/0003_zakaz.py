# Generated by Django 5.2 on 2025-04-07 09:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0002_buy_month_alter_buy_year_alter_zapusk_year'),
        ('main', '0003_alter_category_name_alter_material_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zakaz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(max_length=10)),
                ('material', models.ManyToManyField(to='main.material')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.team')),
            ],
        ),
    ]
