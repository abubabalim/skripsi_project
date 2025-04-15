import core.database as db

from threading import Timer
from datetime import datetime
from ui.utils import COLORS, ROUTES
from ui.widgets import CustomButton, LoadingDialog, DateField, CustomSnackbar
from flet import (
    Column,
    Page,
    ScrollMode,
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
    TextButton,
    AlertDialog,
    TextSpan,
    TextField,
    padding,
    GestureDetector,
    MouseCursor,
    Icon,
    margin,
    border_radius,
    border,
    CrossAxisAlignment,
    Divider,
    MainAxisAlignment,
    ControlEvent,
    DatePicker,
)


class ShowTransaction(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.items = []
        self.transactions = []
        self.table_limit = 10
        self.table_offset = 0

        self.keyword = ""
        self.start_date = ""
        self.end_date = ""
        self.order_by = "tanggal_transaksi"
        self.desc = False

        self.scroll = ScrollMode.HIDDEN
        self.debounce_timer = None
        self.show_all_button = CustomButton(
            text="Semua Transaksi",
            color=COLORS.PRIMARY,
            dynamic=False,
            on_tap=lambda _: self.show_all(),
        )
        self.search_field = TextField(
            expand=True,
            border_radius=6,
            content_padding=padding.all(8),
            label="Cari Data Transaksi",
            on_change=self.on_change_search_field,
            prefix_icon=Icons.SEARCH,
            suffix=Container(
                padding=padding.only(top=2),
                content=GestureDetector(
                    content=Icon(Icons.CLOSE),
                    on_tap=self.search_field_reset,
                    mouse_cursor=MouseCursor.CLICK,
                ),
            ),
        )
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
        self.filter_section = Container(
            visible=True,
            margin=margin.only(bottom=-1),
            padding=padding.all(8),
            border=border.all(width=2, color=COLORS.PRIMARY),
            border_radius=border_radius.only(top_left=6, top_right=6, bottom_left=6),
            content=Column(
                controls=[
                    Row([self.start_date_field, self.end_date_field]),
                    self.search_field,
                ],
            ),
        )
        self.filter_section_toggle_button = GestureDetector(
            mouse_cursor=MouseCursor.CLICK,
            on_tap=self.filter_section_toggle,
            content=Container(
                padding=padding.symmetric(vertical=8, horizontal=24),
                bgcolor=COLORS.PRIMARY,
                border_radius=border_radius.only(bottom_left=16, bottom_right=16),
                content=Row(
                    vertical_alignment=CrossAxisAlignment.CENTER,
                    controls=[
                        Text("Filter", color=Colors.WHITE),
                        Icon(Icons.TUNE, color=Colors.WHITE, size=20),
                    ],
                ),
            ),
        )

        self._table_rows = []
        self.table_data = DataTable(
            expand=True,
            columns=[
                DataColumn(
                    label=Text("Tanggal"),
                    # on_sort=lambda _: sort_column("tanggal_transaksi"),
                ),
                DataColumn(label=Text("Kode Transaksi")),
                DataColumn(label=Text("Nama Barang")),
                DataColumn(label=Text("Jumlah")),
                DataColumn(label=Text("Aksi")),
            ],
            show_bottom_border=True,
            rows=self.table_rows,
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
            Text("Lihat Data Transaksi", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Menampilkan data transaksi yang tersimpan di database",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Column(
                spacing=0,
                controls=[
                    self.filter_section,
                    Divider(
                        thickness=2, height=1, leading_indent=7, color=COLORS.PRIMARY
                    ),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=CrossAxisAlignment.START,
                        controls=[
                            Container(
                                padding=padding.only(top=4),
                                content=self.show_all_button,
                            ),
                            self.filter_section_toggle_button,
                        ],
                    ),
                ],
            ),
            Row(alignment=MainAxisAlignment.CENTER, controls=[self.table_data]),
            Container(height=20),
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
    def table_rows(self, transactions):
        self._table_rows = [
            DataRow(
                cells=[
                    DataCell(Text(tsc["tanggal_transaksi"].strftime("%d %B %Y"))),
                    DataCell(Text(tsc["kode_transaksi"])),
                    DataCell(Text(tsc["nama_barang"])),
                    DataCell(Text(tsc["jumlah"])),
                    DataCell(
                        TextButton(
                            text="Hapus",
                            icon=Icons.DELETE_FOREVER,
                            on_click=lambda _, tsc=tsc: self.delete_transaction(tsc),
                        )
                    ),
                ],
                on_select_changed=lambda _, tsc=tsc: self.page.go(
                    f"{ROUTES.SHOW_TRANSACTION_UPDATE}?id_detail={tsc["id"]}"
                ),
            )
            for tsc in transactions
        ]
        self.update()

    def did_mount(self):
        if db.get_db_connection():
            self.fetch_data()
        return super().did_mount()

    # get data transactions
    def fetch_data(
        self,
        search_keyword=None,
        from_start_date=None,
        to_end_date=None,
        order_by=None,
        desc=False,
        offset=0,
    ):
        loading = LoadingDialog(page=self.page)
        loading.display_dialog()

        results = db.get_detail_transaksi(
            search_keyword=search_keyword,
            from_start_date=from_start_date,
            to_end_date=to_end_date,
            order_by=order_by,
            desc=desc,
            offset=offset,
            limit=self.table_limit,
        )
        # print(results)
        if results:
            self.table_offset = offset
            self.build_table_section(results["data"])
            self.build_pagination_button(results["total_count"])
        loading.dismiss_dialog()

    # build table rows
    def build_table_section(self, transactions):
        self.table_rows = transactions
        self.table_data.rows = self.table_rows
        self.table_data.update()

    # build pagination button
    def build_pagination_button(self, total_count=0):
        limit = self.table_limit
        offset = self.table_offset
        is_visible = total_count > 0 and total_count > limit

        self.next_button.visible = is_visible
        self.next_button.on_tap = lambda _: self.fetch_data(
            search_keyword=self.search_field.value,
            from_start_date=self.start_date_field.value,
            to_end_date=self.end_date_field.value,
            order_by=self.order_by,
            desc=self.desc,
            offset=offset + limit if offset + limit < total_count else 0,
        )
        self.next_button.update()

        self.previous_button.visible = is_visible
        self.previous_button.on_tap = lambda _: self.fetch_data(
            search_keyword=self.search_field.value,
            from_start_date=self.start_date_field.value,
            to_end_date=self.end_date_field.value,
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

    # search items by keyword
    def on_change_debounced(self, value):
        self.keyword = value
        self.fetch_data(
            search_keyword=value,
            from_start_date=self.start_date_field.value,
            to_end_date=self.end_date_field.value,
            order_by=self.order_by,
            desc=self.desc,
        )

    # on change search field
    def on_change_search_field(self, e):
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

    # show all button
    def show_all(self):
        self.table_offset = 0
        self.search_field.value = ""
        self.search_field.update()
        self.start_date_field.value = ""
        self.start_date_field.update()
        self.end_date_field.value = ""
        self.end_date_field.update()
        if db.get_db_connection():
            self.fetch_data()

    # show or hide filter section
    def filter_section_toggle(self, e):
        self.filter_section.visible = not self.filter_section.visible
        self.filter_section.update()

    # on reset search field
    def search_field_reset(self, e: ControlEvent):
        self.search_field.value = ""
        self.search_field.update()
        self.table_offset = 0
        self.fetch_data(
            search_keyword=self.search_field.value,
            from_start_date=self.start_date_field.value,
            to_end_date=self.end_date_field.value,
            order_by=self.order_by,
            desc=self.desc,
        )

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
            self.table_offset = 0
            self.fetch_data(
                search_keyword=self.search_field.value,
                from_start_date=self.start_date_field.value,
                to_end_date=self.end_date_field.value,
                order_by=self.order_by,
                desc=self.desc,
            )

        start = (
            self.start_date_field.value
            if not self.start_date_field.value == ""
            else datetime.now().strftime("%Y-%m-%d")
        )
        end = (
            self.end_date_field.value
            if not self.end_date_field.value == ""
            else datetime.now().strftime("%Y-%m-%d")
        )
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
        self.table_offset = 0
        self.fetch_data(
            search_keyword=self.search_field.value,
            from_start_date=self.start_date_field.value,
            to_end_date=self.end_date_field.value,
            order_by=self.order_by,
            desc=self.desc,
        )

    # delete transaction
    def delete_transaction(self, transaction: dict):
        # dismiss delete dialog
        def dismiss_dialog(e):
            delete_dialog.open = False
            self.page.update()

        # confirm delete
        def confirm_delete(transaction):
            dismiss_dialog(None)
            deleting_item(transaction)

        # delete item from database
        def deleting_item(transaction):
            text = None
            color = None
            self.page.overlay.clear()
            loading = LoadingDialog(self.page)
            loading.display_dialog()
            delete_success = False

            try:
                # delete from detail tranaksi
                results = db.delete_detail_transaksi(
                    transaction["id"], transaction["kode_transaksi"]
                )
                if not results:
                    raise Exception("Gagal menghapus data dari detail transaksi")
                delete_success = True
            except Exception as e:
                text = e
                color = Colors.RED_800
                delete_success = False
            else:
                text = "Data transaksi berhasil dihapus"
                color = Colors.GREEN_800
                delete_success = True
            finally:
                loading.dismiss_dialog()
                snackbar = CustomSnackbar(self.page, text=text, color=color)
                snackbar.display()
                if delete_success:
                    self.show_all()

        delete_dialog = AlertDialog(
            open=True,
            title=Text("Konfirmasi Penghapusan"),
            content=Text(
                spans=[
                    TextSpan("Apakah anda yakin akan menghapus transaksi "),
                    TextSpan(
                        transaction["nama_barang"], style=TextStyle(weight="bold")
                    ),
                    TextSpan("\ndengan kode "),
                    TextSpan(
                        transaction["kode_transaksi"],
                        style=TextStyle(weight="bold"),
                    ),
                    TextSpan(" ?"),
                ]
            ),
            actions=[
                TextButton(
                    "Iya", on_click=lambda _, item=transaction: confirm_delete(item)
                ),
                TextButton("Tidak", on_click=dismiss_dialog),
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=dismiss_dialog,
        )

        self.page.overlay.clear()
        self.page.overlay.append(delete_dialog)
        self.page.update()
