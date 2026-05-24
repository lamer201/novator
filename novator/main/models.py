from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
user = get_user_model()


class Status(models.Model):
    name = models.CharField(max_length=20, verbose_name='Статус')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    def __str__(self):
       return self.name


class Material(models.Model):
    name = models.CharField(max_length=100,verbose_name='Наименование')
    slug = models.SlugField(max_length=100, blank=True)
    price = models.FloatField(max_length=10, verbose_name='Стоимость')
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT ,verbose_name='Категория', default='пусто')
    eco_score = models.FloatField(max_length=10, verbose_name='Экологический балл', default=0)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя команды')
    slug = models.SlugField(max_length=100)
    status = models.BooleanField(default=False, verbose_name='Активно')

    def __str__(self):
       return str(self.name)


class ItemProperty(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    property_name = models.CharField(max_length=100)
    property_value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.material.name} - {self.property_name}: {self.property_value}"


class Koeff(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    koeff_value = models.FloatField(max_length=10, verbose_name='Коэффициент')

    def __str__(self):
        return f"{self.material.name} - Коэффициент: {self.koeff_value}"


class UserProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, verbose_name='Роль пользователя')
    sklad = models.OneToOneField('mtr.Sklad', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Склад')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class EcoScore(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.FloatField(max_length=10, verbose_name='Всего баллов')

    def __str__(self):
        return f"{self.team.name} - Экологический балл: {self.score}"


class EcoScoreOperation(models.Model):
    eco_score = models.ForeignKey(EcoScore, on_delete=models.CASCADE, related_name='operations')
    operation = models.FloatField(max_length=10, verbose_name='Экологический балл')
    year = models.IntegerField(verbose_name='Год операции')
    item = models.ForeignKey('bank.ZakazItem', on_delete=models.CASCADE, verbose_name='Позиция заказа', related_name='eco_score_operations', blank=True, null=True)
    eco_event = models.CharField(max_length=100, verbose_name='Экологическое мероприятие', blank=True)
