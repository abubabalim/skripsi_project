from ui.utils import ROUTES
from ui.widgets import LoadingDialog
from core.analysis_results import AnalysisResults
from flet import (
    Column,
    Page,
    ScrollMode,
    Text,
    Container,
    TextButton,
    Icons,
    Row,
    TextThemeStyle,
    TextSpan,
)


class ResultStrategy(Column):
    def __init__(self, page: Page, results: AnalysisResults):
        super().__init__()
        self.page = page
        self.results = results
        self.scroll = ScrollMode.HIDDEN
        self.sort_by = ""
        self.ascending = True
        self.recomended_strategy = Column(controls=[])
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
                "Rekomendasi strategi penjualan yang dihasilkan",
                theme_style=TextThemeStyle.HEADLINE_SMALL,
            ),
            Text(
                f"Terdapat {len(self.results.rules)} rekomendasi strategi penjualan yang dihasilkan",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row([self.recomended_strategy]),
            Container(height=100),
        ]

    def did_mount(self):
        self.build_recomended_strategy()
        return super().did_mount()

    def build_recomended_strategy(self):
        loading = LoadingDialog(page=self.page)
        loading.display_dialog()

        self.recomended_strategy.controls.clear()
        self.recomended_strategy.controls.extend(
            [
                Text(
                    "\n" if index % 2 == 0 and index != 0 else "",
                    spans=[
                        TextSpan(
                            f"Pertimbangkan bundling produk: {", ".join(
                                        str(item) for item in rules["antecedents_nama"]
                                    )} dengan {", ".join(
                                        str(item) for item in rules["consequents_nama"]
                                    )}."
                        ),
                        TextSpan(
                            f"\nTempatkan prouk {", ".join(
                                        str(item) for item in rules["antecedents_nama"]
                                    )} berdekatan dengan {", ".join(
                                        str(item) for item in rules["consequents_nama"]
                                    )} di toko."
                        ),
                    ],
                )
                for index, rules in enumerate(self.results.rules.to_dict("records"))
            ]
        )
        self.recomended_strategy.update()
        loading.dismiss_dialog()
