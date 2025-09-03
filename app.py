from functools import wraps
import random
import string
from cv2 import FileStorage
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, session, url_for
import io
import os
from PIL import Image
from flask_mail import Mail, Message
import numpy as np
import onnxruntime as ort
import psycopg2
from werkzeug.utils import secure_filename
MAX_SIDE = int(os.environ.get("MAX_SIDE", 720)) 
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp"}
MODEL_MAP = {
    "hayao": "models/generator_hayao.onnx",
    "shinkai": "models/AnimeGANv2_Shinkai.onnx",
    "portrait": "models/AnimeGANv3_PortraitSketch_25.onnx",
    "paprika":"models/AnimeGANv2_Paprika.onnx"
}

providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
SESSIONS = {}
for key, path in MODEL_MAP.items():
    if os.path.exists(path):
        try:
            SESSIONS[key] = ort.InferenceSession(path, providers=providers)
            print(f"[INFO] Loaded {key}: {path}, input shape = {SESSIONS[key].get_inputs()[0].shape}")
        except Exception as e:
            print(f"[WARN] Không load được {key} ({path}): {e}")

def get_session_for(model_key: str):
    return SESSIONS.get(model_key) or SESSIONS.get("hayao")

app = Flask(__name__)
app.config["SECRET_KEY"]="Namdz"
DB_CONFIG = {
    'dbname': 'animation',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

# Thêm cấu hình email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nam1234kan@gmail.com'
app.config['MAIL_PASSWORD'] = 'vtxuvfxjtpuwjbji'  # App password, không phải password Gmail thường

mail = Mail(app)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return decorated_function
# USER INTERFACE
@app.route('/index')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session.get('user_id')

    cur.execute("""
        SELECT p.id, u.full_name, p.image_path, p.caption, p.created_at 
        FROM public.posts p 
        JOIN users u ON u.id = p.user_id
        ORDER BY p.created_at DESC
    """)
    rows = cur.fetchall()
    posts = []

    for row in rows:
        post_id = row[0]
        full_name = row[1]
        image = row[2]
        content = row[3]
        created_at = row[4]

        # Kiểm tra like của user
        cur.execute("SELECT * FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
        like_blog = cur.fetchone()
        liked = True if like_blog else False

        # Lấy comment
        cur.execute("""
            SELECT c.id,u.username, u.avatar, c.content ,c.created_at
            FROM comments c
            JOIN users u ON u.id = c.user_id
            WHERE c.post_id = %s
        """, (post_id,))
        comments = []
        for c in cur.fetchall():
            comment_id = c[0]
            username = c[1]
            avatar = c[2]
            content = c[3]
            created_at = c[4]

        # Kiểm tra xem user đã like comment chưa
            cur.execute("SELECT 1 FROM comment_likes WHERE user_id=%s AND comment_id=%s", (user_id, comment_id))
            liked = True if cur.fetchone() else False

        # Lấy số lượng like của comment
            cur.execute("SELECT COUNT(*) FROM comment_likes WHERE comment_id=%s", (comment_id,))
            like_count = cur.fetchone()[0]

            comments.append({
            'id': comment_id,
            'customer_name': username,
            'avatar': avatar,
            'content': content,
            'time': created_at,
            'liked': liked,
            'like_count': like_count
                })
        cur.execute("SELECT COUNT(*) FROM likes WHERE post_id=%s", (post_id,))
        like_count = cur.fetchone()[0]
        posts.append({
            'id': post_id,
            'name': full_name,
            'image': image,
            'content': content,
            'time': created_at,
            'like': liked,
            'like_count': like_count,  
            'comments': comments
        })

    cur.close()
    conn.close()
    return render_template('index.html', posts=posts)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSION={'.mp4','.webm','.mov'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
def allowed_video(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION

@app.route('/add_post', methods=['GET','POST'])
@login_required
def add_post():
    if request.method == 'POST':
        content = request.form.get('content')
        image = request.files.get('image')
        video = request.files.get('video')
        image_url = None
        video_url = None

        # Xử lý ảnh
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join('static/images/post_content', filename)
            image.save(image_path)
            image_url = f"images/post_content/{filename}"

        # Xử lý video
        if video and allowed_video(video.filename):
            filename = secure_filename(video.filename)
            video_path = os.path.join('static/images/post_content', filename)
            video.save(video_path)
            video_url = f"images/post_content/{filename}"

        # Lưu vào DB 1 lần duy nhất
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO posts (user_id, caption, image_path, video_path, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (session['user_id'], content, image_url, video_url))
            conn.commit()
            flash('Đăng bài thành công!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Đã xảy ra lỗi: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()

    return render_template('index.html')

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    user_id = session['user_id']
    username = session['username']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO comments (post_id,user_id,content,created_at) VALUES (%s,%s,%s,NOW())", 
                (post_id, user_id, content))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'customer_name': username, 'content': content})

@app.route('/like_post', methods=['POST'])
@login_required
def like_post():
    post_id = request.form.get('post_id')
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    # Kiểm tra đã like chưa
    cur.execute("SELECT * FROM likes WHERE user_id=%s AND post_id=%s", (user_id, post_id))
    like = cur.fetchone()
    if like:
        cur.execute("DELETE FROM likes WHERE user_id=%s AND post_id=%s", (user_id, post_id))
        liked = False
    else:
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s,%s)", (user_id, post_id))
        liked = True
    conn.commit()
    # Lấy số lượng like mới
    cur.execute("SELECT COUNT(*) FROM likes WHERE post_id=%s", (post_id,))
    like_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({'liked': liked, 'like_count': like_count})


@app.route('/', methods=["POST","GET"])
def login():
     if request.method == "POST":
        user_id = request.form["user_id"]
        password= request.form["password"]

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM public.users
                WHERE username = %s AND password = %s
            """, (user_id, password))

            user = cur.fetchone()

            if user:
                session['user_id'] = user[0]
                session['username'] = user[1] 
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Tài khoản hoặc mật khẩu không đúng!', 'error')

        except Exception as e:
            flash(f'Đã xảy ra lỗi: {str(e)}', 'error')

        finally:
            cur.close()
            conn.close()

     return render_template('login.html')

@app.route('/logout')
def log_out():
     session.clear()
     flash ("You logged out!","info")
     return  redirect(url_for("login"))  

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        user_id = request.form['userID']
        user_name= request.form['fullname']
        password = request.form['password']
        phone= request.form['phone']
        gender = request.form['gender']
        email = request.form['email']
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
            Select * FROM public.users WHERE username = %s
                   """,(user_id,))
            if cur.fetchone():
                flash('ID đã có người dùng rồi. Vui lòng chọn ID khác','error')
                return render_template('register.html')
            code =''.join(random.choices(string.digits, k=6))
            session['register_info']={
                'user_id': user_id,
                'user_name': user_name,
                'password': password,
                'phone': phone,
                'gender': gender,
                'email': email,
                'code': code
            }
            msg = Message("Mã xác nhận đăng ký tài khoản", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Mã xác nhận của bạn là: {code}"
            mail.send(msg)

            flash("Mã xác nhận đã được gửi tới email của bạn. Vui lòng nhập mã để hoàn tất đăng ký.", "info")
            return redirect(url_for('verify_email'))
        except Exception as e:
            flash(f"Lỗi: {str(e)}", 'error')
            return render_template('register.html')
    return render_template('register.html')

@app.route("/verify_email", methods=["GET", "POST"])
def verify_email():
    print(session.get("register_info"))
    reg_info = session.get("register_info")
    if not reg_info:
        flash("Thông tin đăng ký không tồn tại hoặc đã hết hạn.", "error")
        return redirect(url_for("register"))

    if request.method == "POST":
        input_code = request.form["code"].strip()
        print("input_code:", repr(input_code))
        print("reg_info['code']:", repr(reg_info["code"]))

        if input_code == reg_info["code"]:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO public.users (full_name, phone, gender, username, password, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    reg_info["user_name"], reg_info["phone"], reg_info["gender"],
                    reg_info["user_id"], reg_info["password"], reg_info["email"]
                ))
                conn.commit()
                cur.close()
                conn.close()
                flash("Đăng ký thành công! Bạn có thể đăng nhập.", "success")
                return redirect(url_for("login"))

            except Exception as e:
                flash(f"Lỗi khi tạo tài khoản: {str(e)}", "error")
                return redirect(url_for("register"))
        else:
            flash("Mã xác nhận không đúng. Vui lòng thử lại.", "error")

    return render_template("verify.html")

