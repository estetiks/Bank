from app import app
import pickle
import json
import os
from base64 import b64decode, b64encode
from flask import render_template, redirect, request, flash, url_for,  abort, send_from_directory, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import bcrypt
from datetime import datetime, timedelta
import hashlib
import subprocess
import shutil
from app import rules


g = {}

EXCHANGE_RATES = {
    ('USD', 'EUR'): 0.85,
    ('USD', 'RUB'): 70.0,
    ('USD', 'RUB'): 70.0,
    ('EUR', 'USD'): 1.18,
    ('EUR', 'RUB'): 82.0,
    ('RUB', 'USD'): 0.014,
    ('RUB', 'EUR'): 0.012,
}


EXCHANGE_RATES_SHARES = {
    ('HL', 'EUR'): 0.56,
    ('HL', 'USD'): 0.70,
    ('HL', 'RUB'): 76.0,
    ('TUBE', 'USD'): 1.18,
    ('TUBE', 'RUB'): 82.0,
    ('TUBE', 'EUR'): 1.14,
    }



app.config['SECRET_KEY'] = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STATIC_FOLDER'] = 'static'


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIRECTORY = os.path.join(BASE_DIR, 'share')
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'



class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable = False)
    username = db.Column(db.String(25), unique=True, nullable = False)
    email = db.Column(db.String, unique=False, nullable = False)
    password_hash = db.Column(db.String(500), nullable = False)
    balance_RUB = db.Column(db.Float, default=0, nullable=False)
    balance_USD = db.Column(db.Float, default=0, nullable=False)
    balance_EUR = db.Column(db.Float, default=0, nullable=False)
    shares_HL = db.Column(db.Integer, default=0, nullable=False)
    shares_TUBE = db.Column(db.Integer, default=0, nullable=False)

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
        email = request.form['email']
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

        new_user = Users(username=username, password_hash=hashed_password, email=email)
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




@app.route("/restore_password", methods=["GET","POST"])
def restore_password():
    if request.method == "POST":
        global g
        username = request.form["username"]
        user = Users.query.filter_by(username=username).first()
        if not user:
            return redirect(url_for("restore_password"))
        res = make_response(redirect(f"/get_restore_code/{username}"))

        expires = 60
        expires_date = datetime.utcnow() + timedelta(seconds=expires)
        generated_token = os.urandom(32)
        generated_token = hashlib.sha256(generated_token).hexdigest()
        res.set_cookie("token", generated_token, expires=expires_date)
        g['generated_token'] = generated_token
        
        command =['app/share/login', username, 'standoff365@mail.ru']
        result = subprocess.run(command, capture_output=True, text=True)
        log_files = [f for f in os.listdir('.') if f.endswith('.log')]

# Переносим каждый файл в директорию app/share
        for log_file in log_files:
            shutil.move(log_file, os.path.join('app', 'share', log_file))
        generate_code = result.stdout[:-1]
        g['generate_code'] = generate_code

        if user:
            flash("The account recovery code has been sent to your email", category="success")
            return res
        else:
            flash("user not found", category="error")
            return redirect(url_for("restore_password"))
        

    return render_template("restore_password.html")


@app.route("/get_restore_code/<username>", methods=["GET","POST"])
def get_restore_code(username):

    if request.method == "POST":
        global g
        if request.form["code"] == g['generate_code'] and g['generated_token'] == request.cookies.get("token"):
            user = Users.query.filter_by(username=username).first()
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("INCORRECT CODE", category="error")
            return redirect(f"/get_restore_code/{username}")

    return render_template("get_restore_code.html")





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



@app.route('/remove_user', methods=["POST", "GET"])
@login_required
def remove_user():
    if current_user.username != 'admin':
        abort(403)
    else:
        if request.method == "POST":
            user = request.form.get("remove")
            user_to_delete = Users.query.filter_by(username=user).first()
            recovery_data = pickle.dumps(user_to_delete)
            recovery_data = b64encode(recovery_data).decode()
        if user_to_delete: 
            return render_template("remove.html", recovery_data=recovery_data)
        else:
            flash("User not found", category="error")
        return redirect(url_for("dashboard")) 



@app.route('/restore_user', methods=["POST", "GET"])
@login_required
def restore_user():
    if current_user.username != 'admin':
        abort(403)
    else:
        if request.method == "POST":
            recovery_data = request.form['recovery_data']
            try:
                recovery_data = pickle.loads(b64decode(recovery_data))
                flash(f"user {recovery_data.username} restore", category="success")
            except:
                flash("User unrestored", category="error")
            
        return render_template("restore_user.html")





