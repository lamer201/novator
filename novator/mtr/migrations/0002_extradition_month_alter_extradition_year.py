# Generated by Django 5.2 on 2025-04-04 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='extradition',
            name='month',
            field=models.IntegerField(null=True, verbose_name='Месяц отгрузки'),
        ),
        migrations.AlterField(
            model_name='extradition',
            name='year',
            field=models.IntegerField(verbose_name='Год отгрузки'),
        ),
    ]
