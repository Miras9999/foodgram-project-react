from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    CustomUserViewSet)


router_v1 = DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', CustomUserViewSet.as_view(
        {'post': 'following', 'delete': 'following'}
    ), name='following'),
    path('users/subscriptions/', CustomUserViewSet.as_view(
        {'get': 'follow_list'}
    ), name='follow_list'),
    path('recipes/<int:pk>/favorite/', RecipeViewSet.as_view(
        {'post': 'favorite', 'delete': 'favorite'}
    )),
    path('recipes/<int:pk>/shopping_cart/', RecipeViewSet.as_view(
        {'post': 'shopping_cart', 'delete': 'shopping_cart'}
    )),
    path('recipes/download_shopping_cart/', RecipeViewSet.as_view(
        {'get': 'download_shopping_cart'}
    )),
]
