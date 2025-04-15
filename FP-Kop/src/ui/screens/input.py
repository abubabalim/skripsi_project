from flet import *
from ui.widgets import CustomButton
from ui.utils import ROUTES, COLORS


class Input(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.scroll = ScrollMode.AUTO
        self.controls = [
            Container(height=50),
            Text("Input Data", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text("Memasukkan data ke database", theme_style=TextThemeStyle.LABEL_LARGE),
            Container(height=30),
            CustomButton(
                text="Data Barang",
                color=COLORS.PRIMARY,
                on_tap=lambda _: page.go(ROUTES.INPUT_ITEM),
            ),
            CustomButton(
                text="Data Transaksi",
                color=COLORS.SECONDARY,
                on_tap=lambda _: page.go(ROUTES.INPUT_TRANSACTION),
            ),
        ]
