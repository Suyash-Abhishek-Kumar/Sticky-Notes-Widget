"""
storage.py
----------
Handles loading and saving multiple notes to/from a JSON file.
No UI logic — pure file I/O and serialization.
"""

import json
import os
import sys

from note import Note

# Path to the JSON data file, relative to this script's directory.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

_DATA_DIR = os.path.join(BASE_DIR, "data")
_NOTES_FILE = os.path.join(_DATA_DIR, "notes.json")


def _ensure_data_dir():
    """Create the data directory if it doesn't exist yet."""
    os.makedirs(_DATA_DIR, exist_ok=True)


def load_notes() -> list[Note]:
    """
    Load all notes from the JSON file.
    If the file doesn't exist or is malformed, return an empty list.
    """
    _ensure_data_dir()

    if not os.path.exists(_NOTES_FILE):
        return []

    try:
        with open(_NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return [Note.from_dict(item) for item in data]

    except (json.JSONDecodeError, KeyError, TypeError):
        # Corrupted file → start fresh
        pass

    return []


def save_notes(notes: list[Note]):
    """
    Persist all notes to the JSON file using the required format:
    [
      { "id": 1, "text": "...", "x": 100, "y": 100 }
    ]
    """
    _ensure_data_dir()

    payload = [note.to_dict() for note in notes]

    with open(_NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
