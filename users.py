import db


def create_user(username, password):
    sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    db.execute(sql)


def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_all_users():
    sql = "SELECT username, password FROM users"
    return db.query(sql)


def check_password_matches(username, password):
    sql = "SELECT id, password FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 1:
        user_id, correct_password = result[0]

        if password == correct_password:
            return user_id

    return None
