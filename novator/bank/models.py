from django.db import models
from main.models import Status, Team, Material
from constance import config



class Buy(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='buy_team')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год покупки')
    month = models.IntegerField(verbose_name='Месяц покупки', null=True)



class Buildings(models.Model):
    name = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Название объекта', limit_choices_to={'category__pk': 7})

    def __str__(self):
        return self.name.name



class Balance(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    money = models.FloatField(max_length=10, verbose_name='Баланс')



class Zapusk(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год запуска')
    #month = models.IntegerField(verbose_name='Месяц запуска' , null=True)
    object = models.ForeignKey(Buildings, on_delete=models.CASCADE)
    koeff = models.FloatField(max_length=10, default=1.0, verbose_name='Коэффициент запуска')
    profit_money = models.FloatField(max_length=10, default=0.0, verbose_name='Прибыль от запуска')

    def __str__(self):
        return f"Запуск {self.id} - {self.team.name} - {self.year} - {self.object.name}"
    
    def calculate_profit(self):
        self.profit = self.profit * self.koeff
        return self.profit
    


class Profit(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год прибыли')
    amount = models.FloatField(max_length=10, verbose_name='Сумма прибыли')
    object = models.ForeignKey(Zapusk, on_delete=models.CASCADE)


class Zakaz(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год заказа')
    month = models.IntegerField(verbose_name='Месяц заказа', null=True)
    payment = models.BooleanField(default=False, verbose_name='Оплачено')
    issued = models.BooleanField(default=False, verbose_name='Выдано')
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статус заказа')
    description = models.TextField(blank=True, verbose_name='Описание заказа')

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
    koeff = models.FloatField(max_length=10, default=1.0)
    refund = models.BooleanField(default=False, verbose_name='Возврат')

    def get_total(self):
        return self.quantity * self.price
    

class Credit(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=10, verbose_name='Сумма кредита')
    year = models.IntegerField(verbose_name='Год кредита')
    percent = models.FloatField(max_length=5, verbose_name='Процентная ставка')
    remains = models.FloatField(max_length=10, verbose_name='Остаток по телу кредита')
    #remains_percent = models.FloatField(max_length=5, verbose_name='Остаток по процентам')
    status = models.CharField(max_length=20, verbose_name='Статус кредита', default='active')

    """ @property
    def total_price(self):
        return self.remains + self.remains_percent """

    def __str__(self):
        return f"Кредит {self.id} - {self.team.name} - {self.amount}"
    
    def calculate_remains(self, payments):
        total_paid = sum(payment.amount for payment in payments)
        self.remains = max(0, self.amount - total_paid)
        self.remains_percent = max(0, (self.amount * self.percent / 100) - total_paid * (self.percent / 100))

    def make_payment(self, payment_amount):
        if payment_amount > self.remains:
            payment_amount = self.remains
        self.remains -= payment_amount
        self.remains_percent -= payment_amount * (self.percent / 100)

    def is_fully_paid(self):
        return self.remains == 0
    
    def get_total_payment(self):
        return self.remains + (self.remains * self.percent / 100)   
    
    
class CreditPayment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=10, verbose_name='Сумма платежа')
    year = models.IntegerField(verbose_name='Год платежа')

    def __str__(self):
        return f"Платеж {self.id} - Кредит {self.credit.id} - {self.amount}"
    

class Premia(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=10, verbose_name='Сумма премии')
    year = models.IntegerField(verbose_name='Год премии')

    def __str__(self):
        return f"Премия {self.id} - {self.team.name} - {self.amount}"

