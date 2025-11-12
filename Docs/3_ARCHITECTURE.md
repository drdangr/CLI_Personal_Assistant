# Архітектура "Персонального помічника"

## Структура проекту

Проект розділений на модулі для максимальної читаємості та підтримуваності:

```
f_project/
├── config.py           — Константи та конфігурація
├── models.py           — Моделі даних (Field, Record, AddressBook, Note, NoteBook)
├── storage.py          — Збереження та завантаження даних
├── commands.py         — Реєстр команд та їх обробники
├── cli.py              — Парсер командного рядка та головний цикл
└── main.py             — Точка входу
```

## Опис модулів

### `config.py`
Централізована конфігурація з усіма магічними числами та регулярними виразами:
 - `PHONE_DIGITS` — кількість цифр у телефоні (10)
 - `PHONE_REGEX` — паттерн валідації телефону
 - `EMAIL_REGEX` — паттерн валідації email
 - `BIRTHDAY_FORMAT` — формат дати ДР (DD.MM.YYYY)
 - (removed) `COMMAND_SUGGESTION_CUTOFF` — suggestion feature removed; commands are strict

**Переваги:**
- Легко змінити налаштування в одному місці
- Всі константи на виду
- Разом висячі значення закінчені

### `models.py`
Моделі даних та їх поведінка:

**Класи полів:**
- `Field` — базовий клас з валідацією
- `Name` — ім'я контакту
- `Phone` — телефон (10 цифр)
- `Email` — email (базова валідація)
- `Address` — адреса
- `Birthday` — дата народження (DD.MM.YYYY)

**Класи даних:**
- `Record` — контакт з полями та методами (add_phone, edit_phone, set_address, etc.)
- `AddressBook` — словник контактів з пошуком і групуванням ДР
- `Note` — заметка з текстом та тегами
- `NoteBook` — словник заметок з пошуком по текту та тегам

**Переваги:**
- Чітка інкапсуляція даних
- Валідація в точці вводу (у сеттерах)
- Просто тестувати окремо від UI

### `storage.py`
Управління збереженням і завантаженням:
- `Storage` — контейнер для всіх даних (контакти + заметки)
- `save_storage()` — серіалізація в pickle
- `load_storage()` — десеріалізація з обробкою помилок
- `app_storage_dir()` — папка в домашній директорії (~/.personal_assistant_cli/)

**Переваги:**
- Відокремлена логіка персистентності
- Легко переключитися на JSON/CSV/БД


### `commands.py`
Реєстр команд та їх обробники:
- `CommandRegistry` — централізований реєстр з строгим співпадінням по імені
- `@REG.register()` — декоратор для реєстрації команди з параметром `min_args`
- `validate_args()` — метод для централізованої валідації кількості аргументів
- `@input_error` — декоратор для обробки помилок
- `@mutating` — декоратор для автоматичного збереження
- `cmd_*()` — обробники команд (`cmd_add`, `cmd_change`, `cmd_add_note`, ...)

**Переваги:**
- Єдина точка входу для всіх команд
- Легко додати нову команду (3-4 рядки коду)
- Автоматична валідація кількості аргументів
- Автоматична генерація довідки
- Централізована обробка помилок

### `cli.py`
Інтерфейс користувача:
- `parse_input()` — розбір команди з аргументами (підтримує лапки)
- `run_cli()` — головний REPL цикл (команди вводяться строго)

**Переваги:**
- Чистий розділ на парсинг і обробку
- Легко замінити на web/GUI/API

### `main.py`
Точка входу програми — дуже простий файл:
```python
from cli import run_cli

if __name__ == "__main__":
    run_cli()
```


## Потік даних

```
Користувач вводить команду
         ↓
    parse_input() — розбір
         ↓
  REG.resolve() — розпізнавання
         ↓
  REG.validate_args() — перевірка кількості аргументів
         ↓
  handler(args, storage) — обробка
         ↓
  Валідація даних + операція
         ↓
  save_storage() — збереження (якщо @mutating)
         ↓
   Повернення результату
```


## Як використовувати

### Запуск
```bash
python3 main.py
```

### Додавання нової команди (3 кроки)

```python
# 1. Імпортуємо в commands.py
from models import YourModel

# 2. Реєструємо з @REG.register та min_args
@REG.register(
    "your-command", 
    help="Usage: your-command arg1 arg2",
    min_args=2  # автоматична валідація кількості аргументів
)
@input_error
def cmd_your_command(args: List[str], storage: Storage) -> str:
    # Валідація вже пройшла, можна безпечно використовувати args[0], args[1]
    # Обробка
    return "Результат"

# Готово! Команда автоматично з'явиться в help
```

### Використання моделей

```python
from models import Record, Name, Phone, Email, Birthday
from storage import load_storage, save_storage

storage = load_storage()

# Створити контакт
rec = Record(Name("John Doe"))
rec.add_phone(Phone("1234567890"))
rec.add_email(Email("john@example.com"))
rec.set_birthday(Birthday("15.03.1990"))

# Додати до книги
storage.contacts.add_record(rec)

# Зберегти
save_storage(storage)

# Пошук
results = storage.contacts.search("john")
```

## Тестування

Кожен модуль можна тестувати окремо:

```python
# Тест моделей
from models import Phone

try:
    p = Phone("1234567890")  # ✓ OK
    print(p)  # 1234567890
except ValueError as e:
    print(e)

try:
    p = Phone("12345")  # ✗ Error
except ValueError as e:
    print(e)  # Phone must contain exactly 10 digits.
```

## Який наступний крок?

Поточна архітектура дозволяє легко:
- Додати роботу с нечітким вводом команди
