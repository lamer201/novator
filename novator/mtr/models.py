from django.db import models
from main.models import Team, Material


class Extradition(models.Model):
    material = models.ForeignKey(Material,on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год отгрузки')
    month = models.IntegerField(verbose_name='Месяц отгрузки', null=True)




