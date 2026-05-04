import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from collections import OrderedDict

class FileTab:
    def __init__(self, file_path, lines):
        self.file_path = file_path
        self.lines = lines
        self.name = os.path.basename(file_path)

class CopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("一键复制工具 - 多文件版")
        self.root.geometry("900x700")
        self.root.configure(bg="#f8f9fa")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.file_tabs = OrderedDict()
        self.current_tab_id = None
        self.loading_label = None
        self.is_loading = False
        self.loading_frame = None
        
        self.setup_styles()
        self.create_widgets()
    
    def on_closing(self):
        self.is_loading = False
        self.root.destroy()
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('Toolbar.TFrame', background='#ffffff')
        self.style.configure('Status.TFrame', background='#e9ecef')
        self.style.configure('Highlight.TFrame', background='#f1f3f4')
        
        self.style.configure('Main.TButton', 
                            background='#007bff', 
                            foreground='#ffffff',
                            padding=6,
                            font=('Arial', 10))
        self.style.map('Main.TButton',
                       background=[('active', '#0056b3'), ('pressed', '#004085'), ('disabled', '#6c757d')],
                       foreground=[('disabled', '#adb5bd')])
        
        self.style.configure('Copy.TButton', 
                            background='#6c757d', 
                            foreground='#ffffff',
                            padding=4,
                            font=('Arial', 9))
        self.style.map('Copy.TButton',
                       background=[('active', '#5a6268'), ('pressed', '#495057')])
        
        self.style.configure('Notebook.Tab', 
                            background='#e9ecef', 
                            foreground='#495057',
                            padding=[12, 4],
                            font=('Arial', 10))
        self.style.map('Notebook.Tab',
                       background=[('selected', '#ffffff'), ('active', '#dee2e6')],
                       foreground=[('selected', '#007bff'), ('active', '#2d3436')])
        
        self.style.configure('TNotebook', background='#ffffff', borderwidth=1)
        self.style.configure('Vertical.TScrollbar', background='#dee2e6', troughcolor='#ffffff')
    
    def create_widgets(self):
        toolbar_frame = ttk.Frame(self.root, padding="10", style='Toolbar.TFrame')
        toolbar_frame.pack(fill=tk.X, padx=10, pady=5)
        toolbar_frame.configure(relief=tk.RIDGE, borderwidth=1)
        
        self.add_file_btn = ttk.Button(toolbar_frame, text="添加文件", command=self.add_files, style='Main.TButton')
        self.add_file_btn.pack(side=tk.LEFT, padx=2)
        
        self.add_folder_btn = ttk.Button(toolbar_frame, text="添加文件夹", command=self.add_folder_files, style='Main.TButton')
        self.add_folder_btn.pack(side=tk.LEFT, padx=2)
        
        self.copy_all_btn = ttk.Button(toolbar_frame, text="复制所有文件", command=self.copy_all_files, style='Main.TButton')
        self.copy_all_btn.pack(side=tk.LEFT, padx=2)
        
        self.copy_merged_btn = ttk.Button(toolbar_frame, text="合并复制", command=self.copy_merged, style='Main.TButton')
        self.copy_merged_btn.pack(side=tk.LEFT, padx=2)
        
        self.close_tab_btn = ttk.Button(toolbar_frame, text="关闭当前", command=self.close_current_tab, style='Main.TButton')
        self.close_tab_btn.pack(side=tk.LEFT, padx=2)
        
        self.close_all_btn = ttk.Button(toolbar_frame, text="关闭所有", command=self.close_all_tabs, style='Main.TButton')
        self.close_all_btn.pack(side=tk.LEFT, padx=2)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.create_welcome_tab()
        
        self.status_frame = ttk.Frame(self.root, padding="5", style='Status.TFrame')
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_frame.configure(relief=tk.RIDGE, borderwidth=1)
        
        self.status_label = ttk.Label(self.status_frame, text="就绪", font=("Arial", 10), 
                                      foreground="#495057", background="#e9ecef")
        self.status_label.pack(side=tk.LEFT)
        
        self.file_count_label = ttk.Label(self.status_frame, text="已加载 0 个文件", 
                                          font=("Arial", 10), foreground="#495057", background="#e9ecef")
        self.file_count_label.pack(side=tk.RIGHT)
    
    def create_welcome_tab(self):
        self.empty_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.empty_frame, text="欢迎")
        
        self.empty_label = ttk.Label(self.empty_frame, 
                                      text="点击「添加文件」或「添加文件夹」开始\n\n支持同时打开多个文件，点击标签页切换文件\n每行右侧有复制按钮，支持单行复制\n「复制所有文件」逐个复制，「合并复制」合并后复制", 
                                      font=("Arial", 12), 
                                      foreground="#495057", 
                                      background="#ffffff")
        self.empty_label.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if files:
            self.load_files_threaded(list(files))
    
    def add_folder_files(self):
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            try:
                files = [os.path.join(folder, f) for f in os.listdir(folder) 
                        if os.path.isfile(os.path.join(folder, f))]
                files.sort()
                if files:
                    self.load_files_threaded(files)
                else:
                    self.update_status("该文件夹中没有文件", "#dc3545")
            except PermissionError:
                messagebox.showerror("权限错误", f"无法访问文件夹: {folder}")
                self.update_status("无法访问文件夹", "#dc3545")
            except Exception as e:
                messagebox.showerror("错误", f"加载文件夹失败: {str(e)}")
                self.update_status("加载文件夹失败", "#dc3545")
    
    def load_files_threaded(self, files):
        if self.is_loading:
            return
        
        self.is_loading = True
        
        try:
            if hasattr(self, 'empty_frame') and self.empty_frame:
                self.empty_frame.destroy()
                self.empty_frame = None
        except Exception:
            pass
        
        self.loading_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loading_frame, text="加载中...")
        
        self.loading_label = ttk.Label(self.loading_frame, text="正在加载文件...", 
                                       font=("Arial", 14), foreground="#007bff", background="#ffffff")
        self.loading_label.pack(fill=tk.BOTH, expand=True)
        
        self.update_status("正在加载文件...", "#007bff")
        
        def load_task():
            loaded_count = 0
            failed_files = []
            new_tabs = OrderedDict()
            
            for file_path in files:
                if not self.is_loading:
                    break
                try:
                    stat_info = os.stat(file_path)
                    if stat_info.st_size > 10 * 1024 * 1024:
                        failed_files.append((file_path, "文件过大（超过10MB）"))
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    file_tab = FileTab(file_path, lines)
                    new_tabs[file_path] = file_tab
                    loaded_count += 1
                except PermissionError:
                    failed_files.append((file_path, "权限不足"))
                except UnicodeDecodeError:
                    failed_files.append((file_path, "编码不支持"))
                except Exception as e:
                    failed_files.append((file_path, str(e)))
            
            def update_ui():
                if not self.is_loading:
                    return
                
                if self.loading_label:
                    self.loading_label.destroy()
                    self.loading_label = None
                if self.loading_frame:
                    current_idx = self.notebook.index(self.loading_frame)
                    self.notebook.forget(current_idx)
                    self.loading_frame = None
                
                self.is_loading = False
                
                for i in range(self.notebook.index("end") - 1, -1, -1):
                    self.notebook.forget(i)
                
                self.file_tabs = new_tabs
                
                for file_path, file_tab in self.file_tabs.items():
                    self.create_tab_widget(file_tab)
                
                if self.file_tabs:
                    self.notebook.select(0)
                    self.current_tab_id = list(self.file_tabs.keys())[0]
                    self.update_status(f"已加载 {loaded_count} 个文件", "#28a745")
                else:
                    self.current_tab_id = None
                    self.create_welcome_tab()
                    self.update_status("未加载任何文件", "#6c757d")
                
                self.file_count_label.config(text=f"已加载 {len(self.file_tabs)} 个文件")
                
                if failed_files:
                    error_msg = "\n".join([f"{os.path.basename(p)}: {e}" for p, e in failed_files])
                    messagebox.showwarning("部分文件加载失败", f"以下文件无法加载:\n{error_msg}")
            
            self.root.after(0, update_ui)
        
        thread = threading.Thread(target=load_task, daemon=True)
        thread.start()
    
    def create_tab_widget(self, file_tab):
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=file_tab.name)
        
        content_canvas = tk.Canvas(tab_frame, bg="#ffffff", highlightthickness=0)
        content_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=content_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        inner_frame = ttk.Frame(content_canvas)
        content_canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        for i, line in enumerate(file_tab.lines):
            line_frame = ttk.Frame(inner_frame, style='Toolbar.TFrame')
            line_frame.pack(fill=tk.X, pady=0)
            line_frame.bind('<Enter>', lambda e, lf=line_frame: lf.configure(style='Highlight.TFrame'))
            line_frame.bind('<Leave>', lambda e, lf=line_frame: lf.configure(style='Toolbar.TFrame'))
            
            line_num = ttk.Label(line_frame, text=str(i+1), width=4, 
                                foreground="#6c757d", background="#ffffff", anchor="e",
                                font=("Consolas", 10, 'bold'))
            line_num.pack(side=tk.LEFT, padx=(8, 12))
            
            content_label = ttk.Label(line_frame, text=line.rstrip() if line.strip() else " ", 
                                     foreground="#2d3436", background="#ffffff", 
                                     font=("Consolas", 10), anchor="w")
            content_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            copy_btn = ttk.Button(line_frame, text="Copy", width=6,
                                 command=lambda fp=file_tab.file_path, idx=i: self.copy_line(fp, idx),
                                 style='Copy.TButton')
            copy_btn.pack(side=tk.RIGHT, padx=8)
        
        def on_frame_config(event):
            content_canvas.config(scrollregion=content_canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", on_frame_config)
        
        tab_frame.file_path = file_tab.file_path
        tab_frame.inner_frame = inner_frame
        tab_frame.content_canvas = content_canvas
    
    def on_tab_changed(self, event):
        if self.file_tabs:
            try:
                current_idx = self.notebook.index(self.notebook.select())
                keys = list(self.file_tabs.keys())
                if 0 <= current_idx < len(keys):
                    self.current_tab_id = keys[current_idx]
            except Exception:
                pass
    
    def close_current_tab(self):
        if self.current_tab_id and self.current_tab_id in self.file_tabs:
            del self.file_tabs[self.current_tab_id]
            
            try:
                current_idx = self.notebook.index(self.notebook.select())
                self.notebook.forget(current_idx)
            except Exception:
                pass
            
            if self.file_tabs:
                new_idx = min(current_idx, len(self.file_tabs) - 1) if 'current_idx' in dir() else 0
                self.notebook.select(new_idx)
                self.current_tab_id = list(self.file_tabs.keys())[new_idx]
            else:
                self.current_tab_id = None
                self.create_welcome_tab()
            
            self.file_count_label.config(text=f"已加载 {len(self.file_tabs)} 个文件")
            self.update_status(f"已关闭文件，当前 {len(self.file_tabs)} 个文件", "#6c757d")
    
    def close_all_tabs(self):
        self.file_tabs.clear()
        self.current_tab_id = None
        
        for i in range(self.notebook.index("end") - 1, -1, -1):
            self.notebook.forget(i)
        
        self.create_welcome_tab()
        
        self.file_count_label.config(text="已加载 0 个文件")
        self.update_status("已关闭所有文件", "#6c757d")
    
    def copy_line(self, file_path, index):
        if file_path in self.file_tabs:
            file_tab = self.file_tabs[file_path]
            if 0 <= index < len(file_tab.lines):
                text = file_tab.lines[index].strip()
                try:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    self.root.update()
                    self.update_status(f"已复制 {file_tab.name} 第 {index+1} 行", "#28a745")
                except Exception as e:
                    self.update_status(f"复制失败: {str(e)}", "#dc3545")
    
    def copy_all_files(self):
        if not self.file_tabs:
            messagebox.showwarning("警告", "没有打开的文件")
            return
        
        try:
            self.root.clipboard_clear()
            for file_path, file_tab in self.file_tabs.items():
                for line in file_tab.lines:
                    if line.strip():
                        self.root.clipboard_append(line)
            self.root.update()
            self.update_status(f"已复制所有文件内容（共 {len(self.file_tabs)} 个文件）", "#28a745")
        except Exception as e:
            self.update_status(f"复制失败: {str(e)}", "#dc3545")
    
    def copy_merged(self):
        if not self.file_tabs:
            messagebox.showwarning("警告", "没有打开的文件")
            return
        
        result = messagebox.askyesno("合并复制", 
            "是否按文件顺序合并所有文件内容？\n\n是：合并所有行\n否：每个文件分别复制到剪贴板")
        
        if result:
            self._merge_copy()
        else:
            self._separate_copy()
    
    def _merge_copy(self):
        try:
            merged_text = ""
            for file_tab in self.file_tabs.values():
                merged_text += f"=== {file_tab.name} ===\n"
                for line in file_tab.lines:
                    merged_text += line
                merged_text += "\n"
            
            self.root.clipboard_clear()
            self.root.clipboard_append(merged_text.strip())
            self.root.update()
            self.update_status(f"已合并复制 {len(self.file_tabs)} 个文件", "#28a745")
        except Exception as e:
            self.update_status(f"合并复制失败: {str(e)}", "#dc3545")
    
    def _separate_copy(self):
        try:
            self.root.clipboard_clear()
            clipboard_content = []
            for file_tab in self.file_tabs.values():
                file_content = ""
                for line in file_tab.lines:
                    file_content += line
                clipboard_content.append(f"=== {file_tab.name} ===\n{file_content}")
            
            final_content = "\n\n".join(clipboard_content)
            self.root.clipboard_append(final_content.strip())
            self.root.update()
            self.update_status(f"已分别复制 {len(self.file_tabs)} 个文件", "#28a745")
        except Exception as e:
            self.update_status(f"复制失败: {str(e)}", "#dc3545")
    
    def update_status(self, message, color="#495057"):
        self.status_label.config(text=message, foreground=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyApp(root)
    root.mainloop()