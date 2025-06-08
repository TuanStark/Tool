import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import cv2
from PIL import Image, ImageTk
import threading
import os
import time
from tkinter.font import Font

class VideoLooperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎞️ Video Looper")
        self.root.geometry("800x750")
        self.root.configure(bg='#f0f0f0')

        # Định nghĩa fonts và styles
        self.title_font = Font(family="Helvetica", size=16, weight="bold")
        self.button_font = Font(family="Helvetica", size=11)
        self.label_font = Font(family="Helvetica", size=10)
        
        # Định nghĩa màu sắc
        self.primary_color = '#2196f3'
        self.secondary_color = '#f0f0f0'
        self.accent_color = '#1976d2'

        self.video_path = None
        self.cap = None
        self.frame_rate = 30
        self.frame_count = 0
        self.is_playing = False
        self.play_thread = None
        self.exporting = False

        # Configure style
        style = ttk.Style()
        style.configure('Custom.TButton', 
                       padding=10, 
                       font=self.button_font)
        style.configure('Custom.TFrame', 
                       background=self.secondary_color)
        style.configure('Custom.Horizontal.TProgressbar',
                       background=self.primary_color)

        self.setup_ui()

    def setup_ui(self):
        # Main container với padding và màu nền
        main_frame = ttk.Frame(self.root, padding="20", style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Video Looper",
            font=self.title_font,
            bg=self.secondary_color,
            fg=self.primary_color
        )
        title_label.pack(pady=(0, 20))

        # Button frame
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        select_btn = ttk.Button(
            button_frame,
            text="📂 Chọn Video",
            command=self.load_video,
            style='Custom.TButton'
        )
        select_btn.pack(pady=5, padx=20, fill=tk.X)

        # File path label với style mới
        self.label_path = tk.Label(
            main_frame,
            text="Chưa chọn video",
            font=self.label_font,
            bg=self.secondary_color,
            fg='#666666'
        )
        self.label_path.pack(pady=(5, 15))

        # Canvas với border và shadow effect
        canvas_frame = tk.Frame(
            main_frame,
            bg='white',
            bd=1,
            relief=tk.SOLID
        )
        canvas_frame.pack(pady=10, padx=20)
        
        self.canvas = tk.Label(canvas_frame, bg='black')
        self.canvas.pack(padx=2, pady=2)

        # Control buttons với layout cải thiện
        control_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        control_frame.pack(fill=tk.X, pady=20)
        
        # Tạo các nút với style mới
        buttons = [
            ("▶️ Xem Loop", self.start_loop),
            ("⏹️ Dừng", self.stop_loop),
            ("💾 Export Video", self.export_loop)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                control_frame,
                text=text,
                command=command,
                style='Custom.TButton'
            )
            btn.pack(side=tk.LEFT, padx=10, expand=True)

        # Progress bar với style mới
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=(20, 0), padx=20)

    def load_video(self):
        self.stop_loop()
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("All files", "*.*")],
            title="Chọn video"
        )
        if not self.video_path:
            messagebox.showinfo("Thông báo", "Không chọn video nào.")
            return

        if not os.path.isfile(self.video_path):
            messagebox.showerror("Lỗi", f"File không tồn tại: {self.video_path}")
            return

        print(f"Đường dẫn: {self.video_path}")
        print(f"Các file trong thư mục: {os.listdir(os.path.dirname(self.video_path))}")

        self.label_path.config(text=os.path.basename(self.video_path))
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", f"Không mở được video:\n{self.video_path}")
            self.cap = None
            return

        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.frame_count == 0 or self.frame_rate == 0:
            messagebox.showerror("Lỗi", "Video không hợp lệ hoặc không chứa frame.")
            self.cap.release()
            self.cap = None
            return

        duration = self.frame_count / self.frame_rate
        messagebox.showinfo("Thông tin", f"Video: {os.path.basename(self.video_path)}\nThời lượng: {duration:.2f} giây")

    def start_loop(self):
        if self.is_playing or not self.cap:
            return

        self.is_playing = True
        self.play_thread = threading.Thread(
            target=self.play_loop,
            args=(0, self.frame_count - 1),
            daemon=True
        )
        self.play_thread.start()

    def play_loop(self, start_frame, end_frame):
        while self.is_playing:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            for i in range(start_frame, end_frame + 1):
                if not self.is_playing:
                    break
                ret, frame = self.cap.read()
                if not ret:
                    break
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img = img.resize((400, int(400 * frame.shape[0] / frame.shape[1])), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.canvas.config(image=photo)
                self.canvas.image = photo
                self.canvas.update()
                time.sleep(1.0 / self.frame_rate)

    def stop_loop(self):
        self.is_playing = False
        if self.play_thread:
            self.play_thread.join()
        self.canvas.config(image='')
        self.canvas.image = None

    def export_loop(self):
        if not self.cap:
            messagebox.showerror("Lỗi", "Chưa chọn video.")
            return

        if self.exporting:
            messagebox.showinfo("Thông báo", "Đang export, vui lòng chờ.")
            return

        loop_minutes = simpledialog.askfloat(
            "Thời gian lặp",
            "Nhập thời gian lặp (phút):",
            minvalue=0.1
        )
        if not loop_minutes:
            return

        loop_duration = self.frame_count / self.frame_rate
        total_loops = int((loop_minutes * 60) / loop_duration)
        if total_loops < 1:
            messagebox.showerror("Lỗi", "Thời gian quá ngắn để lặp.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")],
            title="Lưu video loop"
        )
        if not save_path:
            return

        self.exporting = True
        threading.Thread(
            target=self._export_loop,
            args=(0, self.frame_count - 1, total_loops, save_path),
            daemon=True
        ).start()

    def _export_loop(self, start_frame, end_frame, total_loops, save_path):
        self.progress['value'] = 0
        self.progress['maximum'] = total_loops * (end_frame - start_frame + 1)

        h, w = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(save_path, fourcc, self.frame_rate, (w, h))

        if not out.isOpened():
            messagebox.showerror("Lỗi", "Không thể tạo file output. Vui lòng kiểm tra định dạng hoặc quyền ghi file.")
            self.exporting = False
            return

        try:
            for loop in range(total_loops):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                for i in range(start_frame, end_frame + 1):
                    ret, frame = self.cap.read()
                    if not ret:
                        messagebox.showerror("Lỗi", f"Lỗi khi đọc frame {i} trong loop {loop + 1}.")
                        out.release()
                        self.exporting = False
                        return
                    out.write(frame)
                    self.progress['value'] += 1
                    self.progress.update()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi export: {str(e)}")
            out.release()
            self.exporting = False
            return

        out.release()
        self.progress['value'] = 0
        self.exporting = False
        if os.path.getsize(save_path) > 0:
            messagebox.showinfo("✅ Thành công", f"Đã xuất video loop {total_loops} lần tại:\n{save_path}")
        else:
            messagebox.showerror("Lỗi", "File output rỗng hoặc bị hỏng.")

    def stop(self):
        self.is_playing = False
        self.exporting = False
        if self.play_thread:
            self.play_thread.join()
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoLooperApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()