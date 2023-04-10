from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import (
    username_name_list_validator,
    username_pattern_validation,
)


class UserRole(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    """
    Переопределение модели User. Модель расширена свойствами role и bio.
    Любой пользователь может получить одну из 3х ролей управления. Только
    superuser получает права доступа к административной части сайта, при этом
    изменение его пользовательской роли не влияет вышеуказанные права.
    Обычный пользователь получив роль 'admin' может осуществлять управление
    пользователя через API без доступа к административной части сайта.
    """

    username = models.CharField(
        verbose_name='Пользователь',
        blank=False,
        unique=True,
        max_length=150,
        validators=[username_pattern_validation, username_name_list_validator],
    )

    email = models.EmailField(
        verbose_name='Почтовый адрес',
        blank=False,
        unique=True,
        max_length=254,
    )

    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        null=True,
    )

    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль',
    )

    first_name = models.CharField(
        verbose_name="Имя пользователя",
        max_length=150,
        blank=True,
        null=True,
    )

    last_name = models.CharField(
        verbose_name="Фамилия пользователя",
        max_length=150,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_username_email'
            )
        ]

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR
