import core.database as db

from datetime import datetime
from ui.utils import COLORS, ROUTES
from ui.widgets.date_field import DateField
from pandas import DataFrame, set_option, concat
from core.analysis_results import AnalysisResults
from mlxtend.frequent_patterns import fpgrowth, association_rules
from ui.widgets import DateField, CustomButton, LoadingDialog, CustomSnackbar
from flet import (
    Column,
    Page,
    ScrollMode,
    TextStyle,
    FontWeight,
    TextField,
    Text,
    Container,
    Row,
    TextThemeStyle,
    DatePicker,
    Colors,
)


class Process(Column):
    def __init__(self, page: Page, results: AnalysisResults):
        super().__init__()
        self.page = page
        self.results = results
        self.scroll = ScrollMode.AUTO
        self.bold_style = TextStyle(weight=FontWeight.BOLD)
        self.start_date_field = DateField(
            label="Tanggal Awal",
            on_click=lambda _: self.date_picker_controller(is_start=True),
            on_reset=lambda _: self.date_field_reset(is_start=True),
        )
        self.end_date_field = DateField(
            label="Tanggal Akhir",
            on_click=lambda _: self.date_picker_controller(is_start=False),
            on_reset=lambda _: self.date_field_reset(is_start=False),
        )
        self.minimum_support_field = TextField(
            expand=True,
            label="Nilai Support Minimum",
            hint_text="Contoh: 0.01",
            value=0.001,
        )
        self.minimum_confidence_field = TextField(
            expand=True,
            label="Nilai Confidence Minimum",
            hint_text="Contoh: 1.0",
            value=0.1,
        )
        self.adavance_setting_section = Column(
            visible=True,
            spacing=16,
            controls=[
                Text(
                    "Silahkan tentukan nilai minimum support dan confidence",
                    style=self.bold_style,
                ),
                Row(
                    controls=[
                        self.minimum_support_field,
                        self.minimum_confidence_field,
                    ]
                ),
            ],
        )
        self.analyze_button = CustomButton(
            text="Mulai Analisis", color=COLORS.PRIMARY, on_tap=self.analyzing
        )
        self.controls = [
            Container(height=50),
            Text("Proses Data", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Mengolah data menjadi pola pembelian",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Text("Silahkan pilih rentang data Transaksi", style=self.bold_style),
            Row(controls=[self.start_date_field, self.end_date_field]),
            Container(height=20),
            self.adavance_setting_section,
            Container(height=20),
            self.analyze_button,
            Container(height=100),
        ]

    # on click date field
    def date_picker_controller(self, is_start: bool):
        def handle_change(e):
            date = e.control.value.strftime("%Y-%m-%d")
            if is_start:
                self.start_date_field.value = date
                self.start_date_field.update()
            else:
                self.end_date_field.value = date
                self.end_date_field.update()

        start = self.start_date_field.value if not self.start_date_field.value else None

        end = self.end_date_field.value if not self.end_date_field.value else None

        date_value = (
            datetime.strptime(
                start if is_start else end,
                "%Y-%m-%d",
            )
            if start or end
            else None
        )

        self.page.open(
            DatePicker(
                value=date_value,
                first_date=datetime(year=2000, month=1, day=1),
                last_date=datetime(year=2500, month=12, day=31),
                on_change=handle_change,
            ),
        )

    # on reset date field
    def date_field_reset(self, is_start):
        if is_start:
            self.start_date_field.value = ""
            self.update()
        else:
            self.end_date_field.value = ""
            self.update()

    # start analyzing transactions data with minimum support and confidence
    def analyzing(self, e):
        # global basket

        self.start_date_field.error_text = ""
        self.end_date_field.error_text = ""
        self.start_date_field.update()
        self.end_date_field.update()

        is_valid = True
        if not self.start_date_field.value:
            self.start_date_field.error_text = "Tanggal awal tidak boleh kosong"
            self.start_date_field.update()
            is_valid = False

        if not self.end_date_field.value:
            self.end_date_field.error_text = "Tanggal akhir tidak boleh kosong"
            self.end_date_field.update()
            is_valid = False

        is_valid = True

        if not is_valid:
            # print("Cannot empty")
            return None

        self.page.overlay.clear()
        loading = LoadingDialog(self.page)
        loading.display_dialog(text="Mengambil data transaksi")
        text = "Snackbar"
        color = None

        try:
            results = db.get_detail_transaksi(
                from_start_date=self.start_date_field.value,
                to_end_date=self.end_date_field.value,
                limit=100000,
            )
            # results = db.get_detail_transaksi(
            #     from_start_date="2024-01-01",
            #     to_end_date="2024-02-01",
            #     limit=100000,
            # )

            if loading.open == False:
                raise KeyboardInterrupt()

            if not results:
                raise Exception("data transaksi kosong")

            set_option("display.width", 0)
            set_option("display.max_columns", None)

            results_df = DataFrame(results["data"])

            items_df = DataFrame(results_df[["kode_barang", "nama_barang"]].copy())
            transactions_df = DataFrame(
                results_df[["kode_transaksi", "tanggal_transaksi"]].copy()
            )
            # transactions_df = transactions_df.drop(columns="id", axis=1)

            detil_df = DataFrame()
            detil_df = concat([detil_df, transactions_df, items_df], axis=1)
            detil_df = (
                detil_df.groupby(["kode_transaksi", "tanggal_transaksi"])
                .agg(
                    {
                        "kode_barang": lambda x: ", ".join(x),
                        "nama_barang": lambda x: ", ".join(x),
                    }
                )
                .reset_index()
            )
            # print(detil_df)

            # Konversi ke format dataframe untuk analisis
            basket = DataFrame()
            basket["kode_transaksi"] = transactions_df["kode_transaksi"]
            basket["kode_barang"] = items_df["kode_barang"]
            basket = (
                basket.groupby(["kode_transaksi", "kode_barang"])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )
            basket.set_index("kode_transaksi", inplace=True)
            basket = basket.map(lambda x: True if x > 0 else False)
            # print(len(basket))

            # Menerapkan FP-Growth
            support = float(self.minimum_support_field.value)
            frequent_itemsets = fpgrowth(basket, min_support=support, use_colnames=True)

            if frequent_itemsets.empty:
                raise Exception("Tidak menghasilkan frequent itemset")

            # print("Frequent Itemsets:")
            # print(frequent_itemsets)

            # Aturan asosiasi
            confidence = float(self.minimum_confidence_field.value)
            rules = association_rules(
                frequent_itemsets, metric="confidence", min_threshold=confidence
            )

            if rules.empty:
                raise Exception("Tidak menghasilkan association rules")

            no_dup_item = items_df.drop_duplicates(subset=["kode_barang"])

            # Fungsi untuk mengganti kode barang dengan nama barang
            def map_items(items, mapping_df):
                mapping_dict = mapping_df.set_index("kode_barang")[
                    "nama_barang"
                ].to_dict()
                return {mapping_dict[item] for item in items}

            frequent_itemsets["itemsets_nama"] = frequent_itemsets["itemsets"].apply(
                lambda x: map_items(x, no_dup_item)
            )
            rules["antecedents_nama"] = rules["antecedents"].apply(
                lambda x: map_items(x, no_dup_item)
            )
            rules["consequents_nama"] = rules["consequents"].apply(
                lambda x: map_items(x, no_dup_item)
            )

            # print("\nAssociation Rules:")
            # print(rules)

            # menambah kolom jumlah dgn nilai 1 ke df barang, dan menjumlahkannya sesuai kelompok kode dan nama
            items_df["jumlah"] = 1
            items_df = (
                items_df.groupby(by=["kode_barang", "nama_barang"])["jumlah"]
                .count()
                .reset_index()
            )

            # self.results.basket = basket.copy()
            self.results.itemsets = frequent_itemsets.copy()
            self.results.rules = rules.copy()
            self.results.items = items_df.copy()
            self.results.transactions = detil_df.copy()
            self.results.support = support
            self.results.confidence = confidence
        except KeyboardInterrupt:
            text = "Proses analisis dibatalkan"
            color = Colors.RED
            # print("Canceled by User")
        except Exception as ex:
            text = f"Proses analisis gagal, eror : {ex}"
            color = Colors.RED
            # print(ex)
        else:
            text = "Proses analisis berhasil"
            color = Colors.GREEN
            self.page.go(ROUTES.RESULT)
        finally:
            loading.dismiss_dialog()
            snackbar = CustomSnackbar(self.page, text=text, color=color)
            snackbar.display()
