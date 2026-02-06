from django.db import models

# Create your models here.

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


