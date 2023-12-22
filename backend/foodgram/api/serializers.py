from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from core.models import (Recipe, Tag, Ingredient, Follow, Favorite, Cart)
from .custom_fields import Base64ImageField
from .utils import object_exist_in_essence, ingredient_create, tag_create


User = get_user_model()

max_amount = 32000
min_amount = 1
recipe_slice = 3


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
    amount = serializers.IntegerField(max_value=max_amount,
                                      min_value=min_amount)
    id = serializers.IntegerField()

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
    ingredients = IngredientRetrieveSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              required=True)
    image = Base64ImageField(use_url=True, required=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    cooking_time = serializers.IntegerField(max_value=max_amount,
                                            min_value=min_amount,
                                            required=True)

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
        read_only_fields = ['is_favorited', 'is_in_shopping_cart']

    def to_representation(self, instance):
        return RecipeSerializer(instance).data

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        if not tags:
            raise serializers.ValidationError("Это поле не может быть пустым")

        if not ingredients:
            raise serializers.ValidationError("Это поле не может быть пустым")

        return data

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        tag_create(tags, recipe)

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

        instance.recipetag_set.all().delete()
        tag_create(new_tags, instance)

        instance.recipeingredientamount_set.all().delete()
        ingredient_create(new_ingredients, instance)

        instance.save()

        return instance


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
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
                  'is_subscribed')

    def create(self, validated_data):
        user = self.context.get('request').user
        following = self.context.get('following')
        if following == user:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя самого!'
            )
        follow_obj, created = Follow.objects.get_or_create(user=user,
                                                           following=following)
        if not created:
            raise serializers.ValidationError('Подписка уже существует!')
        return follow_obj

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get(
                'recipes_limit'
            )
        recipes = obj.following.recipe_set.all().order_by('-created')
        if not recipes.count() > recipe_slice:
            return RecipeShortSerializer(recipes, many=True).data
        if recipes_limit:
            return RecipeShortSerializer(recipes[:int(recipes_limit)],
                                         many=True).data
        return RecipeShortSerializer(recipes[:recipe_slice], many=True).data
