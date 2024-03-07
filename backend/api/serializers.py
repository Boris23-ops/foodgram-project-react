from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import Subscription

User = get_user_model()
MIN_VALUE = 1
MAX_VALUE = 32_000


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
        user = self.context['request'].user
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
        return (
            user.is_authenticated and user.follower.filter(
                author=obj.id).exists())


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

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(
        write_only=True, min_value=MIN_VALUE, max_value=MAX_VALUE
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = IngredientRecipeCreateSerializer(
        many=True, source='ingredient'
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

    def validate_tags(self, data):
        """Валидация данных тегов."""
        tags = data
        if not tags:
            raise ValidationError(
                'Количество тегов не может быть меньше одного!'
            )
        if not tags:
            raise ValidationError('Добавьте тег.')
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги не должны повторяться.')
        return data

    def validate_ingredients(self, data):
        """Валидация данных ингредиентов."""
        if not data:
            raise ValidationError('Добавьте ингредиент.')
        ingredients = [item['id'] for item in data]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise ValidationError(
                    'Такой ингредиент уже есть.'
                )
        return data

    def validate_image(self, image):
        if not image:
            raise ValidationError('Добавьте изображение.')
        return image

    def ingredient_recipe_bulk_create(self, ingredients, recipe):
        """Создание ингредиентов рецепта."""
        ingredient_instances = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_instances)

    def create(self, validated_data):
        """Создание рецепта."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.save()
        self.ingredient_recipe_bulk_create(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()

        self._make_recipe(ingredients, instance)
        return super().update(instance, validated_data)

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
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение информации о добавлении рецепта в список покупок."""

        user = self.context.get('request').user
        return user.is_authenticated and user.shop_cart.filter(
            recipe=obj).exists()


class FavoriteRecipeSerializer(ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(ModelSerializer):
    """Сериализатор для подписки."""

    id = PrimaryKeyRelatedField(source='author.id', read_only=True)
    first_name = CharField(source='author.first_name', read_only=True)
    last_name = CharField(source='author.last_name', read_only=True)
    email = CharField(source='author.email', read_only=True)
    recipes = FavoriteRecipeSerializer(
        many=True, source='author.recipes', read_only=True
    )
    recipes_count = IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя!'
            )
        ]

    def validate(self, data):
        if self.context.get('request').user == data.get('author'):
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data
