# Generated manually: update EcoCompensationOperation to support multiple operations per zakaz
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('contactor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecocompensationoperation',
            name='operation_type',
            field=models.CharField(default='eco_change', max_length=50, verbose_name='Тип операции'),
        ),
        migrations.AddField(
            model_name='ecocompensationoperation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата операции'),
        ),
        migrations.AddField(
            model_name='ecocompensationoperation',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eco_compensation_operations', to='main.team'),
        ),
        migrations.AlterField(
            model_name='ecocompensationoperation',
            name='zakaz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eco_compensations', to='bank.zakaz'),
        ),
        migrations.AlterField(
            model_name='ecocompensationoperation',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание операции'),
        ),
    ]
