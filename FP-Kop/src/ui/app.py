from .screens import *
from ast import literal_eval
from .widgets import Sidebar
from .utils import ROUTES, COLORS
from urllib.parse import urlparse, parse_qs
from core.analysis_results import AnalysisResults
from flet import (
    Container,
    Text,
    Page,
    CrossAxisAlignment,
    Icons,
    padding,
    Row,
    VerticalDivider,
    AlertDialog,
    Colors,
    MouseCursor,
    GestureDetector,
    Icon,
    margin,
    border_radius,
)


class SkripsiApp(Container):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.analysis_result = AnalysisResults()
        self.width = self.page.window.width
        self.height = self.page.window.height
        self.page.on_resized = self.on_resized
        self.page.on_route_change = self.on_route_change
        self.vertical_alignment = CrossAxisAlignment.START
        self.toggle_nav_rail_button = ToggleSidebarButton(
            icon=Icons.MENU_OPEN,
            page=page,
            selected_icon=Icons.MENU,
            selected=False,
            on_click=self.toggle_nav_rail,
        )
        self.nav_rail = Sidebar(page)
        self.active_view = Container(
            expand=True,
            padding=padding.only(right=50),
        )
        self.content = Row(
            [
                self.nav_rail,
                VerticalDivider(
                    width=14,
                    thickness=16,
                    leading_indent=0,
                    trailing_indent=0,
                    color=COLORS.PRIMARY,
                ),
                self.toggle_nav_rail_button,
                self.active_view,
            ],
            vertical_alignment=CrossAxisAlignment.START,
            spacing=0,
        )

    def on_resized(self, e):
        self.width = self.page.window.width
        self.height = self.page.window.height
        self.update()

    def toggle_nav_rail(self, e):
        self.toggle_nav_rail_button.toggle()
        self.nav_rail.visible = not self.nav_rail.visible
        self.update()

    def on_route_change(self, e):
        parsed_url = urlparse(self.page.route)
        if parsed_url.path == ROUTES.DASHBOARD:
            self.nav_rail.selected_index = 0
            view = Dashboard(self.page)
        elif parsed_url.path == ROUTES.SHOW:
            self.nav_rail.selected_index = 1
            view = Show(self.page)
        elif parsed_url.path == ROUTES.SHOW_ITEM:
            self.nav_rail.selected_index = 1
            view = ShowItem(self.page)
        elif parsed_url.path == ROUTES.SHOW_TRANSACTION:
            self.nav_rail.selected_index = 1
            view = ShowTransaction(self.page)
        elif parsed_url.path == ROUTES.SHOW_TRANSACTION_UPDATE:
            self.nav_rail.selected_index = 1
            query_params = parse_qs(parsed_url.query)
            parameter = query_params.get("id_detail", [""])[0]
            id_detail = literal_eval(parameter)
            view = ShowTransactionUpdate(self.page, id_detail)
        elif parsed_url.path == ROUTES.SHOW_RESULT:
            self.nav_rail.selected_index = 2
            view = ShowResult(self.page)
        elif parsed_url.path == ROUTES.INPUT:
            self.nav_rail.selected_index = 2
            view = Input(self.page)
        elif parsed_url.path == ROUTES.INPUT_ITEM:
            self.nav_rail.selected_index = 2
            view = InputItem(self.page)
        elif parsed_url.path == ROUTES.INPUT_TRANSACTION:
            self.nav_rail.selected_index = 2
            view = InputTransaction(self.page)
        elif parsed_url.path == ROUTES.PROCESS:
            self.nav_rail.selected_index = 3
            view = Process(self.page, results=self.analysis_result)
        elif parsed_url.path == ROUTES.PROCESS_ITEM:
            self.nav_rail.selected_index = 3
            view = ProcessItem(self.page, results=self.analysis_result)
        elif parsed_url.path == ROUTES.PROCESS_TRANSACTION:
            self.nav_rail.selected_index = 3
            query_params = parse_qs(parsed_url.query)
            parameter = query_params.get("offset", [""])[0]
            offset = literal_eval(parameter)
            view = ProcessTransaction(
                self.page, results=self.analysis_result, data_offset=offset
            )
        elif parsed_url.path == ROUTES.PROCESS:
            self.nav_rail.selected_index = 3
            view = Process(self.page, results=self.analysis_result)
        elif parsed_url.path == ROUTES.RESULT:
            self.nav_rail.selected_index = 3
            view = Results(self.page, results=self.analysis_result)
        elif parsed_url.path == ROUTES.RESULT_ITEMSET:
            self.nav_rail.selected_index = 3
            view = ResultItemset(self.page, results=self.analysis_result)
        elif parsed_url.path == ROUTES.RESULT_RULES:
            self.nav_rail.selected_index = 3
            view = ResultRules(self.page, results=self.analysis_result)
        elif parsed_url.path == ROUTES.RESULT_STRATEGY:
            self.nav_rail.selected_index = 3
            view = ResultStrategy(self.page, results=self.analysis_result)
        else:
            view = self.active_view
            dialog = AlertDialog(
                open=True,
                title=Text("PAGE NOT FOUND"),
                content=Icon(Icons.WARNING, size=100, color=Colors.RED),
            )
            self.page.overlay.append(dialog)
        self.active_view.content = view
        self.active_view.update()
        self.nav_rail.update()
        # self.page.update()


class ToggleSidebarButton(GestureDetector):
    def __init__(self, page, icon, selected_icon, selected, on_click):
        super().__init__()
        self.icon = icon
        self.page = page
        self.selected_icon = selected_icon
        self.selected = selected
        self.on_tap = on_click
        self.mouse_cursor = MouseCursor.CLICK
        self.content = Container(
            height=40,
            width=50,
            margin=margin.only(top=10),
            bgcolor=COLORS.PRIMARY,
            border_radius=border_radius.only(top_right=100, bottom_right=100),
            content=Icon(name=self.icon, color=Colors.WHITE),
        )

    def toggle(self):
        self.selected = not self.selected
        self.content.content.name = self.selected_icon if self.selected else self.icon
        self.update()
