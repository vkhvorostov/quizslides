"""
Настройки Django для тестирования.
"""
from .settings import *  # noqa

# Используем SQLite в памяти для быстрых тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Отключаем пароли валидации для ускорения
AUTH_PASSWORD_VALIDATORS = []

# Отключаем статику
STATIC_URL = '/static/'
STATIC_ROOT = None

# Ускоряем тесты
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем отправку почты
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'