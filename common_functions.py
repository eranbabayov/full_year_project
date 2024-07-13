import pymssql
import os
import time
from dotenv import load_dotenv
from flask import flash
from app_configuration import *
from flask_mail import Message
import hashlib

load_dotenv()
password = os.getenv('MSSQL_SA_PASSWORD')

while True:
    try:
        conn = pymssql.connect(
            "172.17.0.1",
            "sa",
            password,
            "SecurityPerformance")
        break
    except pymssql.OperationalError:
        time.sleep(1)

conn = pymssql.connect("172.17.0.1", "sa", password, "SecurityPerformance")


def get_user_data_from_db(username=None, password=None):
    with conn.cursor(as_dict=True) as cursor:
        if username and password:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password))
        else:
            cursor.execute(
                f"SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()


def get_client_data(client_id):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            "SELECT * FROM clients WHERE client_id = %s", (client_id,))
        return cursor.fetchone()


def get_user_salt(userID):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            "SELECT * FROM user_info WHERE userID = %s", (userID,))
        return cursor.fetchone()['salt']


def check_if_user_exists_using_email(email: str) -> bool:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s ", (email,))
        if cursor.fetchone():  # todo: check if this condition works
            return True
        return False


def insert_new_user_to_db(new_username, new_password, new_email, salt, reset_token=None):
    try:
        # Set autocommit to False to manage transactions manually
        conn.autocommit(False)

        with conn.cursor(as_dict=True) as cursor:
            # Insert into users table
            cursor.execute(
                "INSERT INTO users (username, password, email, reset_token) VALUES (%s, %s, %s, %s)",
                (new_username, new_password, new_email, reset_token))
            userID = cursor.lastrowid

            # Insert into user_info table
            cursor.execute(
                "INSERT INTO user_info (userID, salt) VALUES (%s, %s)",
                (userID, salt))

            # Insert into password_history table
            cursor.execute(
                "INSERT INTO password_history (userID, password, salt) VALUES (%s, %s, %s)",
                (userID, new_password, salt))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        print(f"Error: {e}")

    finally:
        # Restore autocommit mode
        conn.autocommit(True)


def validate_password(password) -> bool:
    password_policy, _ = get_password_policy()
    with open(os.path.abspath('passwords.txt'), 'r') as common_passwords_file:
        for common_pwd in common_passwords_file:
            if password == common_pwd.strip():
                flash('Password is a known password.')
                return False
    rules_messages = get_config_rules_messages()
    if len(password_policy.test(password)) > 0:
        flash('The Password does not meet the minimum requirements ', 'error')
        for missing_requirement in password_policy.test(password):
            splitted = str(missing_requirement).split("(")
            number = splitted[1].replace(")", "")
            flash(
                "Please enter a password with at least " + number + " " +
                rules_messages[splitted[0]])
        return False
    else:
        return True


def insert_password_reset(email, hash_code):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            '''UPDATE users SET reset_token = %s WHERE email = %s''',
            (hash_code, email))
        conn.commit()


def send_email(mail, recipient, hash_code):
    msg = Message(
        "Confirm Password Change",
        sender="compsec2024@gmail.com",
        recipients=[recipient],
    )
    msg.body = (
        "Hello,\nWe've received a request to reset your password. If you want to reset your password, "
        "click the link below and enter your new password\n http://localhost:5000/password_change/"
        + hash_code
        + "\n\nOr enter the following code in the password reset page: "
        + hash_code
    )
    mail.send(msg)


def change_user_password_in_db(email, new_password) -> bool:
    # Check if the new password matches any of the previous passwords
    if check_previous_passwords(email, new_password):
        flash(
            "Please enter a new password that is not the same as your previous passwords.")
        return False
    new_password_hashed_hex, user_salt_hex = generate_new_password_hashed(new_password, generate_to_hex=True)

    # Update the user's password in the database
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            '''UPDATE users SET password = %s WHERE email = %s''',
            (new_password_hashed_hex, email))
        cursor.execute(
            '''UPDATE user_info SET salt = %s WHERE userID = (SELECT userID FROM users WHERE email = %s)''',
            (user_salt_hex, email))
        cursor.execute(
            '''INSERT INTO password_history (userID,password,salt) VALUES ((SELECT userID FROM users WHERE email = %s), %s, %s)''',
            (email, new_password_hashed_hex, user_salt_hex))
        conn.commit()
    return True


def check_previous_passwords(email, user_new_password):
    with conn.cursor(as_dict=True) as cursor:
        # Get the userID based on the email
        cursor.execute(
            '''SELECT userID FROM users WHERE email = %s''',
            (email,))
        userID = cursor.fetchone()['userID']
        # Retrieve the previous three passwords for the user
        cursor.execute(
            '''SELECT TOP 3 * FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY historyID DESC) AS rn
        FROM password_history WHERE userID = %s) AS recent_passwords ORDER BY rn;''',
            (userID,))
        previous_passwords_data = [(row['password'], row['salt'])
                                   for row in cursor.fetchall()]
        return compare_passwords(user_new_password, previous_passwords_data)


def compare_passwords(user_new_password, previous_passwords_data) -> bool:
    for previous_password, previous_salt in previous_passwords_data:
        previous_salt_bytes = bytes.fromhex(previous_salt)
        user_salted_password = hashlib.pbkdf2_hmac(
            'sha256', user_new_password.encode('utf-8'),
            previous_salt_bytes, 100000)
        if user_salted_password == bytes.fromhex(previous_password):
            return True
    return False


def compare_to_current_password(user_data, password) -> bool:
    current_password = user_data['password']
    current_salt = bytes.fromhex(get_user_salt(user_data['userID']))
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'),
        current_salt, 100000)
    if hashed_password == bytes.fromhex(current_password):
        return True
    else:
        return False


def generate_new_password_hashed(new_password, generate_to_hex=False):
    _, salt_len = get_password_policy()
    user_salt = os.urandom(salt_len)
    new_password_hashed = hashlib.pbkdf2_hmac(
        'sha256', new_password.encode('utf-8'),
        user_salt, 100000)  # save in bytes
    if generate_to_hex:
        return new_password_hashed.hex(), user_salt.hex()
    return new_password_hashed, user_salt


def check_if_reset_token_exists(reset_token):
    with conn.cursor(as_dict=True) as cursor:
        hashed_token = hashlib.sha1(
            reset_token.encode('utf-8')).digest().hex()
        cursor.execute(
            '''SELECT * FROM users WHERE reset_token = %s''',
            (hashed_token,))
        return cursor.fetchone()
