from django.db import models
from main.models import Team, Material


class Buy(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='buy_team')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год покупки')
    month = models.IntegerField(verbose_name='Месяц покупки', null=True)


class Balance(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    money = models.FloatField(max_length=10, verbose_name='Баланс')


class Zapusk(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год запуска')
    object = models.ForeignKey(Buy, on_delete=models.CASCADE)


class Zakaz(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    material = models.ManyToManyField(Material)
    price = models.FloatField(max_length=10)