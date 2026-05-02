"""
ui_note.py
----------
UI logic for a single sticky note window.
Depends on: note.py (data model).
No business logic beyond what's needed to drive the UI.
"""

import tkinter as tk
import tkinter.font as tkfont
import ctypes
from ctypes import wintypes
from note import Note

# ── Windows OS Constants ──────────────────────────────────────────────────────
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
HWND_BOTTOM = 1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2

# ── Visual Constants ──────────────────────────────────────────────────────────
NOTE_WIDTH = 250
NOTE_HEIGHT = 250
MIN_HEIGHT = 70
MAX_HEIGHT = 350
COLLAPSED_HEIGHT = 25
TOP_BAR_HEIGHT = 24

FONT = ("Segoe UI", 11)
DRAG_DEBOUNCE_MS = 50
SNAP_DIST = 20
UNLOCK_DIST = 30
X_SNAP_PADDING = 2
Y_SNAP_PADDING = 2

THEMES = {
    "Yellow": {"bg": "#FFF8B0", "top": "#F2DC7D", "text": "#2B2B2B"},
    "Blue":   {"bg": "#DCEBFF", "top": "#A9C9FF", "text": "#1F2A44"},
    "Green":  {"bg": "#DFFFE0", "top": "#A8E6A3", "text": "#1E3D1E"},
    "Pink":   {"bg": "#FFE4EC", "top": "#FFB6C1", "text": "#4A1F2B"},
    "Purple": {"bg": "#E9E0FF", "top": "#C8B6FF", "text": "#2E1F4A"}
}

HOVER_MAP = {
    "#F2DC7D": "#E6D173",
    "#A9C9FF": "#94B8F7",
    "#A8E6A3": "#92D98D",
    "#FFB6C1": "#F0A3AF",
    "#C8B6FF": "#B6A3F0"
}


