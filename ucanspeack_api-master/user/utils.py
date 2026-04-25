"""Общие утилиты для приложения user."""
from django.contrib.auth import get_user_model


def find_user_by_login_or_email(value: str):
    """
    Ищет пользователя сначала по полю login, затем по email.
    Возвращает экземпляр User или None.

    Используется в:
    - CustomTokenCreateSerializer (логин)
    - ForceLoginView (выход отовсюду + вход)
    """
    if not value:
        return None

    User = get_user_model()
    value = value.strip()

    # Сначала ищем по login (точное совпадение, регистрозависимое)
    user = User.objects.filter(login=value).first()
    if user:
        return user

    # Потом по email (case-insensitive — email обычно нечувствителен)
    user = User.objects.filter(email__iexact=value).first()
    return user
