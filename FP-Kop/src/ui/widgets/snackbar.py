from flet import SnackBar, Text, Page

class CustomSnackbar(SnackBar):
    def __init__(self, page:Page, text, color = None, content = Text()):
        super().__init__(content)
        self.page = page
        self.open = True
        self.text = text
        self.bgcolor = color
        self.content = Text(self.text)
        self.duration = 2500
        
    def display(self):
        self.open = True
        self.page.overlay.append(self)
        self.page.update()
        
    def dismiss(self):
        self.open = False
        self.page.overlay.clear()
        self.page.update()
        
        
    