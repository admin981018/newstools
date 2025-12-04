# home_page.py
import flet as ft
from tools import get_tools

class HomePage(ft.UserControl):
    def __init__(self, on_tool_selected):
        super().__init__()
        self.on_tool_selected = on_tool_selected
        self.tool_cards = []
        self.search_field = ft.TextField(
            label="搜索工具...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.filter_tools,
            expand=True
        )

    def build(self):
        # 初始化所有工具卡片
        self.tool_cards = []
        for name, icon, _ in get_tools():
            card = ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=48, color=ft.colors.BLUE_400),
                    ft.Text(name, size=16, weight="bold", text_align=ft.TextAlign.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=12,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.colors.BLACK12),
                on_click=lambda _, n=name, i=icon: self.on_tool_selected(n, i),
                width=150,
                height=150,
                alignment=ft.alignment.center
            )
            self.tool_cards.append((name, card))

        self.grid = ft.GridView(
            expand=1,
            runs_count=4,
            max_extent=160,
            spacing=20,
            run_spacing=20,
            child_aspect_ratio=1.0
        )
        for _, card in self.tool_cards:
            self.grid.controls.append(card)

        return ft.Column([
            ft.Text("🛠️ 我的工具库", size=28, weight="bold", text_align=ft.TextAlign.CENTER),
            self.search_field,
            ft.Divider(height=20),
            self.grid
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def filter_tools(self, e):
        query = e.control.value.lower().strip()
        self.grid.controls.clear()
        for name, card in self.tool_cards:
            if query in name.lower():
                self.grid.controls.append(card)
        self.grid.update()