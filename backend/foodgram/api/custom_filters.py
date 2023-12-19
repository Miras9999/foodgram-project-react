from django_filters import rest_framework as filter
from django.contrib.auth import get_user_model

from core.models import Recipe, Favorite, Cart, Ingredient
from .utils import filter_queryset, filter_limit

User = get_user_model()


class RecipeFilter(filter.FilterSet):
    tags = filter.CharFilter(method='tags_filter')
    is_favorited = filter.CharFilter(method='favorites_filter')
    is_in_shopping_cart = filter.CharFilter(method='cart_filter')
    ingredients = filter.CharFilter(field_name='ingredients__name',
                                    lookup_expr='istartswith')
    limit = filter.NumberFilter(method='limit_filter')

    def tags_filter(self, queryset, name, value):
        tag_list = self.request.GET.getlist('tags')
        return queryset.filter(tags__name__in=tag_list).distinct()

    def favorites_filter(self, queryset, name, value):
        return filter_queryset(self.request.user, Favorite, queryset)

    def cart_filter(self, queryset, name, value):
        return filter_queryset(self.request.user, Cart, queryset)

    def limit_filter(self, queryset, name, value):
        return filter_limit(queryset, value)

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited', 'author', 'ingredients__name']


class IngredientFilter(filter.FilterSet):
    name = filter.CharFilter(field_name='name',
                             lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class UsersFilter(filter.FilterSet):
    limit = filter.NumberFilter(method='limit_filter')

    def limit_filter(self, queryset, name, value):
        return filter_limit(queryset, value)
