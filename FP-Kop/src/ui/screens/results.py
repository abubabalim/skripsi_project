import core.database as db

from pandas import DataFrame
from datetime import datetime
from ui.utils import COLORS, ROUTES
from core.analysis_results import AnalysisResults
from ui.widgets import LoadingDialog, CustomButton, CustomSnackbar
from flet import (
    Column,
    Page,
    ScrollMode,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    Text,
    Colors,
    ControlState,
    TextStyle,
    FontWeight,
    Container,
    TextButton,
    Row,
    TextThemeStyle,
    MainAxisAlignment,
    Placeholder,
    Divider,
    ProgressRing,
    GestureDetector,
    MouseCursor,
    TextSpan,
)


class Results(Column):
    def __init__(self, page: Page, results: AnalysisResults):
        super().__init__()
        self.page = page
        self.saved = False
        self.analysis_results = results
        self.frequent_itemset = DataFrame()
        self.association_rules = DataFrame()
        self.save_button = CustomButton(
            text="Simpan",
            color=COLORS.PRIMARY,
            on_tap=lambda _: self.on_save(),
            dynamic=False,
        )
        self.scroll = ScrollMode.HIDDEN
        self.bold_style = TextStyle(weight=FontWeight.BOLD)
        self.min_sup = Text(f"Minimum Support : {self.analysis_results.support}")
        self.min_conf = Text(f"Minimum Confidence : {self.analysis_results.confidence}")
        self.statistic_section = Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Column(
                    [
                        Row(
                            [
                                Text("Jumlah Barang    :"),
                                TextButton(
                                    f"{len(self.analysis_results.items)}",
                                    on_click=lambda _: self.page.go(
                                        ROUTES.PROCESS_ITEM
                                    ),
                                ),
                            ],
                            spacing=0,
                        ),
                        Row(
                            [
                                Text("Jumlah Transaksi :"),
                                TextButton(
                                    f"{len(self.analysis_results.transactions)}",
                                    on_click=lambda _: self.page.go(
                                        f"{ROUTES.PROCESS_TRANSACTION}?offset=1"
                                    ),
                                ),
                            ],
                            spacing=0,
                        ),
                    ]
                ),
                Column(
                    [
                        self.min_sup,
                        self.min_conf,
                    ]
                ),
            ],
        )
        self.frequent_itemset_section = Column(
            controls=[
                TitleAndToggle(
                    title="Frequent Itemset",
                    on_tap=self.frequent_itemset_toggle,
                ),
                Text("Tidak Menemukan Frequent Itemset"),
            ]
        )
        self.association_rules_section = Column(
            controls=[
                TitleAndToggle(
                    title="Association Rules",
                    on_tap=self.association_rules_toggle,
                ),
                Text("Tidak Menemukan Association Rules"),
            ]
        )
        self.recomended_strategy_section = Column(
            controls=[
                TitleAndToggle(
                    title="Rekomendasi Strategi",
                    on_tap=self.recomended_strategy_toggle,
                ),
                Placeholder(height=200, width=400, color=Colors.random()),
            ]
        )
        self.processing = Row(
            [
                Container(
                    expand=True,
                    bgcolor=COLORS.TERTIARY,
                    content=ProgressRing(height=40, width=40, color=COLORS.PRIMARY),
                )
            ]
        )
        self.loading = LoadingDialog(self.page)
        self.controls = [
            Container(height=40),
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        [
                            Text(
                                "Hasil Analisis",
                                theme_style=TextThemeStyle.HEADLINE_SMALL,
                            ),
                            Text(
                                "Menampilkan hasil analisis data transaksi",
                                theme_style=TextThemeStyle.LABEL_LARGE,
                            ),
                        ]
                    ),
                    Row(
                        [
                            self.save_button,
                            CustomButton(
                                text="Analisis Baru",
                                color=COLORS.TERTIARY,
                                on_tap=lambda _: self.on_new_analysis(),
                                dynamic=False,
                            ),
                        ]
                    ),
                ],
            ),
            Container(height=30),
            self.statistic_section,
            Divider(),
            self.frequent_itemset_section,
            Divider(),
            self.association_rules_section,
            Divider(),
            self.recomended_strategy_section,
            Container(height=100),
        ]

    def did_mount(self):
        self.frequent_itemset_section_update()
        self.association_rules_section_update()
        self.recomended_strategy_section_update()
        return super().did_mount()

    def frequent_itemset_toggle(self, e):
        self.frequent_itemset_section.controls[0].toggle()
        self.frequent_itemset_section.controls[-1].visible = (
            not self.frequent_itemset_section.controls[-1].visible
        )
        self.frequent_itemset_section.update()

    def frequent_itemset_section_update(self):
        self.frequent_itemset_section.controls[-1] = (
            Text("Tidak Menemukan Frequent Itemset")
            if self.analysis_results.itemsets.empty
            else GestureDetector(
                mouse_cursor=MouseCursor.CLICK,
                on_tap=lambda _: self.page.go(ROUTES.RESULT_ITEMSET),
                content=CustomTable(
                    columns=["Frequent Itemsets", "Support"],
                    rows=[
                        itemset
                        for itemset in self.analysis_results.itemsets.head(5).to_dict(
                            "records"
                        )
                    ],
                    cells=["itemsets_nama", "support"],
                ),
            )
        )
        self.frequent_itemset_section.update()

    def association_rules_toggle(self, e):
        self.association_rules_section.controls[0].toggle()
        self.association_rules_section.controls[-1].visible = (
            not self.association_rules_section.controls[-1].visible
        )
        self.association_rules_section.update()

    def association_rules_section_update(self):
        self.association_rules_section.controls[-1] = (
            Text("Tidak Menemukan Association Rules")
            if self.analysis_results.rules.empty
            else GestureDetector(
                mouse_cursor=MouseCursor.CLICK,
                on_tap=lambda _: self.page.go(ROUTES.RESULT_RULES),
                content=CustomTable(
                    columns=[
                        "Antecedents",
                        "Consequents",
                        "Support",
                        "Confidence",
                        "Lift Ratio",
                    ],
                    rows=[
                        rules
                        for rules in self.analysis_results.rules.head(5).to_dict(
                            "records"
                        )
                    ],
                    cells=[
                        "antecedents_nama",
                        "consequents_nama",
                        "support",
                        "confidence",
                        "lift",
                    ],
                ),
            )
        )
        self.association_rules_section.update()

    def recomended_strategy_toggle(self, e):
        self.recomended_strategy_section.controls[0].toggle()
        self.recomended_strategy_section.controls[-1].visible = (
            not self.recomended_strategy_section.controls[-1].visible
        )
        self.recomended_strategy_section.update()

    def recomended_strategy_section_update(self):
        self.recomended_strategy_section.controls[-1] = (
            Text("Tidak Menemukan Association Rules")
            if self.analysis_results.rules.empty
            else GestureDetector(
                mouse_cursor=MouseCursor.CLICK,
                on_tap=lambda _: self.page.go(ROUTES.RESULT_STRATEGY),
                content=Column(
                    controls=[
                        Text(
                            spans=[
                                TextSpan("Pertimbangkan bundling produk: "),
                                TextSpan(
                                    f"{", ".join(
                                        str(item) for item in rules["antecedents_nama"]
                                    )}",
                                    style=TextStyle(weight=FontWeight.BOLD),
                                ),
                                TextSpan(" dengan "),
                                TextSpan(
                                    f"{", ".join(
                                        str(item) for item in rules["consequents_nama"]
                                    )}.",
                                    style=TextStyle(weight=FontWeight.BOLD),
                                ),
                                TextSpan("\nTempatkan prouk "),
                                TextSpan(
                                    f"{", ".join(
                                        str(item) for item in rules["antecedents_nama"]
                                    )}",
                                    style=TextStyle(weight=FontWeight.BOLD),
                                ),
                                TextSpan(" berdekatan dengan "),
                                TextSpan(
                                    f"{", ".join(
                                        str(item) for item in rules["consequents_nama"]
                                    )}",
                                    style=TextStyle(weight=FontWeight.BOLD),
                                ),
                            ],
                        )
                        for rules in self.analysis_results.rules.head(5).to_dict(
                            "records"
                        )
                    ]
                ),
            )
        )
        self.recomended_strategy_section.update()

    def on_save(self):
        loading = LoadingDialog(self.page)
        loading.display_dialog()
        text = ""
        color = None
        self.saved = False

        try:
            # save new record hasil analisis
            saved_analisis = db.insert_analisis([(datetime.now(),)])
            # print(f"ID ANALISIS : {saved_analisis}")
            if not saved_analisis:
                raise Exception("Gagal menyimpan hasil analisis")

            # save association rules
            rules = [
                (saved_analisis, rule["support"], rule["confidence"], rule["lift"])
                for rule in self.analysis_results.rules.to_dict("records")
            ]
            saved_rules = db.insert_aturan_asosiasi(rules)
            if not saved_rules:
                raise Exception("Gagal menyimpan association rules")

            rules_ids = [item for tup in saved_rules for item in tup]
            # print("RULES IDS : ", rules_ids)

            # save itemset (antecedents & consequents)
            antecedents = [
                (", ".join(str(item) for item in rule["antecedents"]), "antecedents")
                for rule in self.analysis_results.rules.to_dict("records")
            ]
            saved_ante = db.insert_itemset(antecedents)
            if not saved_ante:
                raise Exception("Gagal menyimpan antecedent")
            ante_ids = [item for tup in saved_ante for item in tup]
            # print("ANTECEDENTS : ", ante_ids)

            consequents = [
                (", ".join(str(item) for item in rule["consequents"]), "consequents")
                for rule in self.analysis_results.rules.to_dict("records")
            ]
            saved_cons = db.insert_itemset(consequents)
            if not saved_cons:
                raise Exception("Gagal menyimpan consequents")
            cons_ids = [item for tup in saved_cons for item in tup]
            # print("CONSEQUENTS : ", cons_ids)

            # save ruleitems
            rule_items = [
                [(rule, ante), (rule, conse)]
                for rule, ante, conse in zip(rules_ids, ante_ids, cons_ids)
            ]
            flattened_list = [
                tuple_item for sublist in rule_items for tuple_item in sublist
            ]
            # print("RULE ITEMS : ", flattened_list)

            if not db.insert_rule_items(flattened_list):
                raise Exception("Gagal menyimpan hubungan rules dan itemset")

        except Exception as ex:
            # print(ex)
            text = ex
            color = Colors.RED_600
            self.saved = False
        else:
            text = "Hasil analisis berhasil tersimpan"
            color = Colors.GREEN_600
            self.saved = True
        finally:
            loading.dismiss_dialog()
            snackbar = CustomSnackbar(self.page, text=text, color=color)
            snackbar.display()
            self.save_button.toggle_disable(self.saved)

        # pass

    def on_new_analysis(self):
        self.page.go(ROUTES.PROCESS)
        pass


