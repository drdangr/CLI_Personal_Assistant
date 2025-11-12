"""
Управління збереженням та завантаженням даних
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import pickle

from config import APP_NAME
from models import AddressBook, NoteBook


def app_storage_dir() -> Path:
    """Отримати директорію зберігання даних у домашній папці."""
    base = Path.home() / f".{APP_NAME}"
    base.mkdir(parents=True, exist_ok=True)
    return base


STORAGE_FILE = app_storage_dir() / "storage.pkl"


@dataclass
class Storage:
    """Контейнер для всіх даних застосунку."""

    contacts: AddressBook = field(default_factory=AddressBook)
    notes: NoteBook = field(default_factory=NoteBook)


def save_storage(storage: Storage) -> None:
    """Зберегти дані на диск."""
    with open(STORAGE_FILE, "wb") as f:
        pickle.dump(storage, f)


def load_storage() -> Storage:
    """Завантажити дані з диска або створити нове сховище."""
    if STORAGE_FILE.exists():
        try:
            with open(STORAGE_FILE, "rb") as f:
                obj = pickle.load(f)
                if isinstance(obj, Storage):
                    return obj
        except Exception:
            # Файл пошкоджено — створимо новий
            pass
    return Storage()
