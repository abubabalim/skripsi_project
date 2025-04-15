import pandas as pd

from flet import *
from ui.utils import ROUTES
from ui.widgets import LoadingDialog
from core.analysis_results import AnalysisResults


class ResultRules(Column):
    def __init__(self, page: Page, results: AnalysisResults):
        super().__init__()
        self.page = page
        self.results = results
        self.scroll = ScrollMode.HIDDEN
        self.sort_by = "support"
        self.ascending = True
        self.buying_pattern = Column()
        self.rules_table = DataTable(
            expand=True,
            columns=[
                DataColumn(
                    label=Text("Antecedents"),
                    on_sort=lambda _: self.build_rules_table_row("antecedents"),
                ),
                DataColumn(
                    label=Text("Consequents"),
                    on_sort=lambda _: self.build_rules_table_row("consequents"),
                ),
                DataColumn(
                    label=Text("Support"),
                    on_sort=lambda _: self.build_rules_table_row("support"),
                ),
                DataColumn(
                    label=Text("Confidence"),
                    on_sort=lambda _: self.build_rules_table_row("confidence"),
                ),
                DataColumn(
                    label=Text("Lift"),
                    on_sort=lambda _: self.build_rules_table_row("lift"),
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
                "Association Rules yang dihasilkan",
                theme_style=TextThemeStyle.HEADLINE_SMALL,
            ),
            Text(
                f"Terdapat {len(self.results.rules)} association rules yang dihasilkan",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row([self.rules_table]),
            Column(
                [
                    Text(
                        "Pola Pembelian",
                        theme_style=TextThemeStyle.TITLE_MEDIUM,
                    ),
                    self.buying_pattern,
                ]
            ),
            Container(height=100),
        ]

    def did_mount(self):
        self.build_rules_table_row("support")
        return super().did_mount()

    def build_rules_table_row(self, sort_by):
        loading = LoadingDialog(page=self.page)
        loading.display_dialog()

        self.rules_table.rows.clear()
        self.rules_table.rows.extend(
            [
                DataRow(
                    cells=[
                        DataCell(
                            Text(
                                ", ".join(
                                    str(item) for item in rule["antecedents_nama"]
                                )
                            )
                        ),
                        DataCell(
                            Text(
                                ", ".join(
                                    str(item) for item in rule["consequents_nama"]
                                )
                            )
                        ),
                        DataCell(Text(round(rule["support"], 5))),
                        DataCell(Text(round(rule["confidence"], 5))),
                        DataCell(Text(round(rule["lift"], 5))),
                    ],
                )
                for rule in self.results.rules.sort_values(
                    by=sort_by, ascending=sort_by != self.sort_by
                ).to_dict("records")
            ]
        )
        self.sort_by = sort_by
        self.rules_table.update()
        self.build_buying_pattern()
        loading.dismiss_dialog()

    def build_buying_pattern(self):
        def pattern_text(rule: pd.DataFrame):
            return Text(
                spans=[
                    TextSpan("Konsumen yang membeli "),
                    TextSpan(
                        f"{", ".join(
                                    str(item) for item in rule["antecedents_nama"]
                                )}",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan(", memiliki kemungkinan "),
                    TextSpan(
                        f"{round(rule["confidence"] * 100, 2)}%",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan(" juga membeli "),
                    TextSpan(
                        f"{", ".join(
                                    str(item) for item in rule["consequents_nama"]
                                )}.",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                ],
            )

        self.buying_pattern.controls.clear()
        self.buying_pattern.controls = [
            pattern_text(rule) for rule in self.results.rules.to_dict("records")
        ]
        self.buying_pattern.update()
