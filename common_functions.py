import pymssql
import time
from flask import flash
from app_configuration import *
from flask_mail import Message
import hashlib
import logging
import matplotlib.pyplot as plt
import base64
from io import BytesIO

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
        print("unable to connect")
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


def insert_new_user_to_db(new_username, new_password, new_email, salt):
    with conn.cursor(as_dict=True) as cursor:
        # Start a transaction
        conn.autocommit(False)
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (new_username, new_password, new_email))
        userID = cursor.lastrowid
        cursor.execute(
            "INSERT INTO user_info (userID,salt) VALUES (%s, %s)",
            (userID, salt))
        cursor.execute(
            "INSERT INTO password_history (userID,password,salt) VALUES (%s, %s, %s)",
            (userID, new_password, salt))
        cursor.execute(
            "INSERT INTO user_scores (userID) VALUES (%s)",
            (userID,))
        # Commit the transaction
        conn.commit()


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


def check_if_reset_token_exists(reset_token) -> dict:
    with conn.cursor(as_dict=True) as cursor:
        hashed_token = hashlib.sha1(
            reset_token.encode('utf-8')).digest().hex()
        cursor.execute(
            '''SELECT * FROM users WHERE reset_token = %s''',
            (hashed_token,))
        return cursor.fetchone()


def get_challenges_based_to_challenge_id(challenge_id: int) -> dict:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            "SELECT * FROM Challenges WHERE challengeID = %s", (challenge_id,))
        return cursor.fetchone()


def get_solutions_based_to_challenge_id(challenge_id: int) -> dict:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            "SELECT * FROM solutions WHERE challengeID = %s", (challenge_id,))
        return cursor.fetchall()


def insert_new_grade(user_id: int, grade: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            '''SELECT score1, score2, score3, score4, score5
               FROM last_games_grade
               WHERE userID = %s''', (user_id,))
        result = cursor.fetchone()

        if result:
            score1, score2, score3, score4, score5 = result
            cursor.execute(
                '''UPDATE last_games_grade
                   SET score1 = %s, score2 = %s, score3 = %s, score4 = %s, score5 = %s
                   WHERE userID = %s''',
                (score2, score3, score4, score5, grade, user_id))
        else:
            cursor.execute(
                '''INSERT INTO last_games_grade (userID, score1, score2, score3, score4, score5)
                   VALUES (%s, NULL, NULL, NULL, NULL, %s)''', (user_id, grade))
        conn.commit()


def initialize_game_grade_session_as_dictionary(session):
    if 'game_grade' not in session:
        session['game_grade'] = {}
    elif not isinstance(session['game_grade'], dict):
        session['game_grade'] = {}


def finish_game(session) -> int:
    number_of_answer_questions = len(session['game_grade'].keys())
    logging.debug("########################")
    logging.debug(number_of_answer_questions)
    user_score = 0
    for score in session['game_grade'].values():
        user_score += score[0] + score[1]
    logging.debug(f"user score is: {user_score}")
    total_possible = len(session['game_grade']) * 200
    final_grade = user_score / total_possible * 100 if total_possible > 0 else 0
    final_grade = int(final_grade)
    insert_new_grade(user_id=session['userID'], grade=final_grade)
    return final_grade


def get_summarise_user_info(user_id):
    with conn.cursor() as cursor:
        cursor.execute(
            '''SELECT score1, score2, score3, score4, score5
               FROM last_games_grade
               WHERE userID = %s''', (user_id,))
        user_scores = cursor.fetchone()

        cursor.execute(
            '''SELECT score1, score2, score3, score4, score5
               FROM last_games_grade
               WHERE userID != %s''', (user_id,))
        other_users_scores = cursor.fetchall()

    return user_scores, other_users_scores


def plot_to_img():
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64


if __name__ == '__main__':
    solution_data = get_solutions_based_to_challenge_id(0)
    for solution_key, val in solution_data.items():
        print(solution_key)
        print(val)
