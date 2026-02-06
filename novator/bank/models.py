from django.db import models
from main.models import Status, Team, Material


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
    month = models.IntegerField(verbose_name='Месяц запуска' , null=True)
    object = models.ForeignKey(Buy, on_delete=models.CASCADE)


class Zakaz(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год заказа')
    month = models.IntegerField(verbose_name='Месяц заказа', null=True)
    payment = models.BooleanField(default=False, verbose_name='Оплачено')
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статус заказа')

    def __str__(self):
        return f"Заказ {self.id} - {self.team.name} - {self.year}"
    
    def get_total_sum(self):
        items = self.zakazitem_set.all()
        return sum(item.get_total() for item in items)


class ZakazItem(models.Model):
    zakaz = models.ForeignKey(Zakaz, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    price = models.FloatField(max_length=10) 
    quantity = models.IntegerField()

    def get_total(self):
        return self.quantity * self.price