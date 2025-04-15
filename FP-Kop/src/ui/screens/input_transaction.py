import core.database as db

from ui.utils import COLORS
from pandas import DataFrame, read_csv, read_excel
from ui.widgets import CustomButton, LoadingDialog, CustomSnackbar
from flet import Column, Page, ScrollMode, Text, FilePicker, Colors, Container, TextThemeStyle, Row, FilePickerResultEvent


class InputTransaction(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.scroll = ScrollMode.AUTO
        self.wrap = False
        self.df = DataFrame()
        self.selected_file_text = Text()
        self.file_picker = FilePicker(on_result=self.picker_on_result)
        self.picker_button = CustomButton(
            text="Pilih File",
            color=Colors.WHITE,
            on_tap=lambda _: self.pick_file(),
            outlined=True,
        )
        self.save_button = CustomButton(
            text="Simpan",
            color=COLORS.PRIMARY,
            on_tap=None,
            disabled=True,
        )
        self.controls = [
            Container(height=50),
            Text("Input Data Transaksi", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Memasukkan data transaksi ke database",
                theme_style=TextThemeStyle.LABEL_LARGE,
            ),
            Container(height=30),
            Row(
                controls=[
                    self.picker_button,
                    self.selected_file_text,
                ],
            ),
            self.save_button,
        ]

    # execute when file_picker_button clicked
    def pick_file(self):
        self.page.overlay.append(self.file_picker)
        self.page.update()

        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["csv", "xlsx"],
        )

    # execute after picking or canceling pick_file
    def picker_on_result(self, e: FilePickerResultEvent):

        # convert data to dataframe
        def convert_to_dataframe(e: FilePickerResultEvent):
            file = e.files[0]
            isCsv = file.name.endswith(".csv")
            isXlsx = file.name.endswith(".xlsx")

            if not isCsv and not isXlsx:
                return {"status": False, "message": "Format file tidak didukung"}

            df = read_excel(file.path) if isXlsx else read_csv(file.path)
            return {"status": True, "df": df}

        # check if its has "data barang" column
        def check_column(df: DataFrame):
            if df.empty:
                return {"status": False, "message": "Data Kosong"}

            has_transaction_date = "Tanggal Transaksi" in df.columns
            has_transaction_code = "Kode Transaksi" in df.columns
            has_item_code = "Kode Barang" in df.columns
            has_quantity = "Jumlah" in df.columns
            has_price = "Harga" in df.columns
            has_discount = "Diskon" in df.columns
            has_total_price = "Total Harga" in df.columns

            if (
                has_transaction_date
                and has_transaction_code
                and has_item_code
                and has_quantity
                and has_price
                and has_discount
                and has_total_price
            ):
                return {"status": True, "df": df}

            return {
                "status": False,
                "message": 'Gagal: File harus memiliki kolom "Tanggal Transaksi, Kode Transaksi, Kode Barang, Nama Barang, Jumlah, Harga, Diskon, dan Total Harga"',
            }

        try:
            self.page.overlay.clear()
            loading = LoadingDialog(self.page)
            loading.display_dialog()
            if not e.files:
                raise FileExistsError("No File Selected")
            if not e.files:
                raise Exception("")            
            result = convert_to_dataframe(e)
            if not result["status"]:
                raise Exception(result["message"])
            result = check_column(result["df"])
            if not result["status"]:
                raise Exception(result["message"])
        except FileExistsError as ex:
            # print(ex)
            pass
        except Exception as ex:
            # print(ex)
            snackbar = CustomSnackbar(page=self.page, text=ex, color=Colors.RED)
            snackbar.display()
            self.df = DataFrame()
            self.selected_file_text.value = ""
            self.selected_file_text.update()
            self.save_button.toggle_disable(True)
            self.save_button.update()
        else:
            self.df = result["df"]
            self.selected_file_text.value = ", ".join(map(lambda f: f.name, e.files))
            self.selected_file_text.update()
            self.save_button.toggle_disable(False)
            self.save_button.on_tap = self.save_data
            self.save_button.update()
        finally:
            loading.dismiss_dialog()

    def save_data(self, e):
        text = None
        color = None
        self.page.overlay.clear()
        loading = LoadingDialog(self.page)
        loading.display_dialog()

        try:
            transactions = list(
                self.df[["Kode Transaksi", "Tanggal Transaksi"]]
                .drop_duplicates(subset=["Kode Transaksi"])
                .rename(
                    columns={
                        "Kode Transaksi": "kode_transaksi",
                        "Tanggal Transaksi": "tanggal_transaksi",
                    }
                )
                .itertuples(index=False, name=None)
            )
            
            detils = list(
                self.df[
                    ["Kode Transaksi", "Kode Barang", "Jumlah", "Harga", "Diskon", "Total Harga"]
                ]
                .rename(
                    columns={
                        "Kode Transaksi": "kode_transaksi",
                        "Kode Barang": "kode_barang",
                        "Jumlah": "jumlah",
                        "Harga": "harga",
                        "Diskon": "diskon",
                        "Total Harga": "total_harga",
                    }
                )
                .itertuples(index=False, name=None)
            )
            
            # Save to transaction table
            if not db.insert_transaksi(transactions):
                raise Exception("Input transaction failed")

            # save to detil transaction table
            if not db.insert_detail_transaksi(detils):
                raise Exception("Input detil failed")
        except Exception as e:
            text = "Input data transaksi gagal, pastikan menggunakan data yang belum tersimpan di database"
            color = Colors.RED_800
            # print(e)
        else:
            text = "Input data transaksi berhasil"
            color = Colors.GREEN_800
        finally:
            loading.dismiss_dialog()
            snackbar = CustomSnackbar(self.page, text, color)
            snackbar.display()
            
