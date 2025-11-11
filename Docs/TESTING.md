# 🧪 Рекомендації по тестуванню та розширенню

## Модульне тестування

Кожен модуль можна тестувати окремо, що робить заміни та оновлення безпечними.

### Тестування `models.py`

```python
from models import Phone, Email, Birthday, Record, Name

# Тест Phone валідації
print("=== Phone Validation ===")
try:
    good_phone = Phone("1234567890")
    print(f"✓ Valid: {good_phone}")
except ValueError as e:
    print(f"✗ Error: {e}")

try:
    bad_phone = Phone("123")  # Твердо 10 цифр
    print(f"✓ Valid: {bad_phone}")
except ValueError as e:
    print(f"✓ Caught error: {e}")

# Тест Email валідації
print("\n=== Email Validation ===")
test_emails = [
    ("john@example.com", True),
    ("invalid.email", False),
    ("user@domain.co.uk", True),
    ("", False),
]
for email_str, should_pass in test_emails:
    try:
        email = Email(email_str)
        print(f"✓ {email} - passed")
    except ValueError:
        print(f"✗ {email_str} - rejected (expected)" if not should_pass else f"✗ {email_str} - rejected")

# Тест Birthday
print("\n=== Birthday Validation ===")
try:
    bday = Birthday("15.03.1990")
    print(f"✓ Valid: {bday} -> date: {bday.as_date()}")
except ValueError as e:
    print(f"✗ Error: {e}")

# Тест Record
print("\n=== Record Management ===")
rec = Record(Name("John Doe"))
rec.add_phone(Phone("1234567890"))
rec.add_email(Email("john@example.com"))
rec.set_birthday(Birthday("15.03.1990"))
rec.set_address(models.Address("Kyiv, Ukraine"))

print(f"Record: {rec}")
print(f"Days to birthday: {rec.days_to_birthday()}")
```

### Тестування `storage.py`

```python
from storage import Storage, save_storage, load_storage, STORAGE_FILE
from models import Record, Name, Phone, Note

print(f"Storage file: {STORAGE_FILE}")

# Створити нові дані
storage = Storage()

# Додати контакт
rec = Record(Name("Alice"))
rec.add_phone(Phone("9876543210"))
storage.contacts.add_record(rec)

# Додати заметку
note = Note("Test Note", "This is a test")
note.add_tags("test", "example")
storage.notes.add(note)

# Зберегти
save_storage(storage)
print(f"✓ Saved {len(storage.contacts.data)} contacts and {len(storage.notes.data)} notes")

# Завантажити та перевірити
loaded = load_storage()
print(f"✓ Loaded {len(loaded.contacts.data)} contacts and {len(loaded.notes.data)} notes")
print(f"  Contact: {list(loaded.contacts.all())[0]}")
print(f"  Note: {list(loaded.notes.all())[0]}")
```

### Тестування `commands.py`

```python
from commands import REG, cmd_help
from storage import Storage

storage = Storage()

# Список всіх команд
print("=== Available Commands ===")
for cmd in REG.all_commands():
    print(f"  - {cmd}")

# Розпізнавання команд
print("\n=== Command Resolution ===")
test_inputs = ["help", "add", "change", "???"]
for inp in test_inputs:
    resolved = REG.resolve(inp)
    print(f"  '{inp}' -> '{resolved}'")

# Виклик команди
print("\n=== Help Command ===")
result = cmd_help([], storage)
print(result[:200] + "...")
```

## Сценарії тестування

### Сценарій 1: Повний цикл управління контактом

```python
from storage import load_storage, save_storage, Storage
from models import Record, Name, Phone, Email, Birthday, Address
import os

# Очистити старі дані для чистого тесту
os.system("rm ~/.personal_assistant_cli/storage.pkl 2>/dev/null")

storage = Storage()

# 1. Додати контакт
rec = Record(Name("Maria"))
storage.contacts.add_record(rec)
save_storage(storage)
print(f"✓ Added contact: {rec.name}")

# 2. Додати телефон
storage = load_storage()
rec = storage.contacts.get_record("Maria")
rec.add_phone(Phone("5555555555"))
save_storage(storage)
print(f"✓ Added phone")

# 3. Додати email
storage = load_storage()
rec = storage.contacts.get_record("Maria")
rec.add_email(Email("maria@mail.com"))
save_storage(storage)
print(f"✓ Added email")

# 4. Установить ДР
storage = load_storage()
rec = storage.contacts.get_record("Maria")
rec.set_birthday(Birthday("20.12.1995"))
save_storage(storage)
print(f"✓ Set birthday")

# 5. Отримати весь контакт
storage = load_storage()
rec = storage.contacts.get_record("Maria")
print(f"✓ Full record: {rec}")

# 6. Видалити контакт
storage.contacts.remove_record("Maria")
save_storage(storage)
print(f"✓ Deleted contact")

# 7. Перевірити, що його немає
storage = load_storage()
try:
    rec = storage.contacts.get_record("Maria")
    print(f"✗ Contact still exists!")
except KeyError:
    print(f"✓ Contact successfully deleted")
```