class TitleAndToggle(Row):
    def __init__(self, title, on_tap):
        super().__init__()
        self.selected = True
        self.style = TextStyle(weight=FontWeight.W_600, size=15)
        self.text = Text("", color=COLORS.SECONDARY)
        self.spacing = 2
        self.controls = [
            Text(title, style=self.style),
            Container(width=4),
            Text("[", style=self.style),
            GestureDetector(content=self.text, on_tap=on_tap),
            Text("]", style=self.style),
        ]

    def did_mount(self):
        self.text.value = "Hide" if self.selected else "Show"
        self.text.update()
        return super().did_mount()

    def toggle(self):
        self.selected = not self.selected
        self.text.value = "Hide" if self.selected else "Show"
        self.text.update()


class CustomTable(Row):
    def __init__(self, columns, rows, cells):
        super().__init__()
        self.alignment = (MainAxisAlignment.CENTER,)
        self.controls = [
            DataTable(
                expand=True,
                columns=[DataColumn(label=Text(col)) for col in columns],
                rows=[
                    DataRow(
                        cells=[
                            DataCell(
                                content=Text(
                                    ", ".join(str(item) for item in row[cell])
                                    if not isinstance(row[cell], float)
                                    else round(row[cell], 3)
                                )
                            )
                            for cell in cells
                        ]
                    )
                    for row in rows
                ],
                show_checkbox_column=False,
                data_row_color={ControlState.HOVERED: Colors.BLUE_GREY_50},
                heading_text_style=TextStyle(weight=FontWeight.BOLD),
                data_text_style=TextStyle(size=12, weight=FontWeight.W_500),
                heading_row_color={ControlState.DEFAULT: Colors.BLUE_GREY_100},
            ),
        ]
