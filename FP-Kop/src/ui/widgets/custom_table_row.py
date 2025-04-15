from flet import Row, Container, TextButton, Icons, Text, padding


class CustomTableRow(Row):
    def __init__(self, items):
        super().__init__()
        self.controls = [
            CustomTableCell(
                expand=item["expand"],
                content=TextButton(text="Hapus", icon=Icons.DELETE_FOREVER) if index == -1 else Text(item["label"]),
            )
            for index, item in enumerate(items)
        ]
        # print(items)


class CustomTableCell(Container):
    def __init__(self, expand, content):
        super().__init__()
        self.expand=expand
        self.padding=padding.symmetric(horizontal=8, vertical=16)
        self.content=content