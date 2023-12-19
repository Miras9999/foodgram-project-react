from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)
    amount = models.ManyToManyField('Amount',
                                    through='RecipeIngredientAmount')

    def __str__(self):
        return f"{self.name}({self.measurement_unit})"


class Amount(models.Model):
    amount = models.PositiveIntegerField()
    recipe = models.ManyToManyField('Recipe',
                                    through='RecipeIngredientAmount')

    def __str__(self):
        amount = str(self.amount)
        return amount


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.SET_NULL, null=True)
    amount = models.ForeignKey(Amount, on_delete=models.SET_NULL, null=True)
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.SET_NULL,
                                    null=True)

    class Meta:
        unique_together = (("ingredients", "recipe", "amount"),)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredientAmount')
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    cooking_time = models.PositiveIntegerField()
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='user',
                             on_delete=models.CASCADE)
    following = models.ForeignKey(User,
                                  related_name='following',
                                  on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'following'),)


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             related_name='favorite_user',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='favorite_recipe',
                               on_delete=models.SET_NULL,
                               null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'recipe'),)


class Cart(models.Model):
    user = models.ForeignKey(User,
                             related_name='cart_user',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='cart_recipe',
                               on_delete=models.SET_NULL,
                               null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'recipe'),)
