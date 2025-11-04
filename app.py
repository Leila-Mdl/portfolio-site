from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# ---------------------------
# تنظیمات اولیه برنامه
# ---------------------------
app = Flask(__name__)
app.secret_key = 'mysecretkey'

# ---------------------------
# تنظیمات دیتابیس
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# تنظیمات آپلود فایل‌ها
# ---------------------------
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # حداکثر حجم فایل 2MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """بررسی فرمت مجاز فایل"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------
# مدل‌ها (Models)
# ---------------------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(250))
    link = db.Column(db.String(250))


class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    profile_image = db.Column(db.String(250))
    linkedin = db.Column(db.String(250))
    github = db.Column(db.String(250))


# ساخت دیتابیس در صورت نیاز
with app.app_context():
    db.create_all()

# ---------------------------
# مسیرها (Routes)
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')


# فرم تماس
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_msg = Message(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash("پیامت با موفقیت ارسال شد ✅", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')


# صفحه پروژه‌ها
@app.route('/projects')
def projects():
    all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)


# ورود مدیر
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == "admin123":
            session['admin'] = True
            flash("با موفقیت وارد شدید ✅", "success")
            return redirect(url_for('admin'))
        else:
            flash("رمز اشتباه است ❌", "danger")
    return render_template('login.html')


# پنل ادمین
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        flash("ابتدا وارد شوید ❌", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        link = request.form['link']

        image_file = request.files.get('image_file')
        image_path = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)
            image_path = f'/static/img/{filename}'

        new_project = Project(title=title, description=description, image_url=image_path, link=link)
        db.session.add(new_project)
        db.session.commit()
        flash("پروژه جدید با موفقیت اضافه شد ✅", "success")
        return redirect(url_for('admin'))

    messages = Message.query.all()
    projects = Project.query.all()
    return render_template('admin.html', messages=messages, projects=projects)


# ویرایش پروژه
@app.route('/edit_project/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    if not session.get('admin'):
        flash("ابتدا وارد شوید ❌", "danger")
        return redirect(url_for('login'))

    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        project.title = request.form['title']
        project.description = request.form['description']
        project.link = request.form['link']

        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)
            project.image_url = f'/static/img/{filename}'

        db.session.commit()
        flash("پروژه با موفقیت ویرایش شد ✅", "success")
        return redirect(url_for('admin'))

    return render_template('edit_project.html', project=project)


# حذف پروژه
@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    if not session.get('admin'):
        flash("ابتدا وارد شوید ❌", "danger")
        return redirect(url_for('login'))

    project = Project.query.get_or_404(id)

    if project.image_url:
        image_path = project.image_url.replace('/', os.sep)
        full_path = os.path.join(app.root_path, image_path[1:])
        if os.path.exists(full_path):
            os.remove(full_path)

    db.session.delete(project)
    db.session.commit()

    flash("پروژه و تصویر مربوطه حذف شد 🗑️", "info")
    return redirect(url_for('admin'))


# خروج از اکانت
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("خارج شدید 👋", "info")
    return redirect(url_for('home'))


# ---------------------------
# بخش درباره من (About Me)
# ---------------------------
@app.route('/about')
def about():
    about_info = About.query.first()
    return render_template('about.html', about=about_info)

@app.route('/edit_about', methods=['GET', 'POST'])
def edit_about():
    if not session.get('admin'):
        flash("ابتدا وارد شوید ❌", "danger")
        return redirect(url_for('login'))

    about_info = About.query.first()

    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        description = request.form['description']
        linkedin = request.form['linkedin']
        github = request.form['github']

        # 📸 آپلود عکس پروفایل (اختیاری)
        image_file = request.files.get('profile_image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)
            image_url = f'/static/img/{filename}'
        else:
            image_url = about_info.profile_image if about_info else None

        # ✏️ ذخیره یا بروزرسانی
        if about_info is None:
            about_info = About(
                name=name,
                title=title,
                description=description,
                linkedin=linkedin,
                github=github,
                profile_image=image_url
            )
            db.session.add(about_info)
        else:
            about_info.name = name
            about_info.title = title
            about_info.description = description
            about_info.linkedin = linkedin
            about_info.github = github
            about_info.profile_image = image_url

        db.session.commit()
        flash("بخش درباره من با موفقیت به‌روزرسانی شد ✅", "success")
        return redirect(url_for('about'))

    return render_template('edit_about.html', about=about_info)


# ---------------------------
# اجرای برنامه
# ---------------------------
if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'img'), exist_ok=True)
    app.run(debug=True)
