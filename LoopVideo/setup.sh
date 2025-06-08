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

# Cập nhật pip nếu cần
pip install --upgrade pip

# Cài các thư viện cần thiết
pip install opencv-python pillow

if [ $? -ne 0 ]; then
  echo "❌ Lỗi khi cài thư viện!"
  deactivate
  exit 1
fi

echo "✅ Đã cài xong thư viện opencv-python và pillow."

# Gõ tên file Python muốn chạy (có thể sửa tên file nếu không phải app.py)
echo "▶️ Đang chạy app.py..."
python videoLoop.py
