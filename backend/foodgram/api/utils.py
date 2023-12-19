from rest_framework.response import Response
from rest_framework import status, serializers

from core.models import Amount, Ingredient, RecipeIngredientAmount, Recipe


def filter_queryset(user, model, queryset):
    if not user.is_anonymous:
        obj = model.objects.filter(
            user=user
        ).values('recipe_id')
        return queryset.filter(id__in=obj)
    return queryset.none()


def object_exist_in_essence(context,
                            model,
                            serialize_obj,
                            first_field,
                            second_field):
    if context and context.user and not context.user.is_anonymous:
        return model.objects.filter(
                **{f"{first_field}": serialize_obj,
                   f"{second_field}": context.user}
            ).exists()
    return False


def ingredient_create(ingredients, recipe):
    for ingredient in ingredients:
        if int(ingredient['amount']) < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 минуты'
            )
        amount_obj, created = Amount.objects.get_or_create(
            amount=ingredient['amount']
        )
        ingredient_obj = Ingredient.objects.filter(id=ingredient['id'])
        if not ingredient_obj.exists():
            raise serializers.ValidationError('Ингредиента не существует')
        recipe_ingredient_amount_exist = RecipeIngredientAmount.objects.filter(
            recipe=recipe, ingredients=ingredient_obj.first()
        ).exists()
        if recipe_ingredient_amount_exist:
            raise serializers.ValidationError('Ингредиент уже добавлен')
        RecipeIngredientAmount.objects.create(
            recipe=recipe,
            amount=amount_obj,
            ingredients=ingredient_obj.first()
        )


def recipe_actions(request, model, serializer, pk):
    user = request.user
    recipe = Recipe.objects.filter(id=pk).first()
    model_obj = model.objects.filter(user=user, recipe=recipe).first()
    # if user.is_anonymous:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        if recipe is None:
            raise serializers.ValidationError('Рецепта не сущетсвует!')
        if model_obj is not None:
            raise serializers.ValidationError('Объект уже добавлен')
        model.objects.create(user=user, recipe=recipe)
        serializer = serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        # if user.is_anonymous:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        if recipe is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if model_obj is None:
            raise serializers.ValidationError('Объекта не существует')
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def filter_limit(queryset, value):
    if value:
        return queryset[:int(value)]
    return queryset
