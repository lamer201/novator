from django.db import models

# Create your models here.
class EcoCompensation(models.Model):
    material = models.OneToOneField('main.Material', on_delete=models.CASCADE, related_name='eco_compensations')
    amount = models.FloatField(verbose_name='Сумма компенсации')
    description = models.TextField(blank=True, verbose_name='Описание компенсации')


class EcoCompensationOperation(models.Model):
    zakaz = models.OneToOneField('bank.Zakaz', on_delete=models.CASCADE, related_name='eco_compensations')
    eco_compensation = models.FloatField(verbose_name='Сумма компенсации')
    description = models.TextField(blank=True, verbose_name='Описание компенсации')