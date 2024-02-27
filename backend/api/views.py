from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)
from rest_framework.viewsets import ModelViewSet

from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    FavoriteRecipeSerializer,
    IngredientSerializer,
    ReadRecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSerializer
)
from api.pagination import CustomPagination
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    User
)
from users.models import Subscription


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.prefetch_related(
        'recipe__ingredient', 'tags'
    ).select_related('author').order_by('-pub_date')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от типа метода."""
        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def add_or_delete_recipe(self, request, model, pk):
        """Добавление или удаление рецепта."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            created = model.objects.get_or_create(recipe=recipe, user=user)
            if created:
                serializer = FavoriteRecipeSerializer(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=HTTP_201_CREATED)
            return Response(status=HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            database_obj = model.objects.filter(user=user, recipe=recipe)
            if not database_obj.exists():
                return Response(status=HTTP_400_BAD_REQUEST)
            database_obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        url_path='favorite',
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        return self.add_or_delete_recipe(request, FavoriteRecipe, pk)

    @action(
        methods=['post', 'delete'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из списка покупок."""
        return self.add_or_delete_recipe(request, ShoppingCart, pk)

    @action(
        methods=('get',),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Экшн для скачивания списка покупок."""

        ingredients = IngredientRecipe.objects.filter(
            recipe__shop_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_sum=Sum('amount'))
        wishlist = '\n'.join([
            f'{ingredient["ingredient__name"]}: '
            f'{ingredient["total_sum"]} '
            f'{ingredient["ingredient__measurement_unit"]}.'
            for ingredient in ingredients
        ])
        response = HttpResponse(wishlist, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=wishlist.txt'
        return response


class CustomUserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        methods=('get',),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """просмотр подписок."""

        subs_quryset = Subscription.objects.filter(user=request.user).annotate(
            recipes_count=Count('author__recipes')
        ).order_by('-author_id',)
        page = self.paginate_queryset(subs_quryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """добавление и удаление подписки."""

        follow_obj = Subscription.objects.filter(
            user=request.user, author=get_object_or_404(User, pk=id)
        )
        if request.method == 'DELETE':
            follow_obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        if not follow_obj.exists():
            sub = Subscription.objects.create(
                user=request.user,
                author=get_object_or_404(User, pk=id)
            )
            serializer = SubscribeSerializer(sub, context={'request': request})
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(
            'На одного пользователя нельзя подписаться дважды!',
            status=HTTP_400_BAD_REQUEST
        )


class TagViewSet(ModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(ModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filterset_class = IngredientFilter
