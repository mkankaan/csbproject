import db


def add_member(user_id, room_id):
    sql = f"INSERT INTO members (user_id, room_id) VALUES ('{user_id}', '{room_id}')"
    db.execute(sql)


def get_by_room(room_id):
    sql = """SELECT members.user_id, users.username
            FROM members
            LEFT JOIN users ON users.id = members.user_id
            WHERE room_id = ?"""
    return db.query(sql, [room_id])