def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def keep_aspect_and_multiple_of_8(img: Image.Image, max_side: int = MAX_SIDE):
    w, h = img.size
    scale = min(max_side / max(w, h), 1.0)
    new_w = int(w * scale)
    new_h = int(h * scale)
    new_w = max(8, (new_w // 8) * 8)
    new_h = max(8, (new_h // 8) * 8)
    return img.resize((new_w, new_h), Image.LANCZOS)

def preprocess(pil_img: Image.Image, session: ort.InferenceSession):
    pil_img = pil_img.convert("RGB")
    input_shape = session.get_inputs()[0].shape
    print(f"[DEBUG] preprocess with shape {input_shape}")

    if len(input_shape) == 4:
        N, d1, d2, d3 = input_shape
    else:
        raise ValueError(f"Unexpected input shape: {input_shape}")

    if d1 == 3:  
        H, W = d2, d3
        if isinstance(H, int) and isinstance(W, int):
            pil_img = pil_img.resize((W, H), Image.LANCZOS)
        else:
            pil_img = keep_aspect_and_multiple_of_8(pil_img, MAX_SIDE)

        np_img = np.array(pil_img).astype(np.float32) / 127.5 - 1.0
        np_img = np.transpose(np_img, (2, 0, 1))
        np_img = np.expand_dims(np_img, 0)

    elif d3 == 3:  
        H, W = d1, d2
        if isinstance(H, int) and isinstance(W, int):
            pil_img = pil_img.resize((W, H), Image.LANCZOS)
        else:
            pil_img = keep_aspect_and_multiple_of_8(pil_img, MAX_SIDE)

        np_img = np.array(pil_img).astype(np.float32) / 127.5 - 1.0
        np_img = np.expand_dims(np_img, 0) 

    else:
        raise ValueError("Model input không rõ layout")

    return np_img, pil_img.size



def postprocess(out_tensor: np.ndarray):
    x = np.squeeze(out_tensor, 0) 
    if x.shape[0] == 3 and x.ndim == 3:
        x = np.transpose(x, (1, 2, 0)) 

    x = (x + 1.0) * 127.5
    x = np.clip(x, 0, 255).astype(np.uint8)
    return Image.fromarray(x, mode="RGB")

@app.route('/cartoonize', methods=['GET','POST'])
def cartoonize():
    if request.method == 'GET' :
        return render_template('picture.html')
    file = request.files['image']
    model_key = request.form.get("model", "hayao")  
    if not file or not allowed_file(file.filename):
        return "File không hợp lệ", 400
    session = get_session_for(model_key)
    pil_img = Image.open(file.stream).convert("RGB")
    input_img, _ = preprocess(pil_img,session)

    ort_inputs = {session.get_inputs()[0].name: input_img}
    ort_outs = session.run(None, ort_inputs)
    output = ort_outs[0]

    pil_out = postprocess(output)

    img_io = io.BytesIO()
    pil_out.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
@app.route("/share_to_blog", methods=["POST"])
@login_required
def share_to_blog():
    user_id = session.get('user_id')
    file = request.files.get("image")
    content = request.form.get("content", "")

    if not file or file.filename == "":
        return "Không có ảnh", 400

    os.makedirs('static/images/post_content', exist_ok=True)
    filename = secure_filename(file.filename)
    save_path = os.path.join('static/images/post_content', filename)
    file.save(save_path)
    db_path = f"images/post_content/{filename}"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO posts (user_id, caption, image_path,created_at) VALUES (%s, %s, %s, NOW()) RETURNING id",
        (user_id, content, db_path)
    )
    post_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))
@app.route('/like_comment', methods=['POST'])
@login_required
def like_comment():
    comment_id = request.form.get('comment_id')
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM comment_likes WHERE user_id=%s AND comment_id=%s", (user_id, comment_id))
    liked = cur.fetchone()
    if liked:
        cur.execute("DELETE FROM comment_likes WHERE user_id=%s AND comment_id=%s", (user_id, comment_id))
        liked_now = False
    else:
        cur.execute("INSERT INTO comment_likes (user_id, comment_id) VALUES (%s,%s)", (user_id, comment_id))
        liked_now = True

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM comment_likes WHERE comment_id=%s", (comment_id,))
    like_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({'liked': liked_now, 'like_count': like_count})

@app.route("/account/<int:user_id>")
def account(user_id):
    if 'user_id' not in session:
        return redirect("/login")  
    conn = get_db_connection()
    cur = conn.cursor()
    current_user_id = session['user_id'] 
    cur.execute("SELECT id, username, avatar,slogan FROM users WHERE id=%s", (user_id,))
    user_row = cur.fetchone()
    if not user_row:
        return "User not found", 404
    user = {"id": user_row[0], "username": user_row[1], "avatar": user_row[2],"slogan":user_row[3]}
    cur.execute("SELECT COUNT(*) FROM follows WHERE followed_id=%s", (user['id'],))
    followers_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM follows WHERE follower_id=%s", (user['id'],))
    following_count = cur.fetchone()[0]

    cur.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s", 
                (current_user_id, user['id']))
    is_following = cur.fetchone() is not None

    cur.execute("""
        SELECT p.id, u.full_name, p.image_path, p.caption, p.created_at
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.user_id=%s
        ORDER BY p.created_at DESC
    """, (user['id'],))
    
    posts = []
    for row in cur.fetchall():
        post_id, full_name, image, content, created_at = row

        cur.execute("SELECT 1 FROM likes WHERE user_id=%s AND post_id=%s", (user_id, post_id))
        liked_post = cur.fetchone() is not None
        cur.execute("SELECT COUNT(*) FROM likes WHERE post_id=%s", (post_id,))
        like_count = cur.fetchone()[0]

        cur.execute("""
            SELECT c.id, u.username, u.avatar, c.content, c.created_at
            FROM comments c
            JOIN users u ON u.id = c.user_id
            WHERE c.post_id=%s
            ORDER BY c.created_at ASC
        """, (post_id,))
        comments = []
        for c in cur.fetchall():
            comment_id, username, avatar, comment_content, comment_time = c
            cur.execute("SELECT 1 FROM comment_likes WHERE user_id=%s AND comment_id=%s", (user_id, comment_id))
            liked_comment = cur.fetchone() is not None
            cur.execute("SELECT COUNT(*) FROM comment_likes WHERE comment_id=%s", (comment_id,))
            comment_like_count = cur.fetchone()[0]

            comments.append({
                'id': comment_id,
                'customer_name': username,
                'avatar': avatar,
                'content': comment_content,
                'time': comment_time,
                'liked': liked_comment,
                'like_count': comment_like_count
            })

        posts.append({
            'id': post_id,
            'name': full_name,
            'image': image,
            'content': content,
            'time': created_at,
            'like': liked_post,
            'like_count': like_count,
            'comments': comments
        })

    cur.close()
    conn.close()

    return render_template("account.html",
                           user=user,
                           followers_count=followers_count,
                           following_count=following_count,
                           is_following=is_following,
                           posts=posts)


