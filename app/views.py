from app import app
import os
from base64 import b64decode
from flask import render_template, redirect, request, flash, url_for,  abort, send_from_directory, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import bcrypt
from app import rules

EXCHANGE_RATES = {
    ('USD', 'EUR'): 0.85,
    ('USD', 'RUB'): 70.0,
    ('USD', 'RUB'): 70.0,
    ('EUR', 'USD'): 1.18,
    ('EUR', 'RUB'): 82.0,
    ('RUB', 'USD'): 0.014,
    ('RUB', 'EUR'): 0.012,
}




app.config['SECRET_KEY'] = "test"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:crypto@localhost/crypto_exchange"#os.environ.get("DATABASE")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIRECTORY = os.path.join(BASE_DIR, 'share')
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable = False)
    username = db.Column(db.String(25), unique=True, nullable = False)
    password_hash = db.Column(db.String(500), nullable = False)
    balance = db.Column(db.Float, default=0, nullable=False)

salt = bcrypt.gensalt()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
    if request.method == "POST":
        answ = rules.send_msg_rule(request.form)
        if answ:
            return redirect('/')
    return render_template("main.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    global salt
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not rules.login_creds(request.form):
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("passwords don't match", category='error')
            return render_template('register.html')
        
        user_exists = Users.query.filter_by(username=username).first()

        if user_exists:
            flash('User already exist', category='error')
            return render_template('register.html')

        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

        new_user = Users(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template("register.html")


@app.route("/start_trading")
def start_trade():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        
        
        user = Users.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login or password', category='error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")



@app.route('/download', methods=['GET'])
@login_required
def download_file():
    filename = request.args.get('filename')

    filename = b64decode(filename).decode()
    
    if not filename:
        abort(400, description="Filename parameter is required.")

    file_path = os.path.join(FILES_DIRECTORY, filename)

    if not os.path.isfile(file_path) or not os.path.abspath(file_path).startswith(FILES_DIRECTORY):
        abort(404, description="File not found or access denied.")
    
    return send_from_directory(FILES_DIRECTORY, filename, as_attachment=True)




@app.route('/calculate_money', methods=['POST'])
@login_required
def get_exchange_rate():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    
    # Получение коэффициента конверсии
    rate = EXCHANGE_RATES.get((from_currency, to_currency))

    output = rate * float(amount)

    if output is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404

    
    return jsonify({'output': output})