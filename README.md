# Sticky Notes App

A lightweight desktop sticky notes widget for Windows, built using Python and Tkinter.

This app provides fast, persistent, and customizable sticky notes that behave like desktop widgets.

---

## Features

* Multiple independent notes
* Click-to-edit with Shift+Enter for new lines
* Drag and reposition notes
* Auto-save (no manual saving required)
* Pin / unpin notes (always-on-top support)
* 5 color themes for categorization
* Auto-resizing notes based on content
* Runs on Windows startup
* Packaged as standalone `.exe` (no Python required)

---

## Demo / Preview

<img src="https://github.com/user-attachments/assets/a285ff6f-859c-4628-8bb0-96512883d702" height="200" />
<img src="https://github.com/user-attachments/assets/5279f206-1a40-4300-ad83-ccb19ae7364a" height="200" />



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
git clone https://github.com/Suyash-Abhishek-Kumar/Sticky-Notes-Widget.git
cd sticky-notes-app
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

---

### Steps

1. Press:

```
Win + R
```

2. Type:

```
taskschd.msc
```

3. Click **Create Basic Task…**

4. Name:

```
Sticky Notes Startup
```

5. Trigger:

* Select **When I log on**

6. Action:

* Select **Start a program**

7. Browse and select:

```
dist/StickyNotes/StickyNotes.exe
```

8. Finish setup

---

## Project Structure

```text
.
├── main.py          # App entry point
├── ui_note.py       # UI logic
├── note.py          # Note data model
├── storage.py       # Save/load logic
├── data/            # Notes JSON storage
```

---

## Usage

* **Left click** → Edit note
* **Enter** → Save
* **Shift + Enter** → New line
* **Drag top bar** → Move note
* **Right click** →

  * New note
  * Delete note
  * Change color
  * Pin / Unpin

---

## Known Limitations

* Built using Tkinter (limited native styling)
* Unpinned notes use Z-order tricks (not true desktop layer)
* Windows-only (uses Win32 APIs)

---

## Roadmap

* System tray support
* True desktop widget mode (WorkerW)
* Snap-to-edge behavior
* Opacity control per note

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