@app.route('/calculate_money', methods=['POST'])
@login_required
def calculate_money():
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




@app.route('/calculate_shares', methods=['POST'])
@login_required
def calculate_shares():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    
    # Получение коэффициента конверсии
    rate = EXCHANGE_RATES_SHARES.get((from_currency, to_currency))

    output = rate * amount

    if output is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404

    
    return jsonify({'output': output})





@app.route('/convert_money', methods=['POST'])
@login_required
def convert_money():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    if from_currency == "RUB":
        if float(amount) > current_user.balance_RUB:
            return jsonify({'get': 'insufficient funds'})
        elif float(amount) <= current_user.balance_RUB:
            current_user.balance_RUB = current_user.balance_RUB - float(amount)
    elif from_currency == "USD":
        if float(amount) > current_user.balance_USD:
            return jsonify({'get': 'insufficient funds'})
        elif float(amount) <= current_user.balance_USD:
            current_user.balance_USD = current_user.balance_USD - float(amount)
    elif from_currency == "EUR":
        if float(amount) > current_user.balance_EUR:
            return jsonify({'get': 'insufficient funds'})
        elif float(amount) <= current_user.balance_EUR:
            current_user.balance_EUR = current_user.balance_EUR - float(amount)    


    rate = EXCHANGE_RATES.get((from_currency, to_currency))

    get = rate * float(amount)

    if get is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404
    
    if to_currency == "RUB":
        current_user.balance_RUB = current_user.balance_RUB + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    elif to_currency == "USD":
        current_user.balance_USD = current_user.balance_USD + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    elif to_currency == "EUR":
        current_user.balance_EUR = current_user.balance_EUR + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    else: 
        return jsonify({'get': 'somthung error'})



@app.route('/sell_shares', methods=['POST'])
@login_required
def sell_shares():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    if from_currency == "HL":
        if int(amount) > current_user.shares_HL:
            return jsonify({'get': 'not enough shares'})
        elif int(amount) <= current_user.shares_HL:
            current_user.shares_HL = current_user.shares_HL - int(amount)
    elif from_currency == "TUBE":
        if int(amount) > current_user.shares_TUBE:
            return jsonify({'get': 'not enough shares'})
        elif int(amount) <= current_user.shares_TUBE:
            current_user.shares_TUBE = current_user.shares_TUBE - int(amount)  


    rate = EXCHANGE_RATES_SHARES.get((from_currency, to_currency))

    get = rate * int(amount)

    if get is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404
    
    if to_currency == "RUB":
        current_user.balance_RUB = current_user.balance_RUB + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    elif to_currency == "USD":
        current_user.balance_USD = current_user.balance_USD + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    elif to_currency == "EUR":
        current_user.balance_EUR = current_user.balance_EUR + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    else: 
        return jsonify({'get': 'somthung error'})
    






@app.route('/buy_shares', methods=['POST'])
@login_required
def buy_shares():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    if to_currency == "RUB":
        if float(amount) > current_user.balance_RUB:
            return jsonify({'get': 'insufficient funds'})
        elif float(amount) <= current_user.balance_RUB:
            current_user.balance_RUB = current_user.balance_RUB - float(amount)
    elif to_currency == "USD":
        if float(amount) > current_user.balance_USD:
            return jsonify({'get': 'insufficient funds'})
        elif float(amount) <= current_user.balance_USD:
            current_user.balance_USD = current_user.balance_USD - float(amount)
    elif to_currency == "EUR":
        if float(amount) > current_user.balance_EUR:
            return jsonify({'get': 'insufficient funds'})
        elif float(amount) <= current_user.balance_EUR:
            current_user.balance_EUR = current_user.balance_EUR - float(amount)  


    rate = EXCHANGE_RATES_SHARES.get((from_currency, to_currency))

    get = float(amount) / rate
    get = int(get)

    if get is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404
    
    if from_currency == "HL":
        current_user.shares_HL = current_user.shares_HL + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    elif from_currency == "TUBE":
        current_user.shares_TUBE = current_user.shares_TUBE + get
        db.session.commit()
        return jsonify({'get': 'success!'})
    else: 
        return jsonify({'get': 'somthung error'})