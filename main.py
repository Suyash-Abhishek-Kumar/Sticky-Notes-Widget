"""
main.py
-------
Entry point for the StickyNotes app.
Wires together: storage (load) → Note model → NoteWindow UI → Tk event loop.
"""

import tkinter as tk

import storage
from note import Note
from ui_note import NoteWindow


class NoteApp:
    """Manages the full lifecycle of multiple sticky notes."""

    def __init__(self):
        # 1. Provide a hidden root window so Toplevel notes can exist independently
        self.root = tk.Tk()
        self.root.withdraw()

        # 2. Load all persisted notes
        self.notes: list[Note] = storage.load_notes()

        # Generate a default note if starting completely fresh
        if not self.notes:
            default_note = Note(note_id=self._get_next_id())
            self.notes.append(default_note)

        # 3. Create individual windows for each note
        for note in self.notes:
            self._create_note_window(note)

    def _get_next_id(self) -> int:
        """Calculate the next available unique note ID to prevent reusing IDs."""
        if not self.notes:
            return 1
        return max(note.id for note in self.notes) + 1

    def _create_note_window(self, note: Note):
        """Spawn an independent Toplevel window for a note instance."""
        window = tk.Toplevel(self.root)
        NoteWindow(
            window, 
            note, 
            on_save=self.save_all,
            on_new=self.create_note,
            on_delete=self.delete_note
        )

    def create_note(self, x: int, y: int):
        """Global callback: create a new note model and spawn its window."""
        new_note = Note(note_id=self._get_next_id(), text="", x=x, y=y)
        self.notes.append(new_note)
        self._create_note_window(new_note)
        self.save_all()

    def delete_note(self, note: Note, window: tk.Toplevel):
        """Global callback: delete a note model and destroy its window."""
        if note in self.notes:
            self.notes.remove(note)
        window.destroy()

        self.save_all()

        if not self.notes:
            self.root.quit()

    def save_all(self):
        """Centralized save handler. Saves the entire dataset of notes."""
        storage.save_notes(self.notes)

    def run(self):
        # 4. Start the event loop
        self.root.mainloop()


def main():
    app = NoteApp()
    app.run()


if __name__ == "__main__":
    main()
