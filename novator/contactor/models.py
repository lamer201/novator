from django.db import models

# Create your models here.
class EcoCompensation(models.Model):
    material = models.OneToOneField('main.Material', on_delete=models.CASCADE, related_name='eco_compensations')
    amount = models.FloatField(verbose_name='Сумма компенсации')
    description = models.TextField(blank=True, verbose_name='Описание компенсации')


class EcoCompensationOperation(models.Model):
    zakaz = models.ForeignKey('bank.Zakaz', on_delete=models.CASCADE, related_name='eco_compensations', blank=True, null=True)
    team = models.ForeignKey('main.Team', on_delete=models.CASCADE, related_name='eco_compensation_operations', blank=True, null=True)
    eco_compensation = models.FloatField(verbose_name='Сумма компенсации')
    operation_type = models.CharField(max_length=50, verbose_name='Тип операции', default='eco_change')
    description = models.TextField(blank=True, verbose_name='Описание операции')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата операции')

    @classmethod
    def record(cls, team=None, zakaz=None, eco_compensation=0, operation_type='eco_change', description=''):
        return cls.objects.create(
            team=team,
            zakaz=zakaz,
            eco_compensation=eco_compensation,
            operation_type=operation_type,
            description=description,
        )

class HistoryOperation(models.Model):
    zakaz = models.ForeignKey('bank.Zakaz', on_delete=models.CASCADE, related_name='history_operations', blank=True, null=True)
    team = models.ForeignKey('main.Team', on_delete=models.CASCADE, related_name='history_operations', blank=True, null=True)
    eco_compensation = models.FloatField(verbose_name='Сумма компенсации', default=0)
    operation_type = models.CharField(max_length=50, verbose_name='Тип операции')
    description = models.TextField(blank=True, verbose_name='Описание операции')

    @classmethod
    def record(cls, team=None, zakaz=None, eco_compensation=0, operation_type='operation', description=''):
        return cls.objects.create(
            team=team,
            zakaz=zakaz,
            eco_compensation=eco_compensation,
            operation_type=operation_type,
            description=description,
        )
