"""
Модель данных для контактов и нотаток
"""

from __future__ import annotations

from collections import UserDict
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
import re
from calendar import isleap  # === ДОДАНО ===

from config import (
    BIRTHDAY_FORMAT,
    EMAIL_REGEX,
    PHONE_DIGITS,
    PHONE_REGEX,
)


# ==============================
# Поля для контактов (валідація)
# ==============================


class Field:
    """Базовое поле с рядковым значением."""

    def __init__(self, value: str) -> None:
        self._value = None
        self.value = value  # вызывает setter

    @property
    def value(self) -> str:
        if self._value is None:
            return ""
        return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        self._value = (
            new_value.strip() if isinstance(new_value, str) else str(new_value)
        )

    def __str__(self) -> str:
        return self.value


class Name(Field):
    """Имя контакта."""

    pass


class Phone(Field):
    """Телефон: ровно 10 цифр."""

    _re = re.compile(PHONE_REGEX)

    @Field.value.setter  # type: ignore[attr-defined]
    def value(self, new_value: str) -> None:
        s = (new_value or "").strip()
        if not self._re.fullmatch(s):
            raise ValueError(f"Phone must contain exactly {PHONE_DIGITS} digits.")
        self._value = s


class Email(Field):
    """Email с базовой валидацией."""

    _re = re.compile(EMAIL_REGEX)

    @Field.value.setter  # type: ignore[attr-defined]
    def value(self, new_value: str) -> None:
        s = (new_value or "").strip()
        if not self._re.fullmatch(s):
            raise ValueError("Invalid email format.")
        self._value = s


class Address(Field):
    """Адрес контакта."""

    pass


class Birthday(Field):
    """Дата рождения в формате DD.MM.YYYY."""

    @Field.value.setter  # type: ignore[attr-defined]
    def value(self, new_value: str) -> None:
        s = (new_value or "").strip()
        try:
            dt = datetime.strptime(s, BIRTHDAY_FORMAT)
        except ValueError:
            raise ValueError(f"Birthday must be in {BIRTHDAY_FORMAT} format.")
        self._value = dt.strftime(BIRTHDAY_FORMAT)

    def as_date(self) -> date:
        """Преобразовать в объект date."""
        return datetime.strptime(self.value, BIRTHDAY_FORMAT).date()


# ==============================
# Контакт и Книга контактов
# ==============================


class Record:
    """
    Один контакт с полями и методами управления.

    Пример:
        rec = Record(Name("John Doe"))
        rec.add_phone(Phone("1234567890"))
        rec.add_email(Email("john@example.com"))
        rec.set_birthday(Birthday("15.03.1990"))
        rec.set_address(Address("Kyiv, Ukraine"))

        print(rec)
        # Output: Name: John Doe | Phones: 1234567890 | Emails: john@example.com |
        #         Address: Kyiv, Ukraine | Birthday: 15.03.1990

        print(rec.days_to_birthday())  # количество дней до ДР
    """

    def __init__(self, name: Name) -> None:
        self.name: Name = name
        self.phones: List[Phone] = []
        self.emails: List[Email] = []
        self.address: Optional[Address] = None
        self.birthday: Optional[Birthday] = None

    # ----- Телефоны -----
    def add_phone(self, phone: Phone) -> None:
        """Добавить номер телефона."""
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)

    def remove_phone(self, phone_value: str) -> bool:
        """Удалить номер телефона по значению."""
        for i, p in enumerate(self.phones):
            if p.value == phone_value:
                self.phones.pop(i)
                return True
        return False

    def edit_phone(self, old_value: str, new_value: str) -> None:
        """Изменить номер телефона."""
        for p in self.phones:
            if p.value == old_value:
                p.value = new_value  # вызывает валидацию
                return
        raise KeyError(f"Phone '{old_value}' not found for contact '{self.name}'.")

    # ----- Email -----
    def add_email(self, email: Email) -> None:
        """Добавить email."""
        if email.value not in [e.value for e in self.emails]:
            self.emails.append(email)

    def remove_email(self, email_value: str) -> bool:
        """Удалить email по значению."""
        for i, e in enumerate(self.emails):
            if e.value == email_value:
                self.emails.pop(i)
                return True
        return False

    # ----- Адрес -----
    def set_address(self, address: Address) -> None:
        """Установить адрес."""
        self.address = address

    # ----- День рождения -----
    def set_birthday(self, bday: Birthday) -> None:
        """Установить день рождения."""
        self.birthday = bday

    def days_to_birthday(self, today: Optional[date] = None) -> Optional[int]:
        """
        Кількість днів до найближчого дня народження.

        Використовує get_next_birthday(), яка коректно обробляє
        випадок 29 лютого у невисокосні роки (зсув на 1 березня).
        """
        if not self.birthday:
            return None
        today = today or date.today()
        next_bd = self.get_next_birthday(today)
        if not next_bd:
            return None
        return (next_bd - today).days


    def get_next_birthday(self, today: Optional[date] = None) -> Optional[date]:
        """
        Отримати дату наступного дня народження.

        Аналогічно до days_to_birthday(), але повертає саму дату замість кількості днів.

        Приклади:
        - Сьогодні 10.11, день народження 15.11 → date(2025, 11, 15)
        - Сьогодні 20.11, день народження 15.11 → date(2026, 11, 15)
        """
        if not self.birthday:
            return None

        today = today or date.today()
        born = self.birthday.as_date()

        # === Обробка високосного року для 29 лютого ===
        year = today.year
        month = born.month
        day = born.day
        if month == 2 and day == 29 and not isleap(year):
            day = 1
            month = 3

        next_bd = date(year, month, day)

        if next_bd < today:
            year += 1
            month = born.month
            day = born.day
            if month == 2 and day == 29 and not isleap(year):
                day = 1
                month = 3
            next_bd = date(year, month, day)

        # === Кінець додавання ===
        return next_bd


    def __str__(self) -> str:
        parts = [f"Name: {self.name}"]
        if self.phones:
            parts.append("Phones: " + ", ".join(p.value for p in self.phones))
        if self.emails:
            parts.append("Emails: " + ", ".join(e.value for e in self.emails))
        if self.address:
            parts.append(f"Address: {self.address}")
        if self.birthday:
            parts.append(f"Birthday: {self.birthday.value}")
        return " | ".join(parts)


