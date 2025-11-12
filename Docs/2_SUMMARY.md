

## Як використовувати

### Запуск програми
```bash
python3 main.py
```

### Додати нову команду
1. В `commands.py` створіть функцію-обробник.
2. Зареєструйте її через `@REG.register(..., section=..., min_args=...)`.
3. Вкажіть `min_args` для автоматичної валідації кількості аргументів.
4. Додайте короткий опис у документацію за потреби.

### Замінити сховище
1. Відредагуйте storage.py
2. Змініть save/load функції
3. Решта коду не змінюється


## Приклади використання

### Тестування моделей
```python
from models import Phone, Email

# Валідний телефон
p = Phone("1234567890")  # OK

# Невалідний телефон
try:
    p = Phone("123")  # Error
except ValueError as e:
    print(e)  # "Phone must contain exactly 10 digits."
```

### Робота з контактами
```python
from models import Record, Name, Phone
from storage import load_storage, save_storage

storage = load_storage()

# Створити контакт
rec = Record(Name("Alice"))
rec.add_phone(Phone("9876543210"))
storage.contacts.add_record(rec)

# Зберегти
save_storage(storage)

# Знайти
rec = storage.contacts.get_record("Alice")
```

### Робота з командами
```python
from commands import REG, cmd_help
from storage import Storage

storage = Storage()

# Список всіх команд
for cmd in REG.all_commands():
    print(cmd)

# Виконати команду
result = cmd_help([], storage)
print(result)
```
