from ui.utils import COLORS, ROUTES
from core.analysis_results import AnalysisResults
from ui.widgets import LoadingDialog, CustomButton
from flet import (
    Column,
    Page,
    ScrollMode,
    DataTable,
    DataColumn,
    Text,
    ControlState,
    Colors,
    TextStyle,
    FontWeight,
    Container,
    TextButton,
    Icons,
    TextThemeStyle,
    Row,
    MainAxisAlignment,
    DataRow,
    DataCell,
)


class ProcessTransaction(Column):
    def __init__(self, page: Page, results: AnalysisResults, data_offset):
        super().__init__()
        self.page = page
        self.results = results
        self.data_offset = data_offset
        self.limit = 500
        self.scroll = ScrollMode.HIDDEN
        self.sort_by = ""
        self.ascending = True
        self.transactions_table = DataTable(
            expand=True,
            columns=[
                DataColumn(
                    label=Text("Tanggal Transaksi"),
                    on_sort=lambda _: self.build_transactions_table_row(
                        "tanggal_transaksi", self.sort_by == "tangal_transaksi"
                    ),
                ),
                DataColumn(
                    label=Text("Kode Transaksi"),
                    on_sort=lambda _: self.build_transactions_table_row(
                        "kode_transaksi", self.sort_by == "kode_transaksi"
                    ),
                ),
                DataColumn(label=Text("Nama Barang")),
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
                "Data Transaksi yang dianalisis",
                theme_style=TextThemeStyle.HEADLINE_SMALL,
            ),
            Text(
                f"Terdapat {len(self.results.transactions)} data transaksi yang dianalisis",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row([self.transactions_table]),
            Row(
                alignment=MainAxisAlignment.END,
                controls=[
                    CustomButton(
                        text="Sebelumnya",
                        color=COLORS.PRIMARY,
                        visible=self.data_offset > 1,
                        on_tap=lambda _: self.page.go(
                            f"{ROUTES.PROCESS_TRANSACTION}?offset={self.data_offset-1}"
                        ),
                    ),
                    CustomButton(
                        text="Berikutnya",
                        color=COLORS.PRIMARY,
                        visible=(self.data_offset * self.limit)
                        <= len(self.results.transactions),
                        on_tap=lambda _: self.page.go(
                            f"{ROUTES.PROCESS_TRANSACTION}?offset={self.data_offset+1}"
                        ),
                    ),
                ],
            ),
            Container(height=100),
        ]

    def did_mount(self):
        self.build_transactions_table_row()
        return super().did_mount()

    def build_transactions_table_row(self):
        loading = LoadingDialog(page=self.page)
        loading.display_dialog()

        data = self.results.transactions.iloc[
            (
                0 if self.data_offset == 1 else ((self.data_offset - 1) * self.limit)
            ) : self.data_offset
            * self.limit
        ].copy()

        self.transactions_table.rows.clear()
        self.transactions_table.rows.extend(
            [
                DataRow(
                    cells=[
                        DataCell(Text(item["tanggal_transaksi"].strftime("%d %B %Y"))),
                        DataCell(Text(item["kode_transaksi"])),
                        DataCell(Text(item["nama_barang"], max_lines=5)),
                    ],
                )
                for item in data.to_dict("records")
            ]
        )
        self.transactions_table.update()
        loading.dismiss_dialog()
