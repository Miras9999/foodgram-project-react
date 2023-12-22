from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()

min_value = 1
max_value = 32000


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)
    amount = models.ManyToManyField('Amount',
                                    through='RecipeIngredientAmount',
                                    verbose_name='Количество')

    def __str__(self):
        return f"{self.name}({self.measurement_unit})"


class Amount(models.Model):
    amount = models.PositiveSmallIntegerField(verbose_name='Количество',
                                              validators=[
                                                  MinValueValidator(min_value),
                                                  MaxValueValidator(max_value)
                                              ])
    recipe = models.ManyToManyField('Recipe',
                                    through='RecipeIngredientAmount',
                                    verbose_name='Рецепт')

    def __str__(self):
        amount = str(self.amount)
        return amount


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.SET_NULL,
                               null=True,
                               verbose_name='Рецепт')
    amount = models.ForeignKey(Amount,
                               on_delete=models.SET_NULL,
                               null=True,
                               verbose_name='Количество')
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    verbose_name='Ингредиенты',
                                    related_name='ingredients')

    class Meta:
        unique_together = (("ingredients", "recipe", "amount"),)


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    name = models.CharField('Название', max_length=50)
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredientAmount',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField('Tag',
                                  through='RecipeTag',
                                  verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(min_value), MaxValueValidator(max_value)]
    )
    is_favorited = models.BooleanField('Избранное', default=False)
    is_in_shopping_cart = models.BooleanField('Корзина', default=False)
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет', max_length=7, unique=True, null=True)
    slug = models.SlugField('Слаг', max_length=200, unique=True, null=True)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            null=True,
                            verbose_name='Teг')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               verbose_name='Рецепт')


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='user',
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    following = models.ForeignKey(User,
                                  related_name='following',
                                  on_delete=models.CASCADE,
                                  verbose_name='Подписчик')
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        unique_together = (('user', 'following'),)
        ordering = ('-created',)


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             related_name='favorite_user',
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               related_name='favorite_recipe',
                               on_delete=models.SET_NULL,
                               null=True,
                               verbose_name='Рецепт')
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        unique_together = (('user', 'recipe'),)
        ordering = ('-created',)


class Cart(models.Model):
    user = models.ForeignKey(User,
                             related_name='cart_user',
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               related_name='cart_recipe',
                               on_delete=models.SET_NULL,
                               null=True,
                               verbose_name='Рецепт')
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        unique_together = (('user', 'recipe'),)
        ordering = ('-created',)
