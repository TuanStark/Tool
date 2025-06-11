import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import cv2
from PIL import Image, ImageTk
import threading
import os
import time
import subprocess
import tempfile
import shutil
from tkinter.font import Font
from moviepy.editor import VideoFileClip, concatenate_videoclips

class VideoLooperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎞️ Video Looper")
        self.root.geometry("800x750")
        self.root.configure(bg='#f0f0f0')

        self.title_font = Font(family="Helvetica", size=16, weight="bold")
        self.button_font = Font(family="Helvetica", size=11)
        self.label_font = Font(family="Helvetica", size=10)
        
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
        self.export_progress_thread = None
        self.export_stop_flag = False

        style = ttk.Style()
        style.configure('Custom.TButton', padding=10, font=self.button_font)
        style.configure('Custom.TFrame', background=self.secondary_color)
        style.configure('Custom.Horizontal.TProgressbar', background=self.primary_color)

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20", style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            main_frame,
            text="Video Looper",
            font=self.title_font,
            bg=self.secondary_color,
            fg=self.primary_color
        )
        title_label.pack(pady=(0, 20))

        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        select_btn = ttk.Button(
            button_frame,
            text="📂 Chọn Video",
            command=self.load_video,
            style='Custom.TButton'
        )
        select_btn.pack(pady=5, padx=20, fill=tk.X)

        self.label_path = tk.Label(
            main_frame,
            text="Chưa chọn video",
            font=self.label_font,
            bg=self.secondary_color,
            fg='#666666'
        )
        self.label_path.pack(pady=(5, 15))

        canvas_frame = tk.Frame(
            main_frame,
            bg='white',
            bd=1,
            relief=tk.SOLID
        )
        canvas_frame.pack(pady=10, padx=20)
        
        self.canvas = tk.Label(canvas_frame, bg='black')
        self.canvas.pack(padx=2, pady=2)

        control_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        control_frame.pack(fill=tk.X, pady=20)
        
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

        # Tạo thư mục tạm
        temp_dir = tempfile.mkdtemp()
        
        # Hiển thị thông tin export
        self.exporting = True
        self.export_stop_flag = False
        self.root.title("🎞️ Video Looper - Đang export...")
        
        # Hiển thị label thông tin export
        self.export_info_label = tk.Label(
            self.root,
            text="Đang chuẩn bị export video...",
            font=self.label_font,
            bg='#fff3cd',
            fg='#856404',
            padx=10,
            pady=5,
            relief=tk.RIDGE
        )
        self.export_info_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        
        # Cập nhật giao diện
        self.progress['value'] = 0
        self.root.update()
        
        # Bắt đầu luồng export
        threading.Thread(
            target=self._export_loop_ffmpeg,
            args=(total_loops, save_path, temp_dir),
            daemon=True
        ).start()

    def _export_loop_ffmpeg(self, total_loops, save_path, temp_dir):
        try:
            # Tạo danh sách tệp tạm
            temp_files = []
            
            # Cập nhật label
            if hasattr(self, 'export_info_label'):
                self.export_info_label.config(text="Đang tạo file tạm...")
                self.root.update_idletasks()
            
            # Tạo file tạm để nối
            temp_list_file = os.path.join(temp_dir, "file_list.txt")
            with open(temp_list_file, "w") as f:
                for i in range(total_loops):
                    f.write(f"file '{self.video_path}'\n")
            
            # Cập nhật label
            if hasattr(self, 'export_info_label'):
                self.export_info_label.config(text="Đang export video...")
                self.root.update_idletasks()
            
            # Thiết lập thanh tiến trình
            self.progress['value'] = 0
            self.progress['maximum'] = 100
            
            # Bắt đầu luồng theo dõi tiến trình
            self.export_progress_thread = threading.Thread(
                target=self._monitor_ffmpeg_progress,
                args=(save_path,),
                daemon=True
            )
            self.export_progress_thread.start()
            
            # Chạy ffmpeg để nối video
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
                "-i", temp_list_file, "-c", "copy", save_path
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # Đợi quá trình hoàn thành
            process.communicate()
            
            # Đánh dấu kết thúc
            self.export_stop_flag = True
            if self.export_progress_thread:
                self.export_progress_thread.join(timeout=1.0)
            
            # Kiểm tra kết quả
            if process.returncode != 0:
                messagebox.showerror("Lỗi", "Lỗi khi export video với ffmpeg")
                if os.path.exists(save_path):
                    os.remove(save_path)
            else:
                # Cập nhật tiến trình hoàn thành
                self.progress['value'] = 100
                if hasattr(self, 'export_info_label'):
                    self.export_info_label.config(text="Hoàn thành export video!")
                    self.root.update_idletasks()
                
                # Hiển thị thông báo thành công
                messagebox.showinfo("✅ Thành công", f"Đã xuất video loop {total_loops} lần tại:\n{save_path}")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi export: {str(e)}")
        
        finally:
            # Dọn dẹp
            self.export_stop_flag = True
            self.exporting = False
            self.root.title("🎞️ Video Looper")
            
            # Xóa label thông tin
            if hasattr(self, 'export_info_label'):
                self.export_info_label.destroy()
            
            # Xóa thư mục tạm
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            # Reset thanh tiến trình
            self.progress['value'] = 0

    def _monitor_ffmpeg_progress(self, output_file):
        """Theo dõi tiến trình ffmpeg bằng cách kiểm tra kích thước file đầu ra"""
        if not os.path.exists(os.path.dirname(output_file)):
            return
            
        # Lấy kích thước video gốc
        original_size = os.path.getsize(self.video_path)
        expected_size = original_size * 0.95  # Dự đoán kích thước
        
        # Đợi cho file đầu ra được tạo
        start_time = time.time()
        while not os.path.exists(output_file) and time.time() - start_time < 5:
            time.sleep(0.5)
            
        if not os.path.exists(output_file):
            return
            
        # Theo dõi kích thước file
        last_size = 0
        stalled_count = 0
        
        while not self.export_stop_flag:
            try:
                if os.path.exists(output_file):
                    current_size = os.path.getsize(output_file)
                    
                    # Tính phần trăm tiến trình
                    progress = min(99, int((current_size / expected_size) * 100))
                    
                    # Kiểm tra nếu kích thước không thay đổi
                    if current_size == last_size:
                        stalled_count += 1
                    else:
                        stalled_count = 0
                        last_size = current_size
                    
                    # Nếu kích thước không thay đổi trong 10 lần kiểm tra, tăng tiến trình
                    if stalled_count > 10:
                        progress = min(99, progress + 1)
                        stalled_count = 0
                    
                    # Cập nhật thanh tiến trình
                    self.progress['value'] = progress
                    
                    # Cập nhật tiêu đề và label thông tin
                    self.root.title(f"🎞️ Video Looper - Đang export... {progress}%")
                    if hasattr(self, 'export_info_label'):
                        self.export_info_label.config(text=f"Đang export video... {progress}%")
                    
                    self.root.update_idletasks()
            except:
                pass
                
            time.sleep(0.5)

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