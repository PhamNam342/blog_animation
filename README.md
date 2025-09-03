# 🌟 Nam Blogee - AI Blog Platform with Image Rendering

![GitHub stars](https://img.shields.io/github/stars/PhamNam342/nam_blog?style=social)
![GitHub forks](https://img.shields.io/github/forks/PhamNam342/nam_blog?style=social)
![GitHub issues](https://img.shields.io/github/issues/PhamNam342/nam_blog)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-2.3-lightgrey)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

---

## 📝 Introduction
**Nam Blogee** is a modern **web blog** platform combined with **AI image rendering**, allowing users to:

- Log in and verify their accounts via **Gmail**.  
- Create, post, edit, and delete **blog posts**.  
- Like and comment on posts.  
- Search for other users by username.  
- Convert images into **anime/cartoon style** using AI models.  
- Download images or post them directly to the blog.  

---

## 🎬 Web Demo
**Web interface & AI Image Rendering Demo:**

![Demo Blog](https://user-images.githubusercontent.com/yourusername/demo-blog.gif)

> The GIF shows login, creating a post, rendering an image to anime style, and downloading it.

---

## ⚡ Main Features

### 👤 Account Management
- Register/Login via Gmail  
- Email verification  
- User profile management  

### ✍️ Blog
- Create posts with images  
- Like & Comment on posts  
- Search and view other users’ profiles  

### 🎨 AI Image Rendering
Use `.onnx` models to transform images into anime/cartoon styles:

| Model | Style |
|-------|-------|
| `AnimeGANv2_Paprika.onnx` 🌸 | Anime Paprika |
| `AnimeGANv2_Shinkai.onnx` 🌊 | Shinkai style |
| `AnimeGANv3_PortraitSketch_25.onnx` ✏️ | Portrait Sketch |
| `generator_hayao.onnx` 🎬 | Hayao Miyazaki style |

### 💾 Image Management
- Upload images from your device  
- Render images with AI models  
- Download or post images directly to the blog  

---

## 📂 Project Structure
nam_blog/
├─ models/ # Contains AI models (.onnx)
├─ static/ # CSS, JS, static images
│ ├─ avatar/
│ ├─ images/
│ ├─ script.js
│ └─ style.css
├─ templates/ # HTML templates
│ ├─ account.html
│ ├─ index.html
│ ├─ login.html
│ ├─ picture.html
│ ├─ register.html
│ └─ verify.html
├─ app.py # Main Flask application
└─ requirements.txt # Python dependencies

yaml
Copy code

---

## 🛠️ Technologies Used
- **Python 3.8+** & **Flask**  
- **ONNX Runtime** (for AI models)  
- **Pillow & OpenCV** (image processing)  
- **NumPy** (array processing)  
- **PostgreSQL** (database)  
- **Flask-Mail** (Gmail email verification)  
- **Werkzeug** (utilities, secure_filename)  

---

## 🚀 Installation & Running

### 1️⃣ Clone the repository
```bash
git clone https://github.com/PhamNam342/nam_blog.git
cd nam_blog
2️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
3️⃣ Configure PostgreSQL Database
Create database: nam_blog

Add user and password, for example:

python
Copy code
DB_CONFIG = {
    'dbname': 'nam_blog',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
Create required tables: users, posts, comments, likes, avatars.

Note: Provide SQL scripts or ORM migration for easy database setup.

4️⃣ Configure Gmail
Update Gmail account info in app.py or config.py:

python
Copy code
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'your_app_password'  # Use App Password
5️⃣ Run Flask Server
bash
Copy code
python app.py
Open browser: http://127.0.0.1:5000/

🔧 Running AI Models
Example of rendering an image:

python
Copy code
from PIL import Image
import onnxruntime as ort
import numpy as np

# Load model
model = ort.InferenceSession("models/AnimeGANv2_Paprika.onnx")

# Process input image and run inference
# ...
Users can upload images via the web interface, select a model, render, and download or post the result.

🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add amazing feature'

Push: git push origin feature/amazing-feature

Open a Pull Request

📄 License
Personal / Academic project.

👥 Authors
Pham Nam – Developer & Student
Email: your_email@gmail.com

🙏 Acknowledgments
Gmail API for email verification

ONNX Runtime & open-source AI models

Flask & Python libraries

Web & AI tutorials on the Internet
