from io import BytesIO
import os

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from django.http import HttpResponse
from django.conf import settings
from djoser.views import UserViewSet
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.db.models import Sum

from .serializers import (CustomUserSerializer,
                          RecipeSerializer,
                          RecipeCreateUpdateSeraializer,
                          TagSerializer,
                          FollowSerializer,
                          RecipeShortSerializer,
                          CustomPostUserSerializer,
                          ChangePasswordSerializer,
                          IngredientSerializer)
from .custom_filters import RecipeFilter, IngredientFilter
from core.models import (Recipe,
                         Tag,
                         Ingredient,
                         Favorite,
                         Cart,
                         RecipeIngredientAmount)
from .permissions import (RecipeAuthorOrReadOnly,
                          ReadOnly,
                          IsOwnerOrAdminOrReadOnly)
from .utils import recipe_actions


User = get_user_model()

X_COORDINATE = 100
Y_COORDINATE = 700
Y_OFFSET = 12
FONT_SIZE = 12


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = [filter.DjangoFilterBackend]

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return (ReadOnly(),)
        return (IsOwnerOrAdminOrReadOnly(),)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CustomUserSerializer
        return CustomPostUserSerializer

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = CustomUserSerializer(self.request.user,
                                          context={'request': self.request})
        if not self.request.user.is_anonymous:
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise AuthenticationFailed(
            'Авторизуйтесь для совершения действия!'
        )

    @action(detail=True,
            url_path=r'^\d+/subscribe$',
            methods=['post', 'delete'])
    def following(self, request, id=None):
        user = self.request.user
        following = get_object_or_404(User, pk=id)
        if user.is_anonymous:
            raise AuthenticationFailed(
                'Авторизуйтесь для совершения действия!'
            )
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data,
                context={'request': self.request,
                         'following': following}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow = user.user.filter(following=following).first()
            if not follow:
                raise serializers.ValidationError(
                    'Подписки не существует!'
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            url_path=r'subscriptions',
            methods=['get'])
    def follow_list(self, request):
        if self.request.user.is_anonymous:
            raise serializers.ValidationError(
                'Авторизуйтесь для выполнения действия!'
            )
        follow = self.request.user.user.all()
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        result = paginator.paginate_queryset(follow, request)
        serializer = FollowSerializer(
            result, many=True, context={'request': self.request}
        )
        return paginator.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'tags', 'ingredients'
    ).all()
    serializer_class = RecipeSerializer
    filter_backends = [filter.DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = (RecipeAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        return RecipeCreateUpdateSeraializer

    @action(detail=True,
            url_path=r'^\d+/favorite$',
            methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return recipe_actions(
            request, Favorite, RecipeShortSerializer, pk
        )

    @action(detail=True,
            url_path=r'^\d+/shopping_cart$',
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return recipe_actions(
            request, Cart, RecipeShortSerializer, pk
        )

    @action(detail=False,
            url_path=r'download_shopping_cart',
            methods=['get'])
    def download_shopping_cart(self, request):
        current_user = request.user
        cart = current_user.cart_user.values('recipe_id')
        ingredients = RecipeIngredientAmount.objects.prefetch_related(
            'ingredients', 'amount'
        ).filter(recipe_id__in=cart).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(ingr_sum=Sum('amount__amount')).order_by(
            'ingredients__name'
        )

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer)
        font_path = os.path.join(settings.BASE_DIR,
                                 'core',
                                 'fonts',
                                 'DejaVuSerif.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path))
        x, y = X_COORDINATE, Y_COORDINATE
        for ingredient in ingredients:
            p.setFont('DejaVuSerif', FONT_SIZE)
            p.drawString(x,
                         y,
                         f"{ingredient.get('ingredients__name')}"
                         f"({ingredient.get('ingredients__measurement_unit')})"
                         f" - {ingredient.get('ingr_sum')}")
            y -= Y_OFFSET
        p.showPage()
        p.save()
        pdf_buffer.seek(0)
        response = HttpResponse(pdf_buffer.read(),
                                content_type='application/pdf')
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filter.DjangoFilterBackend,)
    filterset_class = IngredientFilter
