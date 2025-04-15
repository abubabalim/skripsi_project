from flet import *

class DateField(TextField):
    def __init__(self, label, on_click, on_reset):
        super().__init__()
        self.expand = True
        self.read_only = True
        self.border_radius = 6
        self.content_padding = padding.all(8)
        self.label = label
        self.hint_text = "contoh: 2024-01-31"
        self.prefix_icon = Icons.DATE_RANGE
        self.on_click = on_click
        self.suffix = Container(
            padding=padding.only(top=2),
            content=GestureDetector(
                content=Icon(Icons.CLOSE),
                on_tap=on_reset,
                mouse_cursor=MouseCursor.CLICK,
            ),
        )