### Сценарій 2: Робота з нотатками та тегами

```python
from storage import load_storage, save_storage
from models import Note

storage = load_storage()

# Додати заметку з тегами
note1 = Note("Project Ideas", "1. Build API\n2. Add tests\n3. Deploy")
note1.add_tags("work", "urgent")
storage.notes.add(note1)

note2 = Note("Personal", "Remember to call mom on Sunday")
note2.add_tags("personal", "reminder")
storage.notes.add(note2)

save_storage(storage)

# Пошук за текстом
results = storage.notes.search_text("call")
print(f"✓ Search 'call': {[n.title for n in results]}")

# Пошук за тегом
results = storage.notes.search_tag("work")
print(f"✓ Search tag 'work': {[n.title for n in results]}")

# Сортування за датою створення
notes = storage.notes.all(sort_by="created")
print(f"✓ Sorted by date: {[n.title for n in notes]}")

# Сортування за назвою
notes = storage.notes.all(sort_by="title")
print(f"✓ Sorted by title: {[n.title for n in notes]}")
```

### Сценарій 3: Пошук та фільтрація

```python
from storage import load_storage
from models import Record, Name, Phone, Email

storage = load_storage()

# Додати кілька контактів
contacts_data = [
    ("John Smith", ["1111111111"], ["john@mail.com"]),
    ("Jane Doe", ["2222222222"], ["jane@mail.com"]),
    ("John Brown", ["3333333333"], ["john.brown@mail.com"]),
]

for name, phones, emails in contacts_data:
    rec = Record(Name(name))
    for p in phones:
        rec.add_phone(Phone(p))
    for e in emails:
        rec.add_email(Email(e))
    try:
        storage.contacts.add_record(rec)
    except KeyError:
        pass  # Вже існує

# Пошук за іменем
results = storage.contacts.search("John")
print(f"✓ Search 'John': {[r.name.value for r in results]}")

# Пошук за email
results = storage.contacts.search("mail.com")
print(f"✓ Search '@mail.com': {[r.name.value for r in results]}")

# Поточні дні рождения
upcoming = storage.contacts.upcoming_birthdays(7)
if upcoming:
    print(f"✓ Upcoming birthdays: {len(upcoming)} groups")
else:
    print(f"✓ No birthdays in 7 days")
```

## Тестування помилок

Всі помилки мають бути дружні:

```python
from commands import cmd_add
from storage import Storage
from models import Record, Name, Phone

storage = Storage()

# Помилка 1: Контакту не існує
print("=== Test Error Handling ===")
result = cmd_add(["NonExistent", "1234567890"], storage)
print(f"Result: {result}")
# Очікуємо: "Not found: 'NonExistent'."

# Помилка 2: Неправильний телефон
rec = Record(Name("Bob"))
storage.contacts.add_record(rec)
result = cmd_add(["Bob", "123"], storage)
print(f"Result: {result}")
# Очікуємо: "Value error: Phone must contain exactly 10 digits."

# Помилка 3: Не достатньо аргументів
result = cmd_add(["Bob"], storage)
print(f"Result: {result}")
# Очікуємо: "Not enough arguments. Use: help"
```

## CI/CD рекомендації

### GitHub Actions приклад (.github/workflows/test.yml)

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Compile Python files
        run: python -m py_compile config.py models.py storage.py commands.py cli.py main.py
      - name: Test models
        run: python -c "from models import Phone; Phone('1234567890')"
```

## 🎯 Контрольний список якості

Перед передачею коду переконайтеся:

- [ ] Всі файли компілюються без синтаксичних помилок
- [ ] Програма запускається та показує `help`
- [ ] Можна додавати/видаляти контакти
- [ ] Можна додавати/видаляти заметки з тегами
- [ ] Пошук коректно знаходить контакти
- [ ] Помилки вводу виводять дружні повідомлення
- [ ] Дані зберігаються і завантажуються
 - [ ] Команди розпізнаються строго за ім'ям
- [ ] Немає dead кода або невикористаних імпортів

Успіхів з розширенням проекту! 🚀