class AddressBook(UserDict):
    """Книга контактов (имя → Record)."""

    def add_record(self, record: Record) -> None:
        """Добавить контакт."""
        key = record.name.value.lower()
        if key in self.data:
            raise KeyError(f"Contact '{record.name.value}' already exists.")
        self.data[key] = record

    def get_record(self, name: str) -> Record:
        """Получить контакт по имени."""
        key = name.strip().lower()
        if key not in self.data:
            raise KeyError(name)
        return self.data[key]

    def remove_record(self, name: str) -> bool:
        """Удалить контакт по имени."""
        key = name.strip().lower()
        return self.data.pop(key, None) is not None

    def search(self, query: str) -> List[Record]:
        """Поиск контактов по различным полям."""
        q = query.lower().strip()
        results: List[Record] = []
        for r in self.data.values():
            hay = [
                r.name.value.lower(),
                *(p.value for p in r.phones),
                *(e.value.lower() for e in r.emails),
                (r.address.value.lower() if r.address else ""),
                (r.birthday.value if r.birthday else ""),
            ]
            if any(q in h.lower() for h in hay if h):
                results.append(r)
        return results

    def all(self) -> List[Record]:
        """Получить все контакты, отсортированные по имени."""
        return sorted(self.data.values(), key=lambda r: r.name.value.lower())

    def upcoming_birthdays(
        self, days: int, today: Optional[date] = None
    ) -> Dict[int, List[Tuple[str, str, str]]]:
        """
        Контакты с днями рождения в течение next N дней.
        Возвращает: дни_до → список (имя, dd.mm.yyyy, день_недели)
        """
        today = today or date.today()
        bucket: Dict[int, List[Tuple[str, str, str]]] = {}

        for r in self.data.values():
            delta = r.days_to_birthday(today)
            if delta is None or not (0 <= delta <= days):
                continue

            next_bd = r.get_next_birthday(today)
            wk = next_bd.strftime("%A")
            bucket.setdefault(delta, []).append((r.name.value, r.birthday.value, wk))

        # Сортируем каждый список по имени
        for d in bucket:
            bucket[d].sort(key=lambda t: t[0].lower())

        return dict(sorted(bucket.items(), key=lambda kv: kv[0]))


# ==============================
# Нотатки
# ==============================


@dataclass
class Note:
    """Заметка с текстом и тегами."""

    title: str
    text: str
    tags: set[str] = field(default_factory=set)
    created: datetime = field(default_factory=datetime.now)

    def add_tags(self, *tags: str) -> None:
        """Добавить теги к заметке."""
        self.tags.update(t.strip().lower() for t in tags if t.strip())

    def remove_tag(self, tag: str) -> bool:
        """Удалить тег из заметки."""
        t = tag.strip().lower()
        if t in self.tags:
            self.tags.remove(t)
            return True
        return False


class NoteBook(UserDict):
    """Записная книжка (название → Note)."""

    def add(self, note: Note) -> None:
        """Добавить заметку."""
        key = note.title.strip().lower()
        if key in self.data:
            raise KeyError(f"Note '{note.title}' already exists.")
        self.data[key] = note

    def get_note(self, title: str) -> Note:
        """Получить заметку по названию."""
        key = title.strip().lower()
        if key not in self.data:
            raise KeyError(title)
        return self.data[key]

    def remove(self, title: str) -> bool:
        """Удалить заметку по названию."""
        key = title.strip().lower()
        return self.data.pop(key, None) is not None

    def search_text(self, query: str) -> List[Note]:
        """Поиск заметок по тексту и названию."""
        q = query.lower().strip()
        return [
            n for n in self.data.values() if q in n.text.lower() or q in n.title.lower()
        ]

    def search_tag(self, tag: str) -> List[Note]:
        """Поиск заметок по тегу."""
        t = tag.lower().strip()
        return [n for n in self.data.values() if t in n.tags]

    def all(self, sort_by: str = "title") -> List[Note]:
        """Получить все заметки с сортировкой."""
        if sort_by == "created":
            return sorted(self.data.values(), key=lambda n: n.created)
        return sorted(self.data.values(), key=lambda n: n.title.lower())

if __name__ == "__main__":
    from datetime import date

    # Створюємо контакт із днем народження 29 лютого 2000 року

    record = Record(Name("Тестовий Контакт"))
    record.set_birthday(Birthday("29.02.2000"))

    # Тестуємо різні дати
    print("Сьогодні:", date.today())
    print("Наступний день народження:", record.get_next_birthday(date(2025, 11, 12)))
    print("Днів до ДН:", record.days_to_birthday(date(2025, 11, 12)))
 
 