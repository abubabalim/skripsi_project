from flet import *
from ui.utils import ROUTES
from ui.widgets import LoadingDialog
from core.analysis_results import AnalysisResults


class ResultItemset(Column):
    def __init__(self, page: Page, results: AnalysisResults):
        super().__init__()
        self.page = page
        self.results = results
        self.scroll = ScrollMode.HIDDEN
        self.sort_by = "support"
        self.itemset_table = DataTable(
            expand=True,
            columns=[
                DataColumn(
                    label=Text("Itemsets"),
                    on_sort=lambda _: self.build_itemset_table_row("itemsets"),
                ),
                DataColumn(
                    label=Text("Support"),
                    on_sort=lambda _: self.build_itemset_table_row("support"),
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
            Text("Itemset yang dihasilkan", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                f"Terdapat {len(self.results.itemsets)} itemset yang dihasilkan",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row([self.itemset_table]),
            Container(height=100),
        ]

    def did_mount(self):
        self.build_itemset_table_row("support")
        return super().did_mount()

    def build_itemset_table_row(self, sort_by):
        loading = LoadingDialog(page=self.page)
        loading.display_dialog()

        self.itemset_table.rows.clear()
        self.itemset_table.rows.extend(
            [
                DataRow(
                    cells=[
                        DataCell(Text(", ".join(str(item) for item in item["itemsets_nama"]))),
                        DataCell(Text(round(item["support"], 5))),
                    ],
                )
                for item in self.results.itemsets.sort_values(
                    by=sort_by, ascending=sort_by != self.sort_by
                ).to_dict("records")
            ]
        )
        self.sort_by = sort_by
        self.itemset_table.update()
        loading.dismiss_dialog()