class NoteWindow:
    """
    Manages a single borderless sticky note window.

    Responsibilities:
    - Render display mode (Label) and edit mode (Text widget).
    - Handle click-to-edit transitions.
    - Handle drag-to-move with snapping logic.
    - Context menu for creating, deleting, snapping, and pinning notes.
    - Trigger centralized saves via callback.
    - OS-level Pin/Unpin logic.
    """

    def __init__(self, window: tk.Toplevel, note: Note, on_save: callable, on_new: callable, on_delete: callable):
        self._window = window
        self._note = note
        
        # Callbacks provided by main app
        self._on_save = on_save
        self._on_new = on_new
        self._on_delete = on_delete

        # Drag state — tracks mouse offset from window origin
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._snap_lock_x = None
        self._snap_lock_y = None
        
        # Debounce save-on-drag: hold the pending after() id
        self._drag_save_job = None
        
        self._is_editing = False
        self.allow_snapping = True

        self._setup_window()
        self._build_ui()
        self._create_context_menu()
        self._bind_events()
        
        # Load text silently into textbox to measure bounds before rendering
        self._textbox.insert("1.0", self._note.text)
        
        # Apply initial state formatting cleanly avoiding jarring resizes
        if self._note.collapsed:
            self._apply_collapse_state()
            self._show_display_mode()
        else:
            self._show_display_mode()
            self._adjust_height()

        # Show window AFTER everything is ready
        self._window.after(0, self._finalize_show)

    # ── Initialization & UI Building ──────────────────────────────────────────

    def _setup_window(self):
        """Configure the Toplevel window as a borderless sticky note."""
        self._window.withdraw()
        self._window.overrideredirect(True)          # Remove title bar / borders
        self._window.geometry(f"{NOTE_WIDTH}x{NOTE_HEIGHT}+{self._note.x}+{self._note.y}")
        self._window.configure(bg=self._note.bg_color)
        self._window.resizable(False, False)
        
        # Apply slight transparency for a modern clean feel
        self._window.attributes("-alpha", 0.95)
        
        # Force Tkinter to map the window to OS
        self._window.update_idletasks()
        
        # Apply the desktop priority right away (pinned/unpinned behavior)
        self._apply_pin_state()

    def _build_ui(self):
        """Create both the display label and the edit text widget."""
        # Outer frame for subtle border softening
        self._outer_frame = tk.Frame(self._window, highlightthickness=0, highlightbackground="#D9CA82")
        self._outer_frame.pack(fill="both", expand=True)

        # A thin top bar acts as the drag handle region (visual cue)
        self._top_bar = tk.Frame(self._outer_frame, height=TOP_BAR_HEIGHT, cursor="fleur")
        self._top_bar.pack(fill="x", side="top")
        self._top_bar.pack_propagate(False)

        # Toggle collapse/expand button inside the top bar
        self._toggle_btn = tk.Label(
            self._top_bar,
            text="+" if self._note.collapsed else "–",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=6,
            pady=2
        )
        self._toggle_btn.pack(side="right")
        self._toggle_btn.bind("<Button-1>", lambda e: self._cmd_toggle_collapse())
        
        # Header text preview visible during collapsed modes natively
        self._preview_label = tk.Label(
            self._top_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            cursor="fleur",
            padx=6
        )
        self._preview_label.pack(side="left")

        # Main content frame (fills remaining space)
        self._content_frame = tk.Frame(self._outer_frame)
        self._content_frame.pack(fill="both", expand=True)

        # Display label (shown when NOT editing)
        self._label = tk.Label(
            self._content_frame,
            text="",
            font=FONT,
            wraplength=NOTE_WIDTH - 24,  # Increased bounding to account for padding
            justify="left",
            anchor="nw",
            padx=12,
            pady=10,
        )

        # Edit text widget (shown when editing)
        self._textbox = tk.Text(
            self._content_frame,
            font=FONT,
            wrap="word",
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            undo=True,
        )
        
        # Resolve layout colors according to current saved states dynamically
        self._apply_colors()

    def _create_context_menu(self):
        """Create the right-click menu."""
        self._menu = tk.Menu(self._window, tearoff=0)
        self._menu.add_command(label="Pin Note", command=self._cmd_toggle_pin)
        
        # Color submenu
        self._color_menu = tk.Menu(self._menu, tearoff=0)
        for theme_name, theme_colors in THEMES.items():
            self._color_menu.add_command(
                label=theme_name,
                command=lambda n=theme_name, c=theme_colors: self._cmd_change_color(n, c)
            )
        self._menu.add_cascade(label="Color", menu=self._color_menu)
        
        self._menu.add_separator()
        self._menu.add_command(label="Disable Snapping", command=self._toggle_snapping)
        self._snap_menu_index = self._menu.index("end")
        self._menu.add_command(label="New Note", command=self._cmd_new_note)
        self._menu.add_command(label="Delete Note", command=self._cmd_delete_note)
    
    def _bind_events(self):
        """Attach all event handlers."""
        # Click on the label → enter edit mode
        self._label.bind("<Button-1>", self._on_label_click)

        # Drag events on the top bar and content frame → move window
        for widget in (self._top_bar, self._preview_label, self._content_frame):
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<ButtonRelease-1>", self._on_drag_end)

        # Clicking outside this window → save & exit edit mode
        self._window.bind("<FocusOut>", self._on_focus_out)
        
        # Enter key inside the text widget → save & exit edit mode
        self._textbox.bind("<Return>", self._on_enter_key)
        
        # Shift+Enter inside the text widget → insert newline natively
        self._textbox.bind("<Shift-Return>", self._on_shift_enter_key)

        # Right click bindings (<Button-3> on Windows)
        self._label.bind("<Button-3>", self._show_menu)
        self._textbox.bind("<Button-3>", self._show_menu)
        self._top_bar.bind("<Button-3>", self._show_menu)
        self._content_frame.bind("<Button-3>", self._show_menu)
        self._preview_label.bind("<Button-3>", self._show_menu)

    # ── State & UI Updates ────────────────────────────────────────────────────

    def _apply_colors(self):
        """Paint UI dynamically according to current note color profile."""
        bg = self._note.bg_color
        top = self._note.top_bar_color
        text = self._note.text_color
        hover = HOVER_MAP.get(top, top)

        self._window.configure(bg=bg)
        self._outer_frame.configure(bg=bg)
        self._content_frame.configure(bg=bg)
        self._label.configure(bg=bg, fg=text)
        self._textbox.configure(bg=bg, fg=text, insertbackground=text)

        self._set_topbar_color(top)

        # Update dynamic hover bindings cleanly inside lambda
        for widget in (self._top_bar, self._preview_label, self._toggle_btn):
            widget.bind("<Enter>", lambda e, h=hover: self._set_topbar_color(h))
            widget.bind("<Leave>", lambda e, c=top: self._set_topbar_color(c))

    def _set_topbar_color(self, color):
        self._top_bar.configure(bg=color)
        self._preview_label.configure(bg=color)
        self._toggle_btn.configure(bg=color)

    def _apply_pin_state(self):
        """Set window OS positioning (Top/Bottom) gracefully without hijacking focus."""
        self._window.update_idletasks()
        self._window.attributes("-topmost", bool(self._note.pinned))

    def _apply_rounded_corners(self):
        """Apply Windows 11 perfectly smooth hardware-accelerated rounded corners."""
        self._window.update_idletasks()
        try:
            hwnd = int(self._window.wm_frame(), 16)
        except Exception:
            hwnd = self._window.winfo_id()
            
        # Ensure any old jagged GDI regions are destroyed
        ctypes.windll.user32.SetWindowRgn(hwnd, 0, True)
        
        try:
            # Force DWM native anti-aliased corners (Windows 11)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(ctypes.c_int(DWMWCP_ROUND)), 4
            )
        except Exception:
            pass

    def _apply_collapse_state(self):
        """Morph UI into a narrow preview strip or expanding back into full canvas."""
        if self._note.collapsed:
            # Strip content context entirely
            self._content_frame.pack_forget()
            self._toggle_btn.configure(text="+")
            
            # Formulate the truncated title line natively scaling it dynamically
            lines = self._note.text.strip("\n").split('\n')
            first_line = lines[0].strip() if lines else ""
            
            if not first_line:
                preview = "Empty"
            elif len(first_line) > 10:
                preview = first_line[:10] + "..."
            else:
                preview = first_line
                
            self._preview_label.configure(text=preview)
            
            # Compress Height natively avoiding OS flashing
            self._window.geometry(f"{NOTE_WIDTH}x{COLLAPSED_HEIGHT}+{self._note.x}+{self._note.y}")
        else:
            # Expand frame mappings
            self._toggle_btn.configure(text="–")
            self._preview_label.configure(text="")
            self._content_frame.pack(fill="both", expand=True)
            self._adjust_height()
            
        self._apply_rounded_corners()

    def _adjust_height(self):
        """Update window geometry dynamically based on inner text lines."""
        if self._note.collapsed:
            return

        line_count = self._calculate_display_lines(self._note.text)
        padding = 54
        line_height = 20

        # Clamp height to requested constraint pixels (~70 minimum, ~350 maximum)
        final_height = max(MIN_HEIGHT, min((line_count * line_height) + padding, MAX_HEIGHT))
        self._window.geometry(f"{NOTE_WIDTH}x{final_height}+{self._note.x}+{self._note.y}")
        self._apply_rounded_corners()

    def _calculate_display_lines(self, text):
        font = tkfont.Font(font=FONT)
        max_width = NOTE_WIDTH - 24 

        lines = 0
        for line in text.split("\n"):
            if not line:
                lines += 1
                continue
            pixel_width = font.measure(line)
            wrapped_lines = max(1, pixel_width // max_width + 1)
            lines += wrapped_lines
        return lines

    def _finalize_show(self):
        self._apply_rounded_corners()
        self._window.deiconify()

    # ── Mode Switching ────────────────────────────────────────────────────────

    def _show_display_mode(self):
        """Switch to label (read-only) display."""
        self._is_editing = False
        display_text = self._note.text

        # Sync label text from the model
        if not display_text:
            self._label.configure(text="Click to edit...", fg="#999")
        else:
            self._label.configure(text=display_text, fg=self._note.text_color)

        self._textbox.pack_forget()
        self._label.pack(fill="both", expand=True)

        # Re-enable drag on content frame
        self._content_frame.bind("<ButtonPress-1>", self._on_drag_start)
        self._content_frame.bind("<B1-Motion>", self._on_drag_motion)
        self._content_frame.bind("<ButtonRelease-1>", self._on_drag_end)

    def _show_edit_mode(self):
        """Switch to Text widget (editable) mode."""
        self._is_editing = True
        self._label.pack_forget()
        self._textbox.pack(fill="both", expand=True)

        # Populate text widget with current note content
        self._textbox.delete("1.0", "end")
        self._textbox.insert("1.0", self._note.text)

        # Disable drag-from-content-frame while editing
        self._content_frame.unbind("<ButtonPress-1>")
        self._content_frame.unbind("<B1-Motion>")
        self._content_frame.unbind("<ButtonRelease-1>")

        self._textbox.focus_set()

    def _commit_edit(self):
        """Read text from the widget, update model, save, switch to display."""
        raw_text = self._textbox.get("1.0", "end-1c")  # Strip trailing newline
        self._note.update_text(raw_text)
        
        # Dynamically resize the window cleanly post-edit
        self._window.after(0, self._adjust_height)
        
        self._on_save()  # Delegate JSON saving entirely to the app centralized level
        self._show_display_mode()

    # ── Command Handlers ──────────────────────────────────────────────────────

    def _cmd_toggle_collapse(self):
        """Flip collapsed tracker, flush states, format geometry mappings, and save JSON."""
        if self._is_editing:
            self._commit_edit()
        self._note.collapsed = not self._note.collapsed
        self._apply_collapse_state()
        self._on_save()

    def _cmd_toggle_pin(self):
        """Toggle pinned status."""
        self._note.pinned = not self._note.pinned
        self._apply_pin_state()
        self._on_save()

    def _cmd_change_color(self, theme_name, colors):
        """Apply selected preset theme onto logic and visuals, then flush JSON."""
        self._note.update_colors(colors["bg"], colors["top"], colors["text"])
        self._apply_colors()
        self._on_save()

    def _cmd_new_note(self):
        """Trigger global new note callback with offset position."""
        self._on_new(self._note.x + 30, self._note.y + 30)

    def _cmd_delete_note(self):
        """Trigger global delete note callback, removing this window and data."""
        self._on_delete(self._note, self._window)

    def _toggle_snapping(self):
        self.allow_snapping = not self.allow_snapping

    # ── Interaction Events ────────────────────────────────────────────────────

    def _show_menu(self, event):
        """Show context menu at cursor position dynamically adjusting labels."""
        pin_label = "Unpin Note" if self._note.pinned else "Pin Note"
        self._menu.entryconfigure(0, label=pin_label)
        
        snap_label = "Disable Snapping" if self.allow_snapping else "Enable Snapping"
        self._menu.entryconfigure(self._snap_menu_index, label=snap_label)
        
        self._menu.tk_popup(event.x_root, event.y_root)

    def _on_label_click(self, event):
        """Single click on the note body → enter edit mode."""
        self._show_edit_mode()

    def _on_enter_key(self, event):
        """Enter key pressed while editing. Save and return to display mode."""
        self._commit_edit()
        return "break"

    def _on_shift_enter_key(self, event):
        """Shift+Enter key pressed while editing. Insert newline natively."""
        self._textbox.insert(tk.INSERT, "\n")
        return "break"

    def _on_focus_out(self, event):
        """Window lost focus → exit edit mode if active."""
        if self._is_editing:
            self._commit_edit()

    # ── Drag Handling ─────────────────────────────────────────────────────────

    def _on_drag_start(self, event):
        """Record where on the window the click occurred."""
        if self._is_editing:
            return
        self._drag_start_x = event.x_root - self._window.winfo_x()
        self._drag_start_y = event.y_root - self._window.winfo_y()
        self._snap_lock_x = None
        self._snap_lock_y = None

    def _on_drag_motion(self, event):
        """Move the window to follow the mouse cursor with magnetic snapping."""
        if self._is_editing:
            return

        new_x = event.x_root - self._drag_start_x
        new_y = event.y_root - self._drag_start_y
        
        if self.allow_snapping:
            new_x, new_y = self._calculate_snapping(new_x, new_y)

        self._window.geometry(f"+{new_x}+{new_y}")

        # Debounce: cancel any pending save, schedule a new one
        if self._drag_save_job is not None:
            self._window.after_cancel(self._drag_save_job)
        self._drag_save_job = self._window.after(
            DRAG_DEBOUNCE_MS, lambda: self._update_position(new_x, new_y)
        )

    def _calculate_snapping(self, new_x, new_y):
        my_w = self._window.winfo_width()
        my_h = self._window.winfo_height()

        # 1. Maintain lock if within unlock distance (anti-jitter)
        if self._snap_lock_x is not None:
            if abs(new_x - self._snap_lock_x) < UNLOCK_DIST:
                new_x = self._snap_lock_x
            else:
                self._snap_lock_x = None
                
        if self._snap_lock_y is not None:
            if abs(new_y - self._snap_lock_y) < UNLOCK_DIST:
                new_y = self._snap_lock_y
            else:
                self._snap_lock_y = None
                
        if self._snap_lock_x is not None and self._snap_lock_y is not None:
            return new_x, new_y

        # 2. Find new snaps if not locked against other active windows
        for child in self._window.master.winfo_children():
            if isinstance(child, tk.Toplevel) and child is not self._window and child.winfo_exists():
                other_x = child.winfo_x()
                other_y = child.winfo_y()
                other_w = child.winfo_width()
                other_h = child.winfo_height()

                my_left, my_right = new_x, new_x + my_w
                my_top, my_bottom = new_y, new_y + my_h
                other_left, other_right = other_x, other_x + other_w
                other_top, other_bottom = other_y, other_y + other_h

                vertical_close = (
                    abs(my_top - other_top) < SNAP_DIST or
                    abs(my_bottom - other_bottom) < SNAP_DIST or
                    (my_top < other_bottom and my_bottom > other_top)
                )
                
                horizontal_close = (
                    abs(my_left - other_left) < SNAP_DIST or
                    abs(my_right - other_right) < SNAP_DIST or
                    (my_left < other_right and my_right > other_left)
                )
                
                # Horizontal snapping (disabled if current note is collapsed)
                if not self._note.collapsed and self._snap_lock_x is None and vertical_close:
                    if abs(my_left - other_right) < SNAP_DIST:
                        self._snap_lock_x = other_right + X_SNAP_PADDING + 1
                        new_x = self._snap_lock_x
                    elif abs(my_right - other_left) < SNAP_DIST:
                        self._snap_lock_x = other_left - my_w - X_SNAP_PADDING
                        new_x = self._snap_lock_x
                        
                # Vertical Snapping
                if self._snap_lock_y is None and horizontal_close:
                    if abs(my_top - other_bottom) < SNAP_DIST:
                        self._snap_lock_y = other_bottom + Y_SNAP_PADDING
                        new_y = self._snap_lock_y
                    elif abs(my_bottom - other_top) < SNAP_DIST:
                        self._snap_lock_y = other_top - my_h - Y_SNAP_PADDING
                        new_y = self._snap_lock_y

        return new_x, new_y

    def _on_drag_end(self, event):
        """Flush position save when mouse is released."""
        if self._is_editing:
            return

        # Cancel debounced save and save immediately
        if self._drag_save_job is not None:
            self._window.after_cancel(self._drag_save_job)
            self._drag_save_job = None

        self._update_position(self._window.winfo_x(), self._window.winfo_y())

    def _update_position(self, x: int, y: int):
        """Update model with new position and persist via app callback."""
        self._note.update_position(x, y)
        self._on_save()
