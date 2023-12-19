from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from core.models import (Recipe, Tag, Ingredient, RecipeTag,
                         RecipeIngredientAmount, Follow,
                         Favorite, Cart)
from .custom_fields import CustomImageField
from .utils import object_exist_in_essence, ingredient_create


User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Некорректный пароль")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class CustomPostUserSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }


class CustomUserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }

    def get_is_subscribed(self, obj):
        return object_exist_in_essence(self.context.get('request'),
                                       Follow,
                                       obj,
                                       'following',
                                       'user')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientListSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_amount(self, obj):
        recipe_id = self.context.get('recipe_id')
        recipe = Recipe.objects.filter(id=recipe_id).first()
        amount = obj.amount.filter(
            recipeingredientamount__recipe=recipe
        ).first()
        if amount:
            return amount.amount
        return None


class IngredientRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientListSerializer(many=True,
                                           read_only=True)
    image = serializers.ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'author',
                  'name',
                  'image',
                  'text',
                  'ingredients',
                  'tags',
                  'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return object_exist_in_essence(self.context.get('request'),
                                       Favorite,
                                       obj,
                                       'recipe',
                                       'user')

    def get_is_in_shopping_cart(self, obj):
        return object_exist_in_essence(self.context.get('request'),
                                       Cart,
                                       obj,
                                       'recipe',
                                       'user')

    def to_representation(self, instance):
        context = self.context
        context['recipe_id'] = instance.id

        ingredients_serializer = IngredientListSerializer(
            instance=instance.ingredients.all(),
            many=True,
            context=context
        )

        representation = super().to_representation(instance)
        representation['ingredients'] = ingredients_serializer.data

        return representation


class RecipeCreateUpdateSeraializer(serializers.ModelSerializer):
    ingredients = serializers.ListSerializer(child=serializers.DictField(),
                                             write_only=True,
                                             required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              required=True)
    image = CustomImageField(use_url=True, required=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'text',
                  'ingredients',
                  'tags',
                  'cooking_time',
                  'author',
                  'is_favorited',
                  'is_in_shopping_cart')
        extra_kwargs = {
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
            'is_favorited': {'read_only': True},
            'is_in_shopping_cart': {'read_only': True},
        }

    def to_representation(self, instance):
        return RecipeSerializer(instance).data

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        cooking_time = data.get('cooking_time')

        if not tags:
            raise serializers.ValidationError("Это поле не может быть пустым")

        if not ingredients:
            raise serializers.ValidationError("Это поле не может быть пустым")

        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше минуты'
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        # cooking_time = validated_data.get('cooking_time')
        # if cooking_time < 1:
        #     raise serializers.ValidationError(
        #         'Время приготовления не может быть меньше минуты'
        #     )

        for tag in tags:
            recipe_tag_exist = RecipeTag.objects.filter(
                recipe=recipe, tag=tag
            ).exists()
            if recipe_tag_exist:
                raise serializers.ValidationError('Данный тег уже добавлен')
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        ingredient_create(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        new_tags = validated_data.pop('tags', None)
        new_ingredients = validated_data.pop('ingredients', None)
        old_tags = instance.tags.all()
        old_ingredients = instance.ingredients.all()

        # if instance.cooking_time < 1:
        #     raise serializers.ValidationError(
        #         'Время приготовления не может быть меньше минуты'
        #     )

        for old_tag in old_tags:
            recipe_tag_obj = get_object_or_404(RecipeTag,
                                               tag=old_tag,
                                               recipe=instance)
            recipe_tag_obj.delete()

        for new_tag in new_tags:
            recipe_tag_exist = RecipeTag.objects.filter(
                recipe=instance, tag=new_tag
            ).exists()
            if recipe_tag_exist:
                raise serializers.ValidationError('Данный тег уже добавлен')
            RecipeTag.objects.create(recipe=instance,
                                     tag=new_tag)

        for old_ingredient in old_ingredients:
            for amount in old_ingredient.amount.filter(
                recipeingredientamount__recipe=instance
            ):
                recipe_ingredient_amount_obj = (
                    RecipeIngredientAmount.objects.filter(
                        amount=amount,
                        recipe=instance,
                        ingredients=old_ingredient
                    ).first()
                )
                if recipe_ingredient_amount_obj:
                    recipe_ingredient_amount_obj.delete()

        ingredient_create(new_ingredients, instance)
        instance.save()

        return instance


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    following = serializers.HiddenField(
        default=serializers.SerializerMethodField()
    )
    first_name = serializers.CharField(source='following.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='following.last_name',
                                      read_only=True)
    username = serializers.CharField(source='following.username',
                                     read_only=True)
    email = serializers.EmailField(source='following.email',
                                   read_only=True)
    id = serializers.IntegerField(source='following.id',
                                  read_only=True)
    is_subscribed = serializers.BooleanField(source='following.is_subscribed',
                                             read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='following.recipe_set.count',
        read_only=True
    )

    class Meta:
        model = Follow
        fields = ('recipes',
                  'recipes_count',
                  'first_name',
                  'last_name',
                  'email',
                  'username',
                  'id',
                  'following',
                  'is_subscribed')

    def get_following(self, obj):
        return obj.following

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        recipes = obj.following.recipe_set.all().order_by('-created')
        if not recipes.count() > 3:
            return RecipeShortSerializer(recipes, many=True).data
        if recipes_limit:
            return RecipeShortSerializer(recipes[:int(recipes_limit)],
                                         many=True).data
        return RecipeShortSerializer(recipes[:3], many=True).data
