

## Как использовать

### Запуск программы
```bash
python3 main.py
```

### Добавить новую команду
1. В `commands.py` создайте функцию-обработчик.
2. Зарегистрируйте её через `@REG.register(..., section=..., min_args=...)`.
3. Укажите `min_args` для автоматической валідації кількості аргументів.
4. Добавьте краткое описание в документацию при необходимости.

### Заменить хранилище
1. Отредактируйте storage.py
2. Поменяйте save/load функции
3. Остальной код не меняется


## Примеры использования

### Тестирование моделей
```python
from models import Phone, Email

# Валиднэ телефон
p = Phone("1234567890")  # OK

# Невалидный телефон
try:
    p = Phone("123")  # Error
except ValueError as e:
    print(e)  # "Phone must contain exactly 10 digits."
```

### Работа с контактами
```python
from models import Record, Name, Phone
from storage import load_storage, save_storage

storage = load_storage()

# Создать контакт
rec = Record(Name("Alice"))
rec.add_phone(Phone("9876543210"))
storage.contacts.add_record(rec)

# Сохранить
save_storage(storage)

# Найти
rec = storage.contacts.get_record("Alice")
```

### Работа с командами
```python
from commands import REG, cmd_help
from storage import Storage

storage = Storage()

# Список всех команд
for cmd in REG.all_commands():
    print(cmd)

# Выполнить команду
result = cmd_help([], storage)
print(result)
```
