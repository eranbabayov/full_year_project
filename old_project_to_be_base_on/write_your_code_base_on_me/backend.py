import ast
import string

from flask import render_template, request, redirect, url_for, session
from common_functions import *
from app_configuration import app_configuration, get_security_parameters
from flask_mail import Mail
from time import time
import random

app = Flask(__name__)
app = app_configuration(app)
mail = Mail(app)

failed_login_attempts = {}
blocked_ips = {}


@app.before_request
def limit_login_attempts():
    ip_address = request.remote_addr
    login_attempts, block_time = get_security_parameters()

    if ip_address in blocked_ips:
        if blocked_ips[ip_address] < time():
            del blocked_ips[ip_address]
            failed_login_attempts[ip_address] = 0
        else:
            remaining_time = blocked_ips[ip_address] - time()
            return f"Your IP is blocked for {remaining_time} seconds", 403

    failed_login_attempts[ip_address] = failed_login_attempts.get(ip_address, 0)

    if failed_login_attempts[ip_address] >= login_attempts:
        blocked_ips[ip_address] = time() + block_time
        return f"Your IP is blocked for {block_time} seconds", 403


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = get_user_data_from_db(username=username)
        if user_data is None:
            flash('User does not exist')
            return redirect(url_for('login'))

        salt_bytes = bytes.fromhex(get_user_salt(user_id=user_data['user_id']))
        login_hashed_pwd = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt_bytes, 100000)
        user_hashed_password = bytes.fromhex(user_data['password'])

        if user_hashed_password == login_hashed_pwd:
            session['username'] = username
            session['user_id'] = user_data['user_id']
            failed_login_attempts[request.remote_addr] = 0
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            failed_login_attempts[request.remote_addr] += 1
            return redirect(url_for('login'))

    return render_template(
        'login.html',
        user_added=request.args.get('user_added'), password_changed=request.args.get("password_changed"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    _, salt_len = get_password_policy()
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_email = request.form.get('email')
        if check_if_user_exists_using_email(new_email):
            flash("Email already exists! please use different email or login to your account.")
            return redirect(url_for('register'))
        if not validate_password(new_password):
            return redirect(url_for('register'))
        publish_sectors = request.form.getlist('publish_sectors[]')

        user_data = get_user_data_from_db(username=new_username)
        if user_data:
            flash('Username already exists')
            return redirect(url_for('register'))
        new_password_hashed_hex, user_salt_hex = generate_new_password_hashed(new_password, generate_to_hex=True)
        insert_new_user_to_db(
            new_username,
            new_password_hashed_hex,
            new_email,
            user_salt_hex)
        user_id = get_user_data_from_db(username=new_username)['user_id']
        insert_user_sectors_selected_to_db(publish_sectors, user_id)
        session['username'] = new_username
        session['user_id'] = user_id
        return redirect(url_for('login', user_added="user added"))

    sectors = get_all_sectors_names_from_db()
    return render_template('register.html', sectors=sectors)


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    client_data = request.args.getlist('client_data')
    if client_data == ['False']:
        return render_template('dashboard.html', username=username, client_data=client_data)
    if client_data != []:
        client_data = [ast.literal_eval(data) for data in client_data]
        return render_template('dashboard.html', username=username, client_data=client_data)
    return render_template('dashboard.html', username=username)


@app.route('/add_new_client', methods=['GET', 'POST'])
def add_new_client():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fields = [
            'sector_id',
            'package_id',
            'ssn',
            'first_name',
            'last_name',
            'email',
            'phone_number']
        client_data = {field: request.form.get(field) for field in fields}
        client_data['representative_id'] = session['user_id']
        client_id = insert_new_client(client_data)
        return redirect(url_for('dashboard', clientid=client_id))

    sectors = get_user_sectors(session['user_id'])
    return render_template('add_new_client.html', sectors=sectors)


@app.route('/set_new_pwd', methods=['GET', 'POST'])
def set_new_pwd():
    user_data = session.get('user_data')
    username = session.get("username")
    if not user_data and not username:
        return redirect(url_for('index'))
    if request.method == "POST":
        if not user_data:
            user_data = get_user_data_from_db(username=username)
        if user_data:
            user_email = user_data["email"]
            new_password = request.form.get('new_pwd')
            old_password = request.form.get('old_pwd')

            if (isinstance(old_password, str)):
                if not compare_to_current_password(user_data, old_password):
                    flash("The old password you inserted does not match the current used password.\nPlease try again")
                    return redirect(url_for('set_new_pwd', _method='GET'))

                if not validate_password(new_password):
                    return redirect(url_for('set_new_pwd', _method='GET'))

                if change_user_password_in_db(user_email, new_password):
                    return redirect(url_for('login', password_changed=True))

            else:  # reset from email
                if not validate_password(new_password):
                    return redirect(url_for('set_new_pwd', emailReset=True))
                if change_user_password_in_db(user_email, new_password):
                    return redirect(url_for('login', password_changed=True))
                return redirect(url_for('set_new_pwd', emailReset=True))

    return render_template('set_new_pwd.html', emailReset=request.args.get('emailReset'))

@app.route("/password_reset_token", methods=["GET", "POST"])
def password_reset_token():
    if request.method == "POST":
        token = request.form.get("token")
        return redirect(url_for('password_change', token=token))
    return render_template('password_reset_token.html')


@app.route("/password_change/<string:token>", methods=["GET", "POST"])
def password_change(token):
    if request.method == "GET":
        user_data = check_if_reset_token_exists(token)
        if user_data:
            session['user_data'] = user_data
            return redirect(url_for('set_new_pwd', emailReset=True))
        flash('The code was not valid', 'error')
        return render_template('password_reset.html')


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        user_email = request.form["email"]
        if check_if_user_exists_using_email(email=user_email):
            random_string = ''.join(
                random.choices(
                    string.ascii_uppercase +
                    string.digits,
                    k=20))
            hash_code = hashlib.sha1(
                random_string.encode('utf-8')).digest().hex()

            # Insert password reset info into the database
            insert_password_reset(user_email, hash_code)
            # Send email with the random string (randomly generated token)
            send_email(
                mail=mail,
                recipient=user_email,
                hash_code=random_string)

            flash('An email was sent check your mail inbox', 'info')
            return redirect(url_for('password_reset_token'))
        else:
            flash('The user does not exist', 'error')
            return redirect(url_for('password_reset'))
    else:
        return render_template('password_reset.html')


@app.route('/search_client_data', methods=['POST'])
def search_client_data():
    client_first_name = request.form.get('first_name')
    client_last_name = request.form.get('last_name')
    client_data = get_client_data_by_name(client_first_name, client_last_name)
    if client_data:
        return redirect(url_for('dashboard', client_data=client_data))
    return redirect(url_for('dashboard', client_data=False))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
