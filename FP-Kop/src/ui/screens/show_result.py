import pandas as pd
import core.database as db

from flet import *
from collections import defaultdict
from ui.widgets import LoadingDialog


class ShowResult(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.association_rules = pd.DataFrame()
        self.result_table = CustomTable(
            columns=["Nomor", "Waktu Analisis", "Jumlah Pola", ""],
            rows=[],
        )
        self.controls = [
            Container(height=50),
            Text("Lihat Hasil Analisis", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Menampilkan hasil analisis yang tersimpan di database",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row([self.result_table]),
            Container(height=100),
        ]

    def did_mount(self):
        if db.get_db_connection():
            self.get_result()
        return super().did_mount()

    def get_result(self):
        loading = LoadingDialog(self.page)
        loading.display_dialog()

        result = db.get_analisis()
        # print(result)

        if result:
            df = pd.DataFrame(result["data"])
            pd.set_option("display.width", 0)
            pd.set_option("display.max_columns", None)

            # print(df)
            self.build_result_table_rows(df)

        loading.dismiss_dialog()

    def build_result_table_rows(self, df: pd.DataFrame):
        self.result_table.rows.clear()
        self.result_table.rows.extend(
            [
                DataRow(
                    on_select_changed=lambda _, id_analisis=row[
                        "id_analisis"
                    ]: self.display_rules_dialog(id_analisis),
                    cells=[
                        DataCell(Text(row["id_analisis"])),
                        DataCell(Text(row["waktu_pembuatan"].strftime("%d %B %Y"))),
                        DataCell(Text(row["rules_count"])),
                        DataCell(
                            TextButton(
                                text="Hapus",
                                icon=Icons.DELETE_FOREVER,
                                on_click=lambda _, id_analisis=row[
                                    "id_analisis"
                                ]: self.delete_result(id_analisis),
                            )
                        ),
                    ],
                )
                for row in df.to_dict("records")
            ]
        )

        self.result_table.update()

    def delete_result(self, id_analisis):

        def deleting(e):
            confirm_dialog.open = False
            self.page.update()

            loading = LoadingDialog(self.page)
            loading.display_dialog()
            self.page.update()

            result = db.delete_analisis(id_analisis)

            msg = f"{"Berhasil" if result else "Gagal"} menghapus hasil analisis #{id_analisis}"
            color = Colors.GREEN_600 if result else Colors.RED_600
            loading.dismiss_dialog()
            self.page.overlay.append(
                SnackBar(
                    open=True,
                    content=Text(msg),
                    bgcolor=color,
                    duration=2000,
                )
            )
            self.page.update()

            if result:
                self.get_result()

        def dismiss(e):
            confirm_dialog.open = False
            self.page.update()

        confirm_dialog = AlertDialog(
            open=True,
            title=Text(f"Anda ingin menghapus hasil analisis #{id_analisis} ?"),
            actions=[
                TextButton(
                    "Hapus", on_click=deleting, style=ButtonStyle(color=Colors.RED)
                ),
                TextButton("Tidak", on_click=dismiss),
            ],
            content=Text(
                "data akan terhapus secara permanen dari aplikasi",
                theme_style=TextThemeStyle.BODY_MEDIUM,
            ),
        )

        self.page.overlay.clear()
        self.page.overlay.append(confirm_dialog)
        self.page.update()

        pass

    def display_rules_dialog(self, id_analisis):
        rules = db.get_aturan_asosiasi(id_analisis)
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
        result_df = pd.DataFrame(result)
        # print(result_df)

        # return

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

        def on_dismiss(e):
            rules_dialog.open = False
            self.page.update()

        rules_table = CustomTable(
            columns=[
                "Antecedents",
                "Consequents",
                "Support",
                "Confidence",
                "Lift Ratio",
            ],
            rows=[
                DataRow(
                    cells=[
                        DataCell(Text(rule["antecedent_name"])),
                        DataCell(Text(rule["consequent_name"])),
                        DataCell(Text(rule["support"])),
                        DataCell(Text(rule["confidence"])),
                        DataCell(Text(rule["lift_ratio"])),
                    ],
                )
                for rule in result_df.to_dict("records")
            ],
        )

        rules_dialog = AlertDialog(
            open=True,
            title=Text(f"Association Rules dari Analisis #{id_analisis}"),
            actions=[TextButton("Tutup", on_click=on_dismiss)],
            content=Column(
                spacing=20,
                tight=True,
                scroll=ScrollMode.HIDDEN,
                controls=[
                    Row([rules_table]),
                    Column(
                        controls=[
                            Text(
                                "Pola Pembelian",
                                theme_style=TextThemeStyle.TITLE_MEDIUM,
                            ),
                            Column(
                                spacing=2,
                                controls=[
                                    pattern_text(rule)
                                    for rule in result_df.to_dict("records")
                                ]
                            ),
                        ]
                    ),
                    Column(
                        controls=[
                            Text(
                                "Rekomendasi Strategi",
                                theme_style=TextThemeStyle.TITLE_MEDIUM,
                            ),
                            Column(
                                [
                                    strategy_text(rule)
                                    for rule in result_df.to_dict("records")
                                ]
                            ),
                        ]
                    ),
                ],
            ),
        )

        self.page.overlay.clear()
        self.page.overlay.append(rules_dialog)
        self.page.update()


class CustomTable(DataTable):
    def __init__(self, columns, rows):
        super().__init__(columns=[])
        self.columns = [DataColumn(Text(col)) for col in columns]
        self.rows = rows
        self.expand = True
        self.show_bottom_border = True
        self.heading_row_color = {ControlState.DEFAULT: Colors.BLUE_GREY_100}
        self.heading_text_style = TextStyle(weight=FontWeight.BOLD)
        self.data_row_color = {ControlState.HOVERED: Colors.BLUE_GREY_50}
        self.data_text_style = TextStyle(size=12, weight=FontWeight.W_500)
