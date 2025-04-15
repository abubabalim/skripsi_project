import pandas as pd
import core.database as db

from flet import *
from ui.utils import COLORS
from ui.widgets import CustomButton, LoadingDialog, CustomSnackbar


class InputItem(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.scroll = ScrollMode.AUTO
        self.wrap = False
        self.df = pd.DataFrame()
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
            Text("Input Data Barang", theme_style=TextThemeStyle.HEADLINE_SMALL),
            Text(
                "Memasukkan data barang ke database",
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

            df = pd.read_excel(file.path) if isXlsx else pd.read_csv(file.path)
            return {"status": True, "df": df}

        # check if its has "data barang" column
        def check_column(df: pd.DataFrame):
            if df.empty:
                return {"status": False, "message": "Data Kosong"}

            has_item_code = "Kode Barang" in df.columns
            has_barcode = "Barcode" in df.columns
            has_item_name = "Nama Barang" in df.columns

            if has_item_code and has_barcode and has_item_name:
                return {"status": True, "df": df}

            return {
                "status": False,
                "message": 'Gagal: File harus memiliki kolom "Kode Barang, Barcode, dan Nama Barang"',
            }
        
        try:
            self.page.overlay.clear()
            loading = LoadingDialog(self.page)
            loading.display_dialog()
            if not e.files:
                raise FileExistsError("No File Selected")
            result = convert_to_dataframe(e)
            if not result["status"]:
                raise Exception(result["message"])
            result = check_column(result["df"])
            if not result["status"]:
                raise Exception(result["message"])
        except FileExistsError as ex:
            print(ex)
        except Exception as ex:
            snackbar = CustomSnackbar(page=self.page, text=ex, color=Colors.RED)
            snackbar.display()
            print(ex)
            self.df = pd.DataFrame()
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
        

    # Save data to database
    def save_data(self, e):
        text = None
        color = None
        self.page.overlay.clear()
        loading = LoadingDialog(self.page)
        loading.display_dialog()
        try:
            data = [(item["Kode Barang"], item["Barcode"], item["Nama Barang"])
                for item in self.df.to_dict(orient="records")
            ]
                      
            if not db.insert_barang(data):
                raise Exception()
        except Exception as e:
            text = "Input data barang gagal, pastikan menggunakan data yang belum tersimpan di database"
            color = Colors.RED_800
            print(e)
        else:
            text = "Input data barang berhasil"
            color = Colors.GREEN_800
        finally:
            loading.dismiss_dialog()
            snackbar = CustomSnackbar(page=self.page, text=text, color=color)
            snackbar.display()
