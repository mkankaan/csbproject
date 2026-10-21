import db


def add_member(user_id, room_id):
    sql = f"INSERT INTO members (user_id, room_id) VALUES ('{user_id}', '{room_id}')"
    db.execute(sql)
