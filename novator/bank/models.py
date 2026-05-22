from django.db import models
from main.models import Status, Team, Material
from constance import config



class Balance(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    money = models.FloatField(max_length=10, verbose_name='Баланс')


class Consumers(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название потребителя')
    profit_val = models.FloatField(max_length=10, default=0, verbose_name='Прибыль')


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
    consumer = models.ForeignKey(Consumers, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Потребитель')
    profit_koeff = models.FloatField(max_length=10, default=0, verbose_name='Коэффициент прибыли')

    def __str__(self):
        return f"{self.material.name}"

    def get_total(self):
        return self.quantity * self.price
    
    @property
    def calculate_profit(self):
        if self.consumer is None:
            return 0
        return self.profit_koeff * self.consumer.profit_val
        
    

class Credit(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=10, verbose_name='Сумма кредита')
    year = models.IntegerField(verbose_name='Год кредита')
    percent = models.FloatField(max_length=5, verbose_name='Процентная ставка')
    remains = models.FloatField(max_length=10, verbose_name='Остаток по телу кредита')
    #remains_percent = models.FloatField(max_length=5, verbose_name='Остаток по процентам')
    status = models.CharField(max_length=20, verbose_name='Статус кредита', default='active')


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


