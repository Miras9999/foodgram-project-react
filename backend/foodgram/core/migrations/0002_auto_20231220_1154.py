# Generated by Django 3.2 on 2023-12-20 11:54

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='amount',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='amount',
            name='recipe',
            field=models.ManyToManyField(through='core.RecipeIngredientAmount', to='core.Recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_recipe', to='core.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='favorite_recipe', to='core.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='following',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
        migrations.AlterField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='amount',
            field=models.ManyToManyField(through='core.RecipeIngredientAmount', to='core.Amount', verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(32000)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/images/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='core.RecipeIngredientAmount', to='core.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='is_favorited',
            field=models.BooleanField(default=False, verbose_name='Избранное'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(default=False, verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(through='core.RecipeTag', to='core.Tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='recipeingredientamount',
            name='amount',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.amount', verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipeingredientamount',
            name='ingredients',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipeingredientamount',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.tag', verbose_name='Teг'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, null=True, unique=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, null=True, unique=True, verbose_name='Слаг'),
        ),
    ]
