import core.database as db

from datetime import datetime
from ui.utils import COLORS, ROUTES
from ui.widgets import CustomButton, LoadingDialog, CustomSnackbar
from flet import (
    Column,
    Page,
    ScrollMode,
    Text,
    Colors,
    TextStyle,
    FontWeight,
    Container,
    TextThemeStyle,
    Row,
    AlertDialog,
    TextField,
    ListView,
    KeyboardType,
    NumbersOnlyInputFilter,
    ListTile,
    DatePicker,
)


class ShowTransactionUpdate(Column):
    def __init__(self, page: Page, id_detail):
        super().__init__()
        self.page = page
        self.items = []
        self.id_detail = id_detail
        self.detil_transaction = None
        self.selected_item = None
        self.list_barang = ListView(controls=[])
        self.search_item_field = TextField(
            label="Cari kode atau nama barang",
            on_change=self.search_on_change,
        )
        self.search_item_dialog = AlertDialog(
            open=True,
            title=self.search_item_field,
            content=Container(
                width=400,
                content=self.list_barang,
            ),
            on_dismiss=self.dismiss_dialog,
        )
        self.scroll = ScrollMode.HIDDEN
        self.tstyle = TextStyle(weight=FontWeight.BOLD)
        # self.tanggal_transaksi = TextField(
        #     read_only=True,
        #     hint_text="contoh: 2024-01-01",
        #     # on_click=self.display_date_picker,
        # )
        self.kode_transaksi = TextField(
            hint_text="contoh: JF82U002.240307.12310846",
            read_only=True,
        )
        self.nama_barang = TextField(
            read_only=True,
            hint_text="contoh: OREO COK 66,5 GR",
            capitalization=True,
            on_click=self.display_barang_search,
        )
        self.jumlah = TextField(
            hint_text="contoh: 5500",
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
        )
        self.update_form = Column(
            tight=True,
            spacing=0,
            controls=[
                Text("Kode Transaksi", style=self.tstyle),
                self.kode_transaksi,
                Container(height=10),
                Text("Nama Barang", style=self.tstyle),
                self.nama_barang,
                Container(height=10),
                Text("Jumlah", style=self.tstyle),
                self.jumlah,
            ],
        )
        self.title = Text("", theme_style=TextThemeStyle.LABEL_LARGE)
        self.controls = [
            Container(height=50),
            Text("Ubah Data Transaksi", theme_style=TextThemeStyle.HEADLINE_SMALL),
            self.title,
            Container(height=30),
            self.update_form,
            Row(
                controls=[
                    CustomButton(
                        text="Simpan",
                        color=COLORS.PRIMARY,
                        on_tap=self.confirm_update,
                    ),
                    CustomButton(
                        text="Batal",
                        color=COLORS.SECONDARY,
                        on_tap=lambda _: page.go(ROUTES.SHOW_TRANSACTION),
                    ),
                ]
            ),
        ]

    def did_mount(self):
        if db.get_db_connection():
            self.fetch_data()
        return super().did_mount()

    def fetch_data(self):
        self.page.overlay.clear()
        loading = LoadingDialog(self.page)
        loading.display_dialog()

        results = db.get_barang(limit=10000)
        # print(results)
        self.items = results["data"] if results else []
        self.list_barang.controls = [
            ListTile(
                leading=Text(item["kode_barang"], style=TextStyle(size=14)),
                title=Text(item["nama_barang"], style=TextStyle(size=14)),
                on_click=lambda _, item=item: self.select_item(item),
            )
            for item in self.items
        ]

        detil = db.get_detail_transaksi(where_id=self.id_detail, limit=10000)
        # print(detil)
        if detil:
            tsc = detil["data"][0]
            self.title.value = f'Mengubah data transaksi "{tsc["kode_transaksi"]}" yang tersimpan di database'
            self.title.update()

            # self.tanggal_transaksi.value = tsc["tanggal_transaksi"].strftime("%d %B %Y")
            self.kode_transaksi.value = tsc["kode_transaksi"]
            self.nama_barang.value = tsc["nama_barang"]
            self.jumlah.value = tsc["jumlah"]

            self.selected_item = list(
                filter(lambda x: x["nama_barang"] == tsc["nama_barang"], self.items)
            )[0]
            # print(self.selected_item)

        loading.dismiss_dialog()

    def display_date_picker(self, e):
        def handle_change(e):
            date = e.control.value.strftime("%d %B %Y")
            self.tanggal_transaksi.value = date
            self.tanggal_transaksi.update()
            code = e.control.value.strftime("%y%m%d")
            parts = self.kode_transaksi.value.split(".")
            parts[1] = code
            self.kode_transaksi.value = ".".join(parts)
            self.kode_transaksi.update()

        def handle_dismissal(e):
            pass
            # print(f"DatePicker dismissed")

        date_picker = DatePicker(
            open=True,
            value=datetime.strptime(self.tanggal_transaksi.value, "%d %B %Y"),
            first_date=datetime(year=2000, month=1, day=1),
            last_date=datetime(year=2500, month=12, day=31),
            on_change=handle_change,
            on_dismiss=handle_dismissal,
        )
        self.page.open(date_picker)

    def display_barang_search(self, e):
        self.page.overlay.clear()
        self.search_item_dialog.open = True
        self.page.overlay.append(self.search_item_dialog)
        self.page.update()

    def dismiss_dialog(self, e):
        self.search_item_dialog.open = False
        self.search_item_dialog.update()
        self.page.overlay.clear()

    def search_on_change(self, e):
        keyword: str = e.control.value
        self.list_barang.controls = [
            ListTile(
                leading=Text(item["kode_barang"], style=TextStyle(size=14)),
                title=Text(item["nama_barang"], style=TextStyle(size=14)),
                on_click=lambda _, item=item: self.select_item(item),
            )
            for item in self.items
            if keyword in item["kode_barang"] or keyword.upper() in item["nama_barang"]
        ]
        self.list_barang.update()

    def select_item(self, item):
        self.selected_item = item
        self.nama_barang.value = item["nama_barang"]
        self.nama_barang.update()
        self.search_item_field.value = item["nama_barang"]
        self.search_item_field.update()
        self.dismiss_dialog(None)

    def confirm_update(self, e):
        detil = {
            "kode_barang": self.selected_item["kode_barang"],
            "jumlah": self.jumlah.value,
        }

        # print(self.id_detail, detil)

        # VALIDASI FORM
        self.kode_transaksi.error_text = (
            "Kode transaksi tidak boleh kosong"
            if self.kode_transaksi.value == ""
            else ""
        )
        self.jumlah.error_text = (
            "Jumlah tidak boleh kosong"
            if self.jumlah.value == ""
            else "Jumlah harus lebih dari 0" if int(self.jumlah.value) < 1 else ""
        )
        self.kode_transaksi.update()
        self.jumlah.update()

        if not self.kode_transaksi.error_text == "" or not self.jumlah.error_text == "":
            return None

        updated = False
        self.page.overlay.clear()
        loading = LoadingDialog(self.page)
        loading.display_dialog()
        # time.sleep(0.5)
        try:
            response = db.update_detail_transaksi(
                id_detail=self.id_detail,
                kode_barang=self.selected_item["kode_barang"],
                jumlah=self.jumlah.value,
            )
            if not response:
                raise Exception("Gagal mengubah data detail transaksi")
        except Exception as ex:
            # print(f"Error: {ex}")
            text = ex
            color = Colors.RED_800
            updated = True
        else:
            # print("update success")
            text = "Data transaksi berhasil diubah"
            color = Colors.GREEN_800
            updated = True
        finally:
            loading.dismiss_dialog()
            snackbar = CustomSnackbar(page=self.page, text=text, color=color)
            snackbar.display()
            if updated:
                self.page.go(ROUTES.SHOW_TRANSACTION)
