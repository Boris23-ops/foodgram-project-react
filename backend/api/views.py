from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientsFilter, RecipeFilter
from api.pagination import Pagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer, FavoriteRecipeSerializer,
                             IngredientSerializer, ReadRecipeSerializer,
                             ShoppingCartSerializer,
                             SubscriptionCreateSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, User)


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly]
    pagination_class = Pagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от типа метода."""

        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def add_to_base(self, request, serializer, pk):
        serializer = serializer(
            data={
                'user': request.user.id,
                'recipe': pk
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def delete_from_base(self, user, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        database_obj = model.objects.filter(user=user, recipe=recipe)
        if not database_obj.exists():
            return Response(
                {'errors': 'Рецепт не найден в базе.'},
                status=HTTP_400_BAD_REQUEST
            )
        database_obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Экшн для добавления или удаления рецепта из избранного."""
        if request.method == 'POST':
            return self.add_to_base(request, FavoriteRecipeSerializer, pk)
        return self.delete_from_base(request.user, FavoriteRecipe, pk)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Экшн для добавления или удаления рецепта из списка покупок."""
        if request.method == 'POST':
            return self.add_to_base(request, ShoppingCartSerializer, pk,)
        return self.delete_from_base(request.user, ShoppingCart, pk)

    def generate_shopping_cart_list(self, user):
        """Генерация списка покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shop_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_sum=Sum('amount'))
        wishlist = '\n'.join([
            f'{ingredient["ingredient__name"]}: '
            f'{ingredient["total_sum"]} '
            f'{ingredient["ingredient__measurement_unit"]}.'
            for ingredient in ingredients
        ])
        return wishlist

    @action(
        methods=('get',),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Экшн для скачивания списка покупок."""
        wishlist = self.generate_shopping_cart_list(request.user)

        response = HttpResponse(wishlist, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=wishlist.txt'
        return response


class UserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            return self.create_subscription(request, id)
        return self.delete_subscription(request, id)

    def create_subscription(self, request, id):
        get_object_or_404(User, pk=id)
        user = request.user
        serializer = SubscriptionCreateSerializer(
            data={
                'user': user.id,
                'author': id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_subscription(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        delete_count, _ = user.follower.filter(author=author).delete()
        if not delete_count:
            return Response(
                {'detail': 'Подписка не найдена.'},
                status=HTTP_400_BAD_REQUEST
            )
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = SubscriptionSerializer(
            page, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    pagination_class = None
