"""
Конфигурация приложения «Персональный помощник»
"""

# Приложение
APP_NAME = "personal_assistant_cli"
APP_VERSION = "1.0.0"

# Валидация контактов
PHONE_DIGITS = 10
PHONE_REGEX = r"^\d{10}$"
EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
BIRTHDAY_FORMAT = "%d.%m.%Y"

# Дни рождения по умолчанию
UPCOMING_DAYS_DEFAULT = 7

# Форматирование вывода
SEPARATOR = "\n\n---\n\n"
