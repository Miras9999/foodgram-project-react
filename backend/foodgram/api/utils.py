from rest_framework.response import Response
from rest_framework import status, serializers

from core.models import (Amount, Ingredient, RecipeIngredientAmount, Recipe,
                         RecipeTag)


def filter_queryset(user, model, queryset):
    if not user.is_anonymous:
        obj = model.objects.filter(
            user=user
        ).values('recipe_id')
        return queryset.filter(id__in=obj)
    return queryset.none()


def object_exist_in_essence(request,
                            model,
                            serialize_obj,
                            first_field,
                            second_field):
    if request and not request.user.is_anonymous:
        return model.objects.filter(
            **{f"{first_field}": serialize_obj,
               f"{second_field}": request.user}
        ).exists()
    return False


def ingredient_create(ingredients, recipe):
    recipe_ingr_amount = []
    ingredients_id = []
    for ingredient in ingredients:
        amount_obj, created = Amount.objects.get_or_create(
            amount=ingredient['amount']
        )
        ingredient_obj = Ingredient.objects.filter(id=ingredient['id'])
        if not ingredient_obj.exists():
            raise serializers.ValidationError('Ингредиента не существует!')
        if ingredient['id'] in ingredients_id:
            raise serializers.ValidationError('Ингредиент дублируется!')
        ingredients_id.append(ingredient['id'])
        recipe_ingr_amount_composition = RecipeIngredientAmount(
            recipe=recipe,
            amount=amount_obj,
            ingredients=ingredient_obj.first()
        )
        recipe_ingr_amount.append(recipe_ingr_amount_composition)
    RecipeIngredientAmount.objects.bulk_create(recipe_ingr_amount)


def recipe_actions(request, model, serializer, pk):
    user = request.user
    recipe = Recipe.objects.filter(id=pk).first()
    model_obj = model.objects.filter(user=user, recipe=recipe).first()
    if request.method == 'POST':
        if recipe is None:
            raise serializers.ValidationError('Рецепта не сущетсвует!')
        if model_obj is not None:
            raise serializers.ValidationError('Объект уже добавлен')
        model.objects.create(user=user, recipe=recipe)
        serializer = serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if recipe is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if model_obj is None:
            raise serializers.ValidationError('Объекта не существует')
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def tag_create(tags, recipe):
    recipe_tags = []
    tags_exist = []
    for tag in tags:
        if tag in tags_exist:
            raise serializers.ValidationError('Данный тег уже добавлен')
        tags_exist.append(tag)
        recipe_tag_composition = RecipeTag(recipe=recipe, tag=tag)
        recipe_tags.append(recipe_tag_composition)
    RecipeTag.objects.bulk_create(recipe_tags)
