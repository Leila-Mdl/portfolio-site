from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

# ------------------ تنظیمات پایه ------------------
app = Flask(__name__)
app.secret_key = "mysecretkey"

# مسیر مطلق برای دیتابیس
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "messages.db")

# اطمینان از وجود پوشه‌ی database
os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

# تنظیم دیتابیس SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------ مدل دیتابیس ------------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

# ------------------ مسیرهای سایت ------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/skills')
def skills():
    return render_template('skills.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_msg = Message(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash("پیامت با موفقیت ارسال شد 🌟", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')


# ------------------ ورود مدیر ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']

        if password == "admin123":  # رمز ورود مدیر
            session['admin'] = True
            flash("با موفقیت وارد شدید ✅", "success")
            return redirect(url_for('admin'))
        else:
            flash("رمز اشتباهه ❌", "danger")

    return render_template('login.html')


# ------------------ خروج از حساب ------------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("از حساب خارج شدید 👋", "info")
    return redirect(url_for('home'))


# ------------------ صفحه مدیریت ------------------
@app.route('/admin')
def admin():
    if not session.get('admin'):
        flash("لطفاً ابتدا وارد شوید ⚠️", "warning")
        return redirect(url_for('login'))

    messages = Message.query.all()
    return render_template('admin.html', messages=messages)


# ------------------ حذف پیام ------------------
@app.route('/delete/<int:id>')
def delete_message(id):
    if not session.get('admin'):
        flash("دسترسی غیرمجاز ❌", "danger")
        return redirect(url_for('home'))

    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash("پیام حذف شد 🗑️", "info")
    return redirect(url_for('admin'))


# ------------------ اجرای برنامه ------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
