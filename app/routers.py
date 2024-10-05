from config import *
import pickle
import os
from base64 import b64decode, b64encode
from flask import Blueprint, render_template, redirect, request, flash, url_for,  abort, send_from_directory, session, jsonify, make_response
from flask_login import login_required, login_user, logout_user, current_user
import bcrypt
from datetime import datetime, timedelta
import hashlib
import subprocess
import shutil
import rules
from models import Users, db, salt

bp = Blueprint('bank', __name__, template_folder='templates')

g = {}


@bp.route('/', methods = ['GET', 'POST'])
@bp.route('/index', methods = ['GET', 'POST'])
def index():
    if request.method == "POST":
        answ = rules.send_msg_rule(request.form)
        if answ:
            return redirect('/')
    return render_template("main.html")



@bp.route('/register', methods=['GET', 'POST'])
def register():
    global salt
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not rules.login_creds(request.form):
            return redirect(url_for("bank.register"))

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
        
        return redirect(url_for('bank.login'))
    
    return render_template("register.html")


@bp.route("/start_trading")
def start_trade():
    if current_user.is_authenticated:
        return redirect(url_for('bank.dashboard'))
    else:
        return redirect(url_for('bank.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        
        
        user = Users.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            login_user(user)
            return redirect(url_for('bank.dashboard'))
        else:
            flash('Invalid login or password', category='error')
    
    return render_template('login.html')




@bp.route("/restore_password", methods=["GET","POST"])
def restore_password():
    if request.method == "POST":
        global g
        username = request.form["username"]
        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("user not found", category="error")
            return redirect(url_for("bank.restore_password"))
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

        for log_file in log_files:
            shutil.move(log_file, os.path.join('app/share', log_file))
        generate_code = result.stdout[:-1]
        g['generate_code'] = generate_code

        if user:
            flash("The account recovery code has been sent to your email", category="success")
            return res
        else:
            flash("user not found", category="error")
            return redirect(url_for("bank.restore_password"))
        

    return render_template("restore_password.html")


@bp.route("/get_restore_code/<username>", methods=["GET","POST"])
def get_restore_code(username):

    if request.method == "POST":
        global g
        if request.form["code"] == g['generate_code'] and g['generated_token'] == request.cookies.get("token"):
            user = Users.query.filter_by(username=username).first()
            login_user(user)
            return redirect(url_for('bank.dashboard'))
        else:
            flash("INCORRECT CODE", category="error")
            return redirect(f"/get_restore_code/{username}")

    return render_template("get_restore_code.html")





@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('bank.login'))


@bp.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")



@bp.route('/download', methods=['GET'])
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



@bp.route('/remove_user', methods=["POST", "GET"])
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
        return redirect(url_for("bank.dashboard")) 



@bp.route('/restore_user', methods=["POST", "GET"])
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





@bp.route('/calculate_money', methods=['POST'])
@login_required
def calculate_money():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    

    rate = EXCHANGE_RATES.get((from_currency, to_currency))

    output = rate * float(amount)

    if output is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404

    
    return jsonify({'output': output})




@bp.route('/calculate_shares', methods=['POST'])
@login_required
def calculate_shares():
    data = request.get_json()
    amount = data.get('amount')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')

    

    rate = EXCHANGE_RATES_SHARES.get((from_currency, to_currency))

    output = rate * amount

    if output is None or rate is None:
        return jsonify({'error': 'Exchange rate not found.'}), 404

    
    return jsonify({'output': output})





@bp.route('/convert_money', methods=['POST'])
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



@bp.route('/sell_shares', methods=['POST'])
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
    






@bp.route('/buy_shares', methods=['POST'])
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