@app.route("/follow/<int:followed_id>", methods=["POST"])
def follow(followed_id):
    if 'user_id' not in session:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    follower_id = session['user_id']
    if follower_id == followed_id:
        return jsonify({"error": "Không thể follow chính mình"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM follows WHERE follower_id=%s AND followed_id=%s", (follower_id, followed_id))
    if cur.fetchone():
        cur.execute("DELETE FROM follows WHERE follower_id=%s AND followed_id=%s", (follower_id, followed_id))
        following_now = False
    else:
        cur.execute("INSERT INTO follows (follower_id, followed_id) VALUES (%s,%s)", (follower_id, followed_id))
        following_now = True
    cur.execute("SELECT COUNT(*) FROM follows WHERE followed_id=%s", (followed_id,))
    followers_count = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"followers_count": followers_count, "following_now": following_now})
AVATAR_FOLDER = 'static/avatar'
app.config['AVATAR_FOLDER'] = AVATAR_FOLDER
@app.route('/change_avatar', methods=['POST'])
def change_avatar():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']

    if 'avatar' not in request.files:
        return redirect(url_for('account', user_id=user_id))
    
    file: FileStorage = request.files['avatar']
    if file.filename == '':
        return redirect(url_for('account', user_id=user_id))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
        ext = filename.rsplit('.', 1)[1].lower()
        save_name = f"{user_id}.{ext}"
        file_path = os.path.join(app.config['AVATAR_FOLDER'], save_name)
        file.save(file_path)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET avatar=%s WHERE id=%s", (f'/avatar/{save_name}', user_id))
        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for('account', user_id=user_id))
@app.route("/search_users")
def search_users():
    username_query = request.args.get('username', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE username ILIKE %s LIMIT 10", (f"%{username_query}%",))
    users = [{"id": r[0], "username": r[1]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users)
@app.route('/save_slogan', methods=['POST'])
@login_required
def save_slogan():
    slogan = request.form.get('slogan', '').strip()
    if not slogan:
        return jsonify({'error': 'Slogan không được để trống'}), 400
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET slogan = %s WHERE id = %s", (slogan, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'slogan': slogan})

if __name__ == "__main__":
    app.run(debug=True)
