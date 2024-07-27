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
import random

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


def get_solutions_based_to_challenge_id(challenge_id: int) -> list:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(
            "SELECT * FROM solutions WHERE challengeID = %s", (challenge_id,))
        return cursor.fetchall()


def get_questions_and_solutions_based_to_categories_list(category) -> tuple | None:
    # Generate a random category from the categories list

    with conn.cursor(as_dict=True) as cursor:
        # Retrieve a random question from the chosen category
        cursor.execute(
            "SELECT * FROM Challenges WHERE category = %s", (category,))
        results = cursor.fetchall()
        if not results:
            return None
        # select a random challenge from all the challenges
        random_challenge = random.choice(results)
        solution = get_solutions_based_to_challenge_id(random_challenge['challengeID'])
        random.shuffle(solution)

    return random_challenge, solution


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
    session['game_grade'] = {}


def finish_game(session) -> int:
    user_score = 0
    for score in session['game_grade'].values():
        user_score += score[0] + score[1]
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


def plot_category_scores(category, user_scores, other_users_scores):
    # Create a figure and a grid of subplots
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))

    # Plot user scores
    if user_scores:
        axs[0].plot(user_scores, marker='o', label='Your Scores')
        axs[0].set_title(f'Your Scores in {category}')
        axs[0].set_xlabel('Attempts')
        axs[0].set_ylabel('Scores')
        axs[0].legend()
    else:
        axs[0].text(0.5, 0.5, 'You haven\'t played yet', horizontalalignment='center', verticalalignment='center')
        axs[0].set_title(f'Your Scores in {category}')
        axs[0].set_xlabel('Attempts')
        axs[0].set_ylabel('Scores')

    # Calculate averages for other users
    other_users_avg_scores = []
    if other_users_scores:
        for scores in other_users_scores:
            filtered_scores = [score for score in scores if score is not None]
            if filtered_scores:
                other_users_avg_scores.append(sum(filtered_scores) / len(filtered_scores))

    # Plot average scores distribution
    if other_users_avg_scores:
        user_avg_score = calculate_average(user_scores)
        min_avg_score = min(other_users_avg_scores + [user_avg_score])
        max_avg_score = max(other_users_avg_scores + [user_avg_score])
        bins = max(10, int(max_avg_score - min_avg_score + 1))  # At least 10 bins

        axs[1].hist(other_users_avg_scores, bins=bins, alpha=0.7, label='Other Users', density=True)
        axs[1].axvline(user_avg_score, color='r', linestyle='dashed', linewidth=2, label='Your Average')
        axs[1].set_title(f'Average Scores Distribution in {category}')
        axs[1].set_xlabel('Average Score')
        axs[1].set_ylabel('Density')
        axs[1].legend()
    else:
        axs[1].text(0.5, 0.5, 'No scores from other users', horizontalalignment='center', verticalalignment='center')
        axs[1].set_title(f'Average Scores Distribution in {category}')
        axs[1].set_xlabel('Average Score')
        axs[1].set_ylabel('Density')

    # Convert the figure to a base64 image
    plt.tight_layout()
    img_str = plot_to_img()
    plt.close(fig)

    return img_str


def get_category_scores(user_id, category):
    with conn.cursor() as cursor:
        cursor.execute(
            f'''SELECT score1, score2, score3, score4, score5
                FROM {category}
                WHERE userID = %s''', (user_id,))
        user_scores = cursor.fetchone()

        cursor.execute(
            f'''SELECT score1, score2, score3, score4, score5
                FROM {category}
                WHERE userID != %s''', (user_id,))
        other_users_scores = cursor.fetchall()

    return user_scores, other_users_scores


def save_grade_based_to_category(user_id: int, grade: float, table_name: str) -> None:
    with conn.cursor() as cursor:
        # Sanitize the table name to prevent SQL injection
        table_name = table_name.replace(" ", "_").lower() + "_scores"  # Example of simple sanitation

        # Ensure that the table_name does not contain any disallowed characters
        if not table_name.isidentifier():
            raise ValueError("Invalid table name")

        # Check if a record exists for the given user in the specified category table
        cursor.execute(
            f'''SELECT score1, score2, score3, score4, score5
                FROM {table_name}
                WHERE userID = %s''', (user_id,)
        )
        result = cursor.fetchone()

        if result:
            # Shift scores and insert the new grade
            score1, score2, score3, score4, score5 = result
            cursor.execute(
                f'''UPDATE {table_name}
                   SET score1 = %s, score2 = %s, score3 = %s, score4 = %s, score5 = %s
                   WHERE userID = %s''',
                (score2, score3, score4, score5, grade, user_id)
            )
        else:
            # Insert a new record if none exists
            cursor.execute(
                f'''INSERT INTO {table_name} (userID, score1, score2, score3, score4, score5)
                   VALUES (%s, NULL, NULL, NULL, NULL, %s)''',
                (user_id, grade)
            )

        conn.commit()


def calculate_average(scores):
    if not scores:
        return 0
    filtered_scores = [score for score in scores if score is not None]
    return sum(filtered_scores) / len(filtered_scores) if filtered_scores else 0


def calculate_user_rank(user_avg_score, other_users_avg_scores):
    if not other_users_avg_scores:
        return "N/A"
    all_avg_scores = other_users_avg_scores + [user_avg_score]
    return sorted(all_avg_scores, reverse=True).index(user_avg_score) + 1


def plot_scores(scores):
    plt.figure(figsize=(10, 5))
    if scores:
        plt.plot(scores, marker='o', label='Your Scores')
        plt.title('Your Last 5 Game Scores')
        plt.xlabel('Games')
        plt.ylabel('Scores')
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'You haven\'t played yet', horizontalalignment='center', verticalalignment='center')
        plt.title('Your Last 5 Game Scores')
        plt.xlabel('Games')
        plt.ylabel('Scores')
    return plot_to_img()


def plot_avg_scores_distribution(user_avg_score, other_users_avg_scores):
    plt.figure(figsize=(10, 5))
    if other_users_avg_scores:
        min_avg_score = min(other_users_avg_scores + [user_avg_score])
        max_avg_score = max(other_users_avg_scores + [user_avg_score])
        bins = max(10, int(max_avg_score - min_avg_score + 1))  # At least 10 bins
        plt.hist(other_users_avg_scores, bins=bins, alpha=0.7, label='Other Users')
        plt.axvline(user_avg_score, color='r', linestyle='dashed', linewidth=2, label='Your Average')
        plt.title('Average Scores Distribution')
        plt.xlabel('Average Score')
        plt.ylabel('Number of Users')
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'No scores from other users', horizontalalignment='center', verticalalignment='center')
        plt.title('Average Scores Distribution')
        plt.xlabel('Average Score')
        plt.ylabel('Number of Users')
    return plot_to_img()


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
