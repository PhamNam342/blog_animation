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
<img width="1911" height="1004" alt="Screenshot 2025-09-03 131520" src="https://github.com/user-attachments/assets/16b43b2b-ceb0-4608-8877-ab2f05f6d772" />
<img width="1891" height="1003" alt="Screenshot 2025-09-03 131548" src="https://github.com/user-attachments/assets/e9cb8c9c-6901-4dc5-8cae-95b535c215eb" />
<img width="1907" height="1006" alt="Screenshot 2025-09-03 131602" src="https://github.com/user-attachments/assets/ba291701-028f-4693-b726-20559e54e3c6" />
<img width="1881" height="1007" alt="Screenshot 2025-09-03 131652" src="https://github.com/user-attachments/assets/b44bfbf2-a51b-4ab0-b9a3-1c841bceaf50" />
<img width="1903" height="994" alt="Screenshot 2025-09-03 131710" src="https://github.com/user-attachments/assets/58f246e8-7762-4d52-85bd-97f9c771bc6e" />

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
-  Render images with AI models -
-  Download or post images directly to the blog
  
    ---

   ## 📂 Project Structure
```
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
```

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

---

### 1️⃣ Clone the repository
```
git clone https://github.com/PhamNam342/nam_blog.git cd nam_blog
```

--- 

### 2️⃣ Install dependencies
```
pip install -r requirements.txt
```

---


### 3️⃣ Configure PostgreSQL Database
```
Create database: nam_blog Add user and password, for example: 
DB_CONFIG = { 'dbname': 'nam_blog', 
                'user': 'postgres',     
                'password': 'your_password', 
                'host': 'localhost', 'port': '5432'
                } Create required tables: users, posts, comments, likes, avatars.
```

                --- 

                
### 4️⃣ Configure Gmail
```
MAIL_USERNAME = 'your_email@gmail.com' 
MAIL_PASSWORD = 'your_app_password' # Use App Password 
```

--- 


### 5️⃣ Run Flask Server
```
python app.py
Open browser: http://127.0.0.1:5000/
```

---

### 🔧 Running AI Models
Example of rendering an image:
from PIL import Image
import onnxruntime as ort
import numpy as np

---


## 🗄 Database Schema

### Main Tables

- **users**: Stores user authentication and profile information  
- **posts**: Stores blog posts with content, images, and metadata  
- **comments**: Stores comments for each post  
- **likes**: Tracks likes on posts  
- **commnent_likes**: Tracks likes on comments  
- **follows**: Track follow

### Key Fields

#### Users Table (`users`)
| Field        | Type    | Description                       |
|-------------|---------|------------------------------------|
| id          | SERIAL  | Primary key                        |
| username    | TEXT    | Unique username                    |
| email       | TEXT    | Gmail account used for login       |
| password    | TEXT    | Hashed password (if not OAuth)     |
| avatar      | TEXT    | URL/path to user avatar            |
| created_at  | TIMESTAMP | Account creation time            |

#### Posts Table (`posts`)
| Field       | Type      | Description                          |
|------------|-----------|---------------------------------------|
| id         | SERIAL    | Primary key                           |
| user_id    | INTEGER   | Foreign key to `users.id`             |
| title      | TEXT      | Blog post title                       |
| caption    | TEXT      | Blog post content                     |
| image_path | TEXT      | Path to uploaded or AI rendered image |
| created_at | TIMESTAMP | Post creation time                    |

#### Comments Table (`comments`)
| Field      | Type    | Description                        |
|------------|---------|------------------------------------|
| id         | SERIAL  | Primary key                        |
| post_id    | INTEGER | Foreign key to `posts.id`          |
| user_id    | INTEGER | Foreign key to `users.id`          |
| content    | TEXT    | Comment content                    |
| created_at | TIMESTAMP | Comment creation time            |

#### Likes Table (`likes`)
| Field    | Type    | Description                         |
|----------|---------|-------------------------------------|
| id       | SERIAL  | Primary key                         |
| post_id  | INTEGER | Foreign key to `posts.id`           |
| user_id  | INTEGER | Foreign key to `users.id`           |

#### Comment_likes
| Field      | Type    | Description                         |
|------------|---------|-------------------------------------|
| user_id    | INTEGER | Foreign key to `users.id`           |
| comment_id | INTEGER | Foreign key to `comment.id`         |

#### follows
| Field      | Type    | Description                         |
|------------|---------|-------------------------------------|
| follower_id| INTEGER | Foreign key to `users.id`           |
| followed_id | INTEGER| Foreign key to `users.id`           |

# Load mmodel
for example:
model = ort.InferenceSession("models/AnimeGANv2_Paprika.onnx")

---

# Process input image and run inference
# ...
Users can upload images via the web interface, select a model, render, and download or post the result.

### 🤝 Contributing
Fork the repository
```
Create a feature branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add amazing feature'

Push: git push origin feature/amazing-feature

Open a Pull Request
```

---

### Flask Configuration
```
app.secret_key = 'your_secret_key'  # Change for production
```

---

### 📄 License
Personal / Academic project.

---

### 👥 Authors
Pham Nam – Developer & Student
Email: nam1234kan@gmail.com

---

### 🙏 Acknowledgments
```
Gmail API for email verification
ONNX Runtime & open-source AI models
Flask & Python libraries
Hanoi University of Science and Technology
Real estate data sources for Hanoi market
Open source libraries and frameworks used

**For questions or support, please contact the development team or create an issue in the repository.**
