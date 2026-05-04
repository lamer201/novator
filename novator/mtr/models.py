from django.db import models
from main.models import Team, Material
from django.db import transaction
from django.core.exceptions import ValidationError



class Sklad(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название склада')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='sklad_team', blank=True, null=True)
    slug = models.SlugField(max_length=100, blank=True)
    category = models.CharField(max_length=100, verbose_name='Категория склада', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        ordering = ["name"]

    def __str__(self):
        return self.name



""" class Material(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    sklad = models.ForeignKey(Sklad, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"


    def __str__(self):
        return self.material.name """



class Stock(models.Model):
    """
    Остаток материала на складе.
    """
    warehouse = models.ForeignKey(
        Sklad,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name="Склад"
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name="Материал"
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Количество"
    )

    class Meta:
        unique_together = ("warehouse", "material")
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.warehouse} – {self.material}: {self.quantity}"



class Extradition(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    year = models.IntegerField(verbose_name='Год выдачи')
    month = models.IntegerField(verbose_name='Месяц выдачи', null=True)

    def __str__(self):
        return f"{self.team.name} - {self.material.name} - {self.year}/{self.month}"



class Shipment(models.Model):
    """
    Операция перемещения материала со склада-отправителя на склад-получатель.
    """
    date_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    from_warehouse = models.ForeignKey(
        Sklad,
        on_delete=models.PROTECT,
        related_name="shipments_from",
        verbose_name="Склад отгрузки"
    )
    to_warehouse = models.ForeignKey(
        Sklad,
        on_delete=models.PROTECT,
        related_name="shipments_to",
        verbose_name="Склад получения"
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name="Материал"
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        verbose_name="Количество"
    )
    description = models.TextField(blank=True, verbose_name="Примечание")

    class Meta:
        verbose_name = "Перемещение"
        verbose_name_plural = "Перемещения"
        ordering = ["-date_time"]

    def __str__(self):
        return f"{self.date_time}: {self.material} ({self.quantity}) {self.from_warehouse} → {self.to_warehouse}"

    def clean(self):
        """Валидация: количество > 0 и склады не совпадают."""
        if self.quantity <= 0:
            raise ValidationError("Количество должно быть положительным.")
        if self.from_warehouse == self.to_warehouse:
            raise ValidationError("Склад отгрузки и склад получения не могут совпадать.")

    @transaction.atomic
    def perform_shipment(self):
        """
        Выполняет перемещение:
        - Проверяет наличие достаточного остатка на складе отгрузки.
        - Уменьшает остаток на складе отгрузки.
        - Увеличивает остаток на складе получения.
        - Сохраняет операцию перемещения.
        """
        self.full_clean()  # вызовет clean() и другие валидации

        # Блокируем записи Stock для обновления, чтобы избежать гонок
        from_stock = Stock.objects.select_for_update().get(
            warehouse=self.from_warehouse,
            material=self.material  
        )
        if from_stock.quantity < self.quantity:
            raise ValidationError(
                f"Недостаточно материала на складе {self.from_warehouse}. "
                f"Доступно: {from_stock.quantity}, требуется: {self.quantity}"
            )

        to_stock, created = Stock.objects.select_for_update().get_or_create(
            warehouse=self.to_warehouse,
            material=self.material,
            defaults={"quantity": 0}
        )

        # Обновляем остатки
        from_stock.quantity -= self.quantity
        to_stock.quantity += self.quantity

        from_stock.save()
        to_stock.save()

        # Сохраняем операцию перемещения
        self.save()

    def save(self, *args, **kwargs):
        """
        Переопределённый save не выполняет перемещение автоматически,
        чтобы разделить создание объекта и бизнес-логику.
        Для выполнения перемещения нужно явно вызвать perform_shipment().
        """
        super().save(*args, **kwargs)