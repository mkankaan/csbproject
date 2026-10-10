import db

def create_user(username, password):
    sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    db.execute(sql)

def get_all_users():
    sql = "SELECT username FROM users"
    return db.query(sql)
