from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def year_create_validator(value):
    """
    Валидатор для проверки года выпуска произведения.
    """
    timezone.activate(settings.TIME_ZONE)
    if value > timezone.now().year:
        raise ValidationError('Год выпуска не может быть больше текущего.')
