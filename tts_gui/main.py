import tkinter as tk
from tkinter import ttk, filedialog
import os
from pathlib import Path
import pygame
from tkinter import messagebox

class TTSVersionSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("TTS版本选择器")
        
        # 初始化pygame音频
        pygame.mixer.init()
        
        # 设置窗口大小和位置
        window_width = 1000
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面组件
        self.create_widgets()
        
        # 初始化变量
        self.current_audio_dir = None
        self.current_audio_files = []
        self.current_index = 0
        self.selected_versions = {}  # 存储选择的版本
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开音频目录", command=self.open_audio_dir)
        file_menu.add_command(label="保存选择结果", command=self.save_selections)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_widgets(self):
        """创建主界面组件"""
        # 顶部控制区域
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 打开目录按钮
        self.open_btn = ttk.Button(control_frame, text="打开音频目录", command=self.open_audio_dir)
        self.open_btn.grid(row=0, column=0, padx=5)
        
        # 当前文件信息
        self.file_label = ttk.Label(control_frame, text="未加载音频文件")
        self.file_label.grid(row=0, column=1, padx=20)
        
        # 播放控制区域
        play_frame = ttk.Frame(control_frame)
        play_frame.grid(row=0, column=2, padx=20)
        
        self.prev_btn = ttk.Button(play_frame, text="上一个", command=self.play_previous)
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        self.play_btn = ttk.Button(play_frame, text="播放", command=self.toggle_play)
        self.play_btn.grid(row=0, column=1, padx=5)
        
        self.next_btn = ttk.Button(play_frame, text="下一个", command=self.play_next)
        self.next_btn.grid(row=0, column=2, padx=5)
        
        # 版本选择区域
        self.version_frame = ttk.LabelFrame(self.main_frame, text="版本选择", padding="10")
        self.version_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 创建版本按钮
        self.version_buttons = {}
        versions = ['_a', '_b', '_c', '_d']
        for i, version in enumerate(versions):
            btn = ttk.Button(self.version_frame, text=f"版本{version}", 
                           command=lambda v=version: self.select_version(v))
            btn.grid(row=0, column=i, padx=10, pady=5)
            self.version_buttons[version] = btn
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def open_audio_dir(self):
        """打开音频目录"""
        directory = filedialog.askdirectory(title="选择音频目录")
        if directory:
            self.current_audio_dir = Path(directory)
            self.load_audio_files()
            
    def load_audio_files(self):
        """加载音频文件"""
        if not self.current_audio_dir:
            return
            
        # 获取所有wav文件并按名称排序
        self.current_audio_files = sorted(
            [f for f in self.current_audio_dir.glob('*.wav')],
            key=lambda x: x.stem
        )
        
        if not self.current_audio_files:
            messagebox.showwarning("警告", "所选目录中没有找到WAV文件")
            return
            
        self.current_index = 0
        self.update_file_info()
        self.status_var.set(f"已加载 {len(self.current_audio_files)} 个音频文件")
        
    def update_file_info(self):
        """更新文件信息显示"""
        if 0 <= self.current_index < len(self.current_audio_files):
            current_file = self.current_audio_files[self.current_index]
            self.file_label.config(text=f"当前文件: {current_file.name}")
            
            # 更新版本按钮状态
            for version, btn in self.version_buttons.items():
                if current_file.stem.endswith(version):
                    btn.state(['pressed'])
                else:
                    btn.state(['!pressed'])
                    
    def toggle_play(self):
        """播放/暂停当前音频"""
        if not self.current_audio_files:
            return
            
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_btn.config(text="播放")
        else:
            current_file = self.current_audio_files[self.current_index]
            pygame.mixer.music.load(str(current_file))
            pygame.mixer.music.play()
            self.play_btn.config(text="暂停")
            
    def play_next(self):
        """播放下一个音频"""
        if not self.current_audio_files:
            return
            
        pygame.mixer.music.stop()
        self.current_index = (self.current_index + 1) % len(self.current_audio_files)
        self.update_file_info()
        self.toggle_play()
        
    def play_previous(self):
        """播放上一个音频"""
        if not self.current_audio_files:
            return
            
        pygame.mixer.music.stop()
        self.current_index = (self.current_index - 1) % len(self.current_audio_files)
        self.update_file_info()
        self.toggle_play()
        
    def select_version(self, version):
        """选择当前文件的最佳版本"""
        if not self.current_audio_files:
            return
            
        current_file = self.current_audio_files[self.current_index]
        base_name = current_file.stem.rsplit('_', 1)[0]
        
        # 更新选择
        self.selected_versions[base_name] = version
        self.status_var.set(f"已选择 {base_name} 的最佳版本: {version}")
        
    def save_selections(self):
        """保存选择结果"""
        if not self.selected_versions:
            messagebox.showwarning("警告", "没有选择任何版本")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            title="保存选择结果"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for base_name, version in self.selected_versions.items():
                    f.write(f"{base_name}{version}\n")
            messagebox.showinfo("成功", "选择结果已保存")
            
    def show_help(self):
        """显示使用说明"""
        help_text = """
使用说明：
1. 点击"打开音频目录"选择包含TTS生成音频的文件夹
2. 使用播放控制按钮浏览不同的音频文件
3. 点击版本按钮选择当前文件的最佳版本
4. 完成所有选择后，点击"保存选择结果"导出结果

快捷键：
- 空格键：播放/暂停
- 左箭头：上一个文件
- 右箭头：下一个文件
"""
        messagebox.showinfo("使用说明", help_text)
        
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("300x200")
        
        # 设置模态窗口
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 居中显示
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - about_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        # 添加内容
        ttk.Label(about_window, 
                 text="TTS版本选择器\n版本 1.0\n\n用于选择TTS生成的最佳音频版本", 
                 justify=tk.CENTER, padding=20).pack(expand=True)

def main():
    root = tk.Tk()
    app = TTSVersionSelector(root)
    root.mainloop()

if __name__ == "__main__":
    main() 