import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pikepdf import Pdf
import threading

class PdfUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 权限批量解除工具")
        self.root.geometry("650x500")

        # 存储待处理的路径列表
        self.input_sources = []

        # --- UI 布局 ---
        
        # 第一步：选择输入
        self.frame_input = tk.LabelFrame(root, text="第一步：选择输入源（可多选）", padx=10, pady=10)
        self.frame_input.pack(fill="x", padx=10, pady=5)
        
        btn_frame = tk.Frame(self.frame_input)
        btn_frame.pack(side="top", fill="x")
        
        tk.Button(btn_frame, text="+ 添加文件夹", command=self.add_directory).pack(side="left", padx=5)
        tk.Button(btn_frame, text="+ 添加单个文件", command=self.add_files).pack(side="left", padx=5)
        tk.Button(btn_frame, text="清空列表", command=self.clear_sources).pack(side="right", padx=5)

        self.source_list_lbl = tk.Label(self.frame_input, text="未选择任何内容", fg="gray", wraplength=550, justify="left")
        self.source_list_lbl.pack(fill="x", pady=5)

        # 第二步：选择输出
        self.frame_output = tk.LabelFrame(root, text="第二步：选择保存位置", padx=10, pady=10)
        self.frame_output.pack(fill="x", padx=10, pady=5)
        
        self.entry_output = tk.Entry(self.frame_output)
        self.entry_output.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(self.frame_output, text="浏览", command=self.select_output).pack(side="right")

        # 第三步：执行
        self.btn_run = tk.Button(root, text="🚀 开始解除权限", bg="#2196F3", fg="white", 
                                 height=2, font=("Helvetica", 10, "bold"), command=self.start_task)
        self.btn_run.pack(pady=10, fill="x", padx=10)

        # 日志输出
        self.log_area = scrolledtext.ScrolledText(root, height=12, padx=10, pady=5, bg="#f5f5f5")
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)

    # --- 按钮回调函数 ---

    def add_directory(self):
        path = filedialog.askdirectory(title="选择文件夹")
        if path:
            self.input_sources.append(("dir", path))
            self.update_source_label()

    def add_files(self):
        paths = filedialog.askopenfilenames(title="选择 PDF 文件", filetypes=[("PDF files", "*.pdf")])
        if paths:
            for p in paths:
                self.input_sources.append(("file", p))
            self.update_source_label()

    def clear_sources(self):
        self.input_sources = []
        self.update_source_label()
        self.log("--- 列表已清空 ---")

    def update_source_label(self):
        if not self.input_sources:
            self.source_list_lbl.config(text="未选择任何内容", fg="gray")
        else:
            text = f"已选择 {len(self.input_sources)} 个项目"
            self.source_list_lbl.config(text=text, fg="black")

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, path)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_task(self):
        if not self.input_sources:
            messagebox.showwarning("提示", "请先添加 PDF 文件或文件夹！")
            return
        if not self.entry_output.get():
            messagebox.showwarning("提示", "请先选择输出保存位置！")
            return
        
        # 修正后的线程启动代码
        t = threading.Thread(target=self.process_logic, daemon=True)
        t.start()

    # --- 核心逻辑 ---

    def process_logic(self):
        output_folder = self.entry_output.get()
        self.btn_run.config(state="disabled")
        self.log("--- 任务开始 ---")
        
        success_count = 0
        fail_count = 0

        # 解析路径
        all_files = []
        for s_type, s_path in self.input_sources:
            if s_type == "file":
                all_files.append(s_path)
            elif s_type == "dir":
                for f in os.listdir(s_path):
                    if f.lower().endswith(".pdf"):
                        all_files.append(os.path.join(s_path, f))

        all_files = list(set(all_files)) # 去重

        for file_path in all_files:
            filename = os.path.basename(file_path)
            output_path = os.path.join(output_folder, f"unlocked_{filename}")

            try:
                # 移除限制
                with Pdf.open(file_path) as pdf:
                    pdf.save(output_path)
                self.log(f"✅ 成功: {filename}")
                success_count += 1
            except Exception as e:
                self.log(f"❌ 失败: {filename} | 原因: {str(e)}")
                fail_count += 1

        self.log(f"--- 任务完成 | 成功: {success_count} | 失败: {fail_count} ---")
        self.btn_run.config(state="normal")
        messagebox.showinfo("完成", f"处理完毕！\n成功：{success_count}\n失败：{fail_count}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PdfUnlockerApp(root)
    root.mainloop()