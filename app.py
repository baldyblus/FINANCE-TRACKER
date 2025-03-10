from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, ExpenseForm
from models import db, User, Expense
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_manager.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', expenses=expenses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account Created! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Username or Password", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    category = request.form.get("category")
    amount = float(request.form.get("amount"))
    expense = Expense(user_id=current_user.id, category=category, amount=amount)
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_expense/<int:id>')
@login_required
def delete_expense(id):
    expense = Expense.query.get(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/generate_pdf')
@login_required
def generate_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Expense Report")
    y = 720
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    for exp in expenses:
        pdf.drawString(100, y, f"{exp.category}: {exp.amount}")
        y -= 20
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
