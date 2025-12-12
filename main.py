# main.py
import ssl
import urllib.request

# 全局禁用SSL证书验证，解决Flet启动时的证书问题
ssl._create_default_https_context = ssl._create_unverified_context
urllib.request.install_opener(
    urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
    )
)

import flet as ft
from home_page import HomePage
from tools import get_tools  # 触发工具发现
import tools.pdf_to_jpg  # 显式导入工具模块
# 移除OCR工具模块的导入

def main(page: ft.Page):
    page.title = "喜洋洋工具库"
    page.window.width = 800
    page.window.height = 600
    page.padding = 20

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
                            leading=ft.IconButton(
                                ft.Icons.ARROW_BACK,
                                on_click=go_back_to_home
                            ),
                            bgcolor=ft.colors.SURFACE_VARIANT
                        ),
                        tool_builders[tool_name](page)
                    ]
                )
            )
            page.update()

    go_back_to_home(None)

if __name__ == "__main__":
    # 运行Flet应用
    ft.app(target=main)