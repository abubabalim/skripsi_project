import core.database as db

from threading import Timer
from ui.utils import COLORS
from ui.widgets import CustomButton, LoadingDialog, CustomSnackbar
from flet import (
    Column,
    Page,
    ScrollMode,
    TextField,
    Icons,
    DataColumn,
    DataRow,
    DataCell,
    Text,
    DataTable,
    ControlState,
    Colors,
    TextStyle,
    FontWeight,
    Container,
    TextThemeStyle,
    Row,
    MainAxisAlignment,
    TextButton,
    KeyboardType,
    AlertDialog,
    TextSpan,
)


class ShowItem(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.items = []
        self.table_limit = 10
        self.table_offset = 0
        self.table_row_count = 0
        self.order_by = "kode_barang"
        self.desc = False
        self.keyword = ""
        self.scroll = ScrollMode.HIDDEN
        self.wrap = False
        self.debounce_timer = None
        self.show_all_button = CustomButton(
            text="Semua Barang",
            color=COLORS.PRIMARY,
            dynamic=False,
            on_tap=lambda _: self.show_all(),
        )
        self.search_field = TextField(
            dense=True,
            border_radius=6,
            hint_text="Cari nama barang",
            suffix_icon=Icons.SEARCH,
            on_change=self.on_change,
        )
        self._table_rows = []
        self.kode_barang_column = DataColumn(
            numeric=False,
            label=Text("Kode Barang"),
            on_sort=lambda _: self.on_sort("kode_barang"),
        )
        self.barcode_column = DataColumn(
            numeric=False,
            label=Text("Barcode"),
            on_sort=lambda _: self.on_sort("barcode"),
        )
        self.nama_barang_column = DataColumn(
            numeric=False,
            label=Text("Nama Barang"),
            on_sort=lambda _: self.on_sort("nama_barang"),
        )
        self.table_data = DataTable(
            expand=True,
            columns=[
                self.kode_barang_column,
                self.barcode_column,
                self.nama_barang_column,
                DataColumn(label=Text("Aksi")),
            ],
            show_bottom_border=True,
            rows=[],
            show_checkbox_column=False,
            data_row_color={ControlState.HOVERED: Colors.BLUE_GREY_50},
            heading_text_style=TextStyle(weight=FontWeight.BOLD),
            data_text_style=TextStyle(size=12, weight=FontWeight.W_500),
            heading_row_color={ControlState.DEFAULT: Colors.BLUE_GREY_100},
        )
        self.previous_button = CustomButton(
            text="Sebelumnya",
            color=COLORS.SECONDARY,
            dynamic=False,
            visible=False,
            on_tap=None,
        )
        self.next_button = CustomButton(
            text="Selanjutnya",
            color=COLORS.SECONDARY,
            dynamic=False,
            visible=False,
            on_tap=None,
        )
        self.controls = [
            Container(height=50),
            Text("Lihat Data Barang", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Menampilkan data barang yang tersimpan di database",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row(
                alignment=MainAxisAlignment.END,
                controls=[self.show_all_button, self.search_field],
            ),
            Row(alignment=MainAxisAlignment.CENTER, controls=[self.table_data]),
            Container(height=10),
            Row(
                alignment=MainAxisAlignment.END,
                controls=[self.previous_button, self.next_button],
            ),
            Container(height=100),
        ]

    @property
    def table_rows(self):
        return self._table_rows

    @table_rows.setter
    def table_rows(self, items):
        self._table_rows = [
            DataRow(
                cells=[
                    DataCell(Text(item["kode_barang"])),
                    DataCell(Text(item["barcode"])),
                    DataCell(Text(item["nama_barang"])),
                    DataCell(
                        TextButton(
                            text="Hapus",
                            icon=Icons.DELETE_FOREVER,
                            on_click=lambda _, item=item: self.delete_item(item),
                        )
                    ),
                ],
                on_select_changed=lambda _, item=item: self.update_item(item),
            )
            for item in items
        ]
        self.update()

    def did_mount(self):
        if db.get_db_connection():
            self.fetch_data()
        return super().did_mount()

    def fetch_data(self, keyword="", order_by="kode_barang", desc=False, offset=0):
        loading = LoadingDialog(self.page)
        loading.display_dialog()
        results = db.get_barang(
            search_keyword=keyword,
            order_by=order_by,
            desc=desc,
            offset=offset,
            limit=self.table_limit,
        )
        if results:
            self.table_offset = offset
            self.build_table_section(results["data"])
            self.build_pagination_button(results["total_count"])
        loading.dismiss_dialog()

    # build table rows
    def build_table_section(self, items):
        self.table_rows = items
        self.table_data.rows = self.table_rows
        self.table_data.update()

    # build pagination button
    def build_pagination_button(self, total_count=0):
        limit = self.table_limit
        offset = self.table_offset
        is_visible = total_count > 0 and total_count > limit

        self.next_button.visible = is_visible
        self.next_button.on_tap = lambda _: self.fetch_data(
            keyword=self.keyword,
            order_by=self.order_by,
            desc=self.desc,
            offset=offset + limit if offset + limit < total_count else 0,
        )
        self.next_button.update()

        self.previous_button.visible = is_visible
        self.previous_button.on_tap = lambda _: self.fetch_data(
            keyword=self.keyword,
            order_by=self.order_by,
            desc=self.desc,
            offset=(
                total_count
                - (limit if total_count % limit == 0 else total_count % limit)
                if offset - limit < 0
                else offset - limit
            ),
        )
        self.next_button.update()

    # sort data by table column
    def on_sort(self, order_by):
        desc = False

        self.kode_barang_column.numeric = (
            False if not order_by == "kode_barang" else self.kode_barang_column.numeric
        )
        self.barcode_column.numeric = (
            False if not order_by == "barcode" else self.barcode_column.numeric
        )
        self.nama_barang_column.numeric = (
            False if not order_by == "nama_barang" else self.nama_barang_column.numeric
        )

        if order_by == "kode_barang":
            self.kode_barang_column.numeric = not self.kode_barang_column.numeric
            desc = self.kode_barang_column.numeric
        elif order_by == "barcode":
            self.barcode_column.numeric = not self.barcode_column.numeric
            desc = self.barcode_column.numeric
        elif order_by == "nama_barang":
            self.nama_barang_column.numeric = not self.nama_barang_column.numeric
            desc = self.nama_barang_column.numeric

        self.order_by = order_by
        self.desc = desc

        self.fetch_data(order_by=self.order_by, desc=self.desc)

    # search items by keyword
    def on_change_debounced(self, value):
        self.keyword = value
        self.fetch_data(keyword=value, order_by=self.order_by, desc=self.desc)

    # on change search field
    def on_change(self, e):
        # Cancel previous timer if it exists
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Start a new timer with a delay of 500ms
        self.debounce_timer = Timer(
            0.5,
            self.on_change_debounced,
            args=[e.control.value],
        )
        self.debounce_timer.start()
        self.update()

    # show all / reset button
    def show_all(self):
        self.keyword = ""
        self.table_offset = 0
        self.table_row_count = 0
        self.search_field.value = ""
        self.search_field.update()
        self.order_by = "kode_barang"
        self.desc = False
        self.kode_barang_column.numeric = False
        self.barcode_column.numeric = False
        self.nama_barang_column.numeric = False

        self.fetch_data()

    # update item
    def update_item(self, item: dict):
        # dismiss update dialog
        def dismiss_dialog(e):
            update_dialog.open = False
            self.page.update()

        # validate textfield
        def validate(item):
            # validate field kode_barang
            kode_barang.error_text = (
                "Kode barang tidak boleh kosong"
                if kode_barang.value == ""
                else (
                    "Kode barang tidak boleh memiliki spasi"
                    if " " in kode_barang.value
                    else ""
                )
            )
            kode_barang.update()

            # validate field barcpde
            barcode.error_text = (
                "Barcode tidak boleh kosong"
                if barcode.value == ""
                else (
                    "Barcode tidak boleh memiliki spasi" if " " in barcode.value else ""
                )
            )
            barcode.update()

            # validate field nama_barang
            nama_barang.error_text = (
                "Nama barang tidak boleh kosong" if nama_barang.value == "" else ""
            )
            nama_barang.update()

            return (
                kode_barang.error_text == ""
                and barcode.error_text == ""
                and nama_barang.error_text == ""
            )

        # confirm save button
        def confirm_update(item):
            if not validate(item):
                return None

            item = {
                "id": item["kode_barang"],
                "kode_barang": kode_barang.value,
                "barcode": barcode.value,
                "nama_barang": nama_barang.value,
            }
            dismiss_dialog(None)
            saving_item(item)

        # save item to database
        def saving_item(item):
            text = None
            color = None
            self.page.overlay.clear()
            loading = LoadingDialog(self.page)
            loading.display_dialog()
            update_success = False
            try:
                results = db.update_barang(
                    kode_lama=item["id"],
                    kode_barang=item["kode_barang"],
                    barcode=item["barcode"],
                    nama_barang=item["nama_barang"],
                )
                if not results:
                    raise Exception()
            except Exception as e:
                text = "Update data barang gagal"
                color = Colors.RED_800
                # print(e)
            else:
                text = "Update data barang berhasil"
                color = Colors.GREEN_800
                update_success = True
            finally:
                loading.dismiss_dialog()
                snackbar = CustomSnackbar(page=self.page, text=text, color=color)
                snackbar.display()

                if update_success:
                    self.show_all()

        tstyle = TextStyle(weight=FontWeight.BOLD)
        kode_barang = TextField(
            hint_text="contoh: 1001",
            keyboard_type=KeyboardType.NUMBER,
            value=item["kode_barang"],
        )
        barcode = TextField(
            hint_text="contoh: 7622210580276",
            keyboard_type=KeyboardType.NUMBER,
            value=item["barcode"],
        )
        nama_barang = TextField(
            hint_text="contoh: OREO COK 66,5 GR",
            capitalization=True,
            value=item["nama_barang"],
        )

        update_dialog = AlertDialog(
            open=True,
            title=Text("Ubah Data Barang"),
            content=Container(
                width=400,
                content=Column(
                    tight=True,
                    controls=[
                        Text("Kode Barang", style=tstyle),
                        kode_barang,
                        Text("Barcode", style=tstyle),
                        barcode,
                        Text("Nama Barang", style=tstyle),
                        nama_barang,
                    ],
                ),
            ),
            actions=[
                TextButton(
                    "Simpan",
                    on_click=lambda e, item=item: confirm_update(item),
                ),
                TextButton("Batal", on_click=dismiss_dialog),
            ],
            actions_alignment=MainAxisAlignment.END,
        )

        self.page.overlay.clear()
        self.page.overlay.append(update_dialog)
        self.page.update()

    # delete item
    def delete_item(self, item: dict):

        # dismiss delete dialog
        def dismiss_dialog(e):
            delete_dialog.open = False
            self.page.update()

        # confirm delete
        def confirm_delete(item):
            dismiss_dialog(None)
            deleting_item(item)

        # delete item from database
        def deleting_item(item):
            text = None
            color = None
            self.page.overlay.clear()
            loading = LoadingDialog(self.page)
            loading.display_dialog()
            delete_success = False
            try:
                results = db.delete_barang(item["kode_barang"])
                if not results:
                    raise Exception()
            except Exception as e:
                text = "Data barang gagal dihapus"
                color = Colors.RED_800
                # print(e)
            else:
                text = "Data barang berhasil dihapus"
                color = Colors.GREEN_800
                delete_success = True
            finally:
                loading.dismiss_dialog()
                snackbar = CustomSnackbar(page=self.page, text=text, color=color)
                snackbar.display()
                if delete_success:
                    self.show_all()

        delete_dialog = AlertDialog(
            open=True,
            title=Text("Konfirmasi Penghapusan"),
            content=Text(
                spans=[
                    TextSpan("Apakah anda yakin akan menghapus "),
                    TextSpan(item["nama_barang"], style=TextStyle(weight="bold")),
                    TextSpan(" dengan kode "),
                    TextSpan(item["kode_barang"], style=TextStyle(weight="bold")),
                    TextSpan(" ?"),
                ]
            ),
            actions=[
                TextButton("Iya", on_click=lambda _, item=item: confirm_delete(item)),
                TextButton("Tidak", on_click=dismiss_dialog),
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=dismiss_dialog,
        )

        self.page.overlay.clear()
        self.page.overlay.append(delete_dialog)
        self.page.update()
