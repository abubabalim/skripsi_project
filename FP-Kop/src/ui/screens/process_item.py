from threading import Timer
from ui.utils import ROUTES
from ui.widgets import LoadingDialog
from core.analysis_results import AnalysisResults
from flet import (
    Column,
    Page,
    ScrollMode,
    TextField,
    Icons,
    DataTable,
    DataColumn,
    Text,
    ControlState,
    Colors,
    TextStyle,
    FontWeight,
    Container,
    TextButton,
    TextThemeStyle,
    Row,
    DataRow,
    DataCell,
)


class ProcessItem(Column):
    def __init__(self, page: Page, results: AnalysisResults):
        super().__init__()
        self.page = page
        self.results = results
        self.scroll = ScrollMode.HIDDEN
        self.sort_by = ""
        self.ascending = True
        self.debounce_timer = None
        self.search_field = TextField(
            dense=True,
            border_radius=6,
            hint_text="Cari nama barang",
            suffix_icon=Icons.SEARCH,
            on_change=self.on_change,
        )
        self.items_table = DataTable(
            expand=True,
            columns=[
                DataColumn(
                    label=Text("Kode Barang"),
                    on_sort=lambda _: self.build_items_table_row(
                        "kode_barang", self.sort_by == "kode_barang"
                    ),
                ),
                DataColumn(
                    label=Text("Nama Barang"),
                    on_sort=lambda _: self.build_items_table_row(
                        "nama_barang", self.sort_by == "nama_barang"
                    ),
                ),
                DataColumn(
                    label=Text("Frekuensi"),
                    on_sort=lambda _: self.build_items_table_row(
                        "jumlah", self.sort_by == "jumlah"
                    ),
                ),
            ],
            rows=[],
            data_row_color={ControlState.HOVERED: Colors.BLUE_GREY_50},
            heading_text_style=TextStyle(weight=FontWeight.BOLD),
            data_text_style=TextStyle(size=12, weight=FontWeight.W_500),
            heading_row_color={ControlState.DEFAULT: Colors.BLUE_GREY_100},
        )
        self.controls = [
            Container(
                height=50,
                content=TextButton(
                    text="Kembali",
                    icon=Icons.KEYBOARD_ARROW_LEFT,
                    on_click=lambda _: self.page.go(ROUTES.RESULT),
                ),
            ),
            Text(
                "Data Barang yang dianalisis", theme_style=TextThemeStyle.HEADLINE_SMALL
            ),
            Text(
                f"Terdapat {len(self.results.items)} data barang yang dianalisis",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            # Row(alignment=MainAxisAlignment.END, controls=[]),
            Row([self.items_table]),
            Container(height=100),
        ]

    def did_mount(self):
        self.build_items_table_row("kode_barang", True)
        return super().did_mount()

    def build_items_table_row(self, sort_by, asc):
        loading = LoadingDialog(page=self.page)
        loading.display_dialog()

        items = self.results.items
        self.items_table.rows.clear()
        self.items_table.rows.extend(
            [
                DataRow(
                    cells=[
                        DataCell(Text(item["kode_barang"])),
                        DataCell(Text(item["nama_barang"])),
                        DataCell(Text(item["jumlah"])),
                    ],
                )
                for item in items.sort_values(
                    by=sort_by, ascending=sort_by != self.sort_by
                ).to_dict("records")
            ]
        )
        self.sort_by = sort_by
        self.items_table.update()
        loading.dismiss_dialog()

    # search items by keyword
    def on_change_debounced(self, value):
        self.table_offset = 0
        self.keyword = value
        items = [item for item in self.results.items.to_dict("records")]
        self.build_items_table_row(items, "kode_barang", True)

    # on change search field
    def on_change(self, e):
        # Cancel previous timer if it exists
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Start a new timer with a delay of 500ms
        self.debounce_timer = Timer(
            1.5,
            self.on_change_debounced,
            args=[e.control.value],
        )
        self.debounce_timer.start()
        self.update()
