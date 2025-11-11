"""
Управление сохранением и загрузкой данных
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import pickle

from config import APP_NAME
from models import AddressBook, NoteBook


def app_storage_dir() -> Path:
    """Получить директорию хранения данных в домашней папке."""
    base = Path.home() / f".{APP_NAME}"
    base.mkdir(parents=True, exist_ok=True)
    return base


STORAGE_FILE = app_storage_dir() / "storage.pkl"


@dataclass
class Storage:
    """Контейнер для всех данных приложения."""

    contacts: AddressBook = field(default_factory=AddressBook)
    notes: NoteBook = field(default_factory=NoteBook)


def save_storage(storage: Storage) -> None:
    """Сохранить данные на диск."""
    with open(STORAGE_FILE, "wb") as f:
        pickle.dump(storage, f)


def load_storage() -> Storage:
    """Загрузить данные с диска или создать новое хранилище."""
    if STORAGE_FILE.exists():
        try:
            with open(STORAGE_FILE, "rb") as f:
                obj = pickle.load(f)
                if isinstance(obj, Storage):
                    return obj
        except Exception:
            # Файл повреждён — создадим новый
            pass
    return Storage()
