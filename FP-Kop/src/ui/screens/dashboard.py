import pandas as pd
import core.database  as db

from flet import *
from collections import defaultdict
from ui.utils import COLORS
from ui.widgets.loading_dialog import LoadingDialog


class Dashboard(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.scroll = ScrollMode.HIDDEN
        self.data_barang = pd.DataFrame()
        self.data_transaksi = pd.DataFrame()
        self.barang = SummaryContainer(
            title="Barang",
            count="",
            color=COLORS.SECONDARY,
            data=[],
        )
        self.transaksi = SummaryContainer(
            title="Transaksi",
            count="",
            color=COLORS.SECONDARY,
            data=[],
        )
        self.buying_pattern = Column()
        self.recomended_strategy = Column()
        self.controls = [
            Container(height=50),
            Text(
                "Dashboard",
                weight=FontWeight.W_600,
                theme_style=TextThemeStyle.HEADLINE_SMALL,
            ),
            Text(
                "Menampilkan infromasi singkat mengenai data yang dikelola",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row(
                expand=True,
                vertical_alignment=CrossAxisAlignment.START,
                controls=[self.barang, self.transaksi],
            ),
            Container(height=20),
            Text(
                "Pola Pembelian dari Analisis Terakhir",
                theme_style=TextThemeStyle.TITLE_MEDIUM,
            ),
            self.buying_pattern,
            Container(height=20),
            Text(
                "Rekomendasi Strategi dari Analisis Terakhir",
                theme_style=TextThemeStyle.TITLE_MEDIUM,
            ),
            self.recomended_strategy,
            Container(height=100),
        ]

    def did_mount(self):
        if db.get_db_connection():
            self.get_top_item()
            self.get_top_transaction()
            self.get_last_analysis()
        return super().did_mount()

    def get_top_item(self):
        # results = self.db.get_transactions()
        try:
            item = db.get_row_count("barang")
            if not item:
                raise Exception("Failed to get barang count")

            most_sold = db.get_top_barang()
            if not most_sold:
                raise Exception("Failed to get most sold barang")
            data = [
                {
                    "d1": f"[{item["kode_barang"]}] {item["nama_barang"]}",
                    "d2": item["total_terjual"],
                }
                for item in most_sold["data"]
            ]

            self.barang.count_update(item["total_count"])
            self.barang.children.update_row(data)
        except Exception as ex:
            print(ex)

    def get_top_transaction(self):
        try:
            tsc_count = db.get_row_count("transaksi")
            if not tsc_count:
                raise Exception("Failed to get transaksi count")
            latest_tsc = db.get_transaksi(
                order_by="tanggal_transaksi", desc=True, limit=5
            )

            if not latest_tsc:
                raise Exception("Failed to get latest transaksi")
            data = [
                {
                    "d1": tsc["kode_transaksi"],
                    "d2": tsc["tanggal_transaksi"].strftime("%d %B %Y"),
                }
                for tsc in latest_tsc["data"]
            ]

            self.transaksi.count_update(tsc_count["total_count"])
            self.transaksi.children.update_row(data)
        except Exception as ex:
            print(ex)

    def get_last_analysis(self):

        def pattern_text(rule: pd.DataFrame):
            return Text(
                spans=[
                    TextSpan("Konsumen yang membeli "),
                    TextSpan(
                        f"{rule["antecedent_name"]}",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan(", memiliki kemungkinan "),
                    TextSpan(
                        f"{round(rule["confidence"] * 100, 2)}%",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan(" juga membeli "),
                    TextSpan(
                        f"{rule["consequent_name"]}.",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                ],
            )

        def strategy_text(rule: pd.DataFrame):
            return Text(
                spans=[
                    TextSpan("Pertimbangkan bundling produk: "),
                    TextSpan(
                        f"{rule["antecedent_name"]}",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan(" dengan "),
                    TextSpan(
                        f"{rule["consequent_name"]}.",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan("\nTempatkan prouk "),
                    TextSpan(
                        f"{rule["antecedent_name"]}",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                    TextSpan(" berdekatan dengan "),
                    TextSpan(
                        f"{rule["consequent_name"]}.",
                        style=TextStyle(weight=FontWeight.BOLD),
                    ),
                ],
            )

        loading = LoadingDialog(self.page)
        loading.display_dialog()

        # GET LATEST ANALISIS ID
        id_analisis = db.get_latest_analisis()
        if not id_analisis:
            loading.dismiss_dialog()
            return

        # GET ASSOCIATION RULES BY ID ANALISIS
        rules = db.get_aturan_asosiasi(id_analisis)
        if not rules:
            loading.dismiss_dialog()
            return

        # Create a defaultdict to group the data by id_rules
        grouped_data = defaultdict(
            lambda: {
                "antecedents": None,
                "consequents": None,
                "support": None,
                "confidence": None,
                "lift_ratio": None,
            }
        )

        # Group the data
        for entry in rules["data"]:
            id_rules = entry["id_rules"]
            kategori = entry["kategori"]

            # Prepare the new entry format for antecedents and consequents
            new_entry = {
                "kode_barang": entry["kode_barang"],
                "nama_barang": entry["nama_barang"],
                "support": entry["support"],
                "confidence": entry["confidence"],
                "lift_ratio": entry["lift_ratio"],
            }

            # Check if it's antecedent or consequent, and store in respective fields
            if kategori == "antecedents":
                grouped_data[id_rules]["antecedents"] = new_entry["kode_barang"]
                grouped_data[id_rules]["antecedent_name"] = new_entry["nama_barang"]
                grouped_data[id_rules]["support"] = new_entry["support"]
                grouped_data[id_rules]["confidence"] = new_entry["confidence"]
                grouped_data[id_rules]["lift_ratio"] = new_entry["lift_ratio"]
            elif kategori == "consequents":
                grouped_data[id_rules]["consequents"] = new_entry["kode_barang"]
                grouped_data[id_rules]["consequent_name"] = new_entry["nama_barang"]

        # Convert the grouped data into a list of dictionaries
        result = []
        for id_rules, items in grouped_data.items():
            merged_entry = {
                "id_rules": id_rules,
                "antecedents": items["antecedents"],
                "antecedent_name": items["antecedent_name"],
                "consequents": items["consequents"],
                "consequent_name": items["consequent_name"],
                "support": items["support"],
                "confidence": items["confidence"],
                "lift_ratio": items["lift_ratio"],
            }
            result.append(merged_entry)

        # Print the result
        pd.set_option("display.width", 0)
        pd.set_option("display.max_columns", None)

        result_df = pd.DataFrame(result)
        # print(result_df)

        self.buying_pattern.controls.clear()
        self.buying_pattern.controls.extend(
            [pattern_text(rule) for rule in result_df.to_dict("records")]
        )

        self.recomended_strategy.controls.clear()
        self.recomended_strategy.controls.extend(
            [strategy_text(rule) for rule in result_df.to_dict("records")]
        )

        loading.dismiss_dialog()


class SummaryContainer(Container):
    def __init__(self, title, count, color, data):
        super().__init__()
        self.data = data
        self.height = 150
        self.count = Text(
            count,
            color=Colors.WHITE,
            theme_style=TextThemeStyle.HEADLINE_LARGE,
        )
        self.bgcolor = color
        self.children = TopDataContainer(
            col1=f"{title} Teratas" if title == "Barang" else f"{title} Terbaru",
            col2="Terjual" if title == "Barang" else "Tanggal",
            data=data,
        )
        self.expand = True
        self.padding = padding.only(top=10, left=20, right=10, bottom=10)
        self.border_radius = border_radius.all(10)
        self.animate = animation.Animation(
            duration=180, curve=AnimationCurve.EASE_IN_OUT
        )
        self.toggle_button = IconButton(
            icon=Icons.EXPAND_MORE,
            icon_color=Colors.WHITE,
            selected_icon=Icons.EXPAND_LESS,
            selected_icon_color=Colors.WHITE,
            on_click=lambda _: self.toggle(),
        )
        self.headline = Column(
            spacing=0,
            controls=[
                Row(
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text(
                            title,
                            color=Colors.WHITE,
                            theme_style=TextThemeStyle.TITLE_LARGE,
                        ),
                        self.toggle_button,
                    ],
                ),
                Divider(color=Colors.WHITE, thickness=1),
            ],
        )
        self.content = Column(
            controls=[
                self.headline,
                Container(
                    alignment=alignment.top_center,
                    padding=padding.only(top=10),
                    content=self.count,
                ),
                Container(
                    padding=padding.only(right=10, bottom=10),
                    content=self.children,
                ),
            ]
        )

    def did_mount(self):
        self.toggle_button.selected = False
        if self.data:
            self.update_some_controls()
        return super().did_mount()

    def update_some_controls(self):
        self.height = 320 if self.toggle_button.selected else 150
        self.children.visible = self.toggle_button.selected
        self.update()

    def count_update(self, count):
        self.count.value = count
        self.count.update()

    def toggle(self):
        self.toggle_button.selected = not self.toggle_button.selected
        self.toggle_button.update()
        self.update_some_controls()


class TopDataContainer(Column):
    def __init__(self, col1, col2, data):
        super().__init__()
        self.visible = False
        self.rows = Column(
            spacing=6,
            controls=[
                Row(
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.row_build(f"{index+1}. {dat["d1"]}"),
                        self.row_build(dat["d2"]),
                    ],
                )
                for index, dat in enumerate(data)
            ],
        )
        self.controls = [
            Row(
                spacing=20,
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.col_build(expand=8, label=col1),
                    Container(expand=1),
                    self.col_build(expand=2, label=col2),
                ],
            ),
            self.rows,
        ]

    def col_build(self, expand, label):
        return Column(
            expand=expand,
            controls=[
                Text(
                    label,
                    color=Colors.WHITE,
                    theme_style=TextThemeStyle.TITLE_SMALL,
                ),
                Divider(color=Colors.WHITE, height=1, thickness=1),
            ],
        )

    def row_build(self, text):
        return Text(
            text,
            color=Colors.WHITE,
            weight=FontWeight.W_100,
        )

    def update_row(self, data):
        self.rows.controls = [
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.row_build(dat["d1"]),
                    self.row_build(dat["d2"]),
                ],
            )
            for dat in data
        ]
        self.rows.update()
