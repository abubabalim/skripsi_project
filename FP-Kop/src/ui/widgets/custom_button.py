from flet import *
from ui.utils import COLORS


class CustomButton(GestureDetector):
    def __init__(
        self,
        text,
        color,
        dynamic=True,
        disabled=False,
        outlined=False,
        visible=True,
        on_tap = None,
    ):
        super().__init__()
        self.on_tap = on_tap
        self.disabled = disabled
        self.outlined = outlined
        self.visible = visible
        self.color = color
        self.dynamic = dynamic
        self.mouse_cursor = MouseCursor.CLICK if not self.disabled else MouseCursor.BASIC
        self.text = Text(
            text,
            text_align=TextAlign.CENTER,
            expand=True,
            style=TextStyle(size=14, color=Colors.WHITE if not outlined else Colors.BLACK),
        )
        self.content = Container(
            bgcolor=self.color if not self.disabled else Colors.GREY_400,
            expand=True,
            padding=padding.symmetric(vertical=10, horizontal=20),
            border=(
                None
                if not outlined
                else border.all(
                    width=1,
                    color=COLORS.PRIMARY_DARK,
                )
            ),
            border_radius=border_radius.all(6),
            content=(Row(controls=[self.text]) if dynamic else self.text),
        )
        
    def toggle_disable(self, value):
        self.disabled = value
        self.mouse_cursor = MouseCursor.CLICK if not value else MouseCursor.BASIC
        self.content.bgcolor = self.color if not value else Colors.GREY_400
        self.update()
