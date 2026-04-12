"""
note.py
-------
Data model for a single sticky note.
No UI logic, no file I/O — pure data representation.
"""


class Note:
    """Represents a single sticky note's data."""

    DEFAULT_TEXT = "Click to edit..."
    DEFAULT_X = 100
    DEFAULT_Y = 100

    def __init__(self, note_id: int, text: str = None, x: int = None, y: int = None, 
                 pinned: bool = False, bg_color: str = "#FFF8B0", 
                 top_bar_color: str = "#F2DC7D", text_color: str = "#2B2B2B",
                 collapsed: bool = False):
        self.id = note_id
        self.text = text if text is not None else self.DEFAULT_TEXT
        self.x = x if x is not None else self.DEFAULT_X
        self.y = y if y is not None else self.DEFAULT_Y
        self.pinned = pinned
        self.bg_color = bg_color
        self.top_bar_color = top_bar_color
        self.text_color = text_color
        self.collapsed = collapsed

    def update_position(self, x: int, y: int):
        """Update the note's on-screen position."""
        self.x = x
        self.y = y

    def update_text(self, text: str):
        """Update the note's text content."""
        self.text = text
        
    def update_colors(self, bg: str, top_bar: str, text: str):
        """Apply theme color choices."""
        self.bg_color = bg
        self.top_bar_color = top_bar
        self.text_color = text

    def to_dict(self) -> dict:
        """Serialize note data to a plain dictionary matching JSON format."""
        return {
            "id": self.id,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "pinned": self.pinned,
            "bg_color": self.bg_color,
            "top_bar_color": self.top_bar_color,
            "text_color": self.text_color,
            "collapsed": self.collapsed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Deserialize a Note from a dictionary."""
        return cls(
            note_id=data.get("id", 1), # Fallback to 1 if migrating older config without IDs
            text=data.get("text"),
            x=data.get("x"),
            y=data.get("y"),
            pinned=data.get("pinned", False),
            bg_color=data.get("bg_color", "#FFF8B0"),
            top_bar_color=data.get("top_bar_color", "#F2DC7D"),
            text_color=data.get("text_color", "#2B2B2B"),
            collapsed=data.get("collapsed", False),
        )
