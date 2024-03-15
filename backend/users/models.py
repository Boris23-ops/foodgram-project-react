from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import (
    CASCADE,
    CharField,
    EmailField,
    ForeignKey,
    Model,
    UniqueConstraint,
    CheckConstraint,
    F, Q,
)

from foodgram.constants import (
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
)


class User(AbstractUser):
    """Модель пользователя."""
    email = EmailField(
        'Электронная почта',
        max_length=MAX_EMAIL_LENGTH,
        unique=True
    )
    username = CharField(
        unique=True,
        max_length=MAX_USERNAME_LENGTH,
        verbose_name='имя пользователя',
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    first_name = CharField(
        'Имя',
        max_length=MAX_NAME_LENGTH
    )
    last_name = CharField(
        'Фамилия',
        max_length=MAX_NAME_LENGTH
    )
    password = CharField(
        'Пароль',
        max_length=MAX_PASSWORD_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(Model):
    """Модель для подписки."""

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-author_id',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribes'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='check_different_users'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
