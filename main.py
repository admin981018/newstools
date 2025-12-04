# main.py
import flet as ft
from home_page import HomePage
from tools import get_tools

# 导入所有工具（触发注册）
import tools.pdf_to_jpg  # 👈 必须导入才能注册！

def main(page: ft.Page):
    page.title = "工具库"
    page.window.width = 800
    page.window.height = 600
    page.padding = 20

    # 存储工具构建函数的映射
    tool_builders = {name: builder for name, _, builder in get_tools()}

    def go_back_to_home(_):
        page.views.clear()
        page.views.append(
            ft.View("/", [
                HomePage(on_tool_selected=open_tool)
            ])
        )
        page.update()

    def open_tool(tool_name, icon):
        if tool_name in tool_builders:
            page.views.append(
                ft.View(
                    f"/{tool_name}",
                    [
                        ft.AppBar(
                            title=ft.Text(tool_name),
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back_to_home),
                            bgcolor=ft.colors.SURFACE_VARIANT
                        ),
                        tool_builders[tool_name](page)
                    ]
                )
            )
            page.update()

    # 初始主页
    go_back_to_home(None)

ft.app(target=main)