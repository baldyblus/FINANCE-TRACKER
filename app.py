from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    category_filter = request.form.get("category")
    date_filter = request.form.get("date")

    query = Expense.query.filter_by(user_id=current_user.id)

    if category_filter:
        query = query.filter_by(category=category_filter)
    if date_filter:
        query = query.filter_by(date=date_filter)

    expenses = query.all()
    total_spending = sum(exp.amount for exp in expenses)

    return render_template("index.html", expenses=expenses, total_spending=total_spending)

@app.route("/add", methods=["POST"])
@login_required
def add_expense():
    date = request.form["date"]
    category = request.form["category"]
    amount = float(request.form["amount"])
    description = request.form["description"]

    new_expense = Expense(user_id=current_user.id, date=date, category=category, amount=amount, description=description)
    db.session.add(new_expense)
    db.session.commit()

    return redirect(url_for("index"))

@app.route("/export/pdf")
@login_required
def export_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(200, 750, f"Expense Report for {current_user.username}")

    y = 720
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    for exp in expenses:
        pdf.drawString(50, y, f"{exp.date} | {exp.category} | ₹{exp.amount} | {exp.description}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="expenses.pdf", mimetype="application/pdf")

@app.route("/graph_data")
@login_required
def graph_data():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    categories = {}
    monthly_expenses = {}

    for exp in expenses:
        categories[exp.category] = categories.get(exp.category, 0) + exp.amount
        month = exp.date[:7]  # Extract YYYY-MM
        monthly_expenses[month] = monthly_expenses.get(month, 0) + exp.amount

    return jsonify({"categories": categories, "monthly_expenses": monthly_expenses})

if __name__ == "__main__":
    app.run(debug=True)
