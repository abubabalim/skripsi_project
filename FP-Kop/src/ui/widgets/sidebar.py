from ui.utils import COLORS, ROUTES
from flet import (
    Container,
    Text,
    Icons,
    padding,
    Column,
    MainAxisAlignment,
    Text,
    TextStyle,
    Colors,
    GestureDetector,
    Page,
    MouseCursor,
    Row,
    border_radius,
    Icon,
    CrossAxisAlignment,
)


class Sidebar(Container):
    def __init__(self, page: Page):
        super().__init__()
        self.visible = True
        self.width = 240
        self.page = page
        self.bgcolor = COLORS.PRIMARY
        self.padding = padding.symmetric(horizontal=24)
        self.selected_index = 0
        self.sidebar_items = [
            {"icon": Icons.DASHBOARD_CUSTOMIZE, "label": "Dashboard"},
            {"icon": Icons.TABLE_VIEW, "label": "Lihat Data"},
            {"icon": Icons.FILE_OPEN, "label": "Input Data"},
            {"icon": Icons.TROUBLESHOOT, "label": "Analisis Data"},
        ]
        self.content = Column(
            alignment=MainAxisAlignment.START,
            controls=[
                Container(height=50),
                Text(
                    page.title,
                    style=TextStyle(color=Colors.WHITE, size=16),
                ),
                Container(height=40),
                self.build_sidebar_tiles(),
            ],
        )

    def build_sidebar_tiles(self):
        return Column(
            controls=[
                SidebarTile(
                    item["icon"],
                    item["label"],
                    index == self.selected_index,
                    lambda _, index=index: self.change_index(index),
                )
                for index, item in enumerate(self.sidebar_items)
            ],
            spacing=16,
        )

    def change_index(self, index):
        self.selected_index = index
        self.content.controls.pop()
        self.content.controls.append(self.build_sidebar_tiles())
        self.update()

        if index == 0:
            self.page.go(ROUTES.DASHBOARD)
        elif index == 1:
            self.page.go(ROUTES.SHOW)
        elif index == 2:
            self.page.go(ROUTES.INPUT)
        elif index == 3:
            self.page.go(ROUTES.PROCESS)
        else:
            self.page.go(ROUTES.SHOW)


class SidebarTile(GestureDetector):
    def __init__(self, icon, label, selected, on_click):
        super().__init__()
        self.on_tap = on_click
        self.icon = icon
        self.label = label
        self.selected = selected
        self.mouse_cursor = MouseCursor.CLICK
        self.content = Row(
            [
                Container(
                    padding=padding.symmetric(vertical=2, horizontal=8),
                    border_radius=border_radius.horizontal(100, 100),
                    bgcolor=(Colors.WHITE if self.selected else Colors.TRANSPARENT),
                    content=Icon(
                        self.icon,
                        color=(COLORS.PRIMARY if self.selected else Colors.WHITE30),
                        size=24,
                    ),
                ),
                Text(
                    self.label,
                    style=TextStyle(
                        color=(Colors.WHITE if self.selected else Colors.WHITE30),
                        size=14,
                    ),
                ),
            ],
            spacing=16,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )

    def toggle(self):
        self.selected = not self.selected
        self.content.controls[0].bgcolor = (
            Colors.WHITE if self.selected else Colors.TRANSPARENT
        )
        self.content.controls[1].style.color = (
            Colors.WHITE if self.selected else Colors.WHITE30
        )
        self.update()
