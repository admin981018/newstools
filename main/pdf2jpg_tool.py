import os
import fitz  # PyMuPDF
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class PDFToJPGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF转JPG批量转换工具")
        self.root.geometry("600x500")

        # 变量
        self.input_path = tk.StringVar()
        self.is_converting = False

        self.setup_ui()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="PDF转JPG批量转换工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 输入路径选择
        ttk.Label(main_frame, text="选择PDF文件或文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Entry(input_frame, textvariable=self.input_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(input_frame, text="浏览", command=self.browse_input).grid(row=0, column=1, padx=(5, 0))

        input_frame.columnconfigure(0, weight=1)

        # 选项框架
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 转换质量
        ttk.Label(options_frame, text="图像质量 (1-100):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=85)
        quality_spinbox = ttk.Spinbox(options_frame, from_=1, to=100, textvariable=self.quality_var, width=10)
        quality_spinbox.grid(row=0, column=1, padx=(5, 0), pady=5)

        # 页面范围
        ttk.Label(options_frame, text="页面范围 (留空转换全部):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.page_range_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.page_range_var, width=10).grid(row=1, column=1, padx=(5, 0), pady=5)
        ttk.Label(options_frame, text="格式: 1-3 或 1,3,5", foreground="gray").grid(row=1, column=2, padx=(5, 0),
                                                                                    pady=5)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        self.convert_btn = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.convert_btn.grid(row=0, column=0, padx=5)

        self.cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_btn.grid(row=0, column=1, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="准备就绪", foreground="blue")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

        # 日志文本框
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.log_text = tk.Text(log_frame, height=10, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 配置权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def browse_input(self):
        # 询问用户选择文件还是文件夹
        choice = messagebox.askquestion("选择输入", "选择PDF文件还是文件夹？\n\n是=选择文件夹，否=选择PDF文件")
        if choice == 'yes':
            path = filedialog.askdirectory(title="选择PDF文件夹")
        else:
            path = filedialog.askopenfilename(
                title="选择PDF文件",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )

        if path:
            self.input_path.set(path)

    def start_conversion(self):
        if not self.input_path.get():
            messagebox.showwarning("警告", "请选择输入路径")
            return

        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)

        # 在新线程中执行转换
        conversion_thread = threading.Thread(target=self.convert_pdfs)
        conversion_thread.daemon = True
        conversion_thread.start()

    def cancel_conversion(self):
        self.is_converting = False
        self.update_status("转换已取消")

    def convert_pdfs(self):
        input_path = self.input_path.get()
        quality = self.quality_var.get()
        page_range = self.page_range_var.get().strip()

        if not input_path:
            self.update_status("错误: 未选择输入路径")
            self.finish_conversion()
            return

        # 解析页面范围
        page_numbers = None
        if page_range:
            try:
                page_numbers = self.parse_page_range(page_range)
            except ValueError as e:
                self.update_status(f"错误: {str(e)}")
                self.finish_conversion()
                return

        try:
            if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
                # 单个文件转换
                self.convert_single_pdf(input_path, quality, page_numbers)
            elif os.path.isdir(input_path):
                # 批量转换
                self.convert_batch(input_path, quality, page_numbers)
            else:
                self.update_status("错误: 无效的输入路径")
        except Exception as e:
            self.update_status(f"转换出错: {str(e)}")

        self.finish_conversion()

    def parse_page_range(self, page_range_str):
        """解析页面范围字符串，如 '1-3' 或 '1,3,5'"""
        page_numbers = set()

        for part in page_range_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_numbers.update(range(start - 1, end))  # 转换为0基索引
            else:
                page_numbers.add(int(part) - 1)  # 转换为0基索引

        return sorted(list(page_numbers))

    def convert_batch(self, input_dir, quality, page_numbers):
        """批量转换PDF文件"""
        # 收集所有PDF文件
        pdf_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))

        total_files = len(pdf_files)
        self.update_status(f"找到 {total_files} 个PDF文件")
        self.progress['maximum'] = total_files

        for i, pdf_path in enumerate(pdf_files):
            if not self.is_converting:
                break

            self.update_status(f"正在转换 ({i + 1}/{total_files}): {os.path.basename(pdf_path)}")
            self.progress['value'] = i + 1
            self.root.update_idletasks()

            try:
                self.convert_single_pdf(pdf_path, quality, page_numbers)
            except Exception as e:
                self.update_status(f"转换失败 {os.path.basename(pdf_path)}: {str(e)}")

        self.update_status(f"批量转换完成，共处理 {len(pdf_files)} 个文件")

    def convert_single_pdf(self, pdf_path, quality, page_numbers):
        """转换单个PDF文件"""
        if not self.is_converting:
            return

        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # 计算输出目录：在PDF同级目录创建"转换后"文件夹
        pdf_dir = os.path.dirname(pdf_path)
        output_base_dir = os.path.join(pdf_dir, "转换后")

        # 计算相对于输入目录的路径（用于保持目录结构）
        input_dir = os.path.dirname(self.input_path.get()) if os.path.isfile(
            self.input_path.get()) else self.input_path.get()
        rel_path = os.path.relpath(pdf_dir, input_dir)

        if rel_path != '.':
            output_dir = os.path.join(output_base_dir, rel_path, pdf_name)
        else:
            output_dir = os.path.join(output_base_dir, pdf_name)

        os.makedirs(output_dir, exist_ok=True)

        try:
            doc = fitz.open(pdf_path)

            # 确定要转换的页面
            if page_numbers:
                pages_to_convert = [p for p in page_numbers if 0 <= p < len(doc)]
            else:
                pages_to_convert = range(len(doc))

            for page_num in pages_to_convert:
                if not self.is_converting:
                    break

                page = doc[page_num]

                # 渲染页面为图像
                mat = fitz.Matrix(2.0, 2.0)  # 2倍分辨率
                pix = page.get_pixmap(matrix=mat)

                # 转换为PIL图像
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))

                # 保存为JPG
                jpg_path = os.path.join(output_dir, f"{pdf_name}_page_{page_num + 1:03d}.jpg")
                img.save(jpg_path, "JPEG", quality=quality, optimize=True)

                self.update_log(f"已保存: {jpg_path}")

            doc.close()
            self.update_status(f"完成转换: {os.path.basename(pdf_path)}")
        except Exception as e:
            self.update_status(f"转换失败 {os.path.basename(pdf_path)}: {str(e)}")

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def update_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def finish_conversion(self):
        self.is_converting = False
        self.progress['value'] = 0
        self.convert_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

        if self.is_converting:  # 如果是取消的
            self.update_status("转换已取消")
        else:
            self.update_status("转换完成")


# 修复导入问题
try:
    import io
except ImportError:
    import io

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToJPGConverter(root)
    root.mainloop()