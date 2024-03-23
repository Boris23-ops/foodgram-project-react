from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)

from foodgram.constants import MAX_VALUE, MIN_VALUE
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SetPasswordSerializer(ModelSerializer):
    """Сериализатор для смены пароля."""

    current_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def validate_current_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise ValidationError('Неверный текущий пароль')
        return value


class UserSerializer(ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Получение информации о подписке."""
        user = self.context.get('request').user
        return user.is_authenticated and user.follower.filter(
            author=obj.id
        ).exists()


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeCreateSerializer(ModelSerializer):
    """Сериализатор для создания ингредиентов рецепта."""

    id = IntegerField()
    amount = IntegerField(
        write_only=True, min_value=MIN_VALUE, max_value=MAX_VALUE
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_id(self, value):
        if not Ingredient.objects.filter(pk=value).exists():
            raise ValidationError('Ингредиент с указанным ID не найден.')
        return value


class CreateRecipeSerializer(ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = IngredientRecipeCreateSerializer(
        many=True,
    )
    author = UserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)
    text = CharField(source='description')
    cooking_time = IntegerField(
        write_only=True, min_value=MIN_VALUE, max_value=MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'cooking_time', 'text'
        )

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('ingredients')

        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Поле отсутствует'}
            )
        if not tags:
            raise ValidationError(
                {'tags': 'Поле отсуствует'}
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                {'tags': 'Теги не уникальны'}
            )

        unique_ingr = {item['id'] for item in ingredients}
        if len(unique_ingr) != len(ingredients):
            raise ValidationError(
                {'ingredients': 'Дублирование ингредиентов'}
            )

        return attrs

    def validate_image(self, image):
        if not image:
            raise ValidationError('Добавьте изображение.')
        return image

    def ingredient_recipe_bulk_create(self, ingredients, recipe):
        """Создание ингредиентов рецепта."""
        ingredient_instances = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_instances)

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredient = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.ingredient_recipe_bulk_create(ingredient, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredient = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.ingredient_recipe_bulk_create(ingredient, instance)
        instance.tags.set(validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data


class ReadIngredientRecipeSerializer(ModelSerializer):
    """Сериализатор для чтения ингредиентов рецепта."""

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializer(ModelSerializer):
    """Сериализатор для чтения рецепта."""

    author = UserSerializer(read_only=True)
    ingredients = ReadIngredientRecipeSerializer(
        many=True, read_only=True, source='recipe'
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    text = CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Получение информации о добавлении рецепта в избранное."""
        user = self.context.get('request').user
        return user.is_authenticated and user.favorites.filter(
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение информации о добавлении рецепта в список покупок."""
        user = self.context.get('request').user
        return user.is_authenticated and user.shop_cart.filter(
            recipe=obj
        ).exists()


class ShortCutRecipeSerializer(ModelSerializer):
    """Сериализатор коротокого отображения рецепта"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    """Сериализатор подписок"""

    recipes = SerializerMethodField(method_name='get_recipe')
    recipes_count = SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipe(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        serialized_recipes = ShortCutRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data
        return serialized_recipes

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionCreateSerializer(ModelSerializer):
    '''Сериализатор для создания подписки.'''

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author'
        )

    def validate(self, attrs):
        user = attrs['user']
        author = attrs['author']
        if not User.objects.filter(pk=author.pk).exists():
            raise ValidationError({'author': 'Автор не найден.'})
        if user == author:
            raise ValidationError(
                {'author': 'Нельзя подписаться на себя.'}
            )
        if user.follower.filter(author=author).exists():
            raise ValidationError(
                {'author': 'Уже подписан.'}
            )

        return attrs

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author,
            context=self.context
        ).data


class BaseRecipeSerializer(ModelSerializer):
    """Базовый сериализатор для избранных рецептов и списка покупок."""

    class Meta:
        abstract = True
        model = None
        fields = (
            'user',
            'recipe'
        )

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if self.Meta.model.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise ValidationError(
                {'recipe': 'Уже существует.'}
            )
        return attrs

    def to_representation(self, instance):
        return ShortCutRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class ShoppingCartSerializer(BaseRecipeSerializer):
    """Сериализатор списка покупок."""

    class Meta(BaseRecipeSerializer.Meta):
        model = ShoppingCart


class FavoriteRecipeSerializer(BaseRecipeSerializer):
    """Сериализатор избранных рецептов."""

    class Meta(BaseRecipeSerializer.Meta):
        model = FavoriteRecipe
