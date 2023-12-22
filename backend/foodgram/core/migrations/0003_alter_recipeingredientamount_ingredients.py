# Generated by Django 3.2 on 2023-12-21 06:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20231220_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredientamount',
            name='ingredients',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingredients', to='core.ingredient', verbose_name='Ингредиенты'),
        ),
    ]
