import core.database as database

from flet import Page, ThemeMode, Theme, SafeArea, app
from ui.utils import ROUTES
from ui.app import SkripsiApp

def main(page: Page):
    # print(config["Database"]["host"])
    database.initialize_database()
    page.title = "Analisis Pola Pembelian Konsumen"
    page.theme_mode = ThemeMode.LIGHT
    page.padding = 0
    page.theme = Theme(font_family="Bahnschrift")
    page.add(SafeArea(content=SkripsiApp(page)))
    page.go(ROUTES.DASHBOARD)

app(main)