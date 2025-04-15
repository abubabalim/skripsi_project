from ui.utils import ROUTES, COLORS
from ui.widgets import CustomButton
from flet import Column, Page, ScrollMode, Text, Container, TextThemeStyle


class Show(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.scroll = ScrollMode.AUTO
        self.wrap = False
        self.page = page
        self.controls = [
            Container(height=50),
            Text("Lihat Data", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Menampilkan data yang tersimpan di database",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            CustomButton(
                text="Data Barang",
                color=COLORS.DARK,
                on_tap=lambda _: page.go(ROUTES.SHOW_ITEM),
            ),
            CustomButton(
                text="Data Transaksi",
                color=COLORS.PRIMARY,
                on_tap=lambda _: page.go(ROUTES.SHOW_TRANSACTION),
            ),
            CustomButton(
                text="Hasil Analisis",
                color=COLORS.SECONDARY,
                on_tap=lambda _: page.go(ROUTES.SHOW_RESULT),
            ),
        ]
