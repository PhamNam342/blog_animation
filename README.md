# 🌟 Nam Blogee - AI Blog Platform with Image Rendering

![GitHub stars](https://img.shields.io/github/stars/PhamNam342/nam_blog?style=social)
![GitHub forks](https://img.shields.io/github/forks/PhamNam342/nam_blog?style=social)
![GitHub issues](https://img.shields.io/github/issues/PhamNam342/nam_blog)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-2.3-lightgrey)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Users](https://img.shields.io/badge/users-120-blue)
![Posts](https://img.shields.io/badge/posts-250-orange)

---

## 📝 Giới thiệu
**Nam Blogee** là một **web blog hiện đại** kết hợp **AI image rendering**, cho phép người dùng:  

- Đăng nhập và xác thực bằng **Gmail**.  
- Tạo, chỉnh sửa, đăng và xoá các bài blog.  
- Like và comment bài viết.  
- Tìm kiếm người dùng khác.  
- Render hình ảnh sang phong cách **anime/hoạt hình** với AI models.  
- Lưu ảnh về máy hoặc đăng trực tiếp lên blog.  

---

## 🎬 Demo Web
**Giao diện web & AI Image Rendering:**

![Demo Blog](https://user-images.githubusercontent.com/yourusername/demo-blog.gif)

> GIF minh họa: đăng nhập, tạo bài viết, render ảnh anime và lưu về máy.

---

## ⚡ Tính năng nổi bật

### 👤 Quản lý tài khoản
- Đăng nhập/đăng ký bằng Gmail.  
- Xác thực email để bảo mật.  
- Quản lý thông tin cá nhân.  

### ✍️ Blog
- Tạo bài viết với hình ảnh.  
- Like & Comment bài viết.  
- Tìm kiếm và xem profile người dùng khác.  

### 🎨 AI Image Rendering
Sử dụng các models `.onnx` để biến hình ảnh thành anime/hoạt hình:  

| Model | Phong cách |
|-------|------------|
| `AnimeGANv2_Paprika.onnx` 🌸 | Anime Paprika |
| `AnimeGANv2_Shinkai.onnx` 🌊 | Phong cách Shinkai |
| `AnimeGANv3_PortraitSketch_25.onnx` ✏️ | Sketch chân dung |
| `generator_hayao.onnx` 🎬 | Hayao Miyazaki |

### 💾 Quản lý hình ảnh
- Upload ảnh từ máy.  
- Render ảnh với AI models.  
- Lưu ảnh về máy hoặc đăng trực tiếp lên blog.  

---

## 📂 Cấu trúc dự án
nam_blog/
├─ models/ # Chứa các AI models (.onnx)
│ ├─ AnimeGANv2_Paprika.onnx
│ ├─ AnimeGANv2_Shinkai.onnx
│ ├─ AnimeGANv3_PortraitSketch_25.onnx
│ └─ generator_hayao.onnx
├─ static/ # CSS, JS, hình ảnh tĩnh
│ ├─ avatar/
│ ├─ images/
│ ├─ script.js
│ └─ style.css
├─ templates/ # Các file HTML
│ ├─ account.html
│ ├─ index.html
│ ├─ login.html
│ ├─ picture.html
│ ├─ register.html
│ └─ verify.html
└─ app.py # File chính Flask
---

## 🛠️ Công nghệ sử dụng
- **Python 3.x** & **Flask**
- **ONNX Runtime** (chạy AI models)
- **HTML / CSS / JavaScript**
- **SMTP / Gmail API** cho xác thực email

---

## 🚀 Cài đặt & chạy dự án

1. **Clone repository**
```bash
git clone https://github.com/PhamNam342/nam_blog.git
cd nam_blog
Cài đặt dependencies

bash
Copy code
pip install -r requirements.txt
Chạy web

bash
Copy code
python app.py
Mở trình duyệt
Truy cập: http://127.0.0.1:5000/
