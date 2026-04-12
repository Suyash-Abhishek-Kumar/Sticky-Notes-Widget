# Sticky Notes App

A lightweight desktop sticky notes widget for Windows, built using Python and Tkinter.

This app provides fast, persistent, and customizable sticky notes that behave like desktop widgets.

---

## Features

### Core

* Multiple independent notes
* Click-to-edit with Shift+Enter for new lines
* Drag and reposition notes
* Auto-save (no manual saving required)
* Pin / unpin notes (always-on-top support)

### Productivity

* Collapse notes into compact header view
* Smart snapping between notes for alignment
* 5 color themes for categorization

### UX Enhancements

* Auto-resizing notes based on content
* Smooth drag behavior with snap locking
* Rounded edges for a cleaner UI
* Desktop-style behavior (stays out of the way when working)

### System

* Runs on Windows startup
* Packaged as standalone `.exe` (no Python required)

---

## Demo / Preview

<p align="center">
  <img src="https://github.com/user-attachments/assets/93c082ea-5d4e-4aed-8554-1215b8485665" height="200" />
  <img src="https://github.com/user-attachments/assets/50bf83e8-f004-4648-9201-74c92d79853c" height="200" />
  <br>
  <img src="https://github.com/user-attachments/assets/463fbe0b-fa27-4fd8-a5e2-28ae8640592f" height="200" />
</p>

---

## Installation

### Option 1 — Download Release (Recommended)

1. Go to the **Releases** section
2. Download the latest `.zip`
3. Extract it
4. Run:

```bash
StickyNotes.exe
```

---

### Option 2 — Run from Source

#### Requirements

* Python 3.10+

#### Steps

```bash
git clone https://github.com/Suyash-Abhishek-Kumar/Stiky-Notes-Widget.git
cd Stiky-Notes-Widget
python main.py
```

---

## Build (Executable)

To build the app yourself:

```bash
pyinstaller --onedir --noconsole --name "StickyNotes" main.py
```

Output:

```bash
dist/StickyNotes/StickyNotes.exe
```

---

## Run on Startup

To ensure the app launches automatically when Windows starts, use **Task Scheduler**.

### Steps

1. Press `Win + R`
2. Type `taskschd.msc`
3. Click **Create Basic Task…**
4. Name it `Sticky Notes Startup`
5. Trigger → **When I log on**
6. Action → **Start a program**
7. Select:

```
dist/StickyNotes/StickyNotes.exe
```

8. Finish setup

---

## Usage

* **Click note** → Edit

* **Enter** → Save

* **Shift + Enter** → New line

* **Drag header** → Move note

* **Right click** →

  * New note
  * Delete note
  * Change color
  * Pin / Unpin

* **Collapse button (– / +)** → Toggle compact mode

* **Drag near another note** → Snap into alignment

---

## Project Structure

```text
.
├── main.py
├── ui_note.py
├── note.py
├── storage.py
├── data/
```

---

## Known Limitations

* Built using Tkinter (limited native styling)
* Desktop behavior is simulated using Z-order (not true widget layer)
* Windows-only (uses Win32 APIs)

---

## Roadmap

* System tray support
* Improved snap alignment (grid / spacing)
* Optional opacity control

---

## Contributing

Contributions are welcome. Feel free to open issues or submit pull requests.

---

## License

MIT License

---

## Author

Built by Suyash Abhishek Kumar

---

## Acknowledgements

* Python Tkinter
* PyInstaller
* Windows Win32 API
