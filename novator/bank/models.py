from django.db import models
from main.models import Status, Team, Material, Category
from constance import config
from simple_history.models import HistoricalRecords



class Balance(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='balance')
    money = models.FloatField(max_length=10, verbose_name='Баланс')
    history = HistoricalRecords()



class Zakaz(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='zakaz')
    year = models.IntegerField(verbose_name='Год заказа')
    month = models.IntegerField(verbose_name='Месяц заказа', null=True)
    payment = models.BooleanField(default=False, verbose_name='Оплачено')
    issued = models.BooleanField(default=False, verbose_name='Выдано')
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статус заказа')
    description = models.TextField(blank=True, verbose_name='Номер договора')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория заказа')

    def __str__(self):
        return f"Заказ {self.id} - {self.team.name} - {self.year}"
    
    def get_total_sum(self):
        items = self.zakazitem_set.all()
        return sum(item.get_total() for item in items)

    @property
    def total_items(self):
        items = self.zakazitem_set.filter(material__category__slug='trubi')
        return sum(item.quantity for item in items)
    
    @property
    def total_km(self):
        items = self.zakazitem_set.filter(material__category__slug='trubi')
        return sum(item.quantity * 20 for item in items)
    
    @property
    def total_eco_score(self):
        items = self.zakazitem_set.all()
        return sum(item.quantity * item.material.eco_score for item in items)


class ZakazItem(models.Model):
    zakaz = models.ForeignKey(Zakaz, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    price = models.FloatField(max_length=10) 
    quantity = models.IntegerField()
    koeff = models.FloatField(max_length=10, default=1.0)
    refund = models.BooleanField(default=False, verbose_name='Возврат')
    profit_val = models.FloatField(max_length=10, default=0, verbose_name='Прибыль')
    profit_koeff = models.FloatField(max_length=10, default=0, verbose_name='Коэффициент прибыли')

    def __str__(self):
        return f"{self.material.name}"

    def get_total(self):
        return self.quantity * self.price
    
    def get_profit(self):
        return  self.profit_koeff * self.profit_val
    
    @property
    def calculate_profit(self):
        return self.profit_koeff * self.profit_val
    
    @property
    def calculate_total_km(self):
        if self.material.category.slug == 'trubi':
            return self.quantity * 20
        return 0


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


class TotalKm(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='total_km_team')
    total_km = models.FloatField(max_length=10, verbose_name='Общее количество км газопровода')

    def __str__(self):
        return f"Общее количество км газопровода - {self.team.name} - {self.total_km}"
    
    def calculate_total_km(self, team):
        zakazy = team.zakaz.all()
        items = ZakazItem.objects.filter(zakaz__in=zakazy, material__category__slug='trubi')
        self.total_km = sum(item.quantity * 20 for item in items)
        return self.total_km


class HistoryOperation(models.Model):
    OPERATION_CHOICES = (
        ('debit', 'Списание'),
        ('credit', 'Пополнение'),
        ('premia', 'Премия'),
        ('zakaz', 'Заказ'),
        ('refund', 'Возврат'),
        ('credit_payment', 'Платеж по кредиту'),
        ('adjustment', 'Корректировка'),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='history')
    operation_type = models.CharField(max_length=30, choices=OPERATION_CHOICES, verbose_name='Тип операции')
    amount = models.FloatField(verbose_name='Сумма операции')
    balance_before = models.FloatField(null=True, blank=True, verbose_name='Баланс до операции')
    balance_after = models.FloatField(null=True, blank=True, verbose_name='Баланс после операции')
    description = models.TextField(blank=True, verbose_name='Описание операции')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата операции')
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.team.name} — {self.get_operation_type_display()} {self.amount}"
