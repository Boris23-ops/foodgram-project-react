from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    ValidationError
)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, ShoppingCart, FavoriteRecipe
from users.models import Subscription
from foodgram.constants import MIN_VALUE, MAX_VALUE

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
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj.id).exists()


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

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Добавьте тег.')
        if len(value) != len(set(value)):
            raise ValidationError('Теги не должны повторяться.')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте ингредиент.')
        ingredients = [item['id'] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise ValidationError(
                    'Такой ингредиент уже есть.'
                )
            if not Ingredient.objects.filter(pk=ingredient).first():
                raise ValidationError('Ингредиент не найден.')
        return value

    def validate_image(self, image):
        if not image:
            raise ValidationError('Добавьте изображение.')
        return image

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 1')
        return cooking_time

    def ingredient_recipe_bulk_create(self, ingredients, recipe):
        """Создание ингредиентов рецепта."""
        ingredient_instances = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            ingredient_instances.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            )
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
        if 'ingredients' not in validated_data or 'tags' not in validated_data:
            raise ValidationError('Поле не может быть пустым.')
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
    is_favorited = SerializerMethodField(method_name='get_favorited')
    is_in_shopping_cart = SerializerMethodField(method_name='get_shopping_cart')
    text = CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_favorited(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return FavoriteRecipe.objects.filter(
                user=request.user,
                recipe=obj).exists()
        return False

    def get_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False


class FavoriteRecipeSerializer(ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        if limit:
            recipes = recipes[:int(limit)]
        serialized_recipes = ShortCutRecipeSerializer(recipes, many=True).data
        return serialized_recipes

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()