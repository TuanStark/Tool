#!/bin/bash

echo "🚀 Tạo virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
  echo "❌ Không tạo được virtual environment. Đảm bảo đã cài python3-venv!"
  exit 1
fi

echo "✅ Đã tạo venv tại ./venv"

echo "🔁 Kích hoạt venv và cài đặt thư viện..."
source venv/bin/activate

if [ $? -ne 0 ]; then
  echo "❌ Không thể kích hoạt virtual environment!"
  exit 1
fi

# Cập nhật pip nếu cần
pip install --upgrade pip

if [ $? -ne 0 ]; then
  echo "❌ Lỗi khi cập nhật pip!"
  deactivate
  exit 1
fi

# Cài đặt ffmpeg nếu chưa có (cho Ubuntu/Debian)
if ! command -v ffmpeg &> /dev/null; then
  echo "📦 Cài đặt ffmpeg..."
  sudo apt-get update && sudo apt-get install -y ffmpeg
  if [ $? -ne 0 ]; then
    echo "❌ Lỗi khi cài đặt ffmpeg! Vui lòng cài thủ công."
    deactivate
    exit 1
  fi
  echo "✅ Đã cài ffmpeg."
else
  echo "✅ ffmpeg đã được cài đặt."
fi

# Xóa thư mục venv hiện tại và tạo mới để tránh lỗi
echo "🔄 Tạo lại virtual environment sạch..."
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Cài các thư viện cần thiết
echo "📦 Cài đặt các thư viện Python..."
pip install opencv-python pillow
pip install imageio==2.31.1
pip install decorator==4.4.2
pip install moviepy==1.0.3

if [ $? -ne 0 ]; then
  echo "❌ Lỗi khi cài thư viện! Thử cài lại với phiên bản khác..."
  pip install moviepy==1.0.2
  
  if [ $? -ne 0 ]; then
    echo "❌ Vẫn không thể cài đặt thư viện!"
    deactivate
    exit 1
  fi
fi

# Kiểm tra cài đặt moviepy.editor
echo "🔍 Kiểm tra cài đặt moviepy.editor..."
python -c "from moviepy.editor import VideoFileClip; print('✅ Moviepy đã được cài đặt đúng cách')" || {
  echo "❌ Vẫn có lỗi với moviepy.editor!"
  echo "Thử cài đặt phiên bản cụ thể của các thư viện phụ thuộc..."
  pip install numpy==1.19.5 
  pip install decorator==4.4.2
  pip install imageio==2.9.0
  pip install moviepy==1.0.3
}

echo "✅ Đã cài xong các thư viện cần thiết."

# Kiểm tra file videoLoop.py tồn tại
if [ ! -f "videoLoop.py" ]; then
  echo "❌ Không tìm thấy file videoLoop.py!"
  echo "Vui lòng đặt script này cùng thư mục với videoLoop.py"
  deactivate
  exit 1
fi

# Chạy chương trình
echo "🎬 ĐANG CHẠY CHƯƠNG TRÌNH VIDEOLOOP.PY..."
echo "----------------------------------------"
python videoLoop.py

# Kiểm tra kết quả chạy chương trình
if [ $? -ne 0 ]; then
  echo "❌ Lỗi khi chạy videoLoop.py!"
  echo "Vui lòng kiểm tra lại file videoLoop.py"
  deactivate
  exit 1
fi

# Kết thúc
echo "----------------------------------------"
echo "✅ Đã chạy xong chương trình videoLoop.py"
deactivate