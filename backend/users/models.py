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


class User(AbstractUser):
    """Модель пользователя."""

    email = EmailField(
        'Электронная почта',
        max_length=254,
        unique=True
    )
    username = CharField(
        unique=True,
        max_length=150,
        verbose_name='имя пользователя',
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    first_name = CharField(
        'Имя',
        max_length=150
    )
    last_name = CharField(
        'Фамилия',
        max_length=150
    )
    password = CharField(
        'Пароль',
        max_length=150
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
                name='user_cannot_follow_self'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
