# tools/pdf_to_jpg.py
import os
import sys
from pathlib import Path
from typing import List, Optional
from pdf2image import convert_from_path
from PIL import Image
import flet as ft

# === 获取 Poppler 路径（自动适配开发/打包环境）===
def get_poppler_path() -> Optional[str]:
    """返回 poppler 的 bin 目录路径，若找不到则返回 None"""
    if sys.platform != "win32":
        return None  # macOS/Linux 通常无需指定

    # 判断是否被 PyInstaller 打包
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).parent.parent  # 项目根目录

    poppler_bin = base_dir / "poppler" / "Library" / "bin"
    if poppler_bin.exists() and (poppler_bin / "pdftoppm.exe").exists():
        return str(poppler_bin)
    else:
        return None  # 交给用户处理（或后续报错）

POPPLER_PATH = get_poppler_path()


def convert_single_pdf(pdf_path: Path, output_dir: Path, status_callback=None):
    """转换单个 PDF 到 JPG，图片命名为 <PDF文件名>_001.jpg"""
    try:
        target_folder = output_dir / pdf_path.stem
        target_folder.mkdir(parents=True, exist_ok=True)

        if status_callback:
            status_callback(f"正在转换 {pdf_path.name}...")

        images = convert_from_path(
            str(pdf_path),
            poppler_path=POPPLER_PATH,
            dpi=150
        )

        pdf_stem = pdf_path.stem
        for i, img in enumerate(images):
            if img.mode != "RGB":
                img = img.convert("RGB")
            img_filename = f"{pdf_stem}_{str(i + 1).zfill(3)}.jpg"
            img_path = target_folder / img_filename
            img.save(img_path, "JPEG", quality=95)

        return True, f"✅ {pdf_path.name} → {len(images)} 页"

    except Exception as e:
        error_msg = str(e)
        if "poppler" in error_msg.lower() or not POPPLER_PATH:
            msg = (
                "❌ Poppler 组件缺失！\n"
                "本工具依赖 Poppler 渲染 PDF。\n"
                "请使用官方完整版（已内置组件），或联系开发者。"
            )
        else:
            msg = f"❌ {pdf_path.name} 转换失败:\n{error_msg}"
        return False, msg


def collect_pdfs(input_path: Path) -> List[Path]:
    """收集所有 PDF 文件（单个文件 or 文件夹递归）"""
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return [input_path]
    elif input_path.is_dir():
        return sorted(input_path.rglob("*.pdf"))
    else:
        return []


def create_pdf_to_jpg_page(page: ft.Page) -> ft.Control:
    # === 状态控件 ===
    input_path_field = ft.TextField(label="输入路径（PDF 或 文件夹）", read_only=True, width=400)
    output_path_field = ft.TextField(label="输出目录", read_only=True, width=400)
    status_text = ft.Text("", size=13, selectable=True, expand=True)

    # === 文件选择器 ===
    file_picker = ft.FilePicker()
    folder_picker_input = ft.FilePicker()
    folder_picker_output = ft.FilePicker()
    page.overlay.extend([file_picker, folder_picker_input, folder_picker_output])

    def on_input_result(e: ft.FilePickerResultEvent):
        path = e.path or (e.files[0].path if e.files else None)
        if path:
            input_path_field.value = path
            input_path_field.update()

    def on_output_result(e: ft.FilePickerResultEvent):
        if e.path:
            output_path_field.value = e.path
            output_path_field.update()

    folder_picker_input.on_result = on_input_result
    folder_picker_output.on_result = on_output_result
    file_picker.on_result = on_input_result

    def pick_input_file(_):
        file_picker.pick_files(allowed_extensions=["pdf"], dialog_title="选择 PDF 文件")

    def pick_input_folder(_):
        folder_picker_input.get_directory_path(dialog_title="选择包含 PDF 的文件夹")

    def pick_output_folder(_):
        folder_picker_output.get_directory_path(dialog_title="选择输出目录")

    def start_conversion(_):
        input_str = input_path_field.value
        output_str = output_path_field.value

        if not input_str or not os.path.exists(input_str):
            status_text.value = "❌ 请输入有效的输入路径（PDF 或 文件夹）"
            status_text.color = "red"
            status_text.update()
            return

        if not output_str:
            status_text.value = "❌ 请选择输出目录"
            status_text.color = "red"
            status_text.update()
            return

        input_p = Path(input_str)
        output_p = Path(output_str)

        pdf_list = collect_pdfs(input_p)
        if not pdf_list:
            status_text.value = "❌ 未找到任何 PDF 文件"
            status_text.color = "red"
            status_text.update()
            return

        status_text.value = f"🔄 准备转换 {len(pdf_list)} 个 PDF 文件...\n"
        status_text.color = "blue"
        status_text.update()

        success_count = 0
        log_lines = []

        for pdf in pdf_list:
            # 保持相对结构：输出 = output_p / (pdf 相对于 input_p 父目录的路径)
            try:
                if input_p.is_file():
                    rel_parent = Path("")
                else:
                    rel_parent = pdf.relative_to(input_p).parent
                target_output_dir = output_p / rel_parent
            except ValueError:
                target_output_dir = output_p

            ok, msg = convert_single_pdf(pdf, target_output_dir)
            log_lines.append(msg)
            if ok:
                success_count += 1

            # 实时更新（限最后10行防卡顿）
            status_text.value = "\n".join(log_lines[-10:])
            status_text.update()

        # 汇总 & 自动打开
        summary = f"\n\n✅ 成功: {success_count}/{len(pdf_list)} 个文件"
        if success_count > 0:
            summary += f"\n📁 输出目录: {output_p}"
            try:
                os.startfile(output_p) if sys.platform == "win32" else None
            except Exception:
                pass

        status_text.value = "\n".join(log_lines) + summary
        status_text.color = "green" if success_count > 0 else "red"
        status_text.update()

    # === UI 布局 ===
    return ft.Column([
        ft.Text("📄 PDF 转 JPG（批量版）", size=24, weight="bold"),
        ft.Row([
            ft.Column([
                ft.Text("📥 输入:", weight="bold"),
                input_path_field,
                ft.Row([
                    ft.ElevatedButton("选择 PDF", icon=ft.Icons.FILE_PRESENT, on_click=pick_input_file),
                    ft.ElevatedButton("选择文件夹", icon=ft.Icons.FOLDER_OPEN, on_click=pick_input_folder),
                ])
            ]),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("📤 输出:", weight="bold"),
                output_path_field,
                ft.ElevatedButton("选择输出目录", icon=ft.Icons.SAVE, on_click=pick_output_folder),
            ])
        ], alignment=ft.MainAxisAlignment.START),

        ft.Divider(height=25),
        ft.ElevatedButton(
            "开始转换",
            icon=ft.Icons.PLAY_ARROW,
            on_click=start_conversion,
            height=50,
            style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.BLUE)
        ),
        ft.Divider(),
        ft.Container(
            content=status_text,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            expand=True,
            bgcolor=ft.colors.BLACK12
        )
    ], expand=True, scroll=ft.ScrollMode.AUTO)


# === 注册工具 ===
from . import register_tool
register_tool("PDF2JPG", ft.Icons.PICTURE_AS_PDF, create_pdf_to_jpg_page)