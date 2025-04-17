from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from finance_advisor import FinanceAdvisorSystem, parse_json_safely
from database import User, Session as DBSession
import pandas as pd
import json
import os
from dotenv import load_dotenv
import asyncio
import logging
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class FlaskUser(UserMixin):
    def __init__(self, user):
        self.id = str(user.id)
        self.username = user.username
        self.user = user


@login_manager.user_loader
def load_user(user_id):
    db_session = DBSession()
    user = db_session.query(User).filter_by(id=int(user_id)).first()
    db_session.close()
    if user:
        return FlaskUser(user)
    return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    if not GEMINI_API_KEY:
        flash("GOOGLE_API_KEY not found in environment variables. Please add it to your .env file.", "error")
    return render_template('dashboard.html')


@app.route('/input')
@login_required
def input():
    return render_template('input.html')


@app.route('/results')
@login_required
def results():
    results = session.get('results', None)
    if not results:
        flash("No analysis results available. Please submit your financial data first.", "error")
        return redirect(url_for('input'))
    return render_template('results.html', results=results)


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


@app.route('/goals')
@login_required
def goals():
    return render_template('goals.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db_session = DBSession()
        user = db_session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(FlaskUser(user))
            flash('Logged in successfully!', 'success')
            db_session.close()
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
        db_session.close()
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db_session = DBSession()
        if db_session.query(User).filter_by(username=username).first():
            flash('Username already exists.', 'error')
            db_session.close()
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db_session.add(user)
        db_session.commit()
        flash('Registration successful! Please log in.', 'success')
        db_session.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/download_template')
def download_template():
    template_path = os.path.join('static', 'data', 'expense_template.csv')
    return send_file(template_path, as_attachment=True)


@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    try:
        monthly_income = float(request.form.get('monthly_income', 0))
        dependants = int(request.form.get('dependants', 0))
        expense_option = request.form.get('expense_option', 'manual')
        num_debts = int(request.form.get('num_debts', 0))

        transactions = None
        manual_expenses = {}
        if expense_option == 'csv':
            file = request.files.get('transaction_file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                with open(file_path, 'rb') as f:
                    parsed_data = parse_csv_transactions(f.read())
                    transactions = parsed_data['transactions']

                os.remove(file_path)
            else:
                flash("Invalid or missing CSV file. Please upload a valid CSV file.", "error")
                return redirect(url_for('input'))
        else:
            categories = ['Housing', 'Utilities', 'Food', 'Transportation', 'Healthcare',
                          'Entertainment', 'Personal', 'Savings', 'Other']
            for cat in categories:
                amount = request.form.get(f'manual_{cat}', 0)
                try:
                    amount = float(amount)
                    if amount > 0:
                        manual_expenses[cat] = amount
                except ValueError:
                    continue

        debts = []
        for i in range(num_debts):
            debt_name = request.form.get(f'debt_name_{i}', f'Debt {i + 1}')
            debt_amount = request.form.get(f'debt_amount_{i}', 0)
            interest_rate = request.form.get(f'debt_rate_{i}', 0)
            min_payment = request.form.get(f'debt_min_payment_{i}', 0)

            try:
                debt_amount = float(debt_amount)
                interest_rate = float(interest_rate)
                min_payment = float(min_payment)
                debts.append({
                    'name': debt_name,
                    'amount': debt_amount,
                    'interest_rate': interest_rate,
                    'min_payment': min_payment
                })
            except ValueError:
                continue

        financial_data = {
            'monthly_income': monthly_income,
            'dependants': dependants,
            'transactions': transactions,
            'manual_expenses': manual_expenses if manual_expenses else None,
            'debts': debts
        }

        finance_system = FinanceAdvisorSystem()
        results = asyncio.run(finance_system.analyze_finances(financial_data))

        session['results'] = results
        return redirect(url_for('results'))

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        flash(f"An error occurred during analysis: {str(e)}", "error")
        return redirect(url_for('input'))


if __name__ == '__main__':
    app.run(debug=True)