from colorfield.fields import ColorField
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    SlugField,
    TextField,
    UniqueConstraint,
)

from users.models import User
from foodgram.constants import (
    MAX_NAME_LENGTH_TAG,
    MAX_NAME_LENGTH_INGREDIENT,
    MAX_NAME_LENGTH_RECIPE,
    MAX_SLUG_LENGTH,
    MIN_VALUE,
    MAX_VALUE,
)


class Tag(Model):
    """Модель тегов."""

    name = CharField(
        'Тег',
        max_length=MAX_NAME_LENGTH_TAG,
        unique=True,
    )
    color = ColorField(
        'Цвет',
        format='hex'
    )
    slug = SlugField(
        'Слаг тега',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name


class Ingredient(Model):
    """Модель ингредиентов."""

    name = CharField(
        'Название ингридиента',
        max_length=MAX_NAME_LENGTH_INGREDIENT,
    )
    measurement_unit = CharField(
        'Единица измерения',
        max_length=MAX_SLUG_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient_fields',),
        ]

    def __str__(self):
        return self.name


class Recipe(Model):
    """Модель рецептов."""

    author = ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=CASCADE,
        related_name='recipes'
    )
    name = CharField(
        'Название рецепта',
        max_length=MAX_NAME_LENGTH_RECIPE,
    )
    image = ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    description = TextField(
        'Описание рецепта',
    )
    ingredients = ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe',
    )
    tags = ManyToManyField(
        Tag,
        verbose_name='Тег',
        through='TagsRecipe',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message='Время готовки не может '
                f'быть меньше {MIN_VALUE} минуты'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='Время готовки не может '
                f'быть больше {MAX_VALUE} минуты'
            ),
        ]
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name


class FavoritesShopCart(Model):
    """Абстрактная модель избранных рецептов и покупок."""

    user = ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE
    )

    class Meta:
        abstract = True


class FavoriteRecipe(FavoritesShopCart):
    """Модель избранных рецептов."""

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'


class ShoppingCart(FavoritesShopCart):
    """Модель списка покупок."""

    class Meta:
        default_related_name = 'shop_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe'
            )
        ]


class TagsRecipe(Model):
    """Промежуточная модель для связи тегов и рецептов."""

    tag = ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ('recipe__name',)

    def __str__(self):
        return f'{self.tag}'


class IngredientRecipe(Model):
    """Промежуточная модель для связи ингредиентов и рецептов."""

    ingredient = ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=CASCADE,
        related_name='ingredient'
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE,
        related_name='recipe'
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_VALUE,
                message='Количество ингредиентов '
                f'не может быть меньше {MIN_VALUE}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='Количество ингредиентов '
                f'не может быть больше {MAX_VALUE}'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        ordering = ('ingredient__name',)
        constraints = [
            UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients_recipe')
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}: {self.amount}'
