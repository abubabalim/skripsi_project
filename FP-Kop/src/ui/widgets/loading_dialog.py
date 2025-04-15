from flet import *


class LoadingDialog(AlertDialog):
    def __init__(self, page: Page, text="Mohon tunggu sebentar..."):
        super().__init__()
        self.page = page
        self.text = text
        self.open = True
        self.content_padding = padding.only(top=16)
        self.content = Column(
            tight=True,
            spacing=10,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            controls=[
                ProgressRing(width=40, height=40),
                Text(text),
            ],
        )

    def change_label(self, text):
        self.content.controls[-1].value = text

    def display_dialog(self, text=None):
        self.open = True
        self.content.controls[-1].value = text if text else self.text
        self.page.overlay.append(self)
        self.page.update()

    def dismiss_dialog(self):
        self.open = False
        self.page.update()
