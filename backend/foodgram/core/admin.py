from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, Favorite, RecipeTag,
                     RecipeIngredientAmount, Cart, Follow)


class TagInline(admin.StackedInline):
    model = RecipeTag
    extra = 0


class IngredientInline(admin.StackedInline):
    model = RecipeIngredientAmount
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    exclude = ('is_favorited', 'is_in_shopping_cart')
    readonly_fields = ['favorite_count']
    list_display = (
        'name',
        'author',
    )
    list_filter = ('author', 'name', 'tags')
    inlines = (TagInline, IngredientInline)

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(Follow